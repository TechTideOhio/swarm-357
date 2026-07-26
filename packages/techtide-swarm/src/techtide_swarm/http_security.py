# file: packages/techtide-swarm/src/techtide_swarm/http_security.py
# description: Fail-closed production auth, constant-time key compare, request size helpers
# reference: techtide_swarm.server
"""HTTP API authentication helpers for mutating routes."""

from __future__ import annotations

import hmac
import os

from fastapi import Header, HTTPException


def _is_production() -> bool:
    env = os.getenv("SWARM_ENV", os.getenv("ENVIRONMENT", "")).strip().lower()
    if env in {"prod", "production"}:
        return True
    if os.getenv("SWARM_REQUIRE_AUTH", "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    # Railway / common PaaS signals
    if os.getenv("RAILWAY_ENVIRONMENT", "").strip():
        return True
    return False


def require_swarm_write_key(x_swarm_api_key: str | None = Header(default=None)) -> bool:
    """Require matching X-SWARM-API-KEY when configured; fail closed in production."""
    expected = os.getenv("SWARM_API_KEY", "").strip()
    if not expected:
        if _is_production():
            raise HTTPException(
                status_code=503,
                detail=(
                    "SWARM_API_KEY is required in production "
                    "(SWARM_ENV=production, SWARM_REQUIRE_AUTH=1, or Railway)"
                ),
            )
        return True
    got = (x_swarm_api_key or "").strip()
    if not hmac.compare_digest(got, expected):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid X-SWARM-API-KEY (server has SWARM_API_KEY set)",
        )
    return True


def optional_swarm_write_key(x_swarm_api_key: str | None = Header(default=None)) -> bool:
    """True when the caller presented the write key. Never raises.

    Read routes stay open so the public site can render live counts, but they
    use this to decide whether the caller may see run contents.
    """
    expected = os.getenv("SWARM_API_KEY", "").strip()
    if not expected:
        # No key configured means no privileged tier exists; outside production
        # this is a local dev box, so treat callers as trusted.
        return not _is_production()
    return hmac.compare_digest((x_swarm_api_key or "").strip(), expected)


def max_run_budget_usd() -> float:
    """Upper bound for POST /api/swarm/run budget_usd (abuse protection)."""
    raw = os.getenv("SWARM_MAX_RUN_BUDGET_USD", "500").strip()
    try:
        return max(0.01, float(raw))
    except ValueError:
        return 500.0


def max_request_bytes() -> int:
    """Soft request body ceiling (bytes) for abuse protection."""
    raw = os.getenv("SWARM_MAX_REQUEST_BYTES", "1048576").strip()
    try:
        return max(1024, int(raw))
    except ValueError:
        return 1_048_576
