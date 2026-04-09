# Changelog

All notable changes to `techtide-swarm` are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [0.1.0] - 2026-04-08

Initial open-source release.

### Added

#### Core

- `Agent` / `AgentConfig` / `AgentResult` - single-agent execution with budget enforcement
- `Swarm.from_config(path)` - load and run a full 357-agent roster from YAML
- `CostController` - per-agent budget caps and per-layer daily limits with auto model downgrade at 80%
- `BashSecurityGate` - 13-pattern regex validator blocking destructive commands, secret exfiltration, and dangerous ops (50+ tests)
- `MemoryManager` - three-layer memory: `.swarm/MEMORY.md` pointer index + `.swarm/topics/` knowledge files + `.swarm/transcripts/` raw logs
- `SwarmStore` - optional Supabase persistence for telemetry and snapshots
- `UltraPlan` / `UltraPlanConfig` - deep Opus planning session

#### CLI (`swarm` command)

- `swarm init` - scaffold `.swarm/` project structure + `.env`
- `swarm demo` - 5-agent simulation (works without API key in mock mode)
- `swarm boot` - load 357-agent roster, validate soul files
- `swarm run <task>` - route task through Conductor, print cost/latency
- `swarm status` - layer health dashboard with Rich tables
- `swarm cost` - model usage cost report
- `swarm agent` - list / inspect / run individual agents
- `swarm dream` - memory consolidation cycle
- `swarm plan <task>` - ULTRAPLAN deep planning via Opus
- `swarm eval` - 5-task benchmark with keyword scoring
- `swarm serve` - start FastAPI HTTP API server
- `swarm mcp list / connect` - MCP server management
- `swarm migrate` - migrate `.swarm/topics/` flat files to Memvid `.mv2`

#### Soul Templates (42 files)

- **Management layer** (10): Conductor, Chief Strategist, Cost Controller, Dream Runner, Health Monitor, Memory Curator, Pattern Promoter, QA Auditor, Routing Optimizer, Skill Extractor
- **Sales layer** (6): CRM Operator, Deal Closer, Funnel Analyst, Outreach Specialist, Prospect Researcher, SDR
- **Support layer** (5): CSAT Analyst, Escalation Handler, KB Maintainer, Tier-1 Resolver, Tier-2 Resolver
- **Marketing layer** (6): Ad Copywriter, Brand Guardian, Campaign Analyst, Content Strategist, Email Campaign Manager, Social Media Manager
- **Research layer** (5): Competitor Analyst, Market Analyst, Product Researcher, Research Synthesizer, Trend Watcher
- **SEO layer** (4): AEO Optimizer, Keyword Researcher, Link Building Specialist, Technical SEO Auditor
- **Operations layer** (5): Automation Builder, Data Quality Agent, Finance Reporter, Infra Agent, Project Coordinator

#### Tools

- `WebSearch` (stub - wire in Exa API key for live results)
- `WebScrape` (stub - wire in Firecrawl API key)
- `Read` / `Write` - filesystem operations through `BashSecurityGate`
- `Bash` - terminal commands validated through `BashSecurityGate`
- MCP tool bridge (`StdioMCPClient`, `HttpMCPClient`, `MCPRegistry`)

#### Infrastructure

- FastAPI HTTP server (`techtide_swarm.server`) with CORS, health check, Supabase snapshot on startup
- Dockerfile (multi-stage, non-root user, port 8000)
- Railway deployment config (`railway.toml`)
- GitHub Actions CI: Python lint/type/test + roster validation + Next.js build + Rust bridge
- Memvid bridge Rust CLI (`packages/memvid-swarm-bridge/`) wrapping `memvid-core` v2
- Landing page template (Next.js 16, Tailwind v4, WebGL cursor) in `.ui_landin_sample/minimal/`

#### Eval Harness

- 5-task benchmark in `evals/` with keyword-based scoring
- Layer routing validation across all 6 business layers

[0.1.0]: https://github.com/TechTideOhio/swarm-357/releases/tag/v0.1.0
