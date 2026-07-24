# How Swarm 357 compares

This is a concise, honest positioning reference. For the canonical “Why not X?” table, see [README.md](../README.md).

| Dimension | Swarm 357 | Typical notes |
|-----------|-----------|----------------|
| Memory | Portable **Memvid** `.mv2` via Rust bridge + flat-file `.swarm/` | Many frameworks assume a hosted vector DB only. |
| Ontology | **Six business layers** + management meta-agents | Crew-style crews are often ad-hoc YAML without domain structure. |
| Cost | Per-agent budgets, layer limits, downgrade signals | Not all SDKs ship layered accounting out of the box. |
| Security | **BashSecurityGate** for shell tooling | Agent frameworks vary; we centralize bash policy. |
| Scale claim | **357 identities** from roster + soul templates (bounded concurrency) | Not the same as 357 simultaneous Opus sessions—see README. |

**When to pick something else:** You need durable LangGraph-style checkpointing, huge PyPI ecosystem plugins, or managed guardrails from a specific vendor SDK—evaluate those tradeoffs explicitly.
