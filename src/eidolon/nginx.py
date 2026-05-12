"""Render nginx stream configuration for DNS load balancing."""

from pathlib import Path

NGINX_TEMPLATE = """\
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
        error_log /var/log/nginx/dns_error.log;
    }}
}}
"""


def render_nginx_conf(ips: list[str]) -> str:
    """Render the nginx stream config with the given IPs as upstream servers."""
    servers = "\n".join(f"        server {ip}:53;" for ip in ips)
    return NGINX_TEMPLATE.format(servers=servers)


def write_nginx_conf(content: str, output_path: str) -> None:
    """Write the rendered nginx configuration to a file."""
    Path(output_path).write_text(content, encoding="utf-8")
