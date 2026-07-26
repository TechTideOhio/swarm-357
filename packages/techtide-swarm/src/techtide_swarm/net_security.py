# file: packages/techtide-swarm/src/techtide_swarm/net_security.py
# description: SSRF guards for agent-controlled outbound HTTP (scheme, host, and resolved IP checks)
# reference: techtide_swarm.tools.web_scrape
"""Outbound URL validation for tools that fetch agent-supplied URLs.

An agent can be steered by untrusted text, so any tool that fetches a URL is a
server-side request forgery primitive. These helpers keep such tools pointed at
the public internet: no cloud metadata endpoints, no private ranges, no
loopback, and no non-HTTP schemes.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit

IPAddress = ipaddress.IPv4Address | ipaddress.IPv6Address

ALLOWED_SCHEMES = frozenset({"http", "https"})

# Hosts that never resolve through DNS but must not be reachable.
_BLOCKED_HOSTNAMES = frozenset({"localhost", "metadata.google.internal"})

MAX_REDIRECTS = 5


class SSRFError(ValueError):
    """Raised when a URL targets a non-public or non-HTTP destination."""


def _unwrap_ipv6(addr: ipaddress.IPv6Address) -> IPAddress:
    """Return the embedded IPv4 address for mapped or tunneled IPv6 forms."""
    if addr.ipv4_mapped is not None:
        return addr.ipv4_mapped
    if addr.sixtofour is not None:
        return addr.sixtofour
    if addr.teredo is not None:
        return addr.teredo[1]
    return addr


def is_public_ip(addr: IPAddress) -> bool:
    """True when the address is routable on the public internet."""
    if isinstance(addr, ipaddress.IPv6Address):
        addr = _unwrap_ipv6(addr)
    return not (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def _resolve(host: str, port: int) -> list[IPAddress]:
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise SSRFError(f"Cannot resolve host: {host}") from exc
    return [ipaddress.ip_address(info[4][0]) for info in infos]


def assert_public_http_url(url: str) -> str:
    """Validate a URL for outbound fetching, or raise :class:`SSRFError`.

    Resolution happens here and again inside the HTTP client, so this is not a
    complete defense against DNS rebinding. It does close the common cases:
    literal private addresses, loopback names, and metadata hostnames.
    """
    parts = urlsplit(url)

    if parts.scheme.lower() not in ALLOWED_SCHEMES:
        raise SSRFError(f"Blocked URL scheme: {parts.scheme or '(none)'}")

    host = (parts.hostname or "").strip().rstrip(".")
    if not host:
        raise SSRFError("URL has no host")
    if host.lower() in _BLOCKED_HOSTNAMES:
        raise SSRFError(f"Blocked host: {host}")

    port = parts.port or (443 if parts.scheme.lower() == "https" else 80)

    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None

    addresses = [literal] if literal is not None else _resolve(host, port)
    if not addresses:
        raise SSRFError(f"Cannot resolve host: {host}")

    for addr in addresses:
        if not is_public_ip(addr):
            raise SSRFError(f"Blocked non-public address for host {host}: {addr}")

    return url
