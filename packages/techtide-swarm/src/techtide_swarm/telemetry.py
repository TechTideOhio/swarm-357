"""Telemetry logging for Swarm 357."""

import json
import logging
from pathlib import Path
from typing import Any

from techtide_swarm.persistence import store

logger = logging.getLogger(__name__)

TELEMETRY_FILE = Path(".swarm/telemetry.jsonl")


def log_telemetry(event_type: str, data: dict[str, Any]) -> None:
    """Log a telemetry event to JSONL and (when configured) Supabase."""
    try:
        TELEMETRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        event = {"type": event_type, **data}
        with open(TELEMETRY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.warning("Error logging telemetry to file: %s", e)
    # Dual-write to Supabase — never raises
    store.log_run(event_type, data)


def get_total_cost() -> float:
    """Return total cost from Supabase when available, else from local JSONL."""
    if store.enabled:
        return store.get_total_cost()
    return _local_total_cost()


def get_layer_stats() -> dict[str, dict[str, Any]]:
    """Return per-layer stats from Supabase when available, else from local JSONL."""
    if store.enabled:
        return store.get_layer_stats()
    return _local_layer_stats()


def get_recent_runs(limit: int = 10) -> list[dict[str, Any]]:
    """Return recent runs from Supabase when available, else from local JSONL."""
    if store.enabled:
        return store.get_runs(limit)
    return _local_recent_runs(limit)


# u2500u2500 Local (file-based) fallbacks u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500

def _local_total_cost() -> float:
    if not TELEMETRY_FILE.exists():
        return 0.0
    total = 0.0
    try:
        with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") == "agent_run":
                    total += event.get("cost_usd", 0.0)
    except OSError:
        pass
    return total


def _local_layer_stats() -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    if not TELEMETRY_FILE.exists():
        return stats
    try:
        with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") == "agent_run":
                    layer = event.get("layer", "unknown")
                    if layer not in stats:
                        stats[layer] = {"calls": 0, "cost": 0.0, "latency": 0}
                    stats[layer]["calls"] += 1
                    stats[layer]["cost"] += event.get("cost_usd", 0.0)
                    stats[layer]["latency"] += event.get("latency_ms", 0)
    except OSError:
        pass
    return stats


def _local_recent_runs(limit: int = 10) -> list[dict[str, Any]]:
    if not TELEMETRY_FILE.exists():
        return []
    events: list[dict[str, Any]] = []
    try:
        with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") in ("swarm_run", "agent_run"):
                    events.append(event)
    except OSError:
        pass
    return events[-limit:][::-1]
