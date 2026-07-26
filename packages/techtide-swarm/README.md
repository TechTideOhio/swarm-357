# techtide-swarm

[![PyPI](https://img.shields.io/pypi/v/techtide-swarm.svg)](https://pypi.org/project/techtide-swarm/)
[![Python](https://img.shields.io/pypi/pyversions/techtide-swarm.svg)](https://pypi.org/project/techtide-swarm/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/TechTideOhio/swarm-357/blob/main/LICENSE)
[![CI](https://github.com/TechTideOhio/swarm-357/actions/workflows/ci.yml/badge.svg)](https://github.com/TechTideOhio/swarm-357/actions/workflows/ci.yml)

Python package for **Swarm 357**: layered orchestration of 357 Claude agent roles across six business layers, portable Memvid memory, cost controls, and a FastAPI HTTP surface.

## Install

```bash
pip install techtide-swarm
swarm demo
```

Editable (from repo root):

```bash
pip install -e "packages/techtide-swarm[dev]"
```

The wheel bundles `config/swarm-compact.yaml` and `templates/soul/` so `swarm boot` works after a plain `pip install`.

## Quickstart

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # or OPENROUTER_API_KEY + ANTHROPIC_BASE_URL
swarm init
swarm boot                            # loads 357-agent compact roster
swarm run "Draft a Tier-1 401 triage checklist" --budget 1.0
swarm serve --port 8000
```

OpenRouter (recommended for evals/cost control):

```bash
export OPENROUTER_API_KEY=...
export ANTHROPIC_BASE_URL=https://openrouter.ai/api
export SWARM_MODEL_SONNET=anthropic/claude-sonnet-4
```

## Public API

```python
from techtide_swarm import (
    Agent, AgentConfig, Swarm, UltraPlan, UltraPlanConfig,
    MemoryManager, CostController, BashSecurityGate, __version__,
)
from techtide_swarm.core.types import LayerType

agent = Agent(AgentConfig(
    name="research-market-001",
    layer=LayerType.RESEARCH,
    role="market_researcher",
    soul="templates/soul/research/market-analyst.md",
    tools=["Read", "Write"],
    model="sonnet",
    budget_limit_usd=1.0,
))
```

Also exported: `AgentResult`, `SwarmExecutionResult`, `SwarmStore`, `MemvidBridge`, `ToolRegistry`, `TOOLSET_MAP`, `registry`.

## CLI

| Command | Purpose |
|---------|---------|
| `swarm init` | Create `.swarm/`, `.env`, memory index |
| `swarm demo` | Stub or live 3-agent demo |
| `swarm boot` | Load roster + print layer budgets |
| `swarm run <task>` | Full swarm or `--layer` execution |
| `swarm agent` | List / inspect / run one agent |
| `swarm status` / `swarm cost` | Telemetry dashboards |
| `swarm dream` | Memory consolidation cycle |
| `swarm plan <task>` | UltraPlan (Opus by default) |
| `swarm migrate` | Flat topics → Memvid `.mv2` |
| `swarm eval` | Budgeted eval harness |
| `swarm serve` | FastAPI via uvicorn |
| `swarm mcp list\|connect` | MCP server tools |

## HTTP API

`uvicorn techtide_swarm.server:app` (or `swarm serve`):

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/health` | version, agent count, API key presence |
| GET | `/api/swarm/status` | layer stats + cost |
| GET | `/api/swarm/agents` | roster summary |
| GET | `/api/swarm/agents/{name}` | agent detail |
| GET | `/api/swarm/cost` | spend report |
| GET | `/api/swarm/runs` | recent runs |
| POST | `/api/swarm/run` | swarm/layer run (`X-SWARM-API-KEY` when set) |
| POST | `/api/agent/run` | single agent |
| POST | `/api/swarm/dream` | dream cycle |

## Environment

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` / `OPENROUTER_API_KEY` | LLM credentials |
| `ANTHROPIC_BASE_URL` | e.g. `https://openrouter.ai/api` |
| `SWARM_MODEL_{OPUS,SONNET,HAIKU}` | Model ID overrides |
| `SWARM_API_KEY` | Protect POST routes |
| `SWARM_MAX_RUN_BUDGET_USD` | Cap request `budget_usd` |
| `SWARM_RATE_LIMIT_PER_MINUTE` | Per-IP rate limit (`0` disables) |
| `SWARM_CONFIG_PATH` | Roster YAML override |
| `MEMVID_SWARM_BRIDGE` | Path to Rust bridge binary |
| `SWARM_WRITE_SAFE_ROOT` | Sandbox for Write tool |

## Docs

| Resource | Link |
|----------|------|
| Documentation site | https://swarm357fe.up.railway.app/docs |
| About and positioning | https://swarm357fe.up.railway.app/about |
| Getting started | https://swarm357fe.up.railway.app/docs/getting-started/quickstart |
| Feature maturity | https://swarm357fe.up.railway.app/docs/resources/status |
| Eval methodology | https://swarm357fe.up.railway.app/docs/evals/methodology |
| Security model | https://swarm357fe.up.railway.app/docs/security/security-model |
| Design system | https://swarm357fe.up.railway.app/docs/resources/design |
| Core repository | [TechTideOhio/swarm-357](https://github.com/TechTideOhio/swarm-357) |
| Landing repository | [TechTideOhio/swarm-357-site](https://github.com/TechTideOhio/swarm-357-site) |

## License

Apache-2.0
