# Swarm 357 — Executable acceptance criteria

This document is the **mechanical** gate list for releases. Every check must be backed by CI, a script, or a live probe — not marketing language.

## Matrix

| Category | Verifier | Pass criteria |
|----------|----------|----------------|
| **Claim integrity** | Roster + health | `python scripts/generate_roster.py --compact --fix-counts` exits 0; Docker/`GET /api/health` → `agents == 357` |
| **Install path** | Clean wheel | Build wheel → fresh venv → `swarm boot` loads 357 agents; Support souls present in package data |
| **Runtime correctness** | Pytest | `pytest packages/techtide-swarm/tests -v -p no:schemathesis` green |
| **Fan-out safety** | Pytest | Layer runs default to one agent per role with a hard cap; full fan-out requires explicit flag |
| **Budgets** | Pytest | Concurrent reservations cannot exceed the ceiling |
| **Auth** | Docker/CI | Production/`SWARM_REQUIRE_AUTH=1` without `SWARM_API_KEY` → fail closed; bad key → **401**; unauthenticated POST ≠ **200** |
| **Failures** | API tests | Execution errors return **4xx/5xx**, never HTTP 200 with `"status":"error"` alone |
| **Models** | Pytest | OpenRouter does not silently map opus/sonnet → Haiku unless `SWARM_OPENROUTER_CHEAP=1` |
| **Durable runtime** | Pytest | Checkpoint save/load/resume; cancel/replay/fork CLI/API |
| **Streaming** | API smoke | `GET /api/swarm/runs/{id}/events` streams SSE |
| **Security tools** | Pytest | Bash denied in server mode; Read/Write confined to workspace root |
| **Bridge** | CI rust job | `cargo fmt/clippy/build` + bridge integration tests with `MEMVID_SWARM_BRIDGE` |
| **Evals** | Baseline artifacts | Single-agent and swarm metrics reported **separately** in `evals/baselines/latest.json`; README numbers regenerated via `scripts/render_eval_assets.py` |
| **Landing** | Split repo | [TechTideOhio/swarm-357-site](https://github.com/TechTideOhio/swarm-357-site) CI build green; not shipped inside this core repo |
| **Supply chain** | Publish workflow | Tagged release builds wheel/sdist, attestations, PyPI publish after CI |

## Commands

```bash
pip install -e "packages/techtide-swarm[dev]"
ruff check packages/techtide-swarm/src
cd packages/techtide-swarm && mypy src && python -m pytest tests -v -p no:schemathesis && cd ../..
python scripts/generate_roster.py --compact --fix-counts

# Clean wheel smoke
python -m build packages/techtide-swarm
python -m venv /tmp/swarm-wheel && /tmp/swarm-wheel/bin/pip install packages/techtide-swarm/dist/*.whl
/tmp/swarm-wheel/bin/swarm boot

# Docker
docker build -t swarm357-api .
docker run --rm -e SWARM_API_KEY=ci -e SWARM_REQUIRE_AUTH=1 -p 8000:8000 swarm357-api
curl -sf http://127.0.0.1:8000/api/health
```

## Definition: “357 agents”

**357 agents** means **357 distinct agent identities** (YAML roster + soul templates) orchestrated by the runtime — not 357 parallel long-running LLM sessions. Default layer execution selects **one agent per role** with a configurable cap.

## Maturity honesty

See [STATUS.md](../STATUS.md). Stable ≠ complete agent platform. Durable checkpoints, SSE, and HITL approvals are **Beta**; dream write-back and Opik remain experimental/planned.
