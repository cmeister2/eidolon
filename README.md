# eidolon

A DNS server that load-balances DNS queries among a set of public DNS nameservers.

DNS queries are proxied via nginx's stream module to a round-robin pool of public resolvers sourced from [public-dns.info](https://public-dns.info). This is designed for use with subdomain brute-forcers, abstracting away resolver management.

## Quick start

```sh
docker run --rm -d -p 127.0.0.1:53:5353/udp ghcr.io/cmeister2/eidolon:global
dig @127.0.0.1 google.com
```

## Supported tags

| Tag      | Source                                    |
|----------|-------------------------------------------|
| `global` | https://public-dns.info/nameservers.csv   |
| `gb`     | https://public-dns.info/nameserver/gb.csv |
| `us`     | https://public-dns.info/nameserver/us.csv |

Images are rebuilt weekly with fresh resolver data.

### Adding a country

Add an entry to `tags.json`:

```json
{
  "de": "nameserver/de.csv"
}
```

The CI and publish workflows pick it up automatically.

## Development

```sh
pip install -e ".[dev]"
pytest
ruff check src/ tests/
mypy src/
```

### Building locally

```sh
pip install .
eidolon --tag gb --output nginx.conf
docker build -t eidolon:gb .
docker run --rm -d -p 127.0.0.1:5353:5353/udp eidolon:gb
dig @127.0.0.1 -p 5353 google.com
```

## How it works

1. The `eidolon` CLI downloads the CSV of public nameservers from public-dns.info
2. Filters to IPv4 addresses with >= 99% reliability
3. Generates an nginx stream config with all valid resolvers as upstreams
4. The config is copied into an `nginx:alpine` Docker image

## CI/CD

- **CI**: Runs on every push/PR - lint, type check, tests, Docker build smoke test
- **Publish**: Weekly scheduled build pushes multi-arch images (amd64/arm64) to GHCR
