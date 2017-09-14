#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A DNS resolver class"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import logging
log = logging.getLogger(__name__)


class DNSResolver(object):
    """
    A class representing a DNS resolver
    """
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.resolver = None 

    def __repr__(self):
        return ("{self.__class__.__name__}(ip_address={self.ip_address!r})"
                .format(self=self))

    def test(self) -> bool:
        if self.resolver is None:
            import dns.resolver
            self.resolver = dns.resolver.Resolver(configure=False)
            self.resolver.nameservers = [self.ip_address]
        
        rc = False

        log.debug("[%-15s] Begin testing", self.ip_address)
        try:
            # Test a TXT record lookup
            self.test_txt_record()

            # Test CNAME
            self.test_cname_response()

            # All tests complete
            log.info("[%-15s] Valid resolver!", self.ip_address)
            rc = True
        except Exception as e:
            log.error("[%-15s] Error hit: %s", self.ip_address, e)

        return rc

    def test_txt_record(self):
        """
        Test that a simple TXT record lookup works
        """
        fqdn = "test.openresolver.com"
        answer = self.resolver.query(fqdn, "TXT")
        if len(answer.rrset) != 1:
            raise TestException("Wrong number of answers for TXT rrset")

        response = answer.rrset[0].to_text()
        log.debug("[%-15s]: TXT query for %s returned %s",
                  self.resolver.nameservers[0],
                  fqdn,
                  response)

        if response != '"open-resolver-detected"':
            raise TestException("Incorrect answer received for TXT query")

    def test_cname_response(self):
        """
        Test that an A query which returns a CNAME works
        """
        fqdn = "cname.github.com"
        answer = self.resolver.query(fqdn, "CNAME")
        for rr in answer:
            if rr.target.to_text() != "github.map.fastly.net.":
                raise TestException("Unexpected target for {0}: {1}"
                                    .format(fqdn, rr.target))
        log.debug("[%-15s]: CNAME query for %s succeeded",
                  self.resolver.nameservers[0],
                  fqdn)


def pool_test_resolver(resolver: DNSResolver):
    """
    Simple function which allows a pool mapper to filter out bad resolvers
    :param resolver: DNS resolver to test
    :return: tuple of (resolver, whether the resolver is valid)
    """
    return resolver, resolver.test()


class TestException(Exception):
    pass
