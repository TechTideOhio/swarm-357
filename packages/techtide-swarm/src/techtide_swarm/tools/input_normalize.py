# file: packages/techtide-swarm/src/techtide_swarm/tools/input_normalize.py
# description: Normalize LLM tool-call payloads into handler kwargs (aliases, coercion, filtering).
# reference: techtide_swarm.tools.registry, techtide_swarm.agent

"""Normalize model tool inputs before dispatching to handlers.

OpenRouter / Claude models frequently emit alternate key names
(``file_path`` vs ``path``, ``contents`` vs ``content``) or non-dict
payloads.  This module makes tool dispatch tolerant without changing
handler signatures.
"""

from __future__ import annotations

import inspect
import json
from typing import Any, Callable

# Per-tool preferred arg aliases → canonical handler parameter names.
_TOOL_ALIASES: dict[str, dict[str, str]] = {
    "Write": {
        "path": "path",
        "file_path": "path",
        "file": "path",
        "filename": "path",
        "filepath": "path",
        "content": "content",
        "contents": "content",
        "text": "content",
        "body": "content",
        "data": "content",
        "value": "content",
    },
    "write_file": {
        "path": "path",
        "file_path": "path",
        "file": "path",
        "filename": "path",
        "content": "content",
        "contents": "content",
        "text": "content",
        "body": "content",
        "data": "content",
    },
    "Read": {
        "path": "path",
        "file_path": "path",
        "file": "path",
        "filename": "path",
        "filepath": "path",
        "offset": "offset",
        "limit": "limit",
        "start_line": "offset",
        "max_lines": "limit",
    },
    "read_file": {
        "path": "path",
        "file_path": "path",
        "file": "path",
        "offset": "offset",
        "limit": "limit",
    },
    "Bash": {
        "command": "command",
        "cmd": "command",
        "script": "command",
        "code": "command",
        "timeout": "timeout",
    },
    "run_bash": {
        "command": "command",
        "cmd": "command",
        "script": "command",
        "timeout": "timeout",
    },
    "WebSearch": {
        "query": "query",
        "q": "query",
        "search": "query",
        "search_query": "query",
        "prompt": "query",
    },
    "web_search": {
        "query": "query",
        "q": "query",
        "search": "query",
        "search_query": "query",
    },
    "Scrape": {
        "url": "url",
        "link": "url",
        "href": "url",
        "page": "url",
    },
    "web_scrape": {
        "url": "url",
        "link": "url",
        "href": "url",
    },
}


def coerce_to_dict(raw: Any) -> dict[str, Any]:
    """Coerce a tool_use.input payload to a plain dict."""
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    # Pydantic / SDK models
    if hasattr(raw, "model_dump"):
        try:
            dumped = raw.model_dump()
            if isinstance(dumped, dict):
                return dumped
        except Exception:
            pass
    if hasattr(raw, "dict") and callable(raw.dict):
        try:
            dumped = raw.dict()
            if isinstance(dumped, dict):
                return dumped
        except Exception:
            pass
    # Mapping-like
    try:
        return dict(raw)
    except Exception:
        pass
    # JSON string
    if isinstance(raw, str):
        text = raw.strip()
        if text.startswith("{"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
    return {}


def normalize_tool_input(tool_name: str, raw: Any) -> dict[str, Any]:
    """Map aliases and coerce types for a tool call."""
    data = coerce_to_dict(raw)
    aliases = _TOOL_ALIASES.get(tool_name, {})
    # Also try case-insensitive tool name lookup
    if not aliases:
        for key, value in _TOOL_ALIASES.items():
            if key.lower() == tool_name.lower():
                aliases = value
                break

    normalized: dict[str, Any] = {}
    for key, value in data.items():
        canon = aliases.get(key) or aliases.get(key.lower()) or key
        # First alias wins; don't overwrite an already-set canonical key
        if canon in normalized and key != canon:
            continue
        normalized[canon] = value

    # Write without content is a common model miss — default to empty string
    # so the handler can still create/truncate the file and return a clear result.
    if tool_name in ("Write", "write_file") and "path" in normalized and "content" not in normalized:
        normalized["content"] = ""

    return normalized


def filter_handler_kwargs(handler: Callable[..., Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    """Drop keys the handler does not accept (unless **kwargs)."""
    try:
        sig = inspect.signature(handler)
    except (TypeError, ValueError):
        return kwargs
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        return kwargs
    allowed = {
        name
        for name, p in sig.parameters.items()
        if p.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    }
    return {k: v for k, v in kwargs.items() if k in allowed}
