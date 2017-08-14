#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Imports resolvers into a database from the public-dns.info data"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import argparse
import csv
import logging
import requests
import sys
import dnsresolver
import resolver_db
log = logging.getLogger(__name__)


def resolver_publicdns(args: argparse.Namespace):
    """
    Test a list of IP addresses and add valid addresses to the database file
    """
    # Get a database for the resolvers
    db = resolver_db.ResolverDB(args.database)

    if args.publicdns == "global":
        # Special target - download all servers
        target = "https://public-dns.info/nameservers.csv"
    else:
        # Download the associated target CSV file
        target = ("http://public-dns.info/nameserver/{filename}.csv"
                  .format(filename=args.publicdns))
    r = requests.get(target)

    # If the download failed, exit here instead
    r.raise_for_status()

    # The CSV data is in hand. Use the CSV reader to read it.
    decoded_content = r.content.decode('utf-8')

    all_resolvers = list(csv.DictReader(decoded_content.splitlines(), delimiter=','))
    valid_resolvers = [dnsresolver.DNSResolver(res["ip"])
                       for res in all_resolvers
                       if res["reliability"] == "1.00"]
    db.set_valid_many(valid_resolvers)

    log.info("Imported %d valid resolvers out of %d", len(valid_resolvers), len(all_resolvers))

    return ScriptRC.SUCCESS


def main():
    """Main handling function. Wraps resolver_import."""

    stdout_fmt = logging.Formatter("%(asctime)s %(levelname)-5.5s %(message)s")
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(stdout_fmt)
    stdout_handler.setLevel(logging.INFO)

    file_fmt = logging.Formatter("%(asctime)s %(levelname)-5.5s %(message)s")
    file_handler = logging.FileHandler(filename="import.log",
                                       mode="w")
    file_handler.setFormatter(file_fmt)
    file_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.DEBUG)

    # Run main script.
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--database", help="Database filename (SQLite)", required=True)
        parser.add_argument("--publicdns", help="Which CSV file to download from http://public-dns.info",
                            required=True)

        args = parser.parse_args()
        rc = resolver_publicdns(args)

    except Exception as e:
        log.exception(e)
        rc = ScriptRC.EXCEPTION

    log.info("Returning %d", rc)
    return rc


class ScriptRC(object):
    SUCCESS = 0
    FAILURE = 1
    EXCEPTION = 2


class ScriptException(Exception):
    pass


if __name__ == '__main__':
    sys.exit(main())
