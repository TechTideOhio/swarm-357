"""Memory tools that expose MemoryManager as agent-callable tools.

Registers:
  - Memory      (recall by query)          — toolset: management_tools
  - MemoryShare (write a key/content pair) — toolset: management_tools
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from techtide_swarm.tools.registry import registry

logger = logging.getLogger(__name__)

# Lazy singleton — created on first call so tests can override the cwd.
_memory_manager: object | None = None


def _get_mm():  # type: ignore[return]
    """Return (or create) the process-level MemoryManager singleton."""
    global _memory_manager  # noqa: PLW0603
    if _memory_manager is None:
        from techtide_swarm.memory import MemoryManager
        _memory_manager = MemoryManager(swarm_root=Path(os.getcwd()))
    return _memory_manager


def reset_memory_manager() -> None:
    """Reset the singleton — used in tests to point at a tmp_path."""
    global _memory_manager  # noqa: PLW0603
    _memory_manager = None


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def memory_recall(query: str, agent_id: str = "swarm", top_k: int = 5) -> str:
    """Query the shared memory store and return matching entries."""
    try:
        mm = _get_mm()
        results = mm.recall(agent_id=agent_id, query=query)
        if not results:
            return json.dumps({"results": [], "message": "No matching memories found."})
        return json.dumps({"results": results[:top_k]})
    except Exception as exc:
        logger.exception("memory_recall error: %s", exc)
        return json.dumps({"error": str(exc)})


def memory_share(key: str, content: str, from_agent: str = "swarm", to_agent: str = "swarm") -> str:
    """Store a piece of knowledge in the shared memory under *key*."""
    try:
        mm = _get_mm()
        mm.share(from_agent=from_agent, to_agent=to_agent, key=key, content=content)
        return json.dumps({"status": "ok", "key": key})
    except Exception as exc:
        logger.exception("memory_share error: %s", exc)
        return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# Self-registration
# ---------------------------------------------------------------------------

registry.register(
    name="Memory",
    schema={
        "description": (
            "Recall relevant information from the shared agent memory store. "
            "Returns the most relevant stored knowledge for the given query."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language query to search memories.",
                },
                "agent_id": {
                    "type": "string",
                    "description": "Agent identifier scope for recall (default 'swarm').",
                    "default": "swarm",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    handler=memory_recall,
    toolset="management_tools",
)

registry.register(
    name="MemoryShare",
    schema={
        "description": (
            "Write a piece of knowledge to the shared agent memory store so "
            "other agents can retrieve it later via the Memory tool."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Short identifier for the memory entry.",
                },
                "content": {
                    "type": "string",
                    "description": "The content to store.",
                },
                "from_agent": {
                    "type": "string",
                    "description": "Name of the agent writing this memory (default 'swarm').",
                    "default": "swarm",
                },
                "to_agent": {
                    "type": "string",
                    "description": "Target agent that can retrieve this memory (default 'swarm').",
                    "default": "swarm",
                },
            },
            "required": ["key", "content"],
        },
    },
    handler=memory_share,
    toolset="management_tools",
)
