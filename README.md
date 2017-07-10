# eidolon
A DNS server that balances queries amongst a number of servers

# Aims
The aim of this server is that DNS queries made to it should succeed in the overwhelming majority of cases, even after receiving lots of requests. This is achieved by balancing the queries amongst a set of backend resolvers.

This is designed to be used in subdomain brute forcers so that much of the DNS logic of handling open resolvers can be abstracted away, and those tools can just query this server directly.

# Design
The current proposed design:

- A DNS server which supports programmatic resolution of domain names
  - PowerDNS
  - Unbound
- A Python script which implements the DNS lookup logic
- A Dockerfile to wrap this all up in a neat package.
