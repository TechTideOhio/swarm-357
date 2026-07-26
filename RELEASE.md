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
git tag -a v0.2.2 -m "techtide-swarm 0.2.2"
git push origin v0.2.2
```

5. `publish.yml` runs CI gate → build → attestations → PyPI → GitHub Release.

## Governance (operator checklist)

Apply on `TechTideOhio/swarm-357`:

- Branch protection on `main`: require PR, squash-only, delete head branches
- Required status checks (minimum):
  - `python (3.10)`, `python (3.12)`
  - `roster`, `build-package`, `docs-links`
  - `rust-bridge`, `docker`, `dependency-audit`
- Dependabot enabled (`.github/dependabot.yml`)
- Secret scanning + push protection
- CodeQL workflow (`.github/workflows/codeql.yml`) + CODEOWNERS
- PyPI trusted publisher: repo `TechTideOhio/swarm-357`, workflow `publish.yml`, environment `pypi`
- Repo `homepage`: `https://swarm357fe.up.railway.app`

## Post-release verification

```bash
python -m venv /tmp/swarm-verify && /tmp/swarm-verify/bin/pip install techtide-swarm==0.2.2
/tmp/swarm-verify/bin/swarm boot
curl -sf "$SWARM_API_URL/api/health"
```

## Landing deploy

Deploy from `TechTideOhio/swarm-357-site` (Railway root = repo root).

- Frontend: https://swarm357fe.up.railway.app
- Backend: https://swarm357be.up.railway.app (`NEXT_PUBLIC_API_URL=https://swarm357be.up.railway.app`)
- Site BFF: set server-only `SWARM_API_KEY` (never `NEXT_PUBLIC_SWARM_WRITE_KEY`)
- Backend CORS: `ALLOWED_ORIGINS=https://swarm357fe.up.railway.app`
