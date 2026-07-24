"""HTTP API authentication helpers for mutating routes."""
from __future__ import annotations

import os

from fastapi import Header, HTTPException


def require_swarm_write_key(x_swarm_api_key: str | None = Header(default=None)) -> bool:
    """When SWARM_API_KEY is set on the server, require matching X-SWARM-API-KEY header."""
    expected = os.getenv("SWARM_API_KEY", "").strip()
    if not expected:
        return True
    got = (x_swarm_api_key or "").strip()
    if got != expected:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid X-SWARM-API-KEY (server has SWARM_API_KEY set)",
        )
    return True


def max_run_budget_usd() -> float:
    """Upper bound for POST /api/swarm/run budget_usd (abuse protection)."""
    raw = os.getenv("SWARM_MAX_RUN_BUDGET_USD", "500").strip()
    try:
        return max(0.01, float(raw))
    except ValueError:
        return 500.0
