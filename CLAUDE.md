# CLAUDE.md

Guidance for Claude Code and other agents working in **TechTideOhio/swarm-357** (this public core repo).

Maturity claims must match [STATUS.md](STATUS.md). Do not invent Stable/Beta surfaces that STATUS marks Not implemented. Numbers for evals come from `evals/baselines/latest.json` via `scripts/render_eval_assets.py` — never hand-edit README/EVALS metrics.

## What This Repo Is

TechTide Swarm 357 is a **357-role catalog plus orchestration runtime** across 6 business layers (Sales 62, Support 55, Marketing 68, SEO 47, Research 58, Operations 57) plus Management (10 meta-agents). It is an organizational ontology for agents — **not** a claim that 357 Opus sessions run in parallel.

| Path | Purpose |
|------|---------|
| `packages/techtide-swarm/` | Installable Python package: `techtide_swarm` + `swarm` CLI + FastAPI server |
| `packages/memvid-swarm-bridge/` | Rust CLI wrapping **crates.io `memvid-core`** for `MemoryManager` |
| `templates/soul/` | Layer personality templates (also bundled in the wheel) |
| `config/` | Compact roster YAML (`swarm-compact.yaml`) for Docker and local boots |
| `evals/` | 25-task harness, baselines, judge |
| `docs/` | VERIFY, EVALS, DEPLOY_RAILWAY, MEMVID_BRIDGE, DATA_PLANE, etc. |
| `scripts/` | Roster generation, eval asset render, quickstart |

