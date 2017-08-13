#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Imports resolvers into a database"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import argparse
import logging
import multiprocessing.dummy as mp
import sys
import dnsresolver
import resolver_db
log = logging.getLogger(__name__)


def resolver_import(args: argparse.Namespace):
    """
    Test a list of IP addresses and add valid addresses to the database file
    """
    # Get a database for the resolvers
    db = resolver_db.ResolverDB(args.database)

    # Get the IP addresses that we'll be testing
    ip_addresses = set(get_ip_addresses(args))

    # Convert all addresses to DNSResolver objects
    resolvers = [dnsresolver.DNSResolver(ip) for ip in ip_addresses]
    num_resolvers = len(resolvers)

    if not args.forcetest:
        # Filter out resolvers that have already been tested
        resolvers = list(filter(db.resolver_not_tested, resolvers))
        log.info("Out of %d resolvers, %d have not yet been tested",
                 num_resolvers,
                 len(resolvers))
        num_resolvers = len(resolvers)

    log.info("Testing %d resolvers", num_resolvers)

    # Spin up a thread pool to do queries in parallel.
    process_pool = mp.Pool(processes=5)

    # Use the thread pool to validate the resolvers.
    num_valid_resolvers = 0

    for zindex, (resolver, valid) in enumerate(process_pool.imap(dnsresolver.pool_test_resolver, resolvers)):
        index = zindex + 1
        if valid:
            num_valid_resolvers += 1
            db.set_valid(resolver)
        else:
            db.set_invalid(resolver)

        # Log out the current progress.
        if index % 10 == 0:
            log_level = logging.INFO
        else:
            log_level = logging.DEBUG

        log.log(log_level,
                "Tested %d / %d resolvers (%d valid)",
                index,
                num_resolvers,
                num_valid_resolvers)

    return ScriptRC.SUCCESS


def get_ip_addresses(args: argparse.Namespace):
    """
    Get a list of IP addresses from the arguments
    :param args: Command line arguments
    :return: list of IP addresses
    """
    if args.ip_list_file:
        # The addresses are in a file. Extract the addresses.
        with open(args.ip_list_file, "rb") as f:
            ip_list_file_data = f.readlines()

        ip_list = [x.rstrip().decode("utf-8") for x in ip_list_file_data]

    elif args.ip_address:
        # The address is a single argument
        ip_list = [args.ip_address]

    else:
        raise ScriptException("Expected one of: ip_list_file, ip_address")

    return ip_list


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
        parser.add_argument("--forcetest",
                            action="store_true",
                            help="Retests input IP addresses that have already been scanned before")

        # We need an input to this program.
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument('--ip_list_file')
        input_group.add_argument('--ip_address')

        args = parser.parse_args()
        rc = resolver_import(args)

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
