import json
import pytest
from unittest import mock
from src.api.lambda_function import get_currency_data


def test_get_currency_data_success(mock_environment_variables):
    # Mocking the pymysql.connect and cursor to return dummy data
    with mock.patch('pymysql.connect') as mock_connect, \
         mock_connect.return_value.cursor.return_value as mock_cursor:

        # Sample currency data to be returned by the query
        sample_currency_data = [
            {"currency": "USD", "today": 1.2345, "yesterday": 1.234, "difference": 0.0005},
            {"currency": "EUR", "today": 1.0, "yesterday": 0.998, "difference": 0.002},
        ]

        # Mocking the fetchall method to return the sample currency data
        mock_cursor.fetchall.return_value = sample_currency_data

        # Calling the function to get currency data
        response = get_currency_data({}, {})

        print(f"check: {response}")
    # # Asserting the response
    # assert response["statusCode"] == 200
    # assert json.loads(response["body"]) == sample_currency_data


def test_get_currency_data_failure(mock_environment_variables):
    # Mocking the pymysql.connect and cursor to raise an exception
    with mock.patch('pymysql.connect') as mock_connect, \
         mock_connect.return_value.cursor.return_value as mock_cursor:

        # Mocking the execute method to raise an exception
        mock_cursor.execute.side_effect = Exception("Error executing query")

        # Calling the function to get currency data
        response = get_currency_data({}, {})

    # Asserting the response
    assert response["statusCode"] == 500
    assert "error" in json.loads(response["body"])
