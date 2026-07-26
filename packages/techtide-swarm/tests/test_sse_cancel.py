# file: packages/techtide-swarm/tests/test_sse_cancel.py
# description: SSE auth/close and durable cancel across Swarm instances
# reference: techtide_swarm.runtime.events, techtide_swarm.swarm, techtide_swarm.server

from __future__ import annotations

import asyncio
import textwrap
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from techtide_swarm.runtime.checkpoint import MemoryCheckpointStore, set_default_store
from techtide_swarm.runtime.events import EventBus, EventType, SwarmEvent, get_event_bus
from techtide_swarm.runtime.state import RunState, RunStatus
from techtide_swarm.swarm import Swarm


@pytest.mark.asyncio
async def test_event_bus_subscribe_close() -> None:
    bus = EventBus()
    run_id = "run-sse-1"
    await bus.publish(
        SwarmEvent(type=EventType.RUN_STARTED, run_id=run_id, data={"ok": True})
    )

    async def consumer() -> list[SwarmEvent]:
        out: list[SwarmEvent] = []
        async for ev in bus.subscribe(run_id):
            out.append(ev)
        return out

    task = asyncio.create_task(consumer())
    await asyncio.sleep(0.05)
    await bus.close(run_id)
    events = await asyncio.wait_for(task, timeout=2)
    assert len(events) >= 1
    assert events[0].type == EventType.RUN_STARTED


def test_sse_requires_write_key_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    from techtide_swarm.server import create_app

    monkeypatch.setenv("SWARM_API_KEY", "sse-secret")
    monkeypatch.delenv("SWARM_ENV", raising=False)
    monkeypatch.delenv("SWARM_REQUIRE_AUTH", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)

    root = Path(__file__).resolve().parent.parent.parent.parent
    cfg = root / "config" / "swarm-compact.yaml"
    app = create_app(config_path=cfg)
    client = TestClient(app)

    unauth = client.get("/api/swarm/runs/fake-run/events")
    assert unauth.status_code == 401


@pytest.mark.asyncio
async def test_sse_stream_ends_after_bus_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from techtide_swarm.server import create_app

    monkeypatch.setenv("SWARM_API_KEY", "sse-secret")
    monkeypatch.delenv("SWARM_ENV", raising=False)
    monkeypatch.delenv("SWARM_REQUIRE_AUTH", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)

    root = Path(__file__).resolve().parent.parent.parent.parent
    cfg = root / "config" / "swarm-compact.yaml"
    app = create_app(config_path=cfg)
    run_id = "run-sse-close"
    bus = get_event_bus()
    await bus.publish(
        SwarmEvent(type=EventType.RUN_STARTED, run_id=run_id, data={})
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        async def _close() -> None:
            await asyncio.sleep(0.05)
            await bus.close(run_id)

        closer = asyncio.create_task(_close())
        async with client.stream(
            "GET",
            f"/api/swarm/runs/{run_id}/events",
            headers={"X-SWARM-API-KEY": "sse-secret"},
        ) as resp:
            assert resp.status_code == 200
            body = ""
            async for chunk in resp.aiter_text():
                body += chunk
                if "stream.end" in body:
                    break
        await closer
        assert "stream.end" in body
        assert "run.started" in body


@pytest.mark.asyncio
async def test_durable_cancel_survives_new_swarm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    compact = textwrap.dedent("""\
        swarm:
          version: "2.0"
          layer_budgets:
            research: {daily_limit_usd: 100.0, model_preference: sonnet}
            management: {daily_limit_usd: 100.0, model_preference: opus}
        layers:
          management:
            roles:
              conductor: {count: 1, model: opus, budget_usd: 5.0, tools: [Read]}
            soul: templates/soul/management/conductor.md
          research:
            roles:
              market_analyst: {count: 1, model: sonnet, budget_usd: 2.0, tools: [Read]}
            soul: templates/soul/research/market-analyst.md
    """)
    cfg = tmp_path / "compact.yaml"
    cfg.write_text(compact, encoding="utf-8")
    store = MemoryCheckpointStore()
    set_default_store(store)

    swarm_a = Swarm(cfg, checkpoint_store=store)
    await swarm_a.boot()
    state = RunState(task="cancel me", status=RunStatus.RUNNING)
    store.save(state)
    swarm_a.cancel_run(state.run_id)

    swarm_b = Swarm(cfg, checkpoint_store=store)
    await swarm_b.boot()
    assert swarm_b._is_cancelled(state.run_id) is True
    loaded = swarm_b.inspect_run(state.run_id)
    assert loaded is not None
    assert loaded.cancel_requested is True
    assert loaded.status == RunStatus.CANCELLED


def test_file_ops_confined_to_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from techtide_swarm.tools import file_ops

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SWARM_UNSAFE_FS", raising=False)
    monkeypatch.delenv("SWARM_WORKSPACE_ROOT", raising=False)
    outside = Path("/tmp/swarm357-escape-test-should-deny.txt")
    result = file_ops.read_file(str(outside))
    assert "outside workspace root" in result or "Path denied" in result
