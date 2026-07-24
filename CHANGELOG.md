# Changelog

All notable changes to TechTide Swarm 357 are documented here.

## [0.1.0] — 2026-04-09

### Added

- Structured HTTP request logging (JSON) and `X-Correlation-ID` via ASGI middleware ([`structured_logging`](packages/techtide-swarm/src/techtide_swarm/structured_logging.py)).
- Optional eval LLM judge (`SWARM_EVAL_LLM_JUDGE`) and optional dream-cycle Haiku notes (`SWARM_DREAM_USE_LLM`) in eval harness and `MemoryManager.run_dream_cycle`.
- Docs: [docs/BASELINE_MATRIX.md](docs/BASELINE_MATRIX.md), [docs/DATA_PLANE.md](docs/DATA_PLANE.md), [docs/COMPARISON.md](docs/COMPARISON.md); extended [docs/DEPLOY_RAILWAY.md](docs/DEPLOY_RAILWAY.md) checklist and troubleshooting.
- [CONTRIBUTING.md](CONTRIBUTING.md) for contributors.
- Objective verification scorecard: [docs/VERIFY.md](docs/VERIFY.md).
- `scripts/generate_roster.py --compact` to validate `config/swarm-compact.yaml` expansion to 357 agents.
- HTTP API protections: optional `SWARM_API_KEY` / `X-SWARM-API-KEY` on POST routes; per-IP rate limiting (`SWARM_RATE_LIMIT_PER_MINUTE`); hard cap on `budget_usd` via `SWARM_MAX_RUN_BUDGET_USD`.
- Docker-friendly config resolution: `SWARM_CONFIG_PATH` or `/app/config/swarm-compact.yaml`.
- CI: Docker build + `/api/health` assert `agents == 357`.
- Railway deployment notes: [docs/DEPLOY_RAILWAY.md](docs/DEPLOY_RAILWAY.md).

### Changed

- Landing: `NEXT_PUBLIC_SWARM_WRITE_KEY` documented for protected POST demos; Live Numbers links to `/api/health`.
