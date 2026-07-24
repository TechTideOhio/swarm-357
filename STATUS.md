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
| Per-agent `budget_limit_usd` enforcement | **Beta** | Enforced after each model turn (stops before further tool rounds when over budget) |
| `MemoryManager` — flat-file memory | **Stable** | `.swarm/topics/*.json` share/recall with substring matching |
| `MemoryManager` — Memvid `.mv2` backend | **Beta** | Requires `memvid-swarm-bridge` binary (Rust) |
| `run_dream_cycle()` — contradiction detection | **Beta** | String-overlap heuristics; optional Haiku notes when `SWARM_DREAM_USE_LLM=1` |
| `BashSecurityGate` — 13-pattern command validation | **Stable** | 50+ tests covering all patterns |
| `UltraPlan` — Opus planning sessions | **Beta** | Single API call; stub when no key |
| Telemetry — JSONL logging | **Beta** | Local file append; optional Supabase dual-write; HTTP API emits structured JSON logs + `X-Correlation-ID` |
| Tool system (Read, Write, WebSearch) | **Beta** | WebSearch uses Exa/Firecrawl when installed and configured; otherwise explicit stub JSON (see `tools/web_search.py`) |
| HTTP API (`techtide_swarm.server`) | **Beta** | GET routes public; POST routes optional `SWARM_API_KEY` + `X-SWARM-API-KEY`; per-IP rate limit; `budget_usd` capped by `SWARM_MAX_RUN_BUDGET_USD` |

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
| CI (GitHub Actions) | **Stable** | Python tests, Next.js build, Rust bridge, roster validators, Docker `/api/health` smoke |
| PyPI publishing | **Beta** | [`.github/workflows/publish.yml`](../.github/workflows/publish.yml) on `v*` tags (trusted publishing); verify project on PyPI |
| Evaluation harness | **Beta** | Keyword overlap + optional Haiku judge when `SWARM_EVAL_LLM_JUDGE=1` |
| Landing page | **Beta** | Next.js 16; public GET-only data by default; optional `NEXT_PUBLIC_SWARM_WRITE_KEY` for demo POSTs |
| Memvid bridge (Rust binary) | **Stable** | `create`, `put`, `search`, `verify` commands |
| Claim verification | **Stable** | [docs/VERIFY.md](docs/VERIFY.md) + `scripts/generate_roster.py --compact --fix-counts` |

## What is NOT yet implemented

- Real-time parallel agent execution across layers in `swarm run`
- Sandboxed execution environments for untrusted agent code
- Circuit breakers for external APIs
- Persistent observability (Opik, Prometheus, etc.)
- Human-in-the-loop gates
- Agent-to-agent direct messaging
- Durable execution / checkpointing (LangGraph-style)
- SSO / multi-tenancy / data residency
