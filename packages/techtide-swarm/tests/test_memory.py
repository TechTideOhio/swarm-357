"""MemoryManager and recall."""

import pytest

from techtide_swarm import MemoryManager


@pytest.mark.asyncio
async def test_dream_cycle_detects_contradiction():
    mem = MemoryManager()
    mem.log_interaction("research-001", "Market size?", "TAM is $4.2B")
    mem.log_interaction("research-002", "Market size?", "TAM is $3.8B")
    report = await mem.run_dream_cycle()
    assert report["status"] == "ok"
    assert report["contradictions_found"] >= 1


@pytest.mark.asyncio
async def test_dream_cycle_no_contradictions():
    mem = MemoryManager()
    mem.log_interaction("a", "Q?", "A")
    report = await mem.run_dream_cycle()
    assert report["status"] == "ok"
    assert report["contradictions_found"] == 0


@pytest.mark.asyncio
async def test_dream_cycle_shared_key_contradiction():
    mem = MemoryManager()
    mem.share(from_agent="a", to_agent="b", key="pricing", content="$100/mo")
    mem._shared.append({"from": "c", "to": "b", "key": "pricing", "content": "$200/mo"})
    report = await mem.run_dream_cycle()
    assert report["contradictions_found"] >= 1


def test_share_and_recall():
    mem = MemoryManager()
    mem.share(
        from_agent="a",
        to_agent="b",
        key="k1",
        content="Acme pricing is 100",
    )
    rows = mem.recall("b", "pricing")
    assert len(rows) >= 1
    assert "Acme" in rows[0]["content"] or "100" in rows[0]["content"]
