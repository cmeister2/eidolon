"""Download CSV data from public-dns.info."""

import logging
import time

import requests

BASE_URL = "https://public-dns.info/"

log = logging.getLogger(__name__)


def fetch_csv(url: str, timeout: int = 30, retries: int = 3) -> str:
    """Download CSV content from a URL and return decoded UTF-8 text.

    Retries on connection errors with exponential backoff.
    """
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r.content.decode("utf-8")
        except requests.ConnectionError as e:
            last_exc = e
            if attempt < retries - 1:
                delay = 2 ** (attempt + 1)
                log.warning(
                    "Attempt %d failed (%s), retrying in %ds", attempt + 1, e, delay
                )
                time.sleep(delay)
    raise last_exc  # type: ignore[misc]


def build_url(csv_path: str) -> str:
    """Construct a full public-dns.info URL from a CSV path fragment."""
    return BASE_URL + csv_path
