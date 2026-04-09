# TechTide Swarm 357

Layered agent orchestration for business automation -- 357 Claude AI agents across 6 business layers, backed by portable Memvid memory and honest cost controls.

```
                  Management (10) -- Conductor, strategy, memory curation
                       |
    +--------+---------+---------+---------+---------+
    |        |         |         |         |         |
  Sales    Support  Marketing   SEO    Research  Operations
   (62)     (55)      (68)     (47)     (58)       (57)
```

## Install

```bash
pip install -e "packages/techtide-swarm[dev]"
swarm demo
```

`swarm demo` works with or without an API key -- it shows the architecture and a sample stub when no key is set, or runs a live agent when `ANTHROPIC_API_KEY` is configured.

## What This Does

- **`swarm run <task>`** -- Routes a task through the Conductor, which selects agents by role across layers. Passes context sequentially. Shows real cost and latency.
- **`swarm boot`** -- Loads the 357-agent roster from `config/swarm.yaml`, validates soul files, and prints the layer manifest with budget allocations.
- **`swarm agent --list`** -- List all agents. `swarm agent <name> --run "task"` to run a specific one.
- **`swarm dream`** -- Runs memory consolidation: loads `.swarm/topics/`, detects contradictions via string overlap.
- **`swarm plan <task>`** -- Deep planning via Claude Opus.
- **`swarm eval`** -- Runs 5 benchmark tasks, scores by keyword overlap, compares against baseline.
- **`swarm status`** / **`swarm cost`** -- Layer health and cost dashboards from local telemetry.

## Architecture

| Component | Location | What it does |
|-----------|----------|-------------|
| Python package | [`packages/techtide-swarm/`](packages/techtide-swarm/) | `Agent`, `Swarm`, `CostController`, `MemoryManager`, `BashSecurityGate`, CLI |
| Memvid bridge (Rust) | [`packages/memvid-swarm-bridge/`](packages/memvid-swarm-bridge/) | CLI binary for `.mv2` create/put/search/verify |
| Agent roster | [`config/swarm.yaml`](config/swarm.yaml) | 357 agent entries across 7 layers with roles, models, budgets |
| Soul templates | [`templates/soul/`](templates/soul/) | 8 personality files with YAML front-matter + system prompts |
| Eval harness | [`evals/`](evals/) | 5-task benchmark with keyword scoring and baseline comparison |
| Landing page | [`.ui_landin_sample/minimal/`](.ui_landin_sample/minimal/) | Next.js 16 template (content in progress) |
| Memvid core (vendored) | [`.repos and items/memvid-main/`](.repos%20and%20items/memvid-main/) | Upstream Rust library referenced by bridge `Cargo.toml` |

## Key Differentiators

**Portable .mv2 memory** -- Each agent layer gets a single-file Memvid store with WAL-based crash safety, full-text + vector search, and integrity verification. No database server needed.

**Business-layer ontology** -- Not just "agent A talks to agent B." Six domain layers + management meta-agents model a real organizational structure.

**Layered cost controls** -- Per-agent budget caps (enforced during `Agent.run()`), per-layer daily limits, and automatic model downgrade at 80% utilization.

**BashSecurityGate** -- 13-pattern regex validator wired into the `Bash` tool. Blocks destructive commands, secret exfiltration, and dangerous system operations. 50+ tests.

## Feature Maturity

See [STATUS.md](STATUS.md) for the full breakdown. Summary:

| Feature | Status |
|---------|--------|
| Agent + Swarm orchestration | Beta |
| CLI (all 11 commands) | Stable/Beta |
| Memory (flat-file + Memvid) | Beta |
| BashSecurityGate | Stable |
| Cost controls | Beta (enforcement: Alpha) |
| Dream cycle | Alpha |
| Eval harness | Alpha |
| WebSearch tool | Stub |

## Why Not [X]?

| Framework | Swarm 357 advantage | Their advantage |
|-----------|--------------------|--------------------|
| LangGraph | Portable `.mv2` memory; business-layer ontology | Durable checkpointing; larger ecosystem; PyPI package |
| CrewAI | Enforced cost controls; security gate; layered architecture | Faster time-to-first-value; YAML crew config |
| OpenAI Agents SDK | Multi-agent orchestration; memory persistence | Input/output guardrails; simpler API surface |

## Memvid Bridge

Build (requires Rust 1.85+):
```bash
cd packages/memvid-swarm-bridge && cargo build --release
```

Set `MEMVID_SWARM_BRIDGE` to the binary path. See [`docs/MEMVID_BRIDGE.md`](docs/MEMVID_BRIDGE.md).

## Development

```bash
make install    # pip install editable + dev deps
make test       # pytest (56 tests, <1s)
make lint       # ruff check
make typecheck  # mypy strict
make all        # install + lint + typecheck + test
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

## CI

GitHub Actions: [`.github/workflows/swarm357-ci.yml`](.github/workflows/swarm357-ci.yml)
- Python: install, ruff, mypy, pytest
- Roster: validate 357 agent counts
- Next.js: build + typecheck
- Rust: cargo build + bridge integration tests

## Required Environment

```bash
ANTHROPIC_API_KEY=sk-ant-...    # for live agent execution
```

Optional:
```bash
SWARM_MODEL_OPUS=claude-opus-4-6
SWARM_MODEL_SONNET=claude-sonnet-4-6
SWARM_MODEL_HAIKU=claude-haiku-4-5-20251001
MEMVID_SWARM_BRIDGE=/path/to/memvid-swarm-bridge
```

## Deployment

### Railway

Two Railway services back this product:

| Service | Build | Root | Health check |
|---------|-------|------|--------------|
| `backend` | Dockerfile | `/` | `/api/health` |
| `frontend` | Nixpacks (Next.js 16) | `.ui_landin_sample/minimal/` | `/` |

```bash
# 1. Authenticate & link
railway login
railway init              # creates a new Railway project

# 2. Deploy backend (uses root Dockerfile + railway.toml)
railway up --service backend

# 3. Set backend env vars (replace with real values)
railway variables set ANTHROPIC_API_KEY=sk-ant-... --service backend
railway variables set SUPABASE_URL=https://xxxx.supabase.co --service backend
railway variables set SUPABASE_SERVICE_KEY=eyJ... --service backend

# 4. Deploy frontend
railway up --service frontend --rootDirectory .ui_landin_sample/minimal

# 5. Wire services together
#    - Get backend URL: railway domain --service backend
#    - Set on frontend:
railway variables set NEXT_PUBLIC_API_URL=https://<backend>.up.railway.app --service frontend
#    - Allow frontend origin on backend CORS:
railway variables set ALLOWED_ORIGINS=https://<frontend>.up.railway.app --service backend

# 6. Verify
curl https://<backend>.up.railway.app/api/health   # {"status":"ok","agents":357,...}
curl -I https://<frontend>.up.railway.app/          # HTTP/2 200
```

**Custom domain:** Railway dashboard → Service → Settings → Domains → Add Custom Domain, then add a CNAME record at your DNS provider pointing to the Railway-assigned hostname. TLS is auto-provisioned.

<!-- GIF: 30-second screen recording of the live demo — add here once deployed -->

## License

Apache-2.0
