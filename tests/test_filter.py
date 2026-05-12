"""Tests for CSV parsing and resolver filtering."""

from eidolon.filter import Resolver, filter_resolvers, parse_resolvers


def test_parse_resolvers(sample_csv: str) -> None:
    """Parse the sample fixture and verify all rows are read."""
    resolvers = parse_resolvers(sample_csv)
    assert len(resolvers) == 6
    assert resolvers[0] == Resolver(ip="1.2.3.4", reliability=1.0)


def test_parse_resolvers_empty() -> None:
    """Empty input and header-only CSV both produce empty lists."""
    assert parse_resolvers("") == []
    assert parse_resolvers("ip,reliability\n") == []


def test_parse_resolvers_malformed_reliability() -> None:
    """Rows with non-numeric reliability are skipped."""
    csv_text = "ip,reliability\n1.2.3.4,bad\n5.6.7.8,0.99\n"
    resolvers = parse_resolvers(csv_text)
    assert len(resolvers) == 1
    assert resolvers[0].ip == "5.6.7.8"


def test_parse_resolvers_missing_fields() -> None:
    """Rows with missing ip or reliability are skipped."""
    csv_text = "ip,reliability\n,1.00\n1.2.3.4,\n"
    assert parse_resolvers(csv_text) == []


def test_filter_ipv4_only() -> None:
    """IPv6 addresses are excluded."""
    resolvers = [
        Resolver(ip="1.2.3.4", reliability=1.0),
        Resolver(ip="2001:db8::1", reliability=1.0),
    ]
    result = filter_resolvers(resolvers)
    assert result == ["1.2.3.4"]


def test_filter_reliability_threshold() -> None:
    """Only resolvers meeting the minimum reliability are included."""
    resolvers = [
        Resolver(ip="1.2.3.4", reliability=1.0),
        Resolver(ip="5.6.7.8", reliability=0.50),
        Resolver(ip="9.10.11.12", reliability=0.99),
        Resolver(ip="10.0.0.1", reliability=0.98),
    ]
    result = filter_resolvers(resolvers, min_reliability=0.99)
    assert result == ["1.2.3.4", "9.10.11.12"]


def test_filter_combined(sample_csv: str) -> None:
    """Both IPv4 and reliability filters applied to the sample fixture."""
    resolvers = parse_resolvers(sample_csv)
    result = filter_resolvers(resolvers, min_reliability=0.99)
    assert result == ["1.2.3.4", "192.168.1.1", "9.10.11.12"]


def test_filter_output_sorted() -> None:
    """Output IPs are sorted for deterministic nginx config."""
    resolvers = [
        Resolver(ip="9.0.0.1", reliability=1.0),
        Resolver(ip="1.0.0.1", reliability=1.0),
        Resolver(ip="5.0.0.1", reliability=1.0),
    ]
    result = filter_resolvers(resolvers)
    assert result == ["1.0.0.1", "5.0.0.1", "9.0.0.1"]


def test_filter_custom_threshold() -> None:
    """A custom reliability threshold is respected."""
    resolvers = [
        Resolver(ip="1.2.3.4", reliability=0.80),
        Resolver(ip="5.6.7.8", reliability=0.70),
    ]
    result = filter_resolvers(resolvers, min_reliability=0.75)
    assert result == ["1.2.3.4"]


def test_filter_nan_reliability() -> None:
    """Resolvers with NaN reliability are excluded."""
    resolvers = [
        Resolver(ip="1.2.3.4", reliability=float("nan")),
        Resolver(ip="5.6.7.8", reliability=1.0),
    ]
    result = filter_resolvers(resolvers)
    assert result == ["5.6.7.8"]


def test_filter_inf_reliability() -> None:
    """Resolvers with infinite reliability are excluded."""
    resolvers = [
        Resolver(ip="1.2.3.4", reliability=float("inf")),
        Resolver(ip="5.6.7.8", reliability=float("-inf")),
        Resolver(ip="9.10.11.12", reliability=1.0),
    ]
    result = filter_resolvers(resolvers)
    assert result == ["9.10.11.12"]


def test_parse_resolvers_ip_address_column() -> None:
    """The real public-dns.info CSV uses ip_address, not ip."""
    csv_text = "ip_address,name,reliability\n1.2.3.4,,1.00\n5.6.7.8,,0.50\n"
    resolvers = parse_resolvers(csv_text)
    assert len(resolvers) == 2
    assert resolvers[0] == Resolver(ip="1.2.3.4", reliability=1.0)
