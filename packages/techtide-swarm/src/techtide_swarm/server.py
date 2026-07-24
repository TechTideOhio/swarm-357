"""FastAPI server exposing TechTide Swarm 357 as an HTTP API."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, AsyncIterator, Callable

import yaml
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from techtide_swarm.http_security import max_run_budget_usd, require_swarm_write_key
from techtide_swarm.llm import resolve_api_key
from techtide_swarm.rate_limit import SwarmRateLimitMiddleware
from techtide_swarm.structured_logging import CorrelationIdASGIMiddleware

if TYPE_CHECKING:
    pass

_server_logger = logging.getLogger(__name__)

# ── Allowed CORS origins ─────────────────────────────────────────────────────
# Extend at deploy time via ALLOWED_ORIGINS=https://a.example.com,https://b.example.com
_EXTRA_ORIGINS = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]
_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://swarm357.com",
    "https://www.swarm357.com",
    "https://techtide.ai",
    "https://www.techtide.ai",
    *_EXTRA_ORIGINS,
]

# ── Default config path (editable install, Docker /app, or SWARM_CONFIG_PATH) ─
def default_config_path() -> Path:
    """Resolve swarm-compact.yaml for local dev, Docker (/app/config), wheel data, or env."""
    env = os.getenv("SWARM_CONFIG_PATH", "").strip()
    if env:
        return Path(env)
    docker = Path("/app/config/swarm-compact.yaml")
    if docker.is_file():
        return docker
    from techtide_swarm.paths import bundled_compact_config

    bundled = bundled_compact_config()
    if bundled is not None:
        return bundled
    return Path(__file__).resolve().parent.parent.parent.parent.parent / "config" / "swarm-compact.yaml"


# ── Request models ───────────────────────────────────────────────────────────

class SwarmRunRequest(BaseModel):
    task: str
    budget_usd: float = 25.0
    layer: str | None = None


class AgentRunRequest(BaseModel):
    agent_name: str
    task: str


# ── Lifespan ─────────────────────────────────────────────────────────────────

def _make_lifespan(cfg: Path) -> Callable[[FastAPI], Any]:
    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
        """Snapshot current swarm config to Supabase on startup."""
        from techtide_swarm.persistence import store
        if store.enabled and cfg.exists():
            try:
                with open(cfg, encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}
                store.snapshot_config(config_data)
            except Exception as exc:  # noqa: BLE001
                _server_logger.warning("Config snapshot failed: %s", exc)
        yield
    return _lifespan


# ── App factory ──────────────────────────────────────────────────────────────

def create_app(config_path: Path | None = None) -> FastAPI:
    """Create and return the FastAPI application."""
    cfg = config_path if config_path is not None else default_config_path()

    from techtide_swarm import __version__ as _pkg_version

    app = FastAPI(
        title="TechTide Swarm 357 API",
        description="357 Claude AI agents organized into 6 business layers",
        version=_pkg_version,
        lifespan=_make_lifespan(cfg),
    )

    # Innermost (closest to routes): correlation id + structured JSON logs.
    app.add_middleware(CorrelationIdASGIMiddleware)
    app.add_middleware(SwarmRateLimitMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID"],
    )

    # ── Roster cache (loaded once per app instance) ──────────────────────────
    _roster: list[dict[str, Any]] = []

    def _get_roster() -> list[dict[str, Any]]:
        nonlocal _roster
        if _roster:
            return _roster
        try:
            from techtide_swarm.swarm import Swarm
            if cfg.exists():
                swarm = Swarm(cfg)
                _roster = swarm._get_roster()
            else:
                _roster = []
        except Exception:
            _roster = []
        return _roster

    def _find_agent(name: str) -> dict[str, Any] | None:
        for a in _get_roster():
            if a.get("name") == name:
                return a
        return None

    # ── Routes ───────────────────────────────────────────────────────────────

    @app.get("/api/health")
    async def health() -> dict[str, Any]:
        from techtide_swarm import __version__ as _pkg_version

        return {
            "status": "ok",
            "version": _pkg_version,
            "agents": len(_get_roster()),
            "api_key_set": bool(resolve_api_key()),
        }

    @app.get("/api/swarm/status")
    async def swarm_status() -> dict[str, Any]:
        from techtide_swarm.telemetry import get_layer_stats, get_total_cost
        stats = get_layer_stats()
        total = get_total_cost()
        return {
            "layers": stats,
            "total_cost_usd": round(total, 6),
            "roster_size": len(_get_roster()),
        }

    @app.get("/api/swarm/agents")
    async def swarm_agents() -> dict[str, Any]:
        roster = _get_roster()
        agents = [
            {
                "name": a.get("name", ""),
                "layer": a.get("layer", ""),
                "role": a.get("role", ""),
                "model": a.get("model", "sonnet"),
                "budget_usd": a.get("budget_usd", a.get("budget_limit_usd", 1.0)),
                "tools": a.get("tools", []),
            }
            for a in roster
        ]
        return {"agents": agents, "total": len(agents)}

    @app.get("/api/swarm/agents/{name}")
    async def swarm_agent_detail(name: str) -> dict[str, Any]:
        agent_cfg = _find_agent(name)
        if agent_cfg is None:
            raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

        soul_preview = ""
        soul_path = agent_cfg.get("soul", "")
        if soul_path:
            p = Path(soul_path)
            if not p.is_absolute():
                p = cfg.parent.parent / soul_path
            if p.exists():
                soul_preview = p.read_text(encoding="utf-8")[:500]

        return {
            "name": agent_cfg.get("name", ""),
            "layer": agent_cfg.get("layer", ""),
            "role": agent_cfg.get("role", ""),
            "model": agent_cfg.get("model", "sonnet"),
            "budget_usd": agent_cfg.get("budget_usd", agent_cfg.get("budget_limit_usd", 1.0)),
            "tools": agent_cfg.get("tools", []),
            "soul": soul_path,
            "soul_preview": soul_preview,
        }

    @app.get("/api/swarm/cost")
    async def swarm_cost() -> dict[str, Any]:
        from techtide_swarm.telemetry import get_layer_stats, get_total_cost
        total = get_total_cost()
        stats = get_layer_stats()
        per_layer = {layer: round(data["cost"], 6) for layer, data in stats.items()}
        return {
            "total_cost_usd": round(total, 6),
            "per_layer_usd": per_layer,
        }

    @app.get("/api/swarm/runs")
    async def swarm_runs(limit: int = 10) -> dict[str, Any]:
        from techtide_swarm.telemetry import get_recent_runs
        runs = get_recent_runs(limit=limit)
        return {"runs": runs, "total": len(runs)}

    @app.post("/api/swarm/run")
    async def swarm_run(
        req: SwarmRunRequest,
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
    ) -> dict[str, Any]:
        from techtide_swarm.swarm import Swarm

        cap = max_run_budget_usd()
        if req.budget_usd > cap:
            raise HTTPException(
                status_code=400,
                detail=f"budget_usd must be <= {cap} (SWARM_MAX_RUN_BUDGET_USD)",
            )

        try:
            if not cfg.exists():
                return _stub_swarm_result(req.task)

            swarm = Swarm(cfg)
            if req.layer:
                results = await swarm.execute_layer(
                    req.layer, req.task, budget_usd=min(req.budget_usd, cap)
                )
                total_cost = sum(r.cost_usd for r in results)
                final = results[-1].output if results else ""
                return {
                    "pipeline_id": f"layer-{req.layer}",
                    "status": "ok",
                    "total_cost_usd": round(total_cost, 6),
                    "final_output": final,
                    "agent_results": [_agent_result_dict(r) for r in results],
                }
            else:
                result = await swarm.execute(req.task, budget_usd=min(req.budget_usd, cap))
                return {
                    "pipeline_id": result.pipeline_id,
                    "status": result.status,
                    "total_cost_usd": round(result.total_cost_usd, 6),
                    "final_output": result.final_output,
                    "agent_results": [_agent_result_dict(r) for r in result.agent_results],
                }
        except Exception as exc:
            return {
                "pipeline_id": "error",
                "status": "error",
                "total_cost_usd": 0.0,
                "final_output": "",
                "agent_results": [],
                "error": str(exc),
            }

    @app.post("/api/agent/run")
    async def agent_run(
        req: AgentRunRequest,
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
    ) -> dict[str, Any]:
        from techtide_swarm.agent import Agent, AgentConfig
        from techtide_swarm.core.types import LayerType

        agent_cfg = _find_agent(req.agent_name)
        if agent_cfg is None:
            raise HTTPException(status_code=404, detail=f"Agent '{req.agent_name}' not found")

        try:
            layer_str = agent_cfg.get("layer", "operations")
            try:
                layer = LayerType(layer_str)
            except ValueError:
                layer = LayerType.OPERATIONS

            config = AgentConfig(
                name=agent_cfg.get("name", req.agent_name),
                layer=layer,
                role=agent_cfg.get("role", ""),
                soul=agent_cfg.get("soul", ""),
                tools=agent_cfg.get("tools", []),
                model=agent_cfg.get("model", "sonnet"),
                budget_limit_usd=float(
                    agent_cfg.get("budget_usd", agent_cfg.get("budget_limit_usd", 1.0))
                ),
            )
            agent = Agent(config)
            result = await agent.run(req.task)
            return _agent_result_dict(result)
        except Exception as exc:
            return {
                "output": "",
                "cost_usd": 0.0,
                "latency_ms": 0,
                "status": "error",
                "agent_name": req.agent_name,
                "error": str(exc),
            }

    @app.post("/api/swarm/dream")
    async def swarm_dream(
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
    ) -> dict[str, Any]:
        from techtide_swarm.memory import MemoryManager
        from techtide_swarm.persistence import store as _store
        mem = MemoryManager()
        try:
            report = await mem.run_dream_cycle()
            _store.log_dream(report)
            return report
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    return app


# ── Helpers ──────────────────────────────────────────────────────────────────

def _agent_result_dict(result: Any) -> dict[str, Any]:
    return {
        "output": result.output,
        "cost_usd": round(result.cost_usd, 6),
        "latency_ms": result.latency_ms,
        "status": result.status,
        "agent_name": result.agent_name,
        "error": result.error,
    }


def _stub_swarm_result(task: str) -> dict[str, Any]:
    return {
        "pipeline_id": "stub-no-config",
        "status": "stub",
        "total_cost_usd": 0.0,
        "final_output": f"[STUB] Task received: {task}",
        "agent_results": [],
    }


# ── Singleton app for `uvicorn techtide_swarm.server:app` ───────────────────
app = create_app()
