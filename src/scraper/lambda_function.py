import json


def fetch_currency_data(event, context):
    response = {
        "response": "hello"
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }
