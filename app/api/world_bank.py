import requests
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from ..utils import format_population


def fetch_country_data(country_code):
    # Example: Population indicator (SP.POP.TOTL)
    code = country_code.strip().upper()
    url = f"https://api.worldbank.org/v2/country/{code}/indicator/SP.POP.TOTL?format=json"

    try:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except requests.exceptions.SSLError:
            response = requests.get(url, timeout=20, verify=False)
            response.raise_for_status()
        raw_data = response.json()

        # World Bank returns a list where the second element is the data
        series = raw_data[1] if len(raw_data) > 1 else None
        latest_val = series[0].get("value") if series else None

        pop_display = format_population(latest_val)

        return {
            "country": code,
            "population": latest_val,
            "population_display": pop_display,
            "source": "World Bank",
        }
    except Exception as e:
        return {"country": code, "error": str(e), "source": "World Bank"}


def fetch_indicator_latest(country_code, indicator_id):
    code = country_code.strip().upper()
    ind = indicator_id.strip().upper()
    url = f"https://api.worldbank.org/v2/country/{code}/indicator/{ind}?format=json"

    try:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except requests.exceptions.SSLError:
            response = requests.get(url, timeout=20, verify=False)
            response.raise_for_status()
        raw_data = response.json()
        series = raw_data[1] if len(raw_data) > 1 else None
        if not series:
            return None
        for point in series:
            val = point.get("value")
            if val is not None:
                return val
        return None
    except Exception:
        return None