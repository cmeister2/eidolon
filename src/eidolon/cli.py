"""CLI entrypoint for generating nginx DNS load-balancer config."""

import argparse
import json
import logging
import sys
from pathlib import Path

from eidolon.fetch import build_url, fetch_csv
from eidolon.filter import filter_resolvers, parse_resolvers
from eidolon.nginx import render_nginx_conf, write_nginx_conf

log = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """Fetch resolver CSV, filter, and write nginx config. Returns 0 on success."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5.5s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Generate nginx DNS load-balancer config"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--tag", help="Tag name from tags.json (e.g. global, gb, us)")
    source.add_argument("--url", help="Explicit CSV URL to download")
    parser.add_argument(
        "--tags-file",
        default="tags.json",
        help="Path to tags.json",
    )
    parser.add_argument("--output", required=True, help="Output path for nginx.conf")
    parser.add_argument(
        "--min-reliability",
        type=float,
        default=0.99,
        help="Minimum reliability threshold (default: 0.99)",
    )

    args = parser.parse_args(argv)

    if args.tag:
        tags_path = Path(args.tags_file)
        if not tags_path.exists():
            log.error("Tags file not found: %s", tags_path)
            return 1
        try:
            tags = json.loads(tags_path.read_text())
        except json.JSONDecodeError:
            log.error("Invalid JSON in tags file: %s", tags_path)
            return 1
        csv_path = tags.get(args.tag)
        if csv_path is None:
            log.error("Unknown tag %r. Available: %s", args.tag, ", ".join(tags.keys()))
            return 1
        url = build_url(csv_path)
    else:
        url = args.url

    log.info("Downloading: %s", url)
    try:
        csv_text = fetch_csv(url)
    except Exception:
        log.exception("Failed to download CSV")
        return 1

    resolvers = parse_resolvers(csv_text)
    ips = filter_resolvers(resolvers, min_reliability=args.min_reliability)

    if not ips:
        log.error("No valid resolvers found after filtering")
        return 1

    log.info("Filtered to %d valid resolvers out of %d total", len(ips), len(resolvers))

    conf = render_nginx_conf(ips)
    write_nginx_conf(conf, args.output)
    log.info("Wrote nginx config to %s", args.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
