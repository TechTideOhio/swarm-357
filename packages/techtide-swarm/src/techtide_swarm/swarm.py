# file: packages/techtide-swarm/src/techtide_swarm/swarm.py
# description: Multi-agent swarm orchestration with durable run state and bounded fan-out
# reference: techtide_swarm.runtime.state, techtide_swarm.budget, techtide_swarm.runtime.routing
"""Multi-agent swarm orchestration with checkpointed runs."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

from techtide_swarm.agent import Agent, AgentConfig, AgentResult
from techtide_swarm.budget import BudgetLedger
from techtide_swarm.core.types import LayerType
from techtide_swarm.llm import model_id, resolve_api_key, resolved_model_info
from techtide_swarm.runtime.checkpoint import CheckpointStore, default_checkpoint_store
from techtide_swarm.runtime.events import EventBus, EventType, SwarmEvent, get_event_bus
from techtide_swarm.runtime.routing import RoutingError, parse_routing_decision, routing_prompt
from techtide_swarm.runtime.state import RunState, RunStatus, StepState, StepStatus
from techtide_swarm.telemetry import log_telemetry

# Default: one agent per role in a layer (not the full 55–68 clone fan-out).
_DEFAULT_LAYER_MAX_AGENTS = int(os.getenv("SWARM_LAYER_MAX_AGENTS", "16"))
_UNSAFE_FULL_FANOUT = os.getenv("SWARM_UNSAFE_FULL_FANOUT", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


@dataclass
class SwarmExecutionResult:
    """Result of Swarm.execute."""

    pipeline_id: str
    agent_results: list[AgentResult]
    total_cost_usd: float
    status: str
    final_output: str
    run_state: RunState | None = None


@dataclass
class LayerBudget:
    """Per-layer spend limits."""

    daily_limit_usd: float = 500.0
    spent_usd: float = 0.0
    model_preference: str = "sonnet"
    utilization_pct: float = 0.0


class CostController:
    """Track and cap layer spend (in-memory; extend with persistence)."""

    def __init__(self) -> None:
        self._layers: dict[str, LayerBudget] = {}
        self._lock = asyncio.Lock()

    def set_budget(
        self,
        layer: str,
        *,
        daily_limit_usd: float,
        model_preference: str = "sonnet",
    ) -> None:
        lb = self._layers.get(layer, LayerBudget())
        lb.daily_limit_usd = daily_limit_usd
        lb.model_preference = model_preference
        lb.utilization_pct = (lb.spent_usd / daily_limit_usd * 100) if daily_limit_usd else 0.0
        self._layers[layer] = lb

    async def record_spend_async(self, layer: str, cost_usd: float) -> None:
        async with self._lock:
            self.record_spend(layer, cost_usd)

    def record_spend(self, layer: str, cost_usd: float) -> None:
        """Accumulate spend for a layer and refresh utilization."""
        if cost_usd <= 0:
            return
        lb = self._layers.get(layer)
        if lb is None:
            lb = LayerBudget()
            self._layers[layer] = lb
        lb.spent_usd += cost_usd
        lb.utilization_pct = (
            (lb.spent_usd / lb.daily_limit_usd * 100) if lb.daily_limit_usd else 0.0
        )

    def get_swarm_cost_report(self) -> dict[str, Any]:
        layers_out: dict[str, dict[str, Any]] = {}
        for name, lb in self._layers.items():
            layers_out[name] = {
                "spent_usd": lb.spent_usd,
                "daily_limit_usd": lb.daily_limit_usd,
                "utilization_pct": round(
                    (lb.spent_usd / lb.daily_limit_usd * 100) if lb.daily_limit_usd else 0.0,
                    2,
                ),
                "model_preference": lb.model_preference,
            }
        return {"layers": layers_out}

    def should_downgrade_model(self, layer: str, threshold_pct: float = 80.0) -> bool:
        lb = self._layers.get(layer)
        if lb is None:
            return False
        util = (lb.spent_usd / lb.daily_limit_usd * 100) if lb.daily_limit_usd else 0.0
        return util >= threshold_pct


class Swarm:
    """357-agent swarm facade — compact layered roster + durable execution."""

    def __init__(
        self,
        config_path: str | Path,
        *,
        checkpoint_store: CheckpointStore | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.config_path = Path(config_path)
        self.cost_controller = CostController()
        self._booted = False
        self._checkpoint = checkpoint_store or default_checkpoint_store()
        self._events = event_bus or get_event_bus()
        self._cancelled: set[str] = set()
        self._raw: dict[str, Any] = {}
        if self.config_path.is_file():
            self._raw = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
        self._is_compact = "layers" in self._raw and "agents" not in self._raw

    @classmethod
    def from_config(cls, path: str | Path) -> Swarm:
        return cls(path)

    def _expand_compact_roster(self) -> list[dict[str, Any]]:
        """Generate flat agent entries from the compact layers/roles format."""
        layers = self._raw.get("layers", {})
        agents: list[dict[str, Any]] = []
        for layer_name, layer_cfg in layers.items():
            default_soul = layer_cfg.get("soul", "")
            soul_overrides = layer_cfg.get("soul_overrides", {})
            for role_name, role_cfg in layer_cfg.get("roles", {}).items():
                count = int(role_cfg.get("count", 1))
                soul = soul_overrides.get(role_name, default_soul)
                for i in range(1, count + 1):
                    agents.append(
                        {
                            "name": f"{layer_name}-{role_name.replace('_', '-')}-{i:03d}",
                            "layer": layer_name,
                            "role": role_name,
                            "soul": soul,
                            "model": role_cfg.get("model", "sonnet"),
                            "budget_usd": role_cfg.get("budget_usd", 1.0),
                            "tools": role_cfg.get("tools", ["Read", "Write"]),
                        }
                    )
        return agents

    def _get_roster(self) -> list[dict[str, Any]]:
        """Return the flat agent roster regardless of config format."""
        if self._is_compact:
            return self._expand_compact_roster()
        return cast("list[dict[str, Any]]", self._raw.get("agents", []))

    def _agents_for_layer(
        self,
        layer: str,
        *,
        one_per_role: bool = True,
        max_agents: int | None = None,
        full_fanout: bool = False,
    ) -> list[AgentConfig]:
        """Return AgentConfig objects for a layer with bounded fan-out."""
        roster = self._get_roster()
        configs: list[AgentConfig] = []
        seen_roles: set[str] = set()
        unsafe = full_fanout or _UNSAFE_FULL_FANOUT
        limit = None if unsafe else (max_agents if max_agents is not None else _DEFAULT_LAYER_MAX_AGENTS)

        for entry in roster:
            if entry.get("layer") != layer:
                continue
            role = entry.get("role", "agent")
            if one_per_role and not unsafe and role in seen_roles:
                continue
            try:
                layer_type = LayerType(entry["layer"])
            except ValueError:
                continue
            configs.append(
                AgentConfig(
                    name=entry["name"],
                    layer=layer_type,
                    role=role,
                    soul=entry.get("soul", ""),
                    tools=entry.get("tools", []),
                    model=entry.get("model", "sonnet"),
                    budget_limit_usd=float(entry.get("budget_usd", 1.0)),
                )
            )
            seen_roles.add(role)
            if limit is not None and len(configs) >= limit:
                break
        return configs

    def _default_pipeline_configs(self) -> list[AgentConfig]:
        """One representative agent per layer — used when no routing logic is specified."""
        layers_in_order = [
            "research",
            "seo",
            "marketing",
            "sales",
            "support",
            "operations",
            "management",
        ]
        configs: list[AgentConfig] = []
        for layer in layers_in_order:
            layer_agents = self._agents_for_layer(layer)
            if layer_agents:
                configs.append(layer_agents[0])
            else:
                try:
                    layer_type = LayerType(layer)
                except ValueError:
                    continue
                configs.append(
                    AgentConfig(
                        name=f"{layer}-stub-001",
                        layer=layer_type,
                        role="agent",
                        soul="",
                        tools=["Read", "Write"],
                        model="sonnet",
                        budget_limit_usd=1.0,
                    )
                )
        return configs

    async def boot(self) -> None:
        """Warm CostController layer budgets from YAML configuration."""
        layer_budgets: dict[str, Any] = self._raw.get("swarm", {}).get("layer_budgets", {})
        for layer_name, budget_cfg in layer_budgets.items():
            self.cost_controller.set_budget(
                layer_name,
                daily_limit_usd=float(budget_cfg.get("daily_limit_usd", 500.0)),
                model_preference=budget_cfg.get("model_preference", "sonnet"),
            )
        self._booted = True

    async def ensure_booted(self) -> None:
        if not self._booted:
            await self.boot()

    def cancel_run(self, run_id: str) -> None:
        self._cancelled.add(run_id)

    def inspect_run(self, run_id: str) -> RunState | None:
        return self._checkpoint.load(run_id)

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._checkpoint.list_runs(limit=limit)

    async def _emit(self, event: SwarmEvent) -> None:
        await self._events.publish(event)

    async def execute_layer(
        self,
        layer: str,
        task: str,
        budget_usd: float = 100.0,
        max_parallel: int = 10,
        *,
        one_per_role: bool = True,
        max_agents: int | None = None,
        full_fanout: bool = False,
        simulate: bool = False,
    ) -> list[AgentResult]:
        """Run bounded agents in a layer in parallel with atomic budget reservations."""
        await self.ensure_booted()
        configs = self._agents_for_layer(
            layer,
            one_per_role=one_per_role,
            max_agents=max_agents,
            full_fanout=full_fanout,
        )
        if not configs:
            return []

        if simulate or not resolve_api_key():
            if not simulate and not resolve_api_key():
                raise RuntimeError(
                    "No API key configured. Pass simulate=True / --simulate for explicit simulation."
                )
            return [
                AgentResult(
                    agent_name=c.name,
                    output=f"[simulated] {layer}/{c.role}: {task[:80]}",
                    cost_usd=0.0,
                    latency_ms=0,
                    status="simulated",
                )
                for c in configs
            ]

        use_haiku = self.cost_controller.should_downgrade_model(layer)
        sem = asyncio.Semaphore(max_parallel)
        ledger = BudgetLedger.from_float(budget_usd)

        async def run_one(cfg: AgentConfig) -> AgentResult:
            async with sem:
                # Reserve per-agent budget ceiling to prevent concurrent overshoot
                reserve_amt = min(cfg.budget_limit_usd, float(ledger.remaining_usd))
                rid = await ledger.try_reserve(reserve_amt, layer=layer)
                if rid is None:
                    return AgentResult(
                        agent_name=cfg.name,
                        output="",
                        cost_usd=0.0,
                        latency_ms=0,
                        status="skipped",
                        error="budget exhausted",
                    )
                effective_model = "haiku" if use_haiku else cfg.model
                run_cfg = AgentConfig(
                    name=cfg.name,
                    layer=cfg.layer,
                    role=cfg.role,
                    soul=cfg.soul,
                    tools=cfg.tools,
                    model=effective_model,
                    budget_limit_usd=cfg.budget_limit_usd,
                    max_turns=cfg.max_turns,
                )
                try:
                    agent = Agent(run_cfg)
                    result = await agent.run(task)
                    await ledger.commit(rid, result.cost_usd)
                    await self.cost_controller.record_spend_async(layer, result.cost_usd)
                    return result
                except Exception as exc:  # noqa: BLE001
                    await ledger.release(rid)
                    return AgentResult(
                        agent_name=cfg.name,
                        output="",
                        cost_usd=0.0,
                        latency_ms=0,
                        status="error",
                        error=str(exc),
                    )

        return list(await asyncio.gather(*[run_one(cfg) for cfg in configs]))

    async def execute(
        self,
        task: str,
        budget_usd: float = 25.0,
        *,
        simulate: bool = False,
        run_id: str | None = None,
        resume_from: RunState | None = None,
    ) -> SwarmExecutionResult:
        """Run a cross-layer pipeline with durable checkpoints and structured routing."""
        await self.ensure_booted()

        if resume_from is not None:
            state = resume_from
            state.status = RunStatus.RUNNING
            state.touch()
        else:
            state = RunState(
                task=task,
                budget_usd=budget_usd,
                simulate=simulate,
                status=RunStatus.RUNNING,
            )
            if run_id:
                state.run_id = run_id

        pipeline_id = state.run_id
        self._checkpoint.save(state)
        await self._emit(
            SwarmEvent(EventType.RUN_STARTED, pipeline_id, {"task": task[:200], "simulate": simulate})
        )

        results: list[AgentResult] = []
        total = state.spent_usd
        final_chunks: list[str] = [s.output_text for s in state.steps if s.output_text]
        status = "ok"

        try:
            if simulate or (not resolve_api_key() and simulate):
                state.status = RunStatus.SIMULATED
                state.final_output = f"[simulated] {task}"
                self._checkpoint.save(state)
                await self._emit(SwarmEvent(EventType.RUN_COMPLETED, pipeline_id, {"status": "simulated"}))
                return SwarmExecutionResult(
                    pipeline_id=pipeline_id,
                    agent_results=[],
                    total_cost_usd=0.0,
                    status="simulated",
                    final_output=state.final_output,
                    run_state=state,
                )

            if not resolve_api_key():
                raise RuntimeError(
                    "No OPENROUTER_API_KEY or ANTHROPIC_API_KEY configured. "
                    "Use --simulate for an explicit simulation."
                )

            # Resume: skip completed steps
            completed_roles = {
                s.role for s in state.steps if s.status == StepStatus.COMPLETED and s.role
            }

            if not state.roles:
                conductor_cfg = next(
                    (c for c in self._agents_for_layer("management") if c.role == "conductor"),
                    None,
                )
                if not conductor_cfg:
                    conductor_cfg = AgentConfig(
                        name="management-conductor",
                        layer=LayerType.MANAGEMENT,
                        role="conductor",
                        soul="",
                        tools=[],
                        model="opus",
                        budget_limit_usd=10.0,
                        max_turns=2,
                    )
                conductor = Agent(conductor_cfg.model_copy(update={"tools": [], "max_turns": 2}))
                available_roles = list({a.get("role", "agent") for a in self._get_roster()})
                prompt = routing_prompt(task, available_roles)
                step = state.add_step(
                    StepState(
                        run_id=pipeline_id,
                        role="conductor",
                        agent_name=conductor_cfg.name,
                        layer="management",
                        status=StepStatus.RUNNING,
                        input_text=prompt,
                        model_resolved=model_id(conductor_cfg.model),
                    )
                )
                self._checkpoint.save(state)
                conductor_res = await conductor.run(prompt)
                results.append(conductor_res)
                total += conductor_res.cost_usd
                await self.cost_controller.record_spend_async(
                    conductor_cfg.layer.value, conductor_res.cost_usd
                )
                step.output_text = conductor_res.output
                step.cost_usd = conductor_res.cost_usd
                step.latency_ms = conductor_res.latency_ms
                if conductor_res.status != "success":
                    step.status = StepStatus.FAILED
                    step.error = conductor_res.error
                    state.status = RunStatus.FAILED
                    state.error = f"Conductor failed: {conductor_res.error}"
                    self._checkpoint.save(state)
                    await self._emit(
                        SwarmEvent(EventType.RUN_FAILED, pipeline_id, {"error": state.error})
                    )
                    return SwarmExecutionResult(
                        pipeline_id=pipeline_id,
                        agent_results=results,
                        total_cost_usd=total,
                        status="error",
                        final_output=state.error or "",
                        run_state=state,
                    )
                try:
                    decision = parse_routing_decision(
                        conductor_res.output, set(available_roles)
                    )
                except RoutingError as exc:
                    step.status = StepStatus.FAILED
                    step.error = str(exc)
                    state.status = RunStatus.FAILED
                    state.error = f"Routing validation failed: {exc}"
                    self._checkpoint.save(state)
                    await self._emit(
                        SwarmEvent(EventType.RUN_FAILED, pipeline_id, {"error": state.error})
                    )
                    return SwarmExecutionResult(
                        pipeline_id=pipeline_id,
                        agent_results=results,
                        total_cost_usd=total,
                        status="error",
                        final_output=state.error,
                        run_state=state,
                    )
                step.status = StepStatus.COMPLETED
                state.roles = decision.roles
                state.metadata["routing_rationale"] = decision.rationale
                state.metadata["conductor_model"] = resolved_model_info(conductor_cfg.model)
                self._checkpoint.save(state)
                await self._emit(
                    SwarmEvent(
                        EventType.STEP_COMPLETED,
                        pipeline_id,
                        {"roles": state.roles, "step_id": step.step_id},
                    )
                )

            for role in state.roles:
                if pipeline_id in self._cancelled:
                    state.status = RunStatus.CANCELLED
                    status = "cancelled"
                    break
                if role in completed_roles:
                    continue
                if total >= budget_usd:
                    break

                agent_cfg: AgentConfig | None = None
                for a in self._get_roster():
                    if a.get("role") != role:
                        continue
                    try:
                        layer_type = LayerType(a["layer"])
                    except ValueError:
                        continue
                    agent_cfg = AgentConfig(
                        name=a["name"],
                        layer=layer_type,
                        role=a.get("role", "agent"),
                        soul=a.get("soul", ""),
                        tools=a.get("tools", []),
                        model=a.get("model", "sonnet"),
                        budget_limit_usd=float(a.get("budget_usd", 1.0)),
                    )
                    break
                if not agent_cfg:
                    raise RoutingError(f"role '{role}' has no agent in roster")

                if self.cost_controller.should_downgrade_model(agent_cfg.layer.value):
                    agent_cfg = agent_cfg.model_copy(update={"model": "haiku"})

                max_turns = min(int(getattr(agent_cfg, "max_turns", 10) or 10), 5)
                agent = Agent(agent_cfg.model_copy(update={"max_turns": max_turns}))
                context_prompt = task
                if final_chunks:
                    context_prompt += "\n\nPrevious context:\n" + "\n".join(final_chunks)

                step = state.add_step(
                    StepState(
                        run_id=pipeline_id,
                        role=role,
                        agent_name=agent_cfg.name,
                        layer=agent_cfg.layer.value,
                        status=StepStatus.RUNNING,
                        input_text=context_prompt,
                        model_resolved=model_id(agent_cfg.model),
                    )
                )
                self._checkpoint.save(state)
                await self._emit(
                    SwarmEvent(
                        EventType.STEP_STARTED,
                        pipeline_id,
                        {"step_id": step.step_id, "role": role, "agent": agent_cfg.name},
                    )
                )

                res = await agent.run(context_prompt)
                results.append(res)
                total += res.cost_usd
                state.spent_usd = total
                await self.cost_controller.record_spend_async(agent_cfg.layer.value, res.cost_usd)
                step.output_text = res.output
                step.cost_usd = res.cost_usd
                step.latency_ms = res.latency_ms
                if res.status == "success":
                    step.status = StepStatus.COMPLETED
                    if res.output:
                        final_chunks.append(res.output)
                else:
                    step.status = StepStatus.FAILED
                    step.error = res.error
                self._checkpoint.save(state)
                await self._emit(
                    SwarmEvent(
                        EventType.COST,
                        pipeline_id,
                        {"spent_usd": total, "step_cost": res.cost_usd},
                    )
                )

            if state.status not in {RunStatus.CANCELLED, RunStatus.FAILED}:
                state.status = RunStatus.COMPLETED
            state.final_output = "\n\n".join(final_chunks)
            state.spent_usd = total
            self._checkpoint.save(state)
            await self._emit(
                SwarmEvent(
                    EventType.RUN_COMPLETED,
                    pipeline_id,
                    {"status": state.status.value, "spent_usd": total},
                )
            )
        except Exception as exc:
            status = "error"
            state.status = RunStatus.FAILED
            state.error = str(exc)
            self._checkpoint.save(state)
            await self._emit(SwarmEvent(EventType.RUN_FAILED, pipeline_id, {"error": str(exc)}))
            raise
        finally:
            log_telemetry(
                "swarm_run",
                {
                    "pipeline_id": pipeline_id,
                    "task": task[:120],
                    "total_cost_usd": total,
                    "agents_used": [r.agent_name for r in results],
                    "latency_ms": sum(r.latency_ms for r in results),
                    "status": status if state.status != RunStatus.CANCELLED else "cancelled",
                    "models": [s.model_resolved for s in state.steps if s.model_resolved],
                },
            )

        return SwarmExecutionResult(
            pipeline_id=pipeline_id,
            agent_results=results,
            total_cost_usd=total,
            status="cancelled" if state.status == RunStatus.CANCELLED else ("ok" if status == "ok" else status),
            final_output=state.final_output,
            run_state=state,
        )

    async def resume(self, run_id: str) -> SwarmExecutionResult:
        state = self._checkpoint.load(run_id)
        if state is None:
            raise KeyError(f"run not found: {run_id}")
        if state.status in {RunStatus.COMPLETED, RunStatus.SIMULATED}:
            return SwarmExecutionResult(
                pipeline_id=run_id,
                agent_results=[],
                total_cost_usd=state.spent_usd,
                status=state.status.value,
                final_output=state.final_output,
                run_state=state,
            )
        return await self.execute(
            state.task,
            budget_usd=state.budget_usd,
            simulate=state.simulate,
            resume_from=state,
        )

    async def replay(self, run_id: str) -> SwarmExecutionResult:
        """Re-run a prior task as a new run, linking parent_run_id."""
        state = self._checkpoint.load(run_id)
        if state is None:
            raise KeyError(f"run not found: {run_id}")
        return await self.execute(state.task, budget_usd=state.budget_usd, simulate=state.simulate)

    async def fork(self, run_id: str, *, edit_task: str | None = None) -> SwarmExecutionResult:
        from techtide_swarm.runtime.state import new_id

        state = self._checkpoint.load(run_id)
        if state is None:
            raise KeyError(f"run not found: {run_id}")
        new_state = RunState(
            run_id=new_id(),
            task=edit_task or state.task,
            budget_usd=state.budget_usd,
            simulate=state.simulate,
            parent_run_id=run_id,
            roles=list(state.roles),
            status=RunStatus.PENDING,
            metadata={"forked_from": run_id},
        )
        return await self.execute(
            new_state.task,
            budget_usd=new_state.budget_usd,
            simulate=new_state.simulate,
            resume_from=new_state,
        )
