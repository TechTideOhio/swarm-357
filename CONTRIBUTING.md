# Contributing

Thanks for helping improve Swarm 357. This repo is Python-first (`packages/techtide-swarm`) with an optional Rust Memvid bridge. The product landing page lives in a separate repository: [TechTideOhio/swarm-357-site](https://github.com/TechTideOhio/swarm-357-site).

## Setup

```bash
pip install -e "packages/techtide-swarm[dev]"
make test   # or: cd packages/techtide-swarm && pytest -v -p no:schemathesis
```

Optional bridge:

```bash
cd packages/memvid-swarm-bridge && cargo build
export MEMVID_SWARM_BRIDGE="$(pwd)/target/debug/memvid-swarm-bridge"
```

## Rules

- Do not re-add scrubbed local trees (planning research dumps, vendored Memvid checkouts, or the old in-repo landing sample). Landing belongs in swarm-357-site.
- Only workflow YAML (+ Dependabot) are allowed under `.github/`.
- Keep claims in README/STATUS mechanically true; prefer CI gates over prose.
- Conventional Commits for PR titles.

## Docs

- Acceptance criteria: [docs/VERIFY.md](docs/VERIFY.md)
- Maturity: [STATUS.md](STATUS.md)
- Releases: [RELEASE.md](RELEASE.md)
