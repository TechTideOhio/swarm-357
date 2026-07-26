# Release process

## Prerequisites

- [ ] CI green on `main` (`.github/workflows/ci.yml`)
- [ ] [docs/VERIFY.md](docs/VERIFY.md) acceptance criteria satisfied
- [ ] [STATUS.md](STATUS.md) maturity matrix matches reality
- [ ] Landing site CI green on [swarm-357-site](https://github.com/TechTideOhio/swarm-357-site)
- [ ] CHANGELOG has a dated section for the release

## Cut a release

1. Bump `packages/techtide-swarm/pyproject.toml` version and fallback `__version__`.
2. Update CHANGELOG + README correction notes if needed.
3. Merge to `main` with squash PR; wait for CI.
4. Tag and push:

```bash
git tag -a v0.2.1 -m "techtide-swarm 0.2.1"
git push origin v0.2.1
```

5. `publish.yml` runs CI gate → build → attestations → PyPI → GitHub Release.

## Governance (operator checklist)

Apply on `TechTideOhio/swarm-357`:

- Branch protection on `main`: require PR, require CI status checks, squash merges, delete branch on merge
- Dependabot enabled (`.github/dependabot.yml`)
- Secret scanning + push protection
- Code scanning (CodeQL or equivalent) when available for the org plan
- PyPI trusted publisher: repo `TechTideOhio/swarm-357`, workflow `publish.yml`, environment `pypi`

## Post-release verification

```bash
python -m venv /tmp/swarm-verify && /tmp/swarm-verify/bin/pip install techtide-swarm==0.2.1
/tmp/swarm-verify/bin/swarm boot
curl -sf "$SWARM_API_URL/api/health"
```

## Landing deploy

Deploy from `TechTideOhio/swarm-357-site` (Railway root = repo root). Point `NEXT_PUBLIC_API_URL` at the backend.
