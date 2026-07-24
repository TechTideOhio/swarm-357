"""Tests for the FastAPI HTTP server."""
from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture()
def app():
    """Use repo-root compact config so roster size is always 357 in CI."""
    from techtide_swarm.server import create_app

    root = Path(__file__).resolve().parent.parent.parent.parent
    cfg = root / "config" / "swarm-compact.yaml"
    return create_app(config_path=cfg)


@pytest.mark.asyncio
async def test_health_check(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_correlation_id_header_roundtrip(app):
    """Use Starlette TestClient so response headers from http middleware are visible."""
    from starlette.testclient import TestClient

    client = TestClient(app)
    resp = client.get("/api/health", headers={"X-Correlation-ID": "test-cid-123"})
    assert resp.status_code == 200
    assert resp.headers.get("x-correlation-id") == "test-cid-123"


@pytest.mark.asyncio
async def test_health_agents_count_357(app):
    """Shipped compact roster must report 357 identities (claim integrity)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["agents"] == 357


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


# ── SwarmStore tests ─────────────────────────────────────────────────────────

def test_supabase_optional_dep_declared():
    """supabase must be listed as an optional dependency."""
    toml_path = Path(__file__).parent.parent / "pyproject.toml"
    content = toml_path.read_text(encoding="utf-8")
    assert "supabase" in content, "supabase missing from pyproject.toml optional-dependencies"


def test_store_disabled_without_env(monkeypatch):
    """SwarmStore.enabled is False when SUPABASE_URL is absent."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    from techtide_swarm.persistence import SwarmStore
    store = SwarmStore()
    assert store.enabled is False


def test_store_log_run_noop(monkeypatch):
    """log_run() is silent when store is disabled."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    from techtide_swarm.persistence import SwarmStore
    store = SwarmStore()
    # Must not raise
    store.log_run("agent_run", {"agent_name": "x", "cost_usd": 0.0, "latency_ms": 0, "status": "success"})


def test_store_get_runs_empty_when_disabled(monkeypatch):
    """get_runs() / get_total_cost() / get_layer_stats() return empty values when disabled."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    from techtide_swarm.persistence import SwarmStore
    store = SwarmStore()
    assert store.get_runs() == []
    assert store.get_total_cost() == 0.0
    assert store.get_layer_stats() == {}


def test_store_recall_memory_empty_when_disabled(monkeypatch):
    """recall_memory() returns [] when store is disabled."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    from techtide_swarm.persistence import SwarmStore
    store = SwarmStore()
    assert store.recall_memory(query="test", agent_id="agent-001", top_k=5) == []


def test_log_telemetry_calls_store(monkeypatch, tmp_path):
    """log_telemetry() calls store.log_run() after writing JSONL."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

    calls: list[tuple[str, dict]] = []

    import techtide_swarm.persistence as _persistence
    import techtide_swarm.telemetry as tel
    monkeypatch.setattr(_persistence.store, "log_run", lambda t, d: calls.append((t, d)))
    monkeypatch.setattr(tel, "TELEMETRY_FILE", tmp_path / "telemetry.jsonl")

    tel.log_telemetry("agent_run", {"agent_name": "test", "cost_usd": 0.01, "latency_ms": 100, "status": "success"})
    assert len(calls) == 1
    assert calls[0][0] == "agent_run"


def test_memory_share_calls_store(monkeypatch, tmp_path):
    """MemoryManager.share() calls store.store_memory()."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

    calls: list[dict] = []

    import techtide_swarm.persistence as _persistence
    monkeypatch.setattr(
        _persistence.store,
        "store_memory",
        lambda from_agent, to_agent, key, content: calls.append(
            {"from_agent": from_agent, "to_agent": to_agent, "key": key, "content": content}
        ),
    )

    from techtide_swarm.memory import MemoryManager
    mm = MemoryManager(swarm_root=tmp_path)
    mm.share(from_agent="a", to_agent="b", key="k1", content="hello")
    assert len(calls) == 1
    assert calls[0]["key"] == "k1"


@pytest.mark.asyncio
async def test_dream_endpoint_calls_store_log_dream(monkeypatch):
    """POST /api/swarm/dream calls store.log_dream() with the report."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

    logged: list[dict] = []

    import techtide_swarm.persistence as _persistence
    monkeypatch.setattr(_persistence.store, "log_dream", lambda r: logged.append(r))

    root = Path(__file__).resolve().parent.parent.parent.parent
    from techtide_swarm.server import create_app

    app = create_app(config_path=root / "config" / "swarm-compact.yaml")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/swarm/dream")
    assert resp.status_code == 200
    assert len(logged) == 1
    assert "status" in logged[0]


def test_swarm_store_exported():
    """SwarmStore must be importable from the top-level package."""
    from techtide_swarm import SwarmStore
    assert hasattr(SwarmStore, "enabled")


# ── Repo-level checks ─────────────────────────────────────────────────────────

def _repo_root() -> Path:
    # tests/ → techtide-swarm/ → packages/ → swarm357/ (repo root)
    return Path(__file__).parent.parent.parent.parent


def test_dockerfile_exists():
    """Dockerfile must exist at repo root for Railway deployment."""
    assert (_repo_root() / "Dockerfile").exists(), "Dockerfile missing at repo root"


def test_railway_config_exists():
    """railway.toml must exist at repo root."""
    assert (_repo_root() / "railway.toml").exists(), "railway.toml missing at repo root"


@pytest.mark.asyncio
async def test_swarm_runs_list(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/swarm/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert "runs" in data
    assert isinstance(data["runs"], list)
    assert "total" in data


# ── API auth & limits ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_post_run_requires_api_key_when_configured(app, monkeypatch):
    monkeypatch.setenv("SWARM_API_KEY", "secret-test-key")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/swarm/run",
            json={"task": "hello", "budget_usd": 0.1},
        )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_post_run_succeeds_with_api_key(app, monkeypatch):
    monkeypatch.setenv("SWARM_API_KEY", "secret-test-key")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/swarm/run",
            json={"task": "hello", "budget_usd": 0.1},
            headers={"X-SWARM-API-KEY": "secret-test-key"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_swarm_run_budget_exceeds_cap(app, monkeypatch):
    monkeypatch.setenv("SWARM_MAX_RUN_BUDGET_USD", "10")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/swarm/run",
            json={"task": "hello", "budget_usd": 999.0},
        )
    assert resp.status_code == 400
    assert "budget_usd" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_rate_limit_returns_429(app, monkeypatch):
    from techtide_swarm.rate_limit import reset_limiter_for_tests

    monkeypatch.setenv("SWARM_RATE_LIMIT_PER_MINUTE", "2")
    reset_limiter_for_tests()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.get("/api/health")).status_code == 200
        assert (await client.get("/api/health")).status_code == 200
        resp = await client.get("/api/health")
    assert resp.status_code == 429
    monkeypatch.setenv("SWARM_RATE_LIMIT_PER_MINUTE", "120")
    reset_limiter_for_tests()
