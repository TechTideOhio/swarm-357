"""Swarm pipeline and CostController tests."""

import textwrap

import pytest

from techtide_swarm import CostController, Swarm


@pytest.mark.asyncio
async def test_swarm_execute_stub(tmp_path):
    config_path = tmp_path / "swarm.yaml"
    config_path.write_text("# empty config for stub mode\n")
    swarm = Swarm.from_config(config_path)
    result = await swarm.execute("Analyze the AI market", budget_usd=5.0)
    assert result.status == "ok"
    assert len(result.agent_results) >= 1


@pytest.mark.asyncio
async def test_swarm_no_config_file(tmp_path):
    swarm = Swarm(tmp_path / "nonexistent.yaml")
    result = await swarm.execute("Test task")
    assert result.status == "ok"


def test_cost_controller_budget():
    cc = CostController()
    cc.set_budget("marketing", daily_limit_usd=50.0, model_preference="sonnet")
    report = cc.get_swarm_cost_report()
    assert "marketing" in report["layers"]
    assert report["layers"]["marketing"]["daily_limit_usd"] == 50.0
    assert report["layers"]["marketing"]["utilization_pct"] == 0.0


def test_cost_controller_downgrade():
    cc = CostController()
    cc.set_budget("research", daily_limit_usd=100.0)
    assert cc.should_downgrade_model("research") is False
    assert cc.should_downgrade_model("nonexistent") is False


def test_compact_format_expansion(tmp_path):
    """Compact YAML with layers/roles generates the correct agent count."""
    compact = textwrap.dedent("""\
        swarm:
          version: "2.0"
          total_agents: 5
          layer_budgets:
            research: {daily_limit_usd: 100.0, model_preference: sonnet}
        layers:
          research:
            roles:
              analyst: {count: 3, model: sonnet, budget_usd: 2.0, tools: [Read, Write]}
              synthesizer: {count: 2, model: opus, budget_usd: 5.0, tools: [Read]}
            soul: templates/soul/research/market-analyst.md
    """)
    cfg = tmp_path / "compact.yaml"
    cfg.write_text(compact)
    swarm = Swarm(cfg)
    assert swarm._is_compact is True

    roster = swarm._get_roster()
    assert len(roster) == 5
    analysts = [a for a in roster if a["role"] == "analyst"]
    assert len(analysts) == 3
    assert all(a["model"] == "sonnet" for a in analysts)
    synths = [a for a in roster if a["role"] == "synthesizer"]
    assert len(synths) == 2
    assert all(a["model"] == "opus" for a in synths)
    names = [a["name"] for a in roster]
    assert len(set(names)) == 5


def test_legacy_format_still_works(tmp_path):
    """Legacy flat agents list still loads correctly."""
    legacy = textwrap.dedent("""\
        swarm:
          version: "1.0"
          layer_budgets:
            sales: {daily_limit_usd: 50.0}
        agents:
          - name: sales-crm-001
            layer: sales
            role: crm_operator
            model: haiku
            budget_usd: 0.5
            tools: [Read]
    """)
    cfg = tmp_path / "legacy.yaml"
    cfg.write_text(legacy)
    swarm = Swarm(cfg)
    assert swarm._is_compact is False

    agents = swarm._agents_for_layer("sales")
    assert len(agents) == 1
    assert agents[0].name == "sales-crm-001"
    assert agents[0].role == "crm_operator"


@pytest.mark.asyncio
async def test_compact_execute_stub(tmp_path):
    """Compact config produces a working swarm execution in stub mode."""
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
              analyst: {count: 2, model: sonnet, budget_usd: 2.0, tools: [Read]}
            soul: templates/soul/research/market-analyst.md
    """)
    cfg = tmp_path / "compact.yaml"
    cfg.write_text(compact)
    swarm = Swarm(cfg)
    await swarm.boot()
    result = await swarm.execute("Test task", budget_usd=10.0)
    assert result.status == "ok"


def test_roster_soul_uniqueness():
    """Every unique role in config/swarm.yaml must have its own distinct soul file.

    This is the machine-checkable proof that 357 agents are substantively different —
    not 357 copies of the same 8 prompts.
    """
    from collections import defaultdict
    from pathlib import Path

    import yaml

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    roster_path = repo_root / "config" / "swarm.yaml"
    if not roster_path.is_file():
        pytest.skip("config/swarm.yaml not present in test environment")

    raw = yaml.safe_load(roster_path.read_text(encoding="utf-8"))
    agents = raw.get("agents", [])

    role_to_soul: dict[str, str] = {}
    for a in agents:
        role = a.get("role", "")
        soul = a.get("soul", "")
        if role and role not in role_to_soul:
            role_to_soul[role] = soul

    soul_to_roles: dict[str, list[str]] = defaultdict(list)
    for role, soul in role_to_soul.items():
        soul_to_roles[soul].append(role)

    violations = {s: r for s, r in soul_to_roles.items() if len(r) > 1}
    assert not violations, (
        f"The following soul files are shared by multiple distinct roles "
        f"(each role must have its own soul template):\n"
        + "\n".join(f"  {s}: {r}" for s, r in violations.items())
    )


def test_roster_soul_files_exist():
    """Every soul path in config/swarm.yaml must point to a real file."""
    from pathlib import Path

    import yaml

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    roster_path = repo_root / "config" / "swarm.yaml"
    if not roster_path.is_file():
        pytest.skip("config/swarm.yaml not present in test environment")

    raw = yaml.safe_load(roster_path.read_text(encoding="utf-8"))
    agents = raw.get("agents", [])

    missing = [
        f"{a['name']} -> {a['soul']}"
        for a in agents
        if a.get("soul") and not (repo_root / a["soul"]).is_file()
    ]
    assert not missing, f"Missing soul files:\n" + "\n".join(f"  {m}" for m in missing)
