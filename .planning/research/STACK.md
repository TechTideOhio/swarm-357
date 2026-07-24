# Stack Reference

Pinned versions and tool choices for Swarm 357.

## Python (packages/techtide-swarm)

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | >=3.10 | Runtime |
| anthropic | >=0.40 | Claude API client |
| pydantic | >=2.5 | Config validation |
| pyyaml | >=6 | Swarm config files |
| httpx | >=0.27 | HTTP client |
| rich | >=13 | CLI output |
| pytest | >=8 | Testing (dev) |
| pytest-asyncio | >=0.24 | Async test support (dev) |
| ruff | >=0.8 | Linting (dev) |
| mypy | >=1.13 | Type checking (dev) |

Build system: Hatch (`hatchling`).

## Rust (packages/memvid-swarm-bridge)

| Dependency | Version | Purpose |
|------------|---------|---------|
| Rust | >=1.85.0 | Toolchain |
| clap | 4 | CLI argument parsing |
| memvid-core | path dep | `.mv2` file operations |
| serde_json | 1 | JSON serialization |

## Frontend (.ui_landin_sample/minimal)

| Dependency | Version | Purpose |
|------------|---------|---------|
| Next.js | 16.1.1 | App Router framework |
| React | 19.2.3 | UI library |
| Tailwind CSS | v4 | Utility-first CSS |
| motion | 12.23+ | Animation library |
| Lenis | 1.3+ | Smooth scroll |
| @react-three/fiber | 9.5+ | WebGL cursor |
| next-themes | 0.4+ | Dark/light toggle |
| lucide-react | 0.562+ | Icons |

Package manager: npm (CI uses `npm ci`); Bun allowed locally.

## Infrastructure

| Service | Purpose |
|---------|---------|
| GitHub Actions | CI (Python, Next.js, Rust jobs) |
| Opik | Agent trace and eval metrics |
| Anthropic API | Claude models (opus/sonnet/haiku) |

## Environment variables

```
ANTHROPIC_API_KEY    # Required for live agent execution
OPIK_API_KEY         # Optional: trace collection
OPIK_WORKSPACE       # Optional: workspace name for traces
MEMVID_SWARM_BRIDGE  # Optional: path to memvid-swarm-bridge binary
SWARM_MODEL_OPUS     # Override: Opus model ID
SWARM_MODEL_SONNET   # Override: Sonnet model ID
SWARM_MODEL_HAIKU    # Override: Haiku model ID
```
