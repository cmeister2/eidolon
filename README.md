[![Build Status](https://travis-ci.org/cmeister2/eidolon.svg?branch=master)](https://travis-ci.org/cmeister2/eidolon)

# eidolon
A DNS server that load balances DNS queries among a set of public DNS nameservers.

# Aims
The aim of this server is that DNS queries made to it should succeed in the overwhelming majority of cases, even after receiving lots of requests. This is achieved by balancing the queries amongst a set of backend resolvers.

This is designed to be used in subdomain brute forcers so that much of the DNS logic of handling open resolvers can be abstracted away, and those tools can just query this server directly.

# How to run it
You'll likely want to run eidolon like this:
```
docker run --rm -d -p 127.0.0.1:53:5353/udp cmeister2/eidolon:<tag>
```

For example, to use US-only resolvers:
```
docker run --rm -d -p 127.0.0.1:53:5353/udp cmeister2/eidolon:us
```

UDP DNS queries can then be directed at 127.0.0.1:53 - e.g.
```
dig @127.0.0.1 google.com
```

# Supported tags
The following tags are supported for eidolon. The source of the nameserver data is linked to the right. 

 - `global`: https://public-dns.info/nameservers.csv
 - `gb`: https://public-dns.info/nameserver/gb.csv
 - `us`: https://public-dns.info/nameserver/us.csv

Other countries can be added easily; send a pull request!

# Design
This system comprises several parts:
- A set of Python scripts to create a database of valid DNS resolver addresses
- A Python script to create an nginx configuration script which load balances DNS queries amongst the valid DNS resolver addresses.
- A Dockerfile to compose the nginx configuration script with the nginx:alpine Docker image.
