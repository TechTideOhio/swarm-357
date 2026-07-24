# Changelog

All notable changes to TechTide Swarm 357 are documented here.

## [0.1.0] — 2026-07-24

### Added

- `CostController.record_spend()` — layer spend now accumulates from `Swarm.execute` and `execute_layer`, enabling the 80% model-downgrade path.
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

### Fixed

- Conductor fallback roles now validated against the roster (`market_analyst` etc.); no longer silently skips specialists on stub/unparseable routing.
- `swarm boot` and `swarm agent --list` use expanded compact roster (was showing 0 agents for `swarm-compact.yaml`).
- `swarm dream` prints actual `run_dream_cycle` fields (`contradictions_found`, `duplicates_found`, …).
- Memvid bridge failures log warnings instead of silent `pass`; one-time warning when bridge binary is missing.
- Landing: hero reads `heroConfig`; footer contact points at GitHub issues; fabricated testimonials gated off.

### Changed

- Landing: `NEXT_PUBLIC_SWARM_WRITE_KEY` documented for protected POST demos; Live Numbers links to `/api/health`.
- GitHub links updated to `TechTideOhio/swarm-357`.
