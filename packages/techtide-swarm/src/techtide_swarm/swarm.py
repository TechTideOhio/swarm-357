"""Multi-agent swarm orchestration (minimal implementation)."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

from techtide_swarm.agent import Agent, AgentConfig, AgentResult
from techtide_swarm.core.types import LayerType
from techtide_swarm.telemetry import log_telemetry


@dataclass
class SwarmExecutionResult:
    """Result of Swarm.execute."""

    pipeline_id: str
    agent_results: list[AgentResult]
    total_cost_usd: float
    status: str
    final_output: str


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
    """357-agent swarm facade — supports both legacy flat roster and compact layered format."""

    def __init__(self, config_path: str | Path) -> None:
        self.config_path = Path(config_path)
        self.cost_controller = CostController()
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
                    agents.append({
                        "name": f"{layer_name}-{role_name.replace('_', '-')}-{i:03d}",
                        "layer": layer_name,
                        "role": role_name,
                        "soul": soul,
                        "model": role_cfg.get("model", "sonnet"),
                        "budget_usd": role_cfg.get("budget_usd", 1.0),
                        "tools": role_cfg.get("tools", ["Read", "Write"]),
                    })
        return agents

    def _get_roster(self) -> list[dict[str, Any]]:
        """Return the flat agent roster regardless of config format."""
        if self._is_compact:
            return self._expand_compact_roster()
        return cast("list[dict[str, Any]]", self._raw.get("agents", []))

    def _agents_for_layer(self, layer: str) -> list[AgentConfig]:
        """Return AgentConfig objects for all agents in a given layer."""
        roster = self._get_roster()
        configs: list[AgentConfig] = []
        for entry in roster:
            if entry.get("layer") != layer:
                continue
            try:
                layer_type = LayerType(entry["layer"])
            except ValueError:
                continue
            configs.append(
                AgentConfig(
                    name=entry["name"],
                    layer=layer_type,
                    role=entry.get("role", "agent"),
                    soul=entry.get("soul", ""),
                    tools=entry.get("tools", []),
                    model=entry.get("model", "sonnet"),
                    budget_limit_usd=float(entry.get("budget_usd", 1.0)),
                )
            )
        return configs

    def _default_pipeline_configs(self) -> list[AgentConfig]:
        """One representative agent per layer — used when no routing logic is specified."""
        layers_in_order = ["research", "seo", "marketing", "sales", "support", "operations", "management"]
        configs: list[AgentConfig] = []
        for layer in layers_in_order:
            layer_agents = self._agents_for_layer(layer)
            if layer_agents:
                configs.append(layer_agents[0])
            else:
                # fallback stub when YAML is missing or layer not present
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

    async def execute_layer(
        self,
        layer: str,
        task: str,
        budget_usd: float = 100.0,
        max_parallel: int = 10,
    ) -> list[AgentResult]:
        """Run all agents in a single layer in parallel, capped at max_parallel concurrent calls."""
        configs = self._agents_for_layer(layer)
        if not configs:
            return []

        use_haiku = self.cost_controller.should_downgrade_model(layer)
        sem = asyncio.Semaphore(max_parallel)
        spent = 0.0

        async def run_one(cfg: AgentConfig) -> AgentResult:
            nonlocal spent
            async with sem:
                if spent >= budget_usd:
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
                agent = Agent(run_cfg)
                result = await agent.run(task)
                spent += result.cost_usd
                self.cost_controller.record_spend(layer, result.cost_usd)
                return result

        return list(await asyncio.gather(*[run_one(cfg) for cfg in configs]))

    async def execute(self, task: str, budget_usd: float = 25.0) -> SwarmExecutionResult:
        """Run a cross-layer pipeline dynamically orchestrated by the Conductor."""
        pipeline_id = f"pipe-{os.getpid()}"
        
        results: list[AgentResult] = []
        total = 0.0
        final_chunks: list[str] = []
        remaining_budget = budget_usd

        # 1. Boot Conductor
        conductor_cfg = next((c for c in self._agents_for_layer("management") if c.role == "conductor"), None)
        if not conductor_cfg:
            # Fallback conductor
            conductor_cfg = AgentConfig(
                name="management-conductor",
                layer=LayerType.MANAGEMENT,
                role="conductor",
                soul="",
                tools=["Read", "Write"],
                model="opus",
                budget_limit_usd=10.0,
            )
            
        # Routing is text-only — tools during role selection cause flaky multi-turn loops.
        conductor = Agent(conductor_cfg.model_copy(update={"tools": [], "max_turns": 2}))

        status = "ok"
        try:
            # 2. Ask Conductor to route the task
            available_roles = list(set(a.get("role", "agent") for a in self._get_roster()))
            routing_prompt = (
                f"You are the Conductor. Analyze the following task and decide which agent roles are needed to complete it.\n"
                f"Available roles: {', '.join(sorted(available_roles))}\n\n"
                f"Task: {task}\n\n"
                f"Return ONLY a comma-separated list of roles to execute in order. "
                f"Pick 2-5 roles. No tools, no explanation, no markdown."
            )

            conductor_res = await conductor.run(routing_prompt)
            results.append(conductor_res)
            total += conductor_res.cost_usd
            self.cost_controller.record_spend(conductor_cfg.layer.value, conductor_res.cost_usd)

            if conductor_res.status != "success":
                return SwarmExecutionResult(
                    pipeline_id=pipeline_id,
                    agent_results=results,
                    total_cost_usd=total,
                    status="error",
                    final_output=f"Conductor failed: {conductor_res.error}",
                )

            # Parse conductor output; keep only roles that exist in the roster
            available_set = set(available_roles)
            roles_to_run = [
                r.strip()
                for r in conductor_res.output.split(",")
                if r.strip() and r.strip() in available_set
            ]
            if not roles_to_run:
                # Prefer known specialists that exist; else one agent per layer
                preferred = [
                    "market_analyst",
                    "market_researcher",
                    "content_strategist",
                    "outreach_specialist",
                ]
                roles_to_run = [r for r in preferred if r in available_set]
            if not roles_to_run:
                roles_to_run = [
                    c.role for c in self._default_pipeline_configs() if c.role in available_set
                ]

            # 3. Execute the selected roles
            for role in roles_to_run:
                if total >= budget_usd:
                    break

                # Find an agent with this role
                agent_cfg = None
                for a in self._get_roster():
                    if a.get("role") == role:
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
                    continue

                if self.cost_controller.should_downgrade_model(agent_cfg.layer.value):
                    agent_cfg = agent_cfg.model_copy(update={"model": "haiku"})

                # Cap turns so tool loops cannot hang a pipeline indefinitely
                max_turns = min(int(getattr(agent_cfg, "max_turns", 10) or 10), 5)
                agent = Agent(agent_cfg.model_copy(update={"max_turns": max_turns}))

                # Pass previous context to the next agent
                context_prompt = task
                if final_chunks:
                    context_prompt += "\n\nPrevious context:\n" + "\n".join(final_chunks)

                res = await agent.run(context_prompt)
                results.append(res)
                total += res.cost_usd
                remaining_budget -= res.cost_usd
                self.cost_controller.record_spend(agent_cfg.layer.value, res.cost_usd)
                if res.output:
                    final_chunks.append(res.output)
        except Exception:
            status = "error"
            raise
        finally:
            log_telemetry("swarm_run", {
                "pipeline_id": pipeline_id,
                "task": task[:120],
                "total_cost_usd": total,
                "agents_used": [r.agent_name for r in results],
                "latency_ms": sum(r.latency_ms for r in results),
                "status": status,
            })

        return SwarmExecutionResult(
            pipeline_id=pipeline_id,
            agent_results=results,
            total_cost_usd=total,
            status="ok",
            final_output="\n\n".join(final_chunks),
        )
