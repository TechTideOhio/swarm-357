# file: packages/techtide-swarm/src/techtide_swarm/server.py
# description: FastAPI HTTP API for Swarm 357 — hardened run control, SSE, and fail-closed errors
# reference: techtide_swarm.paths, techtide_swarm.runtime.events, techtide_swarm.runtime.routing
"""FastAPI server exposing TechTide Swarm 357 as an HTTP API."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, AsyncIterator, Callable, NoReturn, cast

import yaml
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from techtide_swarm.http_security import (
    max_run_budget_usd,
    optional_swarm_write_key,
    require_swarm_write_key,
)
from techtide_swarm.llm import resolve_api_key, resolved_model_info
from techtide_swarm.paths import resolve_config_path
from techtide_swarm.rate_limit import SwarmRateLimitMiddleware
from techtide_swarm.runtime.routing import RoutingError
from techtide_swarm.structured_logging import CorrelationIdASGIMiddleware

if TYPE_CHECKING:
    pass

_server_logger = logging.getLogger(__name__)

# Server mode disables destructive local tools (terminal / file writes).
os.environ.setdefault("SWARM_SERVER_MODE", "1")

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
    "https://swarm357.techtideai.io",
    "https://swarm357fe.up.railway.app",
    *_EXTRA_ORIGINS,
]


# ── Default config path (thin wrapper over resolve_config_path) ───────────────
def default_config_path() -> Path:
    """Resolve swarm config via unified path search (env, project, Docker, bundled)."""
    return resolve_config_path()


# Run records carry the operator's task text and the model's output. Those are
# business content, so unauthenticated callers get metrics only. Anything not
# listed here is dropped rather than redacted, so a new field cannot leak by
# being forgotten.
_PUBLIC_RUN_FIELDS = frozenset({
    "run_id",
    "type",
    "status",
    "layer",
    "simulate",
    "agent_name",
    "agent",
    "model",
    "cost_usd",
    "spent_usd",
    "budget_usd",
    "latency_ms",
    "duration_ms",
    "timestamp",
    "created_at",
    "updated_at",
})


def _redact_run(run: dict[str, Any]) -> dict[str, Any]:
    """Strip task text, outputs, and errors from a public run record."""
    public = {k: v for k, v in run.items() if k in _PUBLIC_RUN_FIELDS}
    public["redacted"] = True
    return public


def _redact_run_state(state: dict[str, Any]) -> dict[str, Any]:
    """Public view of an inspected run: shape and counters, no content."""
    public = {k: v for k, v in state.items() if k in _PUBLIC_RUN_FIELDS}
    public["steps"] = len(state.get("steps") or [])
    public["approvals"] = len(state.get("approvals") or [])
    public["roles"] = len(state.get("roles") or [])
    public["redacted"] = True
    return public


def _auth_required() -> bool:
    """True when write routes require X-SWARM-API-KEY (key set or force-auth env)."""
    if os.getenv("SWARM_API_KEY", "").strip():
        return True
    flag = os.getenv("SWARM_REQUIRE_AUTH", "").strip().lower()
    return flag in {"1", "true", "yes", "on"}


# ── Request models ───────────────────────────────────────────────────────────

class SwarmRunRequest(BaseModel):
    task: str
    budget_usd: float = 25.0
    layer: str | None = None
    simulate: bool = False
    full_fanout: bool = False


class AgentRunRequest(BaseModel):
    agent_name: str
    task: str


class ForkRunRequest(BaseModel):
    edit_task: str | None = None


class ApprovalDecisionRequest(BaseModel):
    reason: str = ""
    decided_by: str = "api"


# ── Lifespan ─────────────────────────────────────────────────────────────────

def _make_lifespan(cfg: Path) -> Callable[[FastAPI], Any]:
    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
        """Snapshot current swarm config to Supabase on startup."""
        os.environ["SWARM_SERVER_MODE"] = "1"
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


def _raise_run_error(exc: BaseException) -> NoReturn:
    """Map execution errors to HTTP status codes (never silent 200)."""
    if isinstance(exc, HTTPException):
        raise exc
    if isinstance(exc, (ValueError, RoutingError, KeyError)):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    raise HTTPException(status_code=500, detail=str(exc)) from exc


def _swarm_or_503(cfg: Path) -> Any:
    from techtide_swarm.swarm import Swarm

    if not cfg.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Swarm config not found: {cfg}",
        )
    return Swarm(cfg)


def _find_approval(
    swarm: Any, approval_id: str
) -> tuple[Any, Any] | None:
    """Locate (RunState, ApprovalRecord) by approval_id across recent checkpoints."""
    for summary in swarm.list_runs(limit=200):
        state = swarm.inspect_run(summary["run_id"])
        if state is None:
            continue
        for appr in state.approvals:
            if appr.approval_id == approval_id:
                return state, appr
    return None


# ── App factory ──────────────────────────────────────────────────────────────

def create_app(config_path: Path | None = None) -> FastAPI:
    """Create and return the FastAPI application."""
    os.environ["SWARM_SERVER_MODE"] = "1"
    cfg = config_path if config_path is not None else resolve_config_path()

    from techtide_swarm import __version__ as _pkg_version

    # The explorer only lists routes that are already public in this repository,
    # but deployments that care about route enumeration can turn it off.
    docs_disabled = os.getenv("SWARM_DISABLE_API_DOCS", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    app = FastAPI(
        title="TechTide Swarm 357 API",
        description="357 Claude AI agents organized into 6 business layers",
        version=_pkg_version,
        lifespan=_make_lifespan(cfg),
        docs_url=None if docs_disabled else "/docs",
        redoc_url=None if docs_disabled else "/redoc",
        openapi_url=None if docs_disabled else "/openapi.json",
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
                _server_logger.warning("Swarm config missing at %s", cfg)
                _roster = []
        except Exception as exc:  # noqa: BLE001
            _server_logger.exception("Failed to load swarm roster from %s: %s", cfg, exc)
            _roster = []
        return _roster

    def _find_agent(name: str) -> dict[str, Any] | None:
        for a in _get_roster():
            if a.get("name") == name:
                return a
        return None

    # ── Routes ───────────────────────────────────────────────────────────────

    @app.get("/api/health")
    async def health(
        privileged: Annotated[bool, Depends(optional_swarm_write_key)],
    ) -> dict[str, Any]:
        from techtide_swarm import __version__ as _pkg_version

        # Public probe stays minimal. Provider, model routing, and filesystem
        # layout are reconnaissance material, so they need the write key.
        payload: dict[str, Any] = {
            "status": "ok",
            "version": _pkg_version,
            "agents": len(_get_roster()),
            "auth_required": _auth_required(),
        }
        if privileged:
            payload["api_key_set"] = bool(resolve_api_key())
            payload["model"] = resolved_model_info("sonnet")
            payload["config_path"] = str(cfg)
        return payload

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
    async def swarm_runs(
        privileged: Annotated[bool, Depends(optional_swarm_write_key)],
        limit: int = 10,
    ) -> dict[str, Any]:
        from techtide_swarm.telemetry import get_recent_runs
        runs = get_recent_runs(limit=max(1, min(limit, 100)))
        if not privileged:
            runs = [_redact_run(r) for r in runs]
        return {"runs": runs, "total": len(runs), "redacted": not privileged}

    @app.get("/api/swarm/runs/{run_id}")
    async def swarm_run_inspect(
        run_id: str,
        privileged: Annotated[bool, Depends(optional_swarm_write_key)],
    ) -> dict[str, Any]:
        swarm = _swarm_or_503(cfg)
        state = swarm.inspect_run(run_id)
        if state is None:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        dumped = cast("dict[str, Any]", state.model_dump(mode="json"))
        if not privileged:
            return _redact_run_state(dumped)
        return dumped

    @app.post("/api/swarm/runs/{run_id}/resume")
    async def swarm_run_resume(
        run_id: str,
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
    ) -> dict[str, Any]:
        swarm = _swarm_or_503(cfg)
        try:
            await swarm.ensure_booted()
            result = await swarm.resume(run_id)
            return {
                "pipeline_id": result.pipeline_id,
                "status": result.status,
                "total_cost_usd": round(result.total_cost_usd, 6),
                "final_output": result.final_output,
                "agent_results": [_agent_result_dict(r) for r in result.agent_results],
            }
        except Exception as exc:
            _raise_run_error(exc)

    @app.post("/api/swarm/runs/{run_id}/cancel")
    async def swarm_run_cancel(
        run_id: str,
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
    ) -> dict[str, Any]:
        from techtide_swarm.runtime.state import RunStatus

        swarm = _swarm_or_503(cfg)
        state = swarm.inspect_run(run_id)
        if state is None:
            raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
        swarm.cancel_run(run_id)
        state.status = RunStatus.CANCELLED
        state.error = "cancelled via API"
        state.touch()
        swarm.checkpoint.save(state)
        return {"run_id": run_id, "status": "cancelled"}

    @app.post("/api/swarm/runs/{run_id}/replay")
    async def swarm_run_replay(
        run_id: str,
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
    ) -> dict[str, Any]:
        swarm = _swarm_or_503(cfg)
        try:
            await swarm.ensure_booted()
            result = await swarm.replay(run_id)
            return {
                "pipeline_id": result.pipeline_id,
                "status": result.status,
                "total_cost_usd": round(result.total_cost_usd, 6),
                "final_output": result.final_output,
                "agent_results": [_agent_result_dict(r) for r in result.agent_results],
            }
        except Exception as exc:
            _raise_run_error(exc)

    @app.post("/api/swarm/runs/{run_id}/fork")
    async def swarm_run_fork(
        run_id: str,
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
        req: ForkRunRequest | None = None,
    ) -> dict[str, Any]:
        swarm = _swarm_or_503(cfg)
        body = req or ForkRunRequest()
        try:
            await swarm.ensure_booted()
            result = await swarm.fork(run_id, edit_task=body.edit_task)
            return {
                "pipeline_id": result.pipeline_id,
                "status": result.status,
                "total_cost_usd": round(result.total_cost_usd, 6),
                "final_output": result.final_output,
                "agent_results": [_agent_result_dict(r) for r in result.agent_results],
                "parent_run_id": run_id,
            }
        except Exception as exc:
            _raise_run_error(exc)

    @app.get("/api/swarm/runs/{run_id}/events")
    async def swarm_run_events(
        run_id: str,
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
    ) -> StreamingResponse:
        from techtide_swarm.runtime.events import get_event_bus

        bus = get_event_bus()

        async def _event_stream() -> AsyncIterator[str]:
            async for event in bus.subscribe(run_id):
                yield event.to_sse()
            yield "event: stream.end\ndata: {}\n\n"

        return StreamingResponse(
            _event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @app.post("/api/swarm/approvals/{approval_id}/approve")
    async def approval_approve(
        approval_id: str,
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
        req: ApprovalDecisionRequest | None = None,
    ) -> dict[str, Any]:
        from techtide_swarm.runtime.hitl import get_approval_gate

        swarm = _swarm_or_503(cfg)
        body = req or ApprovalDecisionRequest()
        ok = get_approval_gate().resolve(
            approval_id,
            status="approved",
            decided_by=body.decided_by,
            reason=body.reason,
            store=swarm.checkpoint,
        )
        if not ok and _find_approval(swarm, approval_id) is None:
            raise HTTPException(status_code=404, detail=f"Approval not found: {approval_id}")
        found = _find_approval(swarm, approval_id)
        run_id = found[0].run_id if found else ""
        return {
            "approval_id": approval_id,
            "run_id": run_id,
            "status": "approved",
        }

    @app.post("/api/swarm/approvals/{approval_id}/reject")
    async def approval_reject(
        approval_id: str,
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
        req: ApprovalDecisionRequest | None = None,
    ) -> dict[str, Any]:
        from techtide_swarm.runtime.hitl import get_approval_gate

        swarm = _swarm_or_503(cfg)
        body = req or ApprovalDecisionRequest()
        ok = get_approval_gate().resolve(
            approval_id,
            status="rejected",
            decided_by=body.decided_by,
            reason=body.reason,
            store=swarm.checkpoint,
        )
        if not ok and _find_approval(swarm, approval_id) is None:
            raise HTTPException(status_code=404, detail=f"Approval not found: {approval_id}")
        found = _find_approval(swarm, approval_id)
        run_id = found[0].run_id if found else ""
        return {
            "approval_id": approval_id,
            "run_id": run_id,
            "status": "rejected",
        }

    @app.post("/api/swarm/run")
    async def swarm_run(
        req: SwarmRunRequest,
        _authorized: Annotated[bool, Depends(require_swarm_write_key)],
    ) -> dict[str, Any]:
        cap = max_run_budget_usd()
        if req.budget_usd > cap:
            raise HTTPException(
                status_code=400,
                detail=f"budget_usd must be <= {cap} (SWARM_MAX_RUN_BUDGET_USD)",
            )

        if not cfg.exists():
            if req.simulate:
                return _stub_swarm_result(req.task, simulated=True)
            raise HTTPException(
                status_code=503,
                detail=f"Swarm config not found: {cfg}. Pass simulate=true for a stub response.",
            )

        try:
            from techtide_swarm.swarm import Swarm

            swarm = Swarm(cfg)
            await swarm.ensure_booted()
            if req.layer:
                results = await swarm.execute_layer(
                    req.layer,
                    req.task,
                    budget_usd=min(req.budget_usd, cap),
                    full_fanout=req.full_fanout,
                    simulate=req.simulate,
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
            result = await swarm.execute(
                req.task,
                budget_usd=min(req.budget_usd, cap),
                simulate=req.simulate,
            )
            return {
                "pipeline_id": result.pipeline_id,
                "status": result.status,
                "total_cost_usd": round(result.total_cost_usd, 6),
                "final_output": result.final_output,
                "agent_results": [_agent_result_dict(r) for r in result.agent_results],
            }
        except Exception as exc:
            _raise_run_error(exc)
            raise  # pragma: no cover — _raise_run_error always raises

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
            if result.status == "error":
                raise HTTPException(
                    status_code=500,
                    detail=result.error or f"Agent '{req.agent_name}' failed",
                )
            return _agent_result_dict(result)
        except HTTPException:
            raise
        except Exception as exc:
            _raise_run_error(exc)
            raise  # pragma: no cover

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
            raise HTTPException(status_code=500, detail=str(exc)) from exc

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


def _stub_swarm_result(task: str, *, simulated: bool = False) -> dict[str, Any]:
    label = "simulated" if simulated else "stub"
    return {
        "pipeline_id": f"{label}-no-config",
        "status": label,
        "total_cost_usd": 0.0,
        "final_output": f"[{label.upper()}] Task received: {task}",
        "agent_results": [],
    }


# ── Singleton app for `uvicorn techtide_swarm.server:app` ───────────────────
app = create_app()
