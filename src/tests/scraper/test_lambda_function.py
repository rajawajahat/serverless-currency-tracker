import json
import os
import pytest
from unittest import mock
from src.scraper.ecbe_exchange_scraper import ECBExchangeRateScraper
from src.scraper.lambda_function import get_exchange_rates, calculate_difference, update_database, fetch_currency_data


@pytest.fixture
def mocked_connection():
    with mock.patch('pymysql.connect') as mocked_connect:
        mocked_connection = mocked_connect.return_value
        yield mocked_connection


@pytest.fixture
def mocked_cursor(mocked_connection):
    mocked_cursor = mocked_connection.cursor.return_value
    yield mocked_cursor


@pytest.fixture
def mocked_scraper():
    with mock.patch.object(ECBExchangeRateScraper, 'scrape') as mocked_scrape:
        yield mocked_scrape


@pytest.fixture
def mocked_execute_query():
    with mock.patch('src.scraper.lambda_function.execute_query') as mocked_execute:
        yield mocked_execute


def test_get_exchange_rates(mocked_scraper):
    test_rates = [
        {"currency": "USD", "today": 1.2345},
        {"currency": "EUR", "today": 1.0},
        {"currency": "GBP", "today": 0.8765}
    ]
    mocked_scraper.return_value = test_rates
    exchange_rates = get_exchange_rates()
    assert exchange_rates == test_rates


def test_get_exchange_rates_exception(mocked_scraper):
    mocked_scraper.side_effect = Exception("Failed to fetch exchange rates")
    exchange_rates = get_exchange_rates()
    assert exchange_rates == []


def test_calculate_difference():
    today_rate = 1.2345
    yesterday_rate = 1.234
    difference = calculate_difference(today_rate, yesterday_rate)
    assert difference == pytest.approx(0.0005, abs=1e-5)


def test_update_database_insert(mocked_connection):
    mocked_cursor = mocked_connection.cursor.return_value
    mocked_cursor.fetchone.return_value = {"COUNT(*)": 0}

    update_database(mocked_connection, "USD", 1.2345, 0.0005)
    mocked_connection.commit.assert_called_once()


def test_update_database_update(mocked_connection):
    mocked_cursor = mocked_connection.cursor.return_value
    mocked_cursor.fetchone.return_value = {"COUNT(*)": 1}

    update_database(mocked_connection, "USD", 1.2346, 0.0001)
    mocked_connection.commit.assert_called_once()


def test_fetch_currency_data_success(mocked_connection, mocked_cursor, mocked_scraper, mock_environment_variables):
    test_rates = [
        {"currency": "USD", "today": 1.2345},
        {"currency": "EUR", "today": 1.0},
        {"currency": "GBP", "today": 0.8765}
    ]
    mocked_scraper.return_value = test_rates
    mocked_cursor.fetchall.return_value = [
        {"currency": "USD", "today": 1.2344},
        {"currency": "EUR", "today": 1.1},
        {"currency": "JPY", "today": 123.45}
    ]

    response = fetch_currency_data({}, {})
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == "Currency exchange rates updated successfully."