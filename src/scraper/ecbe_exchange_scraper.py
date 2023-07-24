import requests
from bs4 import BeautifulSoup
from typing import List, Dict


class ECBExchangeRateScraper:
    def __init__(self, url: str):
        """
        Initialize the ECBExchangeRateScraper with the given URL.

        Args:
            url (str): The URL from which to fetch exchange rate data.
        """
        self.url = url

    def scrape(self) -> List[Dict[str, float]]:
        """
        Fetch exchange rate data from the ECB website.

        Returns:
            List[Dict[str, float]]: A list of dictionaries containing currency and exchange rate data.
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return self.parse(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data from the URL: {e}")
            return []

    def parse(self, html: str) -> List[Dict[str, float]]:
        """
        Parse the HTML to extract exchange rate data.

        Args:
            html (str): The HTML content to parse.

        Returns:
            List[Dict[str, float]]: A list of dictionaries containing currency and exchange rate data.
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            exchange_rates_table = soup.find("table", {"class": "forextable"})
            if not exchange_rates_table:
                print("No exchange rates table found.")
                return []

            exchange_rates = []
            rows = exchange_rates_table.find_all("tr")
            for row in rows[1:]:
                columns = row.find_all("td")
                if len(columns) >= 2:
                    currency = columns[0].text.strip()
                    rate_str = columns[2].text.strip()
                    rate = float(rate_str) if rate_str != "N/A" else 0.0
                    exchange_rates.append({"currency": currency, "today": rate})

            return exchange_rates
        except Exception as e:
            print(f"Error while parsing the HTML: {e}")
            return []
