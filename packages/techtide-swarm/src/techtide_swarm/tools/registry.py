"""Central tool registry for TechTide Swarm 357.

Each tool module calls ``registry.register()`` at import time to declare its
schema, handler, toolset membership, and optional availability check.

Import chain (circular-import safe):
    tools/registry.py   (no imports from tool modules)
          ^
    tools/*.py          (import from tools.registry at module level)
          ^
    tools/__init__.py   (imports registry + all tool modules)
          ^
    agent.py, swarm.py, etc.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class ToolEntry:
    """Metadata for a single registered tool."""

    __slots__ = ("name", "toolset", "schema", "handler", "check_fn", "description")

    def __init__(
        self,
        name: str,
        toolset: str,
        schema: dict[str, Any],
        handler: Callable[..., str],
        check_fn: Callable[[], bool] | None,
        description: str,
    ) -> None:
        self.name = name
        self.toolset = toolset
        self.schema = schema
        self.handler = handler
        self.check_fn = check_fn
        self.description = description


# ---------------------------------------------------------------------------
# Toolset → default tool name list
# Agents request tools by name; toolsets are used for bulk resolution.
# ---------------------------------------------------------------------------

TOOLSET_MAP: dict[str, list[str]] = {
    "core_tools":       ["Read", "Write", "Bash"],
    "research_tools":   ["WebSearch", "Scrape", "Read", "Write"],
    "sales_tools":      ["WebSearch", "Scrape", "Read", "Write"],
    "support_tools":    ["Read", "Write", "Bash"],
    "marketing_tools":  ["WebSearch", "Scrape", "Read", "Write"],
    "seo_tools":        ["WebSearch", "Scrape", "Read"],
    "ops_tools":        ["Read", "Write", "Bash"],
    "management_tools": ["WebSearch", "Read", "Write", "Memory"],
}


class ToolRegistry:
    """Singleton registry that collects tool schemas and handlers from tool files.

    Tools are registered at import time by each ``tools/*.py`` module.  Agent
    code queries the registry by tool name; schemas are always returned in
    Anthropic Messages API format (not OpenAI format).
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolEntry] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        schema: dict[str, Any],
        handler: Callable[..., str],
        toolset: str,
        check_fn: Callable[[], bool] | None = None,
        description: str = "",
    ) -> None:
        """Register a tool.  Called at module-import time by each tool file."""
        existing = self._tools.get(name)
        if existing and existing.toolset != toolset:
            logger.warning(
                "Tool name collision: '%s' (toolset '%s') overwritten by '%s'",
                name, existing.toolset, toolset,
            )
        self._tools[name] = ToolEntry(
            name=name,
            toolset=toolset,
            schema=schema,
            handler=handler,
            check_fn=check_fn,
            description=description or schema.get("description", ""),
        )
        logger.debug("Registered tool: %s (toolset=%s)", name, toolset)

    # ------------------------------------------------------------------
    # Schema retrieval — Anthropic format
    # ------------------------------------------------------------------

    def get_anthropic_tools(self, tool_names: list[str]) -> list[dict[str, Any]]:
        """Return Anthropic tool definitions for the requested names.

        Tools whose ``check_fn()`` returns False are silently skipped.
        """
        result: list[dict[str, Any]] = []
        seen_checks: dict[int, bool] = {}

        for name in tool_names:
            entry = self._tools.get(name)
            if not entry:
                logger.debug("Unknown tool requested: %s", name)
                continue
            if entry.check_fn is not None:
                fn_id = id(entry.check_fn)
                if fn_id not in seen_checks:
                    try:
                        seen_checks[fn_id] = bool(entry.check_fn())
                    except Exception:
                        seen_checks[fn_id] = False
                if not seen_checks[fn_id]:
                    logger.debug("Tool %s unavailable (check_fn returned False)", name)
                    continue
            result.append({
                "name": entry.name,
                "description": entry.description or entry.schema.get("description", ""),
                "input_schema": entry.schema.get("input_schema", entry.schema),
            })
        return result

    # Alias matching the plan / Hermes naming
    def get_tools_for_agent(self, tool_names: list[str]) -> list[dict[str, Any]]:
        return self.get_anthropic_tools(tool_names)

    # ------------------------------------------------------------------
    # Toolset helpers
    # ------------------------------------------------------------------

    def get_tools_for_toolset(self, toolset_name: str) -> list[str]:
        """Return the canonical tool names for a business-layer toolset."""
        return list(TOOLSET_MAP.get(toolset_name, []))

    def get_all_tool_names(self) -> list[str]:
        """Sorted list of every registered tool name."""
        return sorted(self._tools.keys())

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def is_available(self, name: str) -> bool:
        """Return True when the tool is registered and its check_fn passes."""
        entry = self._tools.get(name)
        if not entry:
            return False
        if entry.check_fn is None:
            return True
        try:
            return bool(entry.check_fn())
        except Exception:
            return False

    def check_toolset_requirements(self) -> dict[str, bool]:
        """Return ``{toolset_name: all_tools_available}`` for every toolset."""
        result: dict[str, bool] = {}
        for ts_name, tool_names in TOOLSET_MAP.items():
            result[ts_name] = all(self.is_available(n) for n in tool_names)
        return result

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def execute_tool(self, name: str, input_data: dict[str, Any]) -> str:
        """Execute a tool by name.

        Resolves in order:
        1. Direct registry key  (e.g. ``"Bash"``)
        2. Handler function name (e.g. ``"run_bash"``) — backward-compat with
           the old flat-dict registry that used snake_case Anthropic names.
        """
        entry = self._tools.get(name)
        if entry is None:
            # Backward-compat: look up by handler function name
            for e in self._tools.values():
                if getattr(e.handler, "__name__", None) == name:
                    entry = e
                    break
        if entry is None:
            return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            return str(entry.handler(**input_data))
        except Exception as exc:
            logger.exception("Tool %s dispatch error: %s", name, exc)
            return json.dumps({"error": f"Tool execution failed: {type(exc).__name__}: {exc}"})


# Module-level singleton — all tool modules import and use this instance.
registry = ToolRegistry()
