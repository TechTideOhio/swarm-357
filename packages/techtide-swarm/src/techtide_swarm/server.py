"""FastAPI server exposing TechTide Swarm 357 as an HTTP API."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Allowed CORS origins ─────────────────────────────────────────────────────
_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://swarm357.com",
    "https://www.swarm357.com",
    "https://techtide.ai",
    "https://www.techtide.ai",
]

# ── Default config path (resolved relative to this file) ────────────────────
_DEFAULT_CONFIG = Path(__file__).parent.parent.parent.parent.parent / "config" / "swarm-compact.yaml"


# ── Request models ───────────────────────────────────────────────────────────

class SwarmRunRequest(BaseModel):
    task: str
    budget_usd: float = 25.0
    layer: str | None = None


class AgentRunRequest(BaseModel):
    agent_name: str
    task: str


# ── App factory ──────────────────────────────────────────────────────────────

def create_app(config_path: Path | None = None) -> FastAPI:
    """Create and return the FastAPI application."""
    cfg = config_path or _DEFAULT_CONFIG

    app = FastAPI(
        title="TechTide Swarm 357 API",
        description="357 Claude AI agents organized into 6 business layers",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
        return {
            "status": "ok",
            "version": "0.1.0",
            "agents": len(_get_roster()),
            "api_key_set": bool(os.environ.get("ANTHROPIC_API_KEY")),
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

    @app.post("/api/swarm/run")
    async def swarm_run(req: SwarmRunRequest) -> dict[str, Any]:
        from techtide_swarm.swarm import Swarm

        try:
            if not cfg.exists():
                return _stub_swarm_result(req.task)

            swarm = Swarm(cfg)
            if req.layer:
                results = await swarm.execute_layer(
                    req.layer, req.task, budget_usd=req.budget_usd
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
                result = await swarm.execute(req.task, budget_usd=req.budget_usd)
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
    async def agent_run(req: AgentRunRequest) -> dict[str, Any]:
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
    async def swarm_dream() -> dict[str, Any]:
        from techtide_swarm.memory import MemoryManager
        mem = MemoryManager()
        try:
            report = await mem.run_dream_cycle()
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
