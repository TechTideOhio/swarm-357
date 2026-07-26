# Changelog

All notable changes to TechTide Swarm 357 are documented here.

## [0.2.1] — 2026-07-25

### Correction (v0.2.0)

v0.2.0 public docs/CI badges still referenced scrubbed paths (`.github` workflows, landing tree, vendored Memvid). Fresh installs could not `swarm boot` from the wheel; Support souls were missing; OpenRouter silently mapped opus/sonnet → Haiku; HTTP errors returned 200; layer fan-out could dispatch entire layers.

### Added

- Restored `.github/workflows/ci.yml` + `publish.yml` (SHA-pinned actions, attestations, no core-repo frontend job).
- Durable runtime: typed `RunState`/`StepState`, SQLite checkpoints, inspect/resume/cancel/replay/fork, SSE events, HITL approval stubs.
- Atomic `BudgetLedger`, structured routing JSON, resilience helpers, workspace-confined Read/Write, argv Bash policy.
- `resolve_config_path()` + `swarm init` installs bundled compact config and all Support souls.
- Structured traces (`.swarm/traces.jsonl`) with optional OTel export (`SWARM_OTEL_EXPORT=1`).
- Split landing to [TechTideOhio/swarm-357-site](https://github.com/TechTideOhio/swarm-357-site).
- Memvid bridge depends on crates.io `memvid-core` 2.x; `Cargo.lock` committed.

### Fixed

- HTTP `ensure_booted()`; meaningful 4xx/5xx; production auth fail-closed without `SWARM_API_KEY`.
- OpenRouter model defaults no longer silently substitute Haiku (opt-in `SWARM_OPENROUTER_CHEAP=1`).
- Layer runs default to one agent per role with a hard cap.
- Telemetry redacts secrets before JSONL write.
- Explicit `--simulate` / `SWARM_SIMULATE` instead of successful stubs without credentials.

### Changed

- Package version **0.2.0 → 0.2.1**.
- Docs/STATUS/VERIFY rewritten as executable acceptance criteria (no “10/10” marketing).

## [0.2.0] — 2026-07-24

### Added

- OpenRouter provider support via [`llm.py`](packages/techtide-swarm/src/techtide_swarm/llm.py) (`OPENROUTER_API_KEY`, `ANTHROPIC_BASE_URL`).
- Tool input normalization ([`tools/input_normalize.py`](packages/techtide-swarm/src/techtide_swarm/tools/input_normalize.py)) — alias coercion (`file_path` → `path`), JSON string inputs, unknown-kwarg filtering.
- Eval harness v2: LLM judge, `$5` hard budget, checkpoint/resume, burn passes, baseline compare ([`evals/run_evals.py`](evals/run_evals.py)).
- Generated eval reporting: [`scripts/render_eval_assets.py`](scripts/render_eval_assets.py), [`docs/EVALS.md`](docs/EVALS.md), [`docs/assets/eval-results.svg`](docs/assets/eval-results.svg).
- Brand + architecture assets under [`docs/assets/`](docs/assets/) (logo, banner, architecture, request lifecycle).
- Landing `/about` route; OG image + PWA icons; TLDR template chrome removed.
- Wheel bundles `config/swarm-compact.yaml` + `templates/soul/` for self-contained `pip install techtide-swarm`.
- `__version__` on package; `/api/health` reports dynamic version.
- Community docs: [`SECURITY.md`](SECURITY.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), [`RELEASE.md`](RELEASE.md).
- CI: Docker `/api/health` agents==357 smoke; Next.js typecheck + build; GitHub Release on `v*` tags.

### Fixed

- `write_file` / Write tool arity and clearer schema when models omit `content`.
- Conductor routing runs text-only (`tools=[]`, `max_turns=2`) to avoid tool-call stalls.
- Agent multi-turn serialization skips thinking blocks; preserves cost on error.
- Eval keyword scoring coerces non-string YAML keywords (e.g. bare `401`).
- Resume re-runs prior `error` checkpoint tasks after harness fixes.
- Landing metadata/sitemap no longer point at `example.com` / TLDR branding.

### Changed

- Package version **0.1.0 → 0.2.0**.
- Root README rewritten with badges, diagrams, and generated eval numbers (25-task catalog; not “5 tasks”).
- Package README expanded for PyPI (API, CLI, HTTP routes, env vars).

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
