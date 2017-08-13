# eidolon
A DNS server that balances queries amongst a number of servers

# Aims
The aim of this server is that DNS queries made to it should succeed in the overwhelming majority of cases, even after receiving lots of requests. This is achieved by balancing the queries amongst a set of backend resolvers.

This is designed to be used in subdomain brute forcers so that much of the DNS logic of handling open resolvers can be abstracted away, and those tools can just query this server directly.

# Design
This system comprises several parts:
- A set of Python scripts to create a database of valid DNS resolver addresses
- A Python script to create an nginx configuration script which load balances DNS queries amongst the valid DNS resolver addresses.
- A Dockerfile to compose the nginx configuration script with the nginx:alpine Docker image.

