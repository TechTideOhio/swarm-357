# file: packages/techtide-swarm/src/techtide_swarm/budget.py
# description: Atomic decimal budget ledger with reservations for concurrent agent runs
# reference: techtide_swarm.swarm, techtide_swarm.agent
"""Thread/async-safe budget ledger using Decimal arithmetic."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


def _d(value: float | Decimal | str | int) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


@dataclass
class Reservation:
    reservation_id: str
    amount: Decimal
    layer: str


@dataclass
class BudgetLedger:
    """Atomic budget ledger: reserve → commit/release under one asyncio lock."""

    ceiling_usd: Decimal
    spent_usd: Decimal = field(default_factory=lambda: Decimal("0"))
    reserved_usd: Decimal = field(default_factory=lambda: Decimal("0"))
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)
    _reservations: dict[str, Reservation] = field(default_factory=dict, repr=False)

    @classmethod
    def from_float(cls, ceiling_usd: float) -> BudgetLedger:
        return cls(ceiling_usd=_d(ceiling_usd))

    @property
    def remaining_usd(self) -> Decimal:
        return self.ceiling_usd - self.spent_usd - self.reserved_usd

    async def try_reserve(self, amount: float | Decimal, *, layer: str = "") -> str | None:
        """Reserve funds. Returns reservation_id or None if insufficient."""
        need = _d(amount)
        if need <= 0:
            rid = str(uuid.uuid4())
            async with self._lock:
                self._reservations[rid] = Reservation(rid, Decimal("0"), layer)
            return rid
        async with self._lock:
            if self.remaining_usd < need:
                return None
            rid = str(uuid.uuid4())
            self.reserved_usd += need
            self._reservations[rid] = Reservation(rid, need, layer)
            return rid

    async def commit(self, reservation_id: str, actual: float | Decimal = 0) -> None:
        """Commit a reservation, charging the actual spend (may be less than reserved)."""
        actual_d = _d(actual)
        async with self._lock:
            res = self._reservations.pop(reservation_id, None)
            if res is None:
                self.spent_usd += actual_d
                return
            self.reserved_usd -= res.amount
            if self.reserved_usd < 0:
                self.reserved_usd = Decimal("0")
            self.spent_usd += actual_d

    async def release(self, reservation_id: str) -> None:
        """Release a reservation without charging."""
        async with self._lock:
            res = self._reservations.pop(reservation_id, None)
            if res is None:
                return
            self.reserved_usd -= res.amount
            if self.reserved_usd < 0:
                self.reserved_usd = Decimal("0")

    def snapshot(self) -> dict[str, Any]:
        return {
            "ceiling_usd": float(self.ceiling_usd),
            "spent_usd": float(self.spent_usd),
            "reserved_usd": float(self.reserved_usd),
            "remaining_usd": float(self.remaining_usd),
        }
