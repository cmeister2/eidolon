#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manages a database of DNS resolvers"""

import logging
import sqlite3
import typing
import dnsresolver
log = logging.getLogger(__name__)


class ResolverDB(object):
    def __init__(self, database_path):
        self.database_path = database_path
        self.conn = sqlite3.connect(self.database_path)
        self.conn.execute("CREATE TABLE IF NOT EXISTS resolvers (ip_address text UNIQUE, valid int)")
        self.conn.commit()
        self.cache = {}

    def set_valid(self, resolver: dnsresolver.DNSResolver):
        if not self.cache:
            self._load_cache()

        key = resolver.ip_address
        if key in self.cache and self.cache[key] == 0:
            log.info("Setting %d as valid, was previously invalid", key)

        log.debug("Setting %s as valid", resolver)
        self.cache[key] = 1
        self.conn.execute("REPLACE INTO resolvers VALUES (?, ?)", (key, 1))
        self.conn.commit()

    def set_invalid(self, resolver: dnsresolver.DNSResolver):
        if not self.cache:
            self._load_cache()

        key = resolver.ip_address
        if key in self.cache and self.cache[key] == 1:
            log.info("Setting %d as invalid, was previously valid", key)

        log.debug("Setting %s as invalid", resolver)
        self.cache[key] = 0
        self.conn.execute("REPLACE INTO resolvers VALUES (?, ?)", (key, 0))
        self.conn.commit()

    def resolver_not_tested(self, resolver: dnsresolver.DNSResolver) -> bool:
        if not self.cache:
            self._load_cache()

        return resolver.ip_address not in self.cache

    def _load_cache(self):
        cursor = self.conn.execute("SELECT ip_address, valid FROM resolvers")
        for row in cursor:
            # The key is the IP address - the value is whether that resolver is valid or not
            self.cache[row[0]] = row[1]

    def valid_resolvers(self) -> typing.List[dnsresolver.DNSResolver]:
        cursor = self.conn.execute("SELECT ip_address FROM resolvers where valid=1")
        resolvers = [dnsresolver.DNSResolver(row[0])
                     for row in cursor]
        return resolvers

