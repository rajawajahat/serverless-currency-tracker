import os
import json
import pymysql
from src.scraper.ecbe_exchange_scraper import ECBExchangeRateScraper


def get_exchange_rates() -> list[dict]:
    """
    Fetches exchange rates from the ECB website.

    Returns:
        list[dict]: A list of exchange rate data in the form of dictionaries.
    """
    url = "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/" \
          "euro_reference_exchange_rates/html/index.en.html"
    try:
        scraper = ECBExchangeRateScraper(url)
        exchange_rates = scraper.scrape()
        return exchange_rates
    except Exception as e:
        print(f"Failed to fetch exchange rates: {str(e)}")
        return []


def calculate_difference(current_rate: float, previous_rate: float) -> float:
    """
    Calculates the difference between two exchange rates.

    Args:
        current_rate (float): The current exchange rate.
        previous_rate (float): The previous exchange rate.

    Returns:
        float: The difference between the current rate and the previous rate.
    """
    return round(current_rate - previous_rate, 4)


def execute_query(cursor, sql: str, params: tuple = None) -> None:
    """
    Executes a SQL query on the database.

    Args:
        cursor: The database cursor.
        sql (str): The SQL query to execute.
        params (tuple, optional): The parameters for the query. Defaults to None.
    """
    try:
        cursor.execute(sql, params)
        print("Query executed successfully.")
    except Exception as e:
        print(f"Failed to execute query: {str(e)}")


def update_database(connection, currency: str, today_rate: float, difference: float) -> None:
    """
    Updates the database with the latest exchange rates.

    Args:
        connection: The database connection.
        currency (str): The currency code.
        today_rate (float): The current exchange rate.
        difference (float): The difference between the current rate and the previous rate.
    """
    with connection.cursor() as cursor:
        sql_check_currency = "SELECT COUNT(*) FROM currency WHERE currency = %s"
        cursor.execute(sql_check_currency, currency)
        record_count = cursor.fetchone()

        if record_count["COUNT(*)"] == 0:
            print("Needs insert.")
            sql_insert_currency = "INSERT INTO currency (currency, today) VALUES (%s, %s)"
            execute_query(cursor, sql_insert_currency, (currency, today_rate))
        else:
            print("Needs update.")
            sql_update_today = "UPDATE currency SET yesterday = today, today = %s, difference = %s WHERE currency = %s"
            execute_query(cursor, sql_update_today, (today_rate, difference, currency))

        connection.commit()
        print("Database updated successfully.")


def fetch_currency_data(event, context) -> dict:
    try:
        rds_host = os.environ["RDS_HOST"]
        rds_user = os.environ["RDS_USERNAME"]
        rds_pass = os.environ["RDS_PASSWORD"]
        rds_db = os.environ["RDS_NAME"]

        connection = pymysql.connect(host=rds_host, user=rds_user, password=rds_pass,
                                     db=rds_db, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

        today_rates = get_exchange_rates()

        yesterday_rates = {}
        with connection.cursor() as cursor:
            sql = "SELECT * FROM currency"
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                yesterday_rates[row["currency"]] = row["today"]

        print(f"yesterday rates: {yesterday_rates}")

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