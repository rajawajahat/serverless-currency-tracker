import json
import pymysql
import os
from typing import Dict, Any


def get_currency_data(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Fetch currency data from the database and return as a JSON response.

    Args:
        event (dict): The event data (unused in this function).
        context (Any): The context data (unused in this function).

    Returns:
        dict: A dictionary containing the JSON response with currency data or an error message.
    """
    try:
        db_config = {
            "host": os.environ["DB_HOST"],
            "user": os.environ["DB_USER"],
            "password": os.environ["DB_PASSWORD"],
            "database": os.environ["DB_NAME"],
        }

        with pymysql.connect(**db_config) as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT currency, today, yesterday, difference FROM currency"
            cursor.execute(sql)
            currency_data = cursor.fetchall()

        response = {
            "statusCode": 200,
            "body": json.dumps(currency_data)
        }
        return response
    except Exception as e:
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
        return response
