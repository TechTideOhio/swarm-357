"""Telemetry logging for Swarm 357."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TELEMETRY_FILE = Path(".swarm/telemetry.jsonl")

def log_telemetry(event_type: str, data: dict[str, Any]) -> None:
    """Log a telemetry event to a local JSONL file."""
    try:
        TELEMETRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        event = {"type": event_type, **data}
        with open(TELEMETRY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.warning("Error logging telemetry: %s", e)

def get_total_cost() -> float:
    """Calculate total cost from telemetry data."""
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

def get_layer_stats() -> dict[str, dict[str, Any]]:
    """Aggregate stats by layer."""
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
