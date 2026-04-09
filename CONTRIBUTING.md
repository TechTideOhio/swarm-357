# Contributing to TechTide Swarm 357

Thank you for contributing. Every improvement makes the swarm better.

Project docs: [README.md](README.md) and [CLAUDE.md](CLAUDE.md).
Feature maturity: [STATUS.md](STATUS.md).

## Quick Start

Work from the swarm357 repo root (in the TechTide monorepo: `Apps/swarm357/`).

```bash
git clone https://github.com/TechTideAI/swarm-357.git
cd swarm-357
make install    # pip install -e packages/techtide-swarm[dev]
make test       # pytest
swarm demo      # works with or without API key
```

## Development Commands

```bash
make install    # install editable package with dev deps
make test       # run all tests
make lint       # ruff check
make typecheck  # mypy strict
make demo       # run swarm demo
make all        # install + lint + typecheck + test
```

## 5 Ways to Contribute

### 1. Add a SOUL.md Template (Beginner)

Every agent runs a personality. Add or edit Markdown under `templates/soul/<layer>/`.
Layer folders: sales, support, marketing, seo, research, operations, management.

### 2. Add a Tool (Intermediate)

Extend `packages/techtide-swarm/src/techtide_swarm/tools/__init__.py` with a new
tool entry in `TOOLS_REGISTRY`. Tools that execute commands **must** go through
`BashSecurityGate` (see the `Bash` tool for the pattern).

### 3. Add an Evaluation Task (Intermediate)

Add a new `EvalTask` to `evals/run_evals.py`. Each task needs:
- Descriptive prompt
- Target layer
- Expected keywords for scoring
- Minimum output length

### 4. Write Example Workflows (Beginner)

Add scenarios to `docs/` or create runnable scripts under `examples/`.

### 5. Improve the CLI (Advanced)

The CLI in `packages/techtide-swarm/src/techtide_swarm/cli.py` handles all
`swarm` subcommands. See [STATUS.md](STATUS.md) for which commands are beta/alpha.

## Code Standards

- **Python 3.10+** with type hints everywhere
- **Ruff** for linting: `make lint`
- **MyPy** for type checking: `make typecheck`
- **Pytest** for tests: `make test`
- Keep functions under 50 lines

## PR Process

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run `make all` (install, lint, typecheck, test)
5. Submit a PR with a clear description

CI runs [`.github/workflows/swarm357-ci.yml`](.github/workflows/swarm357-ci.yml).

## What NOT to Contribute

- Proprietary API keys or credentials
- Copyrighted content in SOUL.md templates
- Changes that break the agent count validation
- Dependencies that are not MIT/Apache/BSD licensed
