#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Writes values from the resolver database into nginx configuration format"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import argparse
import logging
import sys
import resolver_db
log = logging.getLogger(__name__)


# Load balance UDP-based DNS traffic across a number of servers
NGINX_TEMPLATE = """
user  nginx;
worker_processes  1;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {{
    worker_connections  1024;
}}

stream {{
    upstream dns_upstreams {{
{servers}
    }}

    server {{
        listen 5353 udp;
        proxy_pass dns_upstreams;
        proxy_timeout 1s;
        proxy_responses 1;
        error_log dns_error.log;
    }}
}}
"""
SERVER_MAP = "server {0}:53;".format


def generate_nginx_conf(args: argparse.Namespace):
    """
    Dump the database of valid IPs to nginx format
    """
    # Get a database for the resolvers
    db = resolver_db.ResolverDB(args.database)

    # Get all valid resolvers
    valid_resolvers = db.valid_resolvers()
    valid_ips = [res.ip_address for res in valid_resolvers]

    # Turn all valid IPs into their configuration format.
    valid_servers = map(SERVER_MAP, valid_ips)

    # Put the servers into the template.
    configuration = NGINX_TEMPLATE.format(servers="\n".join(valid_servers))

    # Write the configuration to file
    with open(args.outputfile, "wb") as f:
        data = configuration.encode("utf-8")
        f.write(data)
    log.info("Wrote %d servers to %s",
             len(valid_resolvers),
             args.outputfile)

    return ScriptRC.SUCCESS


def main():
    """Main handling function. Wraps generate_nginx_conf."""

    stdout_fmt = logging.Formatter("%(asctime)s %(levelname)-5.5s %(message)s")
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(stdout_fmt)
    stdout_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.addHandler(stdout_handler)
    root_logger.setLevel(logging.DEBUG)

    # Run main script.
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--database", help="Database filename (SQLite)", required=True)
        parser.add_argument("--outputfile", required=True)

        args = parser.parse_args()
        rc = generate_nginx_conf(args)

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