**Landing site is a separate repo:** [TechTideOhio/swarm-357-site](https://github.com/TechTideOhio/swarm-357-site) - live docs at `https://swarm357fe.up.railway.app/docs`, API `https://swarm357be.up.railway.app`.

Do **not** reference scrubbed/private trees in public docs or commits: `.planning/`, `.repos and items/`, `.ui_landin_sample/`. CI `docs-links` bans those strings in markdown.

## Python package (`packages/techtide-swarm/`)

```bash
pip install -e "packages/techtide-swarm[dev]"
# or from PyPI:
pip install techtide-swarm
```

Source: `packages/techtide-swarm/src/techtide_swarm/`.

### Key classes

| Class | Purpose |
|-------|---------|
| `Agent(AgentConfig)` | Single agent — `await agent.run(task)` |
| `Swarm.from_config(path)` | Full swarm — `await swarm.execute(task)` |
| `UltraPlan(UltraPlanConfig)` | Deep Opus-class planning session |
| `MemoryManager` | Flat-file topics + optional Memvid bridge |
| `BashSecurityGate` | 13-pattern bash command validation |
| `CostController` | Layer spend; **logged** 80%→Haiku downgrade (`model_downgrade`) |
| `ApprovalGate` | Bash HITL — durable `ApprovalRecord` + approve/reject wait |

### AgentConfig fields

```python
AgentConfig(
    name="research-market-001",
    layer=LayerType.RESEARCH,   # SALES, SUPPORT, MARKETING, SEO, RESEARCH, OPERATIONS
    role="market_researcher",
    soul="templates/soul/research/market-analyst.md",
    tools=["WebSearch", "Read", "Write"],
    model="sonnet",             # or "opus" / "haiku"
    budget_limit_usd=1.00,
)
```

### CLI (`swarm` command)

```bash
swarm init                              # Bundled compact config + souls + .swarm/
swarm demo                              # Explicit simulation without a key
swarm status                            # Layer health dashboard
swarm cost                              # Model usage cost report
swarm boot                              # Boot roster (357 identities)
swarm run <task>                        # Execute across swarm
swarm dream                             # Experimental memory consolidation
swarm plan <task>                       # ULTRAPLAN
swarm inspect|resume|cancel|replay|fork # Checkpoint control plane
swarm approve <id> | swarm reject <id>  # Bash HITL
swarm eval                              # Catalog + baseline compare
swarm serve                             # FastAPI HTTP API
```

### HTTP API (high level)

- Public: `GET /api/health`, roster/status/cost reads
- Authenticated writes when `SWARM_API_KEY` set: `POST /api/swarm/run`, cancel, approve/reject, **SSE** `GET /api/swarm/runs/{id}/events`
- SSE requires the same write key; bus closes on terminal run; final `stream.end` event
- Production fail-closed without key — see [SECURITY.md](SECURITY.md)

### Memory system

1. `.swarm/MEMORY.md` — Pointer index (keep short)
2. `.swarm/topics/` — Flat-file knowledge (Stable fallback)
3. Optional Memvid `.mv2` via `memvid-swarm-bridge` (Beta)
4. `.swarm/transcripts/`, `.swarm/telemetry.jsonl`, `.swarm/traces.jsonl` — append-only; not loaded wholesale into context
5. SQLite checkpoints under `.swarm/checkpoints.db` — durable `RunState` including `cancel_requested` and approvals

`run_dream_cycle()` is **Experimental** (heuristics; not guaranteed consolidate/prune). Full Opik cloud is **Not implemented** — local JSONL is source of truth; optional/planned hooks only.

### Security defaults (Steinberger local-first)

| Control | Default |
|---------|---------|
| Read/Write confinement | CWD / `SWARM_WORKSPACE_ROOT`; escape only with `SWARM_UNSAFE_FS=1` |
| Bash in server/prod | Denied unless `SWARM_ALLOW_BASH=1` |
| Bash HITL | On in server/production (`SWARM_HITL_BASH`); timeout via `SWARM_HITL_TIMEOUT_SEC` |
| OpenRouter cheap remap | Off unless `SWARM_OPENROUTER_CHEAP=1` (never silent Haiku map) |
| CostController Haiku | Explicit logged downgrade at 80% layer spend — not the same as OpenRouter remap |

### Required env vars

```
ANTHROPIC_API_KEY=sk-ant-...
# or OpenRouter:
# ANTHROPIC_BASE_URL=https://openrouter.ai/api
# OPENROUTER_API_KEY=sk-or-...
```

Optional:

```
MEMVID_SWARM_BRIDGE=/path/to/memvid-swarm-bridge
SWARM_API_KEY=...
SWARM_HITL_BASH=0|1
SWARM_ALLOW_BASH=1
SWARM_WORKSPACE_ROOT=/path
SWARM_UNSAFE_FS=1
SWARM_OPENROUTER_CHEAP=1
ALLOWED_ORIGINS=https://swarm357fe.up.railway.app
```

Prefer OpenRouter with cheap tool-capable models for live tests/evals over expensive direct Anthropic spend.

### Model short names (Claude 4.x)

| Short | Env override | Default model ID |
|-------|--------------|------------------|
| `opus` | `SWARM_MODEL_OPUS` | `claude-opus-4-6` |
| `sonnet` | `SWARM_MODEL_SONNET` | `claude-sonnet-4-6` |
| `haiku` | `SWARM_MODEL_HAIKU` | `claude-haiku-4-5-20251001` |

### SOUL templates

Live under `templates/soul/<layer>/` (packaged into the wheel; Support souls CI-verified). YAML front-matter (`name`, `layer`, `role`, `model`, `budget_limit_usd`, `skills`, `memory`, `tools`) + system prompt.

```
templates/soul/
├── sales/
│   ├── crm-operator.md
│   └── outreach-specialist.md
├── support/
│   └── tier1-resolver.md
├── marketing/
│   └── content-strategist.md
├── seo/
│   └── keyword-researcher.md
├── research/
│   └── market-analyst.md
├── operations/
│   └── project-coordinator.md
└── management/
    └── conductor.md
```

### Code standards

- Python 3.10+ with type hints
- `ruff check src/` / `mypy src/` / `pytest tests/ -v`
- Coverage floor enforced in CI (`--cov-fail-under=40`)
- Functions under 50 lines when practical
- No silent stub success in production paths

## Memvid bridge (`packages/memvid-swarm-bridge/`)

Depends on **crates.io `memvid-core` 2.x** — not a vendored Memvid source tree in this repo.

```bash
cd packages/memvid-swarm-bridge
cargo build --release
cargo test
export MEMVID_SWARM_BRIDGE="$(pwd)/target/release/memvid-swarm-bridge"
```

Bridge verbs: `create` / `put` / `search` / `verify`. See [docs/MEMVID_BRIDGE.md](docs/MEMVID_BRIDGE.md).

`.mv2` is a single-file portable store (WAL, lex, optional vec). Design rules for the upstream library: single-file, crash-safe WAL, append-only frames, sync API.

## Landing site (separate repo)

Product marketing and Try-it-live live in [swarm-357-site](https://github.com/TechTideOhio/swarm-357-site):

- Next.js App Router + TypeScript + Tailwind
- Content/flags in `lib/config.ts`
- Demo writes go through a **same-origin BFF** (`/api/swarm/run`) with server-only `SWARM_API_KEY` — never `NEXT_PUBLIC_SWARM_WRITE_KEY` in the client bundle
- Testimonials/use-case copy must stay honest (scenarios, not fake customers)

Local FE commands (in that repo): `bun run dev` / `bun run build` / `bun run typecheck` (Railway FE uses npm + `package-lock.json`).

## Docs of record

| Doc | Role |
|-----|------|
| [STATUS.md](STATUS.md) | Maturity matrix — single source of truth for Stable/Beta/Experimental/Not implemented |
| [SECURITY.md](SECURITY.md) | Auth, bash, HITL, FS confinement, model mapping honesty |
| [docs/VERIFY.md](docs/VERIFY.md) | Executable acceptance criteria / scorecard |
| [docs/EVALS.md](docs/EVALS.md) | Eval harness; baseline-driven metrics |
| [docs/DEPLOY_RAILWAY.md](docs/DEPLOY_RAILWAY.md) | Railway FE/BE deploy |
| [RELEASE.md](RELEASE.md) | Cut tags, branch protection, publish |
| [README.md](README.md) | Public product entry |

## Agent working rules for this repo

1. Prefer product truth over theater: real HITL/SSE/cancel or demote in STATUS — never leave Beta stubs.
2. Do not edit attached plan/roadmap artifacts unless the user explicitly asks.
3. Do not commit secrets (`.env`, keys). Local secrets stay gitignored (e.g. `.env.local` / Railway env).
4. After behavior changes that affect claims, update STATUS + VERIFY + SECURITY as needed, then re-render eval assets if metrics moved.
5. Public GitHub source of truth: `TechTideOhio/swarm-357`. Site: `TechTideOhio/swarm-357-site`.
