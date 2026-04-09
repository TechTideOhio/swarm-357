# TechTide Swarm 357 — Feature Status

Feature maturity levels:
- **Stable** — tested, documented, safe for production use
- **Beta** — working but evolving, API may change
- **Alpha** — functional but incomplete
- **Planned** — designed but not yet implemented

## Core Package (`packages/techtide-swarm/`)

| Feature | Status | Notes |
|---------|--------|-------|
| `Agent` — single-agent runner | **Stable** | Stub mode (no key) and live Anthropic API mode |
| `AgentConfig` — Pydantic config model | **Stable** | Validated via Pydantic v2 |
| `Swarm` — multi-agent orchestration | **Beta** | Conductor-routes-to-roles pipeline. Sequential execution. |
| `Swarm.execute_layer()` — layer-level parallel execution | **Beta** | `asyncio.gather` with semaphore-based concurrency cap |
| `CostController` — per-layer budget tracking | **Beta** | In-memory tracking; model downgrade signal at 80% utilization |
| Per-agent `budget_limit_usd` enforcement | **Alpha** | Tracked but enforcement during `Agent.run()` is partial |
| `MemoryManager` — flat-file memory | **Stable** | `.swarm/topics/*.json` share/recall with substring matching |
| `MemoryManager` — Memvid `.mv2` backend | **Beta** | Requires `memvid-swarm-bridge` binary (Rust) |
| `run_dream_cycle()` — contradiction detection | **Alpha** | String-overlap heuristics; no LLM analysis yet |
| `BashSecurityGate` — 13-pattern command validation | **Stable** | 50+ tests covering all patterns |
| `UltraPlan` — Opus planning sessions | **Beta** | Single API call; stub when no key |
| Telemetry — JSONL logging | **Beta** | Local file append; no external observability integration |
| Tool system (Read, Write, WebSearch) | **Alpha** | WebSearch is a stub returning placeholder text |

## CLI (`swarm` command)

| Command | Status | Notes |
|---------|--------|-------|
| `swarm init` | **Stable** | Creates project structure + `.env` + memory index |
| `swarm demo` | **Stable** | Architecture overview (no key) or live API call (with key) |
| `swarm run <task>` | **Beta** | Full pipeline or `--layer` for single-layer execution |
| `swarm boot` | **Beta** | Loads roster, validates, prints layer manifest |
| `swarm agent [id]` | **Beta** | `--list`, `--info`, `--run TASK` |
| `swarm status` | **Beta** | Reads from local telemetry JSONL |
| `swarm cost` | **Beta** | Reads from local telemetry JSONL |
| `swarm dream` | **Alpha** | Loads topics, runs contradiction detection |
| `swarm plan <task>` | **Beta** | Stub (no key) or live Opus planning (with key) |
| `swarm migrate` | **Beta** | Flat-file to Memvid `.mv2` migration |

## Infrastructure

| Feature | Status | Notes |
|---------|--------|-------|
| CI (GitHub Actions) | **Stable** | Python tests, Next.js build, Rust bridge build + integration |
| PyPI publishing | **Planned** | Package is editable-install only for now |
| Evaluation harness | **Alpha** | Basic task runner; needs LLM-as-judge scoring |
| Landing page | **Alpha** | Next.js 16 template; content not finalized |
| Memvid bridge (Rust binary) | **Stable** | `create`, `put`, `search`, `verify` commands |

## What is NOT yet implemented

- Real-time parallel agent execution across layers in `swarm run`
- Sandboxed execution environments for untrusted agent code
- Rate limiting / circuit breakers
- Persistent observability (Opik, Prometheus, etc.)
- Human-in-the-loop gates
- Agent-to-agent direct messaging
- Durable execution / checkpointing (LangGraph-style)
- SSO / multi-tenancy / data residency
