import requests
from bs4 import BeautifulSoup


class ECBExchangeRateScraper:
    def __init__(self, url):
        self.url = url

    def scrape(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return self.parse(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data from the URL: {e}")
            return []

    def parse(self, html):
        try:
            soup = BeautifulSoup(html, "html.parser")
            exchange_rates_table = soup.find("table", {"class": "forextable"})
            if not exchange_rates_table:
                print("No exchange rates table found.")
                return []

            exchange_rates = []
            rows = exchange_rates_table.find_all("tr")
            for row in rows[1:]:  # Skipping the header row
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


# Example usage:
if __name__ == "__main__":
    url = "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"
    scraper = ECBExchangeRateScraper(url)
    exchange_rates = scraper.scrape()
    print(exchange_rates)
