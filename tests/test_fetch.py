"""Tests for CSV fetching."""

import responses

from eidolon.fetch import USER_AGENT, fetch_csv


@responses.activate
def test_fetch_csv_sends_user_agent() -> None:
    """public-dns.info receives an identifying User-Agent."""
    url = "https://example.com/resolvers.csv"
    responses.add(responses.GET, url, body="ip,reliability\n", status=200)

    assert fetch_csv(url) == "ip,reliability\n"
    assert responses.calls[0].request.headers["User-Agent"] == USER_AGENT
