# file: packages/techtide-swarm/tests/test_budget_ledger.py
# description: Concurrent budget reservations must not exceed the ceiling
# reference: techtide_swarm.budget

from __future__ import annotations

import asyncio
from decimal import Decimal

import pytest

from techtide_swarm.budget import BudgetLedger


@pytest.mark.asyncio
async def test_concurrent_reservations_cannot_exceed_ceiling() -> None:
    ledger = BudgetLedger.from_float(1.0)
    amounts = [0.4] * 10

    results = await asyncio.gather(
        *[ledger.try_reserve(a, layer="research") for a in amounts]
    )
    accepted = [r for r in results if r is not None]
    rejected = [r for r in results if r is None]

    assert len(accepted) == 2
    assert len(rejected) == 8
    assert ledger.reserved_usd == Decimal("0.800000")
    assert ledger.remaining_usd == Decimal("0.200000")
    assert ledger.spent_usd + ledger.reserved_usd <= ledger.ceiling_usd


@pytest.mark.asyncio
async def test_commit_and_release_free_budget() -> None:
    ledger = BudgetLedger.from_float(5.0)
    rid = await ledger.try_reserve(3.0, layer="sales")
    assert rid is not None
    assert float(ledger.remaining_usd) == pytest.approx(2.0)

    await ledger.release(rid)
    assert float(ledger.reserved_usd) == pytest.approx(0.0)
    assert float(ledger.remaining_usd) == pytest.approx(5.0)

    rid2 = await ledger.try_reserve(4.0, layer="sales")
    assert rid2 is not None
    await ledger.commit(rid2, actual=1.5)
    assert float(ledger.spent_usd) == pytest.approx(1.5)
    assert float(ledger.reserved_usd) == pytest.approx(0.0)
    assert float(ledger.remaining_usd) == pytest.approx(3.5)
