# Swarm 357 — Verification scorecard (10/10)

This document is the **single source of truth** for objective checks. Each category should pass before claiming that maturity level in release notes.

## Category matrix

| Category | Verifier | Pass criteria |
|----------|----------|----------------|
| **Claim integrity** | Roster scripts + `/api/health` | `python scripts/generate_roster.py --fix-counts` and `python scripts/generate_roster.py --compact --fix-counts` exit 0; `GET /api/health` → `agents` == **357** (with shipped compact config). |
| **Runtime correctness** | Pytest | `pytest packages/techtide-swarm/tests -v` green; stub mode when `ANTHROPIC_API_KEY` unset; live mode when key set. |
| **Tools & tasks** | Code + STATUS | No tool claims “live” behavior without env-backed providers; see [STATUS.md](../STATUS.md). |
| **Production ops** | Docker + Railway | `docker build -f Dockerfile .` succeeds; container `GET /api/health` returns 200; [docs/DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md). |
| **Data plane** | SQL migration | [database/migrations/001_initial.sql](../database/migrations/001_initial.sql) matches `SwarmStore` inserts; apply in Supabase SQL editor or CLI. See [DATA_PLANE.md](DATA_PLANE.md). |
| **Security** | Pytest + curl | When `SWARM_API_KEY` is set, `POST /api/swarm/run` without `X-SWARM-API-KEY` returns **401**; rate limit returns **429** when exceeded. |
| **Observability** | Local + optional cloud | `.swarm/telemetry.jsonl` appended on runs; Supabase dual-write when `SUPABASE_*` set. |
| **UX / OSS** | Landing build | `cd .ui_landin_sample/minimal && npm run build` succeeds; README quickstart matches repo layout. |

## Commands (copy-paste)

From repository root `Apps/swarm357` (or `swarm357` if standalone):

```bash
# Python package
pip install -e "packages/techtide-swarm[dev,supabase]"
ruff check packages/techtide-swarm/src
cd packages/techtide-swarm && mypy src && cd ../..

# Roster: legacy flat + compact (Docker/API default)
python scripts/generate_roster.py --fix-counts
python scripts/generate_roster.py --compact --fix-counts

# Tests
python -m pytest packages/techtide-swarm/tests -v

# Docker smoke (optional)
docker build -t swarm357-api -f Dockerfile .
docker run --rm -p 8000:8000 swarm357-api &
curl -s http://127.0.0.1:8000/api/health | jq .
```

## Definition: “357 agents”

**357 agents** means **357 distinct agent identities** (YAML roster expansion + soul templates) orchestrated by the Swarm runtime — not 357 parallel long-running LLM processes or 357 simultaneous Opus calls. Layer concurrency caps apply (`execute_layer` semaphore).
