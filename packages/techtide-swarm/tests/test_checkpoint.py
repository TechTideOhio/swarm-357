# file: packages/techtide-swarm/tests/test_checkpoint.py
# description: MemoryCheckpointStore save/load/resume round-trips
# reference: techtide_swarm.runtime.checkpoint, techtide_swarm.runtime.state

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from techtide_swarm.agent import AgentResult
from techtide_swarm.runtime.checkpoint import MemoryCheckpointStore
from techtide_swarm.runtime.state import RunState, RunStatus, StepState, StepStatus
from techtide_swarm.swarm import Swarm


def test_memory_checkpoint_save_load() -> None:
    store = MemoryCheckpointStore()
    state = RunState(task="ship the launch", budget_usd=10.0, status=RunStatus.RUNNING)
    state.roles = ["market_analyst"]
    state.add_step(
        StepState(
            run_id=state.run_id,
            role="market_analyst",
            agent_name="research-market-analyst-001",
            layer="research",
            status=StepStatus.COMPLETED,
            output_text="done",
        )
    )
    store.save(state)

    loaded = store.load(state.run_id)
    assert loaded is not None
    assert loaded.run_id == state.run_id
    assert loaded.task == "ship the launch"
    assert loaded.roles == ["market_analyst"]
    assert len(loaded.steps) == 1
    assert loaded.steps[0].status == StepStatus.COMPLETED
    assert loaded.steps[0].output_text == "done"

    listed = store.list_runs(limit=10)
    assert any(r["run_id"] == state.run_id for r in listed)


@pytest.mark.asyncio
async def test_swarm_resume_from_memory_checkpoint(
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
    swarm = Swarm(cfg, checkpoint_store=store)
    await swarm.boot()

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-for-resume")

    async def fake_run(self, task: str) -> AgentResult:
        if self.config.role == "conductor":
            output = '{"roles": ["market_analyst"], "rationale": "research"}'
        else:
            output = "analyst ok"
        return AgentResult(
            agent_name=self.config.name,
            output=output,
            cost_usd=0.1,
            latency_ms=1,
            status="success",
        )

    monkeypatch.setattr("techtide_swarm.agent.Agent.run", fake_run)

    # Partial run: save RUNNING state with conductor done, role pending
    state = RunState(
        task="resume me",
        budget_usd=10.0,
        status=RunStatus.RUNNING,
        roles=["market_analyst"],
        spent_usd=0.1,
    )
    state.add_step(
        StepState(
            run_id=state.run_id,
            role="conductor",
            agent_name="management-conductor-001",
            layer="management",
            status=StepStatus.COMPLETED,
            output_text='{"roles": ["market_analyst"]}',
        )
    )
    store.save(state)

    result = await swarm.resume(state.run_id)
    assert result.status == "ok"
    names = [r.agent_name for r in result.agent_results]
    assert any("market" in n or "analyst" in n for n in names)

    loaded = store.load(state.run_id)
    assert loaded is not None
    assert loaded.status == RunStatus.COMPLETED
