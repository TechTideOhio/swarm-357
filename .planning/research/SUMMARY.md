# Research Summary

## Project

TechTide Swarm 357 -- enterprise-grade layered agent orchestration with durable memory and observability.

## Product arc

**Acquire** (Next.js landing) -> **Orchestrate** (`swarm` CLI / Swarm / UltraPlan) -> **Remember** (Memvid `.mv2` per agent or layer) -> **Observe** (Opik traces + `swarm cost`).

## Differentiators (vs generic agent harnesses)

1. **Domain-layered ontology.** Six business layers (Sales 62, Support 55, Marketing 68, SEO 47, Research 58, Operations 57) + Management (10). Templates and roles, not ad-hoc agents.
2. **Portable durable memory.** Memvid `.mv2` single-file store (WAL, crash-safe, vector + lex search) replaces flat `.swarm/` files. No database server required.
3. **Observability and cost surfaces.** Opik tracing, per-agent budget caps (`AgentConfig.budget_limit_usd`), per-layer cost controller, `swarm cost` CLI.
4. **Security gate.** `BashSecurityGate` with 9+ pattern rules, extensible; blocks secret exfil and destructive commands before execution.
5. **Claude Code native.** `CLAUDE.md` as single source of truth. Repo layout designed for Claude Code sessions.

## Key decisions locked

- Monorepo layout: `packages/techtide-swarm` (Python), `packages/memvid-swarm-bridge` (Rust CLI), `.ui_landin_sample/minimal` (Next.js).
- Bridge technology: subprocess CLI (`memvid-swarm-bridge`) -- not FFI, not sidecar HTTP.
- Packaging: Hatch-based `pyproject.toml`, Apache-2.0.
- CI: GitHub Actions (`swarm357-ci.yml`) with Python, Next.js, and Rust jobs.
- Landing: npm + `package-lock.json` in CI; Bun allowed locally.

## Roadmap phase order

1. Repository truth layer (CLAUDE.md + package + README) -- done.
2. Research pack (`.planning/research/`) -- this directory.
3. Memvid bridge integration slice (MemoryManager -> .mv2, migration) -- done (vertical slice).
4. Enterprise proof (docs, tests, controls narrative) -- in progress.
5. Landing alignment (component content, CI fixes) -- in progress.

## Open questions

- Per-agent vs per-layer `.mv2` files: default to per-layer; allow override in config.
- Agent inventory: codegen/templates vs hand-maintained YAML. Recommend templates + codegen.
- Encryption story: upstream Memvid supports `.mv2e`; not yet wired in bridge.
