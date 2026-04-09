# techtide-swarm

Python package for **Swarm 357**: `Agent`, `Swarm`, `UltraPlan`, `MemoryManager` (flat `.swarm/` or Memvid `.mv2` via `memvid-swarm-bridge`), `BashSecurityGate`, and the `swarm` CLI.

## Install (editable, from repo root)

```bash
cd packages/techtide-swarm
pip install -e ".[dev]"
```

Or from the monorepo root:

```bash
pip install -e "packages/techtide-swarm[dev]"
```

Ensure `anthropic` can reach the API when using live `Agent.run` (set `ANTHROPIC_API_KEY`).

## Memvid bridge

Optional: build `packages/memvid-swarm-bridge` and set `MEMVID_SWARM_BRIDGE` to the binary path, or add it to `PATH`. See [docs/MEMVID_BRIDGE.md](../../docs/MEMVID_BRIDGE.md) (repo root).

## CLI

```bash
swarm init
swarm demo
```

Full developer context: [CLAUDE.md](../../CLAUDE.md) at the swarm357 repo root.
