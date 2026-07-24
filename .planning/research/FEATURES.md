# Features: Table Stakes vs Differentiators

## Table stakes (must-have for any agent harness)

| Feature | Status | Location |
|---------|--------|----------|
| Single-agent execution | Done | `agent.py` -- Agent.run() with stub/live modes |
| Multi-agent orchestration | Minimal | `swarm.py` -- Swarm.execute() runs a pipeline |
| CLI interface | Done | `cli.py` -- init, demo, status, cost, boot, run, dream, plan |
| Configuration via YAML | Partial | `swarm.py` loads config; no schema validation yet |
| Environment-based secrets | Done | `.env` + os.getenv throughout |
| Cost tracking | Demo | CostController in-memory; CLI shows illustrative tables |
| API key gating | Done | Agent.run() stubs when no ANTHROPIC_API_KEY |

## Differentiators (what makes Swarm 357 distinct)

| Feature | Status | Location |
|---------|--------|----------|
| Layered business ontology | Done | LayerType enum; 6 layers + management |
| 357 named agent roles | Designed | CLAUDE.md spec; templates not yet generated |
| Portable .mv2 memory | Working | MemoryManager + MemvidBridge + memvid-swarm-bridge |
| Flat-to-Memvid migration | Done | MemoryManager.migrate_flat_to_memvid() |
| Cross-agent knowledge sharing | Done | MemoryManager.share() + recall() |
| Dream cycle (contradiction detection) | Done | MemoryManager.run_dream_cycle() |
| Bash security gate | Done | BashSecurityGate with 9 pattern rules |
| Per-agent budget caps | Config | AgentConfig.budget_limit_usd (enforcement TBD) |
| Deep planning (UltraPlan) | Done | UltraPlan with stub/live Opus |
| Opik observability hooks | Wired | Agent returns trace_url; full integration pending |
| Claude Code native repo | Done | CLAUDE.md as session bootstrap |

## Gaps (not yet implemented)

| Gap | Priority | Notes |
|-----|----------|-------|
| Agent template codegen | High | Generate 357 SOUL.md files from a manifest |
| Config schema validation | Medium | Validate swarm.yaml against a JSON Schema |
| Real budget enforcement | Medium | CostController should block when over limit |
| Opik trace integration | Medium | Send actual spans/metrics to Opik API |
| Encryption bridge | Low | Wire upstream Memvid .mv2e support |
| Multi-turn agent loops | Medium | Agent.run() is single-turn; add tool-use loops |
| Parallel agent execution | Medium | Swarm.execute() is sequential; add asyncio.gather |
