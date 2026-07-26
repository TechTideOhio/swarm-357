# file: packages/techtide-swarm/src/techtide_swarm/llm.py
# description: Resolve LLM API credentials and map short model names without silent downgrades
# reference: techtide_swarm.agent, techtide_swarm.ultra_plan, techtide_swarm.memory
"""LLM client helpers — Anthropic Messages API, optionally via OpenRouter."""

from __future__ import annotations

import logging
import os
from typing import Any

OPENROUTER_BASE_URL = "https://openrouter.ai/api"
_logger = logging.getLogger(__name__)

# Provider-faithful defaults. Never silently map opus/sonnet → haiku.
_OPENROUTER_DEFAULTS = {
    "opus": "anthropic/claude-opus-4",
    "sonnet": "anthropic/claude-sonnet-4",
    "haiku": "anthropic/claude-3-haiku",
}

_ANTHROPIC_DEFAULTS = {
    "opus": "claude-opus-4-6",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5-20251001",
}

# Optional cost-saving overrides (must be explicit — never the silent default).
_OPENROUTER_CHEAP_OVERRIDE = {
    "opus": "anthropic/claude-3-haiku",
    "sonnet": "anthropic/claude-3-haiku",
    "haiku": "anthropic/claude-3-haiku",
}


def resolve_api_key() -> str:
    """Return the active API key, or empty string if unset/placeholder."""
    openrouter = os.getenv("OPENROUTER_API_KEY", "").strip()
    anthropic = os.getenv("ANTHROPIC_API_KEY", "").strip()
    for key in (openrouter, anthropic):
        if key and "your-key" not in key:
            return key
    return ""


def uses_openrouter(api_key: str | None = None) -> bool:
    """True when OpenRouter is configured (explicit key, base URL, or sk-or- key)."""
    key = api_key if api_key is not None else resolve_api_key()
    if os.getenv("OPENROUTER_API_KEY", "").strip():
        return True
    base = os.getenv("ANTHROPIC_BASE_URL", "").strip().lower()
    if "openrouter.ai" in base:
        return True
    return key.startswith("sk-or-")


def cheap_openrouter_mode() -> bool:
    """True only when operator opts into cheap OpenRouter substitutions."""
    raw = os.getenv("SWARM_OPENROUTER_CHEAP", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def model_id(short: str) -> str:
    """Map sonnet/opus/haiku short names to provider model IDs.

    OpenRouter no longer silently remaps opus/sonnet to Haiku. Set
    ``SWARM_OPENROUTER_CHEAP=1`` for explicit cheap defaults, or override
    any short name with ``SWARM_MODEL_OPUS`` / ``SWARM_MODEL_SONNET`` /
    ``SWARM_MODEL_HAIKU``.
    """
    key = (short or "sonnet").strip().lower()
    if uses_openrouter() and cheap_openrouter_mode():
        defaults = _OPENROUTER_CHEAP_OVERRIDE
    elif uses_openrouter():
        defaults = _OPENROUTER_DEFAULTS
    else:
        defaults = _ANTHROPIC_DEFAULTS
    env_map = {
        "opus": os.getenv("SWARM_MODEL_OPUS", defaults["opus"]),
        "sonnet": os.getenv("SWARM_MODEL_SONNET", defaults["sonnet"]),
        "haiku": os.getenv("SWARM_MODEL_HAIKU", defaults["haiku"]),
    }
    resolved = env_map.get(key, env_map["sonnet"])
    _logger.debug("model_id short=%s resolved=%s openrouter=%s", key, resolved, uses_openrouter())
    return resolved


def resolved_model_info(short: str) -> dict[str, Any]:
    """Expose resolved model metadata for health/traces/evals."""
    return {
        "short": (short or "sonnet").strip().lower(),
        "model_id": model_id(short),
        "provider": "openrouter" if uses_openrouter() else "anthropic",
        "cheap_mode": cheap_openrouter_mode() if uses_openrouter() else False,
        "api_key_set": bool(resolve_api_key()),
    }


def create_async_client() -> Any:
    """Build AsyncAnthropic pointed at Anthropic or OpenRouter."""
    from anthropic import AsyncAnthropic

    api_key = resolve_api_key()
    if not api_key:
        raise RuntimeError("No OPENROUTER_API_KEY or ANTHROPIC_API_KEY configured")

    if uses_openrouter(api_key):
        base_url = os.getenv("ANTHROPIC_BASE_URL", OPENROUTER_BASE_URL).strip() or OPENROUTER_BASE_URL
        return AsyncAnthropic(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": os.getenv(
                    "OPENROUTER_HTTP_REFERER", "https://github.com/TechTideOhio/swarm-357"
                ),
                "X-OpenRouter-Title": os.getenv("OPENROUTER_APP_TITLE", "TechTide Swarm 357"),
            },
        )
    return AsyncAnthropic(api_key=api_key)
