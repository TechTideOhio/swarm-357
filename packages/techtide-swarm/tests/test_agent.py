"""Agent stub mode tests -- no API key required."""

import pytest

from techtide_swarm import Agent, AgentConfig
from techtide_swarm.core.types import LayerType
from techtide_swarm.tools import execute_tool


@pytest.mark.asyncio
async def test_agent_stub_returns_success():
    """With SWARM_ALLOW_STUB (conftest), missing keys yield an explicit stub/sim result."""
    config = AgentConfig(
        name="test-research-001",
        layer=LayerType.RESEARCH,
        role="market_researcher",
        tools=["Read"],
        model="sonnet",
        budget_limit_usd=0.50,
    )
    agent = Agent(config)
    result = await agent.run("List top 3 AI agent trends")
    assert result.status in {"stub", "simulated"}
    assert "[stub]" in result.output or "[simulated]" in result.output
    assert config.name in result.output
    assert result.cost_usd == 0.0
    assert result.latency_ms == 0


@pytest.mark.asyncio
async def test_agent_without_stub_flag_errors(monkeypatch):
    monkeypatch.delenv("SWARM_ALLOW_STUB", raising=False)
    monkeypatch.delenv("SWARM_SIMULATE", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    config = AgentConfig(
        name="test-research-002",
        layer=LayerType.RESEARCH,
        role="market_researcher",
        model="sonnet",
    )
    result = await Agent(config).run("ping")
    assert result.status == "error"
    assert result.error and "API_KEY" in result.error


@pytest.mark.asyncio
async def test_agent_stub_includes_layer():
    config = AgentConfig(
        name="test-sales-001",
        layer=LayerType.SALES,
        role="outreach",
        model="haiku",
    )
    agent = Agent(config)
    result = await agent.run("Write a cold email to Acme Corp")
    assert "sales" in result.output.lower()


@pytest.mark.asyncio
async def test_agent_config_defaults():
    config = AgentConfig(name="minimal", layer=LayerType.OPERATIONS, role="ops")
    assert config.model == "sonnet"
    assert config.budget_limit_usd == 1.0
    assert config.max_turns == 10
    assert config.tools == []


def test_bash_tool_blocks_dangerous_commands():
    result = execute_tool("run_bash", {"command": "rm -rf /"})
    assert "BLOCKED" in result
    assert "BashSecurityGate" in result


def test_bash_tool_allows_safe_commands():
    result = execute_tool("run_bash", {"command": "echo hello"})
    assert "BLOCKED" not in result


def test_websearch_tool_identifies_as_stub():
    result = execute_tool("web_search", {"query": "test query"})
    assert "stub" in result.lower()


def test_agent_result_has_no_trace_url():
    """trace_url was removed — verify the field no longer exists."""
    from techtide_swarm.agent import AgentResult
    r = AgentResult(output="x", cost_usd=0.0, latency_ms=0, status="ok")
    assert not hasattr(r, "trace_url")
