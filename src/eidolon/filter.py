"""Parse and filter DNS resolver data from CSV."""

import csv
import ipaddress
from dataclasses import dataclass


@dataclass(frozen=True)
class Resolver:
    """A DNS resolver with its IP address and reliability score."""

    ip: str
    reliability: float


def parse_resolvers(csv_text: str) -> list[Resolver]:
    """Parse CSV text into Resolver objects, skipping malformed rows."""
    resolvers: list[Resolver] = []
    for row in csv.DictReader(csv_text.splitlines(), delimiter=","):
        ip = (row.get("ip") or row.get("ip_address") or "").strip()
        reliability_str = row.get("reliability", "").strip()
        if not ip or not reliability_str:
            continue
        try:
            reliability = float(reliability_str)
        except ValueError:
            continue
        resolvers.append(Resolver(ip=ip, reliability=reliability))
    return resolvers


def filter_resolvers(
    resolvers: list[Resolver],
    min_reliability: float = 0.99,
    ipv4_only: bool = True,
) -> list[str]:
    """Filter resolvers by reliability and IP version, returning sorted IPs."""
    result: list[str] = []
    for r in resolvers:
        if r.reliability < min_reliability:
            continue
        if ipv4_only:
            try:
                ipaddress.IPv4Address(r.ip)
            except (ipaddress.AddressValueError, ValueError):
                continue
        result.append(r.ip)
    result.sort()
    return result
