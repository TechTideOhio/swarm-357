"""Tests for the FastAPI HTTP server."""
from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture()
def app():
    from techtide_swarm.server import create_app
    return create_app()


@pytest.mark.asyncio
async def test_health_check(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_swarm_status(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/swarm/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "layers" in data
    assert "total_cost_usd" in data


@pytest.mark.asyncio
async def test_swarm_agents_list(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/swarm/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert "agents" in data
    assert isinstance(data["agents"], list)


@pytest.mark.asyncio
async def test_swarm_agent_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/swarm/agents/does-not-exist-xyz")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_swarm_agent_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        list_resp = await client.get("/api/swarm/agents")
        agents = list_resp.json()["agents"]
        if not agents:
            pytest.skip("No agents in roster")
        name = agents[0]["name"]
        resp = await client.get(f"/api/swarm/agents/{name}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == name
    assert "layer" in data
    assert "soul_preview" in data


@pytest.mark.asyncio
async def test_swarm_cost(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/swarm/cost")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_cost_usd" in data


@pytest.mark.asyncio
async def test_swarm_run_stub(app):
    """Should return a SwarmExecutionResult-shaped JSON even without API key."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=60.0
    ) as client:
        resp = await client.post(
            "/api/swarm/run",
            json={"task": "summarise top SEO trends", "budget_usd": 0.10},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "pipeline_id" in data
    assert "status" in data
    assert "total_cost_usd" in data
    assert "agent_results" in data


@pytest.mark.asyncio
async def test_swarm_run_with_layer(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=60.0
    ) as client:
        resp = await client.post(
            "/api/swarm/run",
            json={"task": "find leads", "budget_usd": 0.05, "layer": "sales"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_agent_run_stub(app):
    """Single-agent run returns AgentResult shape."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=30.0
    ) as client:
        list_resp = await client.get("/api/swarm/agents")
        agents = list_resp.json()["agents"]
        if not agents:
            pytest.skip("No agents in roster")
        name = agents[0]["name"]
        resp = await client.post(
            "/api/agent/run",
            json={"agent_name": name, "task": "ping"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "output" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_agent_run_unknown(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/agent/run",
            json={"agent_name": "ghost-agent-404", "task": "ping"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_swarm_dream(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=30.0
    ) as client:
        resp = await client.post("/api/swarm/dream")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data


def _repo_root() -> Path:
    # tests/ → techtide-swarm/ → packages/ → swarm357/ (repo root)
    return Path(__file__).parent.parent.parent.parent


def test_dockerfile_exists():
    """Dockerfile must exist at repo root for Railway deployment."""
    assert (_repo_root() / "Dockerfile").exists(), "Dockerfile missing at repo root"


def test_railway_config_exists():
    """railway.toml must exist at repo root."""
    assert (_repo_root() / "railway.toml").exists(), "railway.toml missing at repo root"
