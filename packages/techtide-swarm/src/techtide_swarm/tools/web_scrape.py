# file: packages/techtide-swarm/src/techtide_swarm/tools/web_scrape.py
# description: Agent Scrape tool with SSRF guards on every fetched URL and redirect hop
# reference: techtide_swarm.net_security, techtide_swarm.tools.registry
"""URL content extraction tool.

Backend priority:
  1. Firecrawl - if FIRECRAWL_API_KEY is set and firecrawl is importable
  2. Exa       - if EXA_API_KEY is set and exa_py is importable
  3. httpx     - plain HTTP GET + simple HTML tag stripping (always available)

Every URL is validated against :mod:`techtide_swarm.net_security` before a
request leaves the process, including each redirect hop, because the URL is
agent-supplied and therefore attacker-influenceable.

Registers:
  - Scrape  (toolset: research_tools)
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import re
from typing import Any, cast
from urllib.parse import urljoin

from techtide_swarm.net_security import MAX_REDIRECTS, SSRFError, assert_public_http_url
from techtide_swarm.tools.registry import registry

logger = logging.getLogger(__name__)

_MAX_CHARS = 8000
_MAX_BYTES = 2_000_000


def _has_env(name: str) -> bool:
    val = os.getenv(name)
    return bool(val and val.strip())


def check_web_scrape() -> bool:
    """Return True when at least one real extraction backend is available.

    httpx is always installed (it's a core dependency), so this is always True.
    """
    return True


def _strip_html(html: str) -> str:
    """Very lightweight HTML to plain text conversion."""
    # Remove script/style blocks
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove all other tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _scrape_firecrawl(url: str) -> str:
    fc_mod = importlib.import_module("firecrawl")
    FirecrawlApp = cast(Any, getattr(fc_mod, "FirecrawlApp"))
    app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
    result = app.scrape_url(url, formats=["markdown"])
    if isinstance(result, dict):
        return (result.get("markdown") or result.get("content") or "")[:_MAX_CHARS]
    return str(result)[:_MAX_CHARS]


def _scrape_exa(url: str) -> str:
    exa_mod = importlib.import_module("exa_py")
    Exa = cast(Any, getattr(exa_mod, "Exa"))
    client = Exa(api_key=os.environ["EXA_API_KEY"])
    result = client.get_contents([url], text={"max_characters": _MAX_CHARS})
    if result.results:
        r = result.results[0]
        return (getattr(r, "text", "") or "").strip()[:_MAX_CHARS]
    return "No content retrieved."


def _scrape_httpx(url: str) -> str:
    import httpx

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; TechTideSwarm/1.0; "
            "+https://techtide.io/swarm)"
        )
    }

    # Redirects are followed manually so each hop is re-validated. Letting httpx
    # follow them would allow a public host to bounce the request into a
    # private range or a cloud metadata endpoint.
    current = assert_public_http_url(url)
    with httpx.Client(follow_redirects=False, timeout=20) as client:
        for _ in range(MAX_REDIRECTS + 1):
            response = client.get(current, headers=headers)
            if not response.is_redirect:
                break
            location = response.headers.get("location", "")
            if not location:
                break
            current = assert_public_http_url(urljoin(current, location))
        else:
            raise SSRFError(f"Too many redirects while scraping {url}")

    response.raise_for_status()
    body = response.text[:_MAX_BYTES]
    content_type = response.headers.get("content-type", "")
    if "html" in content_type:
        return _strip_html(body)[:_MAX_CHARS]
    return body[:_MAX_CHARS]


def web_scrape(url: str) -> str:
    """Extract readable content from a URL.

    Tries Firecrawl (rich markdown), then Exa, then plain httpx + HTML strip.
    """
    try:
        assert_public_http_url(url)
    except SSRFError as exc:
        return f"Error scraping {url}: {exc}"

    if _has_env("FIRECRAWL_API_KEY") and importlib.util.find_spec("firecrawl") is not None:
        try:
            return _scrape_firecrawl(url)
        except Exception as exc:
            logger.warning("Firecrawl scrape failed: %s", exc)

    if _has_env("EXA_API_KEY") and importlib.util.find_spec("exa_py") is not None:
        try:
            return _scrape_exa(url)
        except Exception as exc:
            logger.warning("Exa scrape failed: %s", exc)

    # Always-available fallback
    try:
        return _scrape_httpx(url)
    except Exception as exc:
        return f"Error scraping {url}: {exc}"


registry.register(
    name="Scrape",
    schema={
        "description": (
            "Extract readable content from a URL. Returns markdown or plain text. "
            "Uses Firecrawl if FIRECRAWL_API_KEY is set, otherwise Exa or plain HTTP."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape.",
                },
            },
            "required": ["url"],
        },
    },
    handler=web_scrape,
    toolset="research_tools",
    check_fn=check_web_scrape,
)
