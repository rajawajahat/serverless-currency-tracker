import pytest
from unittest import mock
from src.scraper.ecbe_exchange_scraper import ECBExchangeRateScraper


@pytest.fixture
def mocked_requests_get():
    with mock.patch('requests.get') as mocked_get:
        yield mocked_get


def test_scrape_success(mocked_requests_get):
    url = "https://www.example.com"
    test_html = """
    <table class="forextable">
        <tr><td>Currency</td><td>Exchange</td><td>Rate</td></tr>
        <tr><td>USD</td><td>Exchange</td><td>1.2345</td></tr>
        <tr><td>EUR</td><td>Exchange</td><td>1.0</td></tr>
        <tr><td>GBP</td><td>Exchange</td><td>0.8765</td></tr>
    </table>
    """
    mocked_requests_get.return_value.text = test_html

    scraper = ECBExchangeRateScraper(url)
    exchange_rates = scraper.scrape()

    assert len(exchange_rates) == 3
    assert exchange_rates == [
        {"currency": "USD", "today": 1.2345},
        {"currency": "EUR", "today": 1.0},
        {"currency": "GBP", "today": 0.8765}
    ]


def test_scrape_no_table(mocked_requests_get):
    url = "https://www.example.com"
    test_html = "<html><body><h1>No Table Here</h1></body></html>"
    mocked_requests_get.return_value.text = test_html

    scraper = ECBExchangeRateScraper(url)
    exchange_rates = scraper.scrape()

    assert len(exchange_rates) == 0


def test_scrape_parse_error(mocked_requests_get):
    url = "https://www.example.com"
    test_html = """
    <table class="forextable">
        tr><td>Currency</td><td>Exchange</td><td>Rate</td></tr>
    </table>
    """
    mocked_requests_get.return_value.text = test_html

    scraper = ECBExchangeRateScraper(url)
    exchange_rates = scraper.scrape()
    assert len(exchange_rates) == 0
