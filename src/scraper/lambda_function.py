import os
from scraper.ecbe_exchange_scraper import ECBExchangeRateScraper
import json
import pymysql


def get_exchange_rates():
    url = "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/" \
          "euro_reference_exchange_rates/html/index.en.html"
    try:
        scraper = ECBExchangeRateScraper(url)
        exchange_rates = scraper.scrape()
        return exchange_rates
    except Exception as e:
        print(f"Failed to fetch exchange rates: {str(e)}")
        return []


def calculate_difference(current_rate, previous_rate):
    return round(current_rate - previous_rate, 4)


def update_database(connection, currency, today_rate, difference):
    try:
        with connection.cursor() as cursor:
            # Check if the currency record already exists in the table
            sql_check_currency = "SELECT COUNT(*) FROM currency WHERE currency = %s"
            cursor.execute(sql_check_currency, currency)
            record_count = cursor.fetchone()

            print(f"fetchone: {record_count}")

            if record_count["COUNT(*)"] == 0:
                print("Needs insert.")
                # If no record exists, insert a new record with today's rate
                sql_insert_currency = "INSERT INTO currency (currency, today) VALUES (%s, %s)"
                cursor.execute(sql_insert_currency, (currency, today_rate))
            else:
                print("Needs update.")
                # If record exists, update yesterday's rate and today's rate along with the difference
                sql_update_today = "UPDATE currency SET yesterday = today, today = " \
                                   "%s, difference = %s WHERE currency = %s "
                cursor.execute(sql_update_today, (today_rate, difference, currency))

            print("Done with updating")

        print("Committing")
        connection.commit()
        print("committed, done.")
    except Exception as e:
        print(f"Failed to update database: {str(e)}")


def fetch_currency_data(event, context):
    try:
        # Connect to the RDS database
        rds_host = os.environ["RDS_HOST"]
        rds_user = os.environ["RDS_USERNAME"]
        rds_pass = os.environ["RDS_PASSWORD"]
        rds_db = os.environ["RDS_NAME"]

        connection = pymysql.connect(host=rds_host,
                                     user=rds_user,
                                     password=rds_pass,
                                     db=rds_db,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        # Fetch today's exchange rates
        today_rates = get_exchange_rates()

        # Get yesterday's rates from the database
        yesterday_rates = {}
        with connection.cursor() as cursor:
            sql = "SELECT * FROM currency"
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                yesterday_rates[row["currency"]] = row["today"]

        print(f"yesterday rates: {yesterday_rates}")

        # Calculate the difference and update the database
        for exchange_rate in today_rates:
            currency = exchange_rate['currency']
            today_rate = exchange_rate['today']
            yesterday = yesterday_rates.get(currency, 0)

            print(f"currency: {currency}")
            print(f"today: {today_rate}")
            print(f"yesterday: {yesterday}")

            difference = calculate_difference(today_rate, yesterday)
            print(f"Difference between today and yesterday: {difference}")
            update_database(connection, currency, today_rate, difference)

        connection.close()
        return {
            "statusCode": 200,
            "body": json.dumps("Currency exchange rates updated successfully.")
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"An error occurred while updating currency exchange rates: {str(e)}.")
        }
