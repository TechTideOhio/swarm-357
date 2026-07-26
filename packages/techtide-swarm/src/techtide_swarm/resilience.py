# file: packages/techtide-swarm/src/techtide_swarm/resilience.py
# description: Timeouts, bounded retries with jitter, and circuit breakers for model/tool calls
# reference: techtide_swarm.agent, techtide_swarm.swarm
"""Resilience primitives for swarm execution."""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass, field
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")


@dataclass
class CircuitBreaker:
    """Simple failure-threshold circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout_s: float = 30.0
    failures: int = 0
    opened_at: float | None = None
    state: str = "closed"  # closed | open | half_open

    def allow(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if self.opened_at is None:
                return False
            if time.monotonic() - self.opened_at >= self.recovery_timeout_s:
                self.state = "half_open"
                return True
            return False
        return True  # half_open: allow one probe

    def record_success(self) -> None:
        self.failures = 0
        self.state = "closed"
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "open"
            self.opened_at = time.monotonic()


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay_s: float = 0.25
    max_delay_s: float = 4.0
    jitter_s: float = 0.1
    timeout_s: float = 60.0
    breaker: CircuitBreaker = field(default_factory=CircuitBreaker)

    async def run(self, fn: Callable[[], Awaitable[T]], *, label: str = "op") -> T:
        if not self.breaker.allow():
            raise RuntimeError(f"circuit open for {label}")
        last_exc: BaseException | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                result = await asyncio.wait_for(fn(), timeout=self.timeout_s)
                self.breaker.record_success()
                return result
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                self.breaker.record_failure()
                if attempt >= self.max_attempts:
                    break
                delay = min(self.max_delay_s, self.base_delay_s * (2 ** (attempt - 1)))
                delay += random.uniform(0, self.jitter_s)
                await asyncio.sleep(delay)
        assert last_exc is not None
        raise last_exc


_BREAKERS: dict[str, CircuitBreaker] = {}


def breaker_for(name: str) -> CircuitBreaker:
    if name not in _BREAKERS:
        _BREAKERS[name] = CircuitBreaker()
    return _BREAKERS[name]


def default_model_retry() -> RetryPolicy:
    return RetryPolicy(
        max_attempts=3,
        timeout_s=90.0,
        breaker=breaker_for("model"),
    )
