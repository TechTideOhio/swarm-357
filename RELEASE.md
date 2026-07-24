# Release process

## Version policy

Semantic Versioning (`MAJOR.MINOR.PATCH`) for the `techtide-swarm` PyPI package.

- **MAJOR** — breaking public API or CLI changes
- **MINOR** — new features, backwards-compatible (e.g. 0.1.0 → 0.2.0)
- **PATCH** — bug fixes and docs that ship with the package

The GitHub tag is `v{version}` (example: `v0.2.0`).

## Checklist (before tagging)

1. Update `packages/techtide-swarm/pyproject.toml` version and `CHANGELOG.md`.
2. Regenerate eval docs if baselines changed: `python scripts/render_eval_assets.py`.
3. Local gates:
   ```bash
   cd packages/techtide-swarm
   ruff check src
   mypy src
   python -m pytest tests -v -p no:schemathesis
   python -m build
   twine check dist/*
   ```
4. Fresh venv: `pip install dist/*.whl && swarm boot` (must report 357 agents).
5. Landing: `cd .ui_landin_sample/minimal && npm run typecheck && npm run build`.
6. Sweep for template leftovers: `rg -i "tldr|example\\.com|Add to Chrome|Your Site Name" .ui_landin_sample/minimal`.

## Publish flow

CI workflow [`.github/workflows/publish.yml`](.github/workflows/publish.yml):

1. Push tag `v*` to `TechTideOhio/swarm-357`.
2. Job builds wheel/sdist.
3. Publishes to PyPI via OIDC trusted publishing (`environment: pypi`).
4. Creates a GitHub Release with artifacts attached.

```bash
# From the public repo clone (swarm357-sync), after content is mirrored:
git tag -a v0.2.0 -m "techtide-swarm 0.2.0"
git push origin v0.2.0
```

## Verify after publish

```bash
pip index versions techtide-swarm
pip install techtide-swarm==0.2.0
swarm --help
python -c "from techtide_swarm import __version__; print(__version__)"
curl -s https://pypi.org/pypi/techtide-swarm/json | python -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"
```

Confirm the GitHub Release page lists the wheel and sdist.
