"""Real web search tool.

Backend priority:
  1. Exa     — if EXA_API_KEY is set and exa_py is importable
  2. Firecrawl — if FIRECRAWL_API_KEY is set and firecrawl is importable
  3. Stub    — returns an informative message instead of crashing

Registers:
  - WebSearch  (toolset: research_tools)
"""

from __future__ import annotations

import json
import logging
import os

from techtide_swarm.tools.registry import registry

logger = logging.getLogger(__name__)


def _has_env(name: str) -> bool:
    val = os.getenv(name)
    return bool(val and val.strip())


def check_web_search() -> bool:
    """Return True when at least one real search backend is available."""
    if _has_env("EXA_API_KEY"):
        try:
            import exa_py  # noqa: F401
            return True
        except ImportError:
            pass
    if _has_env("FIRECRAWL_API_KEY"):
        try:
            import firecrawl  # noqa: F401
            return True
        except ImportError:
            pass
    return False


def _search_exa(query: str, num_results: int) -> str:
    from exa_py import Exa
    client = Exa(api_key=os.environ["EXA_API_KEY"])
    response = client.search_and_contents(
        query,
        num_results=num_results,
        use_autoprompt=True,
        text={"max_characters": 1500},
    )
    results: list[str] = []
    for i, r in enumerate(response.results, 1):
        snippet = (getattr(r, "text", "") or "").strip()[:500]
        results.append(
            f"{i}. **{r.title}**\n   URL: {r.url}\n   {snippet}"
        )
    return "\n\n".join(results) if results else "No results found."


def _search_firecrawl(query: str, num_results: int) -> str:
    from firecrawl import FirecrawlApp
    app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
    response = app.search(query, limit=num_results)
    data = response if isinstance(response, list) else (response.get("data") or [])
    results: list[str] = []
    for i, item in enumerate(data[:num_results], 1):
        title = item.get("title", "")
        url = item.get("url", "")
        snippet = (item.get("description") or item.get("markdown") or "")[:500]
        results.append(f"{i}. **{title}**\n   URL: {url}\n   {snippet}")
    return "\n\n".join(results) if results else "No results found."


def web_search(query: str, num_results: int = 5) -> str:
    """Search the web and return formatted results.

    Tries Exa first, then Firecrawl; falls back to an informative stub when
    no API keys are available.
    """
    if _has_env("EXA_API_KEY"):
        try:
            import exa_py  # noqa: F401 — verify importable before calling
            return _search_exa(query, num_results)
        except ImportError:
            logger.debug("exa_py not installed; trying next backend")
        except Exception as exc:
            logger.warning("Exa search failed: %s", exc)

    if _has_env("FIRECRAWL_API_KEY"):
        try:
            import firecrawl  # noqa: F401
            return _search_firecrawl(query, num_results)
        except ImportError:
            logger.debug("firecrawl not installed; falling back to stub")
        except Exception as exc:
            logger.warning("Firecrawl search failed: %s", exc)

    # Informative stub — no crash, helpful message
    return json.dumps({
        "stub": True,
        "query": query,
        "message": (
            "WebSearch stub: no search API configured. "
            "Set EXA_API_KEY (pip install exa-py) or "
            "FIRECRAWL_API_KEY (pip install firecrawl-py) to enable real search."
        ),
    })


registry.register(
    name="WebSearch",
    schema={
        "description": (
            "Search the web for up-to-date information. Returns ranked results "
            "with titles, URLs, and text snippets. Requires EXA_API_KEY or "
            "FIRECRAWL_API_KEY to return real results."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (default 5, max 10).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    handler=web_search,
    toolset="research_tools",
    check_fn=check_web_search,
)
