# file: packages/techtide-swarm/tests/test_public_surface.py
# description: Unauthenticated read routes expose metrics only, never run content
# reference: techtide_swarm.server, techtide_swarm.http_security

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

SECRET_TASK = "acquire competitor pricing for northwind industries"
WRITE_KEY = "public-surface-test-key"


@pytest.fixture()
def app(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SWARM_API_KEY", WRITE_KEY)
    from techtide_swarm.server import create_app

    root = Path(__file__).resolve().parent.parent.parent.parent
    return create_app(config_path=root / "config" / "swarm-compact.yaml")


@pytest.fixture()
def fake_runs(monkeypatch: pytest.MonkeyPatch):
    import techtide_swarm.telemetry as telemetry

    runs = [
        {
            "type": "swarm_run",
            "run_id": "run-abc",
            "task": SECRET_TASK,
            "status": "complete",
            "layer": "research",
            "cost_usd": 0.0123,
            "final_output": "internal answer text",
            "timestamp": "2026-07-26T00:00:00Z",
        }
    ]
    monkeypatch.setattr(telemetry, "get_recent_runs", lambda limit=10: runs[:limit])
    return runs


@pytest.mark.asyncio
async def test_public_run_list_hides_task_and_output(app, fake_runs) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/swarm/runs")

    assert resp.status_code == 200
    body = resp.text
    assert SECRET_TASK not in body
    assert "internal answer text" not in body

    data = resp.json()
    assert data["redacted"] is True
    assert data["runs"][0]["run_id"] == "run-abc"
    assert data["runs"][0]["cost_usd"] == 0.0123
    assert "task" not in data["runs"][0]


@pytest.mark.asyncio
async def test_authenticated_run_list_keeps_detail(app, fake_runs) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/swarm/runs", headers={"X-SWARM-API-KEY": WRITE_KEY})

    assert resp.status_code == 200
    data = resp.json()
    assert data["redacted"] is False
    assert data["runs"][0]["task"] == SECRET_TASK


@pytest.mark.asyncio
async def test_bad_key_is_treated_as_public(app, fake_runs) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/swarm/runs", headers={"X-SWARM-API-KEY": "wrong"})

    assert resp.json()["redacted"] is True
    assert SECRET_TASK not in resp.text


@pytest.mark.asyncio
async def test_run_list_limit_is_clamped(app, fake_runs) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/swarm/runs?limit=100000")

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_public_health_omits_recon_fields(app) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")

    data = resp.json()
    assert data["status"] == "ok"
    assert data["agents"] == 357
    assert "config_path" not in data
    assert "model" not in data
    assert "api_key_set" not in data


@pytest.mark.asyncio
async def test_authenticated_health_keeps_diagnostics(app) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health", headers={"X-SWARM-API-KEY": WRITE_KEY})

    data = resp.json()
    assert "config_path" in data
    assert "model" in data
    assert "api_key_set" in data


@pytest.mark.asyncio
async def test_public_run_inspect_is_redacted(app, monkeypatch: pytest.MonkeyPatch) -> None:
    from techtide_swarm.runtime.state import RunState

    state = RunState(run_id="run-xyz", task=SECRET_TASK, final_output="internal answer text")
    monkeypatch.setattr(
        "techtide_swarm.swarm.Swarm.inspect_run",
        lambda self, run_id: state,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/swarm/runs/run-xyz")

    assert resp.status_code == 200
    assert SECRET_TASK not in resp.text
    assert "internal answer text" not in resp.text
    data = resp.json()
    assert data["redacted"] is True
    assert data["run_id"] == "run-xyz"
    assert data["steps"] == 0


@pytest.mark.asyncio
async def test_authenticated_run_inspect_keeps_detail(app, monkeypatch: pytest.MonkeyPatch) -> None:
    from techtide_swarm.runtime.state import RunState

    state = RunState(run_id="run-xyz", task=SECRET_TASK)
    monkeypatch.setattr(
        "techtide_swarm.swarm.Swarm.inspect_run",
        lambda self, run_id: state,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(
            "/api/swarm/runs/run-xyz", headers={"X-SWARM-API-KEY": WRITE_KEY}
        )

    assert resp.json()["task"] == SECRET_TASK


def test_cors_allowlist_covers_production_origins() -> None:
    from techtide_swarm.server import _CORS_ORIGINS

    assert "https://swarm357.techtideai.io" in _CORS_ORIGINS
    assert "https://swarm357fe.up.railway.app" in _CORS_ORIGINS
    assert "*" not in _CORS_ORIGINS
