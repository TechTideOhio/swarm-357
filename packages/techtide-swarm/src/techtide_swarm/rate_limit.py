"""Simple in-memory sliding-window rate limiter for the HTTP API."""
from __future__ import annotations

import os
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


def _per_minute_limit() -> int:
    raw = os.getenv("SWARM_RATE_LIMIT_PER_MINUTE", "120").strip()
    try:
        return max(0, int(raw))
    except ValueError:
        return 120


class SlidingWindowLimiter:
    """Sliding window per key (e.g. client IP)."""

    def __init__(self, limit: int, window_sec: float) -> None:
        self.limit = limit
        self.window_sec = window_sec
        self._hits: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_sec
        arr = [t for t in self._hits[key] if t > cutoff]
        if len(arr) >= self.limit:
            self._hits[key] = arr
            return False
        arr.append(now)
        self._hits[key] = arr
        return True


_limiter: SlidingWindowLimiter | None = None


def _get_limiter() -> SlidingWindowLimiter | None:
    """Return None when SWARM_RATE_LIMIT_PER_MINUTE is 0 (disabled)."""
    global _limiter
    n = _per_minute_limit()
    if n <= 0:
        return None
    if _limiter is None or _limiter.limit != n:
        _limiter = SlidingWindowLimiter(limit=n, window_sec=60.0)
    return _limiter


def reset_limiter_for_tests() -> None:
    """Clear singleton (pytest)."""
    global _limiter
    _limiter = None


def check_rate_limit(client_key: str) -> bool:
    """Return True if request is allowed, False if rate limited."""
    lim = _get_limiter()
    if lim is None:
        return True
    return lim.allow(client_key)


class SwarmRateLimitMiddleware(BaseHTTPMiddleware):
    """Return 429 when per-IP rate exceeds SWARM_RATE_LIMIT_PER_MINUTE (0 = off)."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)
        host = request.client.host if request.client else "unknown"
        if not check_rate_limit(host):
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        return await call_next(request)
