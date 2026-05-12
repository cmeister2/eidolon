"""Tests for nginx config rendering."""

from eidolon.nginx import render_nginx_conf


def test_render_single_server() -> None:
    """A single IP produces a server line in the upstream block."""
    conf = render_nginx_conf(["1.2.3.4"])
    assert "server 1.2.3.4:53;" in conf


def test_render_multiple_servers() -> None:
    """All provided IPs appear as server lines."""
    conf = render_nginx_conf(["1.2.3.4", "5.6.7.8", "9.10.11.12"])
    assert "server 1.2.3.4:53;" in conf
    assert "server 5.6.7.8:53;" in conf
    assert "server 9.10.11.12:53;" in conf


def test_render_stream_block() -> None:
    """Output contains the nginx stream and upstream blocks."""
    conf = render_nginx_conf(["1.2.3.4"])
    assert "stream {" in conf
    assert "upstream dns_upstreams {" in conf


def test_render_listen_port() -> None:
    """The server listens on UDP port 5353."""
    conf = render_nginx_conf(["1.2.3.4"])
    assert "listen 5353 udp;" in conf


def test_render_empty_list() -> None:
    """An empty IP list produces a valid config with no server lines."""
    conf = render_nginx_conf([])
    assert "upstream dns_upstreams {" in conf
    upstream_block = conf.split("upstream dns_upstreams")[1].split("}")[0]
    assert "server " not in upstream_block.replace("server {", "")
