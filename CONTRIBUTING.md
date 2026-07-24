# Contributing to TechTide Swarm 357

Thanks for helping improve Swarm 357. This repo is Python-first (`packages/techtide-swarm`) with an optional Next.js landing under `.ui_landin_sample/minimal/`.

## Quick setup

From `Apps/swarm357`:

```bash
pip install -e "packages/techtide-swarm[dev,supabase]"
python -m ruff check packages/techtide-swarm/src
cd packages/techtide-swarm && python -m mypy src && cd ../..
python -m pytest packages/techtide-swarm/tests -v
```

See [docs/VERIFY.md](docs/VERIFY.md) for the full verification scorecard.

## Pull requests

1. Run **ruff**, **mypy** (from `packages/techtide-swarm`), and **pytest** before pushing.
2. Keep claims aligned with [README.md](README.md): **357 agents** means 357 roster identities, not 357 parallel long-lived LLM sessions.
3. For behavior changes, add or update tests under `packages/techtide-swarm/tests/`.
4. Optional web search backends: install `techtide-swarm[web]` locally; CI does not require them.

## Optional extras

- **Memvid bridge**: build `packages/memvid-swarm-bridge` and set `MEMVID_SWARM_BRIDGE`.
- **Supabase**: apply [database/migrations/001_initial.sql](database/migrations/001_initial.sql); see [docs/DATA_PLANE.md](docs/DATA_PLANE.md).
