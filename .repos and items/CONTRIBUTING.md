# Contributing to TechTide Swarm 357

First off — thank you. Every contribution makes the swarm smarter.

Project docs: [README.md](../README.md) (overview, install, components) and [CLAUDE.md](../CLAUDE.md) (architecture, commands, conventions).

## Quick Start for Contributors

Work from the **swarm357 repository root** (in the TechTide monorepo this is `Apps/swarm357/`).

```bash
git clone https://github.com/TechTideAI/swarm-357.git
cd swarm-357   # or your clone directory name
pip install -e "packages/techtide-swarm[dev]"
swarm demo  # Make sure it works
```

There is no editable install at the monorepo root; the Python package lives under `packages/techtide-swarm/`.

## The 5 Easiest Ways to Contribute

### 1. Add a SOUL.md Template (Beginner)

Every agent needs a personality. Add or edit Markdown under `templates/soul/<layer>/` (for example `templates/soul/marketing/your-role.md`). Layer folders match the swarm layers (sales, support, marketing, seo, research, operations, management). See [CLAUDE.md](../CLAUDE.md) for SOUL template conventions and the agent model.

### 2. Add an Evaluation Metric (Intermediate)

Create a new metric in `packages/techtide-swarm/src/techtide_swarm/observability/tracer.py`. Good candidates:

- `tone_consistency` — Does the agent maintain consistent tone across outputs?
- `source_quality` — Are cited sources authoritative?
- `actionability` — Can the reader immediately act on the output?

### 3. Add an MCP Integration (Intermediate)

Connect the swarm to external services via MCP servers in `packages/techtide-swarm/src/techtide_swarm/tools/`.

### 4. Write Example Workflows (Beginner)

Extend or add scenarios in [`.repos and items/workflows.py`](workflows.py) and the [quickstart](quickstart.py) under this folder, or document new patterns in [README.md](../README.md).

### 5. Improve the CLI (Advanced)

The CLI in `packages/techtide-swarm/src/techtide_swarm/cli.py` needs more commands. Top priorities:

- `swarm run <task>` — Full live execution
- `swarm agent <id>` — Deep agent inspection
- `swarm dream` — Live dream cycle with Rich output

## Code Standards

- **Python 3.10+** with type hints everywhere
- **Ruff** for linting (from swarm357 root): `ruff check packages/techtide-swarm/src`
- **MyPy** for type checking: `cd packages/techtide-swarm && mypy src`
- **Pytest** for tests: `python -m pytest packages/techtide-swarm/tests -v`
- Keep functions under 50 lines. If it's longer, split it.

## PR Process

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run linting: `ruff check packages/techtide-swarm/src && (cd packages/techtide-swarm && mypy src)`
5. Run tests: `python -m pytest packages/techtide-swarm/tests -v`
6. Submit a PR with a clear description

CI runs [`.github/workflows/swarm357-ci.yml`](../.github/workflows/swarm357-ci.yml) (Python tests, Next.js build, and Memvid bridge build plus bridge integration tests).

## What NOT to Contribute

- Proprietary API keys or credentials
- Copyrighted content in SOUL.md templates
- Changes that break the 357 agent count (add, don't remove)
- Dependencies that aren't MIT/Apache/BSD licensed

## Recognition

All contributors get credited in the README and our Automation Vibes podcast shoutouts.
