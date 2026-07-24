# Comparison: Swarm 357 vs Alternatives

## Positioning matrix

| Dimension | Swarm 357 | OpenClaw | Claude Code subagents | CrewAI | LangGraph |
|-----------|-----------|----------|----------------------|--------|-----------|
| **Primary job** | Domain-layered swarm + CLI + durable .mv2 memory + Opik | Multi-agent routing, gateway, per-agent isolation | IDE-native loops, hooks, MCP | Role-based crews with process orchestration | Stateful agent graphs with checkpoints |
| **Agent model** | 6 business layers + management (357 named roles) | Per-agent workspace, sessions, channels | Subagent context isolation | Agents with roles, goals, backstory | Nodes in a graph with state |
| **Memory** | 3-layer (.swarm/) + Memvid .mv2 (portable, searchable) | Agent-scoped sessions | Conversation context | Short/long-term memory abstractions | Checkpointed graph state |
| **Orchestration** | Swarm.execute() pipeline; UltraPlan for deep planning | Orchestration plugins, decentralized discovery | Parallel subagents, tool ecosystem | Sequential, hierarchical, or consensual processes | Directed graphs with conditional edges |
| **Observability** | Opik traces + swarm cost CLI + budget caps | Gateway metrics | IDE terminal output | Built-in logging | LangSmith integration |
| **Security** | BashSecurityGate (9+ rules) | Agent workspace isolation | Sandboxed subprocesses | Tool-level validation | Tool-level validation |
| **Storage format** | Single .mv2 file (WAL, crash-safe, vector+lex) | External DBs | In-memory / file | External vector stores | External stores |
| **Language** | Python + Rust (bridge) | Go / Python | TypeScript | Python | Python |

## Where Swarm 357 wins

1. **Portable memory without infrastructure.** `.mv2` files travel with the agent -- no Redis, no Postgres, no vector DB server.
2. **Business-layer ontology.** Pre-defined roles across Sales, Support, Marketing, SEO, Research, and Operations -- not blank-slate "create your own agents."
3. **Cost surfaces built in.** Per-agent budget limits, per-layer cost controllers, `swarm cost` CLI -- FinOps story from day one.
4. **Claude Code native.** Designed to be loaded via `CLAUDE.md` in a Claude Code session.

## Where Swarm 357 loses (or is not competing)

1. **Not a gateway/mesh.** Does not do request routing, load balancing, or service mesh between agents.
2. **Not multi-model.** Hard dependency on Anthropic Claude (opus/sonnet/haiku). No OpenAI/Gemini adapters.
3. **Not a graph engine.** No conditional branching, cycles, or complex DAG execution.
4. **Not production-hardened.** No SSO, no tenancy, no SLAs. See `ENTERPRISE-GAP.md`.
