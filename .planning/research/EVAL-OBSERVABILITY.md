# Eval and Observability Strategy

## Current state

- Agent.run() returns `trace_url` when `OPIK_WORKSPACE` is set (placeholder URL format)
- CLI `swarm cost` shows illustrative cost tables
- CLI `swarm status` shows illustrative layer health dashboard
- No actual Opik API integration yet
- No eval framework for agent output quality

## Observability layers

### Layer 1: Cost tracking (implemented as demo)

- `CostController` tracks per-layer daily limits and utilization
- `Agent._estimate_cost()` computes approximate cost from token usage
- `swarm cost` CLI renders a model-level cost report

**Next step:** Persist cost data to `.swarm/metrics/costs.jsonl` for trend analysis.

### Layer 2: Trace collection (stub)

- Agent.run() constructs a `trace_url` but does not send data to Opik
- No span/event model for multi-step agent execution

**Next step:** Integrate `opik` Python SDK:
```python
import opik
tracer = opik.Opik(api_key=os.getenv("OPIK_API_KEY"))
with tracer.trace(name=self.config.name) as span:
    # ... agent execution ...
    span.set_attribute("cost_usd", cost)
    span.set_attribute("layer", self.config.layer.value)
```

### Layer 3: Eval metrics (not started)

Candidate metrics per agent run:
- **Relevance:** Does the output address the task? (LLM-as-judge)
- **Completeness:** Are all requested sections present?
- **Tone consistency:** Does it match the SOUL.md personality?
- **Source quality:** Are cited sources authoritative?
- **Actionability:** Can the reader act on the output immediately?

**Approach:** Lightweight eval in `test_agent.py` using golden prompts:
```python
async def test_research_agent_output_shape():
    agent = Agent(AgentConfig(name="eval-001", layer=LayerType.RESEARCH, ...))
    result = await agent.run("List top 3 trends in AI agents")
    assert result.status == "success"
    assert len(result.output) > 100
    assert any(word in result.output.lower() for word in ["trend", "agent", "ai"])
```

### Layer 4: Regression testing (not started)

- Store golden (prompt, expected_output_shape) pairs in `tests/golden/`
- Run on CI; fail if output shape changes unexpectedly
- Not exact string matching -- use heuristics (length, keywords, structure)

## Opik integration plan

1. Add `opik` to `pyproject.toml` optional dependencies
2. Create `observability.py` with `SwarmTracer` class
3. Instrument `Agent.run()` with span creation
4. Instrument `Swarm.execute()` with pipeline-level trace
5. Add `swarm traces` CLI command to list recent traces
6. Dashboard: link to Opik web UI from `swarm status`

## Success criteria

- Every agent run produces a trace with: name, layer, model, cost, latency, status
- `swarm cost` reflects actual (not illustrative) data after a demo run
- At least one golden eval test per layer passes in CI
