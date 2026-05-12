"""Download CSV data from public-dns.info."""

import requests

BASE_URL = "https://public-dns.info/"


def fetch_csv(url: str, timeout: int = 30) -> str:
    """Download CSV content from a URL and return decoded UTF-8 text."""
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.content.decode("utf-8")


def build_url(csv_path: str) -> str:
    """Construct a full public-dns.info URL from a CSV path fragment."""
    return BASE_URL + csv_path
