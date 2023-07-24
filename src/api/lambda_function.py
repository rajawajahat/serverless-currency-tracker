import json
import pymysql

# Database connection configuration
db_config = {
    "host": "mydb-rds.ci36p2p5xaob.us-east-1.rds.amazonaws.com",
    "user": "gauthier",
    "password": "kolweziYetu",
    "database": "kolwezidb",
}


def get_currency_data(event, context):
    try:
        # Connect to the database
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Execute the query to fetch currency data
        sql = "SELECT currency, today, yesterday, difference FROM currency"
        cursor.execute(sql)
        currency_data = cursor.fetchall()

        # Close the database connection
        cursor.close()
        conn.close()

        # Return the data as a JSON response
        response = {
            "statusCode": 200,
            "body": json.dumps(currency_data)
        }
        return response
    except Exception as e:
        # In case of an error, return an error response
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
        return response
