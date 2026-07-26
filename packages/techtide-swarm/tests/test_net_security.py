# file: packages/techtide-swarm/tests/test_net_security.py
# description: SSRF guard fixtures for agent-supplied URLs and redirect hops
# reference: techtide_swarm.net_security, techtide_swarm.tools.web_scrape

from __future__ import annotations

import pytest

from techtide_swarm.net_security import SSRFError, assert_public_http_url, is_public_ip
from techtide_swarm.tools.web_scrape import web_scrape

BLOCKED_URLS = [
    "http://169.254.169.254/latest/meta-data/",
    "http://[fd00::1]/",
    "http://metadata.google.internal/computeMetadata/v1/",
    "http://localhost:8000/api/health",
    "http://127.0.0.1:8000/api/health",
    "http://10.0.0.5/internal",
    "http://192.168.1.1/admin",
    "http://172.16.0.1/",
    "http://0.0.0.0:8000/",
    "http://[::1]:8000/",
    "http://[::ffff:127.0.0.1]/",
    "file:///etc/passwd",
    "gopher://127.0.0.1:11211/",
    "ftp://example.com/secrets",
]


@pytest.mark.parametrize("url", BLOCKED_URLS)
def test_blocked_urls_raise(url: str) -> None:
    with pytest.raises(SSRFError):
        assert_public_http_url(url)


@pytest.mark.parametrize("url", BLOCKED_URLS)
def test_scrape_refuses_blocked_urls_without_network(url: str) -> None:
    result = web_scrape(url)
    assert result.startswith(f"Error scraping {url}:")


def test_missing_host_is_rejected() -> None:
    with pytest.raises(SSRFError):
        assert_public_http_url("http:///no-host")


def test_trailing_dot_localhost_is_rejected() -> None:
    with pytest.raises(SSRFError):
        assert_public_http_url("http://localhost./")


def test_public_literal_is_allowed() -> None:
    assert assert_public_http_url("https://93.184.216.34/") == "https://93.184.216.34/"


def test_is_public_ip_classification() -> None:
    import ipaddress

    assert is_public_ip(ipaddress.ip_address("8.8.8.8")) is True
    assert is_public_ip(ipaddress.ip_address("169.254.169.254")) is False
    assert is_public_ip(ipaddress.ip_address("::ffff:10.0.0.1")) is False
