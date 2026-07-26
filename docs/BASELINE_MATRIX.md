# VERIFY baseline matrix (Phase 0)

Run from the repository root. Last validated with: `ruff`, `mypy` (from `packages/techtide-swarm`), `pytest`, roster scripts, optional Docker smoke.

| Category | Command / check | Expected |
|----------|-------------------|----------|
| Claim integrity | `python scripts/generate_roster.py --fix-counts` | exit 0 |
| Claim integrity | `python scripts/generate_roster.py --compact --fix-counts` | exit 0 |
| Claim integrity | `GET /api/health` → `agents` | `357` (compact config) |
| Runtime | `python -m pytest packages/techtide-swarm/tests -v` | all pass |
| Lint | `python -m ruff check packages/techtide-swarm/src` | clean |
| Types | `cd packages/techtide-swarm && python -m mypy src` | Success |

See [VERIFY.md](VERIFY.md) for the full scorecard and copy-paste commands.
