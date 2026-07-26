# TechTide Swarm 357: Feature Status

Maturity levels:
- **Stable** - tested, documented, safe for production use under stated constraints
- **Beta** - working but evolving; API may change
- **Experimental** - functional but incomplete or opt-in
- **Not implemented** - explicitly out of scope for the current release

## Product framing

Swarm 357 is a **357-role catalog plus orchestration runtime**, not a production-complete autonomous agent platform. Operators own API keys, budgets, and side-effect approvals.

## Core package (`packages/techtide-swarm/`)

| Feature | Status | Notes |
|---------|--------|-------|
| `Agent` - single-agent runner | **Stable** | Live API when keyed; explicit `SWARM_SIMULATE` / `SWARM_ALLOW_STUB` otherwise (no silent success) |
| `AgentConfig` | **Stable** | Pydantic v2 |
| `Swarm` orchestration | **Beta** | Structured JSON routing; durable `RunState` + SQLite checkpoints |
| `execute_layer()` | **Beta** | One-per-role default, hard agent cap; `full_fanout` / `SWARM_UNSAFE_FULL_FANOUT` opt-in |
| Atomic `BudgetLedger` | **Beta** | Reserve/commit under asyncio lock |
| `CostController` | **Beta** | Layer spend + 80% model downgrade |
| `MemoryManager` flat files | **Stable** | Topics share/recall |
| Memvid `.mv2` via bridge | **Beta** | Requires `memvid-swarm-bridge` (crates.io `memvid-core`) |
| `run_dream_cycle()` | **Experimental** | Heuristics; not guaranteed consolidate/prune |
| `BashSecurityGate` + argv policy | **Stable** | Server/prod denies Bash unless `SWARM_ALLOW_BASH=1` |
| Read/Write workspace confinement | **Stable** | Server mode confines to workspace root |
| HTTP API | **Beta** | Fail-closed auth in production; non-200 errors; SSE events |
| HITL approvals | **Beta** | Real Bash gate (`SWARM_HITL_BASH`); `swarm approve`/`reject` + HTTP; timeout rejects |
| SSE event stream | **Beta** | Auth when `SWARM_API_KEY` set; bus closes on terminal run; `stream.end` |
| Structured traces | **Beta** | `.swarm/traces.jsonl`; optional OTel via `SWARM_OTEL_EXPORT=1` |
| UltraPlan | **Beta** | Opus-class planning when keyed |

## CLI

| Command | Status | Notes |
|---------|--------|-------|
| `swarm init` | **Stable** | Installs bundled compact config + Support souls |
| `swarm demo` | **Stable** | Explicit simulation without key |
| `swarm boot` / `run` | **Beta** | Resolves bundled config from wheel installs |
| `swarm inspect/resume/cancel/approve/reject/replay/fork` | **Beta** | Durable cancel flag + HITL control plane |
| `swarm eval` | **Beta** | Separate single vs swarm reporting |
| `swarm serve` | **Beta** | FastAPI |

## Infrastructure

| Feature | Status | Notes |
|---------|--------|-------|
| CI | **Stable** | `.github/workflows/ci.yml` - Python 3.10-3.13, roster, wheel smoke, Docker auth, Rust, docs ban check |
| PyPI publish | **Beta** | `publish.yml` with attestations; CI gate before publish |
| Landing site | **Beta** | Docs at https://swarm357fe.up.railway.app/docs; source in [TechTideOhio/swarm-357-site](https://github.com/TechTideOhio/swarm-357-site) |
| Branch protection / scanning | **Beta** | Operator-applied on GitHub (see RELEASE.md) |

## Not implemented

- Multi-tenant SaaS control plane / SSO
- Distributed rate limiting across many replicas (single-process limiter ships)
- Guaranteed dream-cycle consolidation quality
- Full Opik cloud observability (local JSONL is source of truth)
