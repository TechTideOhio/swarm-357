"""Tools package for TechTide Swarm 357.

Importing this package triggers self-registration of all tool modules into the
singleton ``registry``.  Consumer code can:

  * Call the backward-compatible shims ``get_anthropic_tools`` / ``execute_tool``
    (same API as the old flat-dict system).
  * Access the full registry object directly:
      from techtide_swarm.tools import registry
"""

from __future__ import annotations

from typing import Any

# 1. Import the registry singleton first (no tool-module deps).
from techtide_swarm.tools.registry import TOOLSET_MAP, ToolRegistry, registry  # noqa: F401

# 2. Import each tool module so they self-register at import time.
#    Import errors in optional tools (missing deps) are silently skipped so the
#    package remains importable even without exa-py / firecrawl-py installed.
from techtide_swarm.tools import file_ops as _file_ops  # noqa: F401
from techtide_swarm.tools import terminal as _terminal  # noqa: F401
from techtide_swarm.tools import web_search as _web_search  # noqa: F401
from techtide_swarm.tools import web_scrape as _web_scrape  # noqa: F401
from techtide_swarm.tools import memory_tool as _memory_tool  # noqa: F401

try:
    from techtide_swarm.tools.mcp import load_mcp_configs, mcp_registry  # noqa: F401
except Exception as _mcp_err:  # pragma: no cover
    import logging as _logging
    _logging.getLogger(__name__).debug("MCP module not loaded: %s", _mcp_err)
    # Define stubs so imports don't fail
    load_mcp_configs = None  # type: ignore[assignment]
    mcp_registry = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Backward-compatible shims — same signature as the old flat-dict API.
# agent.py and existing tests import these and need no changes.
# ---------------------------------------------------------------------------

def get_anthropic_tools(tool_names: list[str]) -> list[dict[str, Any]]:
    """Return Anthropic tool definitions for the given tool names.

    Thin wrapper around ``registry.get_anthropic_tools()``.
    """
    return registry.get_anthropic_tools(tool_names)


def execute_tool(name: str, input_data: dict[str, Any]) -> str:
    """Execute a tool by its Anthropic ``name`` field.

    Thin wrapper around ``registry.execute_tool()``.
    """
    return registry.execute_tool(name, input_data)


__all__ = [
    "registry",
    "ToolRegistry",
    "TOOLSET_MAP",
    "get_anthropic_tools",
    "execute_tool",
    "mcp_registry",
    "load_mcp_configs",
]
