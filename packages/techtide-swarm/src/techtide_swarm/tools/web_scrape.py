"""URL content extraction tool.

Backend priority:
  1. Firecrawl — if FIRECRAWL_API_KEY is set and firecrawl is importable
  2. Exa       — if EXA_API_KEY is set and exa_py is importable
  3. httpx     — plain HTTP GET + simple HTML tag stripping (always available)

Registers:
  - Scrape  (toolset: research_tools)
"""

from __future__ import annotations

import logging
import os
import re

from techtide_swarm.tools.registry import registry

logger = logging.getLogger(__name__)

_MAX_CHARS = 8000


def _has_env(name: str) -> bool:
    val = os.getenv(name)
    return bool(val and val.strip())


def check_web_scrape() -> bool:
    """Return True when at least one real extraction backend is available.

    httpx is always installed (it's a core dependency), so this is always True.
    """
    return True


def _strip_html(html: str) -> str:
    """Very lightweight HTML → plain text conversion."""
    # Remove script/style blocks
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove all other tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _scrape_firecrawl(url: str) -> str:
    from firecrawl import FirecrawlApp
    app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
    result = app.scrape_url(url, formats=["markdown"])
    if isinstance(result, dict):
        return (result.get("markdown") or result.get("content") or "")[:_MAX_CHARS]
    return str(result)[:_MAX_CHARS]


def _scrape_exa(url: str) -> str:
    from exa_py import Exa
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
    response = httpx.get(url, headers=headers, follow_redirects=True, timeout=20)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "html" in content_type:
        return _strip_html(response.text)[:_MAX_CHARS]
    return response.text[:_MAX_CHARS]


def web_scrape(url: str) -> str:
    """Extract readable content from a URL.

    Tries Firecrawl (rich markdown), then Exa, then plain httpx + HTML strip.
    """
    if _has_env("FIRECRAWL_API_KEY"):
        try:
            import firecrawl  # noqa: F401
            return _scrape_firecrawl(url)
        except ImportError:
            logger.debug("firecrawl not installed; trying Exa")
        except Exception as exc:
            logger.warning("Firecrawl scrape failed: %s", exc)

    if _has_env("EXA_API_KEY"):
        try:
            import exa_py  # noqa: F401
            return _scrape_exa(url)
        except ImportError:
            logger.debug("exa_py not installed; falling back to httpx")
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
