"""Tests for the CLI entrypoint."""

import json
from pathlib import Path

import responses

from eidolon.cli import main

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@responses.activate
def test_main_with_url(tmp_path: Path) -> None:
    """Fetch CSV via --url, generate nginx config with valid resolvers."""
    csv_text = (FIXTURES_DIR / "sample.csv").read_text()
    responses.add(
        responses.GET, "https://example.com/test.csv", body=csv_text, status=200
    )

    output = tmp_path / "nginx.conf"
    rc = main(["--url", "https://example.com/test.csv", "--output", str(output)])

    assert rc == 0
    content = output.read_text()
    assert "server 1.2.3.4:53;" in content
    assert "server 9.10.11.12:53;" in content
    assert "2001:db8::1" not in content


@responses.activate
def test_main_with_tag(tmp_path: Path) -> None:
    """Resolve a tag via tags.json and fetch the correct URL."""
    csv_text = (FIXTURES_DIR / "sample.csv").read_text()
    responses.add(
        responses.GET,
        "https://public-dns.info/nameserver/gb.csv",
        body=csv_text,
        status=200,
    )

    tags_file = tmp_path / "tags.json"
    tags_file.write_text(json.dumps({"gb": "nameserver/gb.csv"}))

    output = tmp_path / "nginx.conf"
    rc = main(["--tag", "gb", "--tags-file", str(tags_file), "--output", str(output)])

    assert rc == 0
    assert output.exists()


@responses.activate
def test_main_http_failure(tmp_path: Path) -> None:
    """HTTP 500 results in exit code 1 and no output file."""
    responses.add(responses.GET, "https://example.com/fail.csv", status=500)

    output = tmp_path / "nginx.conf"
    rc = main(["--url", "https://example.com/fail.csv", "--output", str(output)])

    assert rc == 1
    assert not output.exists()


@responses.activate
def test_main_no_valid_resolvers(tmp_path: Path) -> None:
    """Exit code 1 when all resolvers are filtered out."""
    csv_text = "ip,reliability\n2001:db8::1,1.00\n"
    responses.add(
        responses.GET, "https://example.com/test.csv", body=csv_text, status=200
    )

    output = tmp_path / "nginx.conf"
    rc = main(["--url", "https://example.com/test.csv", "--output", str(output)])

    assert rc == 1


def test_main_unknown_tag(tmp_path: Path) -> None:
    """Exit code 1 when the requested tag is not in tags.json."""
    tags_file = tmp_path / "tags.json"
    tags_file.write_text(json.dumps({"gb": "nameserver/gb.csv"}))

    output = tmp_path / "nginx.conf"
    rc = main(["--tag", "xx", "--tags-file", str(tags_file), "--output", str(output)])

    assert rc == 1
