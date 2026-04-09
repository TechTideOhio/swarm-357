# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

TechTide Swarm 357 is a 357-agent Claude AI system organized into 6 business layers (Sales 62, Support 55, Marketing 68, SEO 47, Research 58, Operations 57) plus a Management layer (10 meta-agents). This workspace contains:

- **`.repos and items/`** — Reference materials: CLI shim (`cli.py` → imports installed package), quickstart demo (`quickstart.py`), example workflows (`workflows.py`), design spec PDF, and the **Memvid** Rust library (`.repos and items/memvid-main/memvid-main/`)
- **`packages/techtide-swarm/`** — Installable Python package (`pyproject.toml`): `pip install -e "packages/techtide-swarm[dev]"` from this repo root provides `techtide_swarm` and the `swarm` CLI entry point
- **`packages/memvid-swarm-bridge/`** — Rust CLI that wraps `memvid-core` for `MemoryManager` (`create` / `put` / `search` / `verify`)
- **`.ui_landin_sample/minimal/`** — Production-ready Next.js 16 landing page template for the Swarm 357 product

## Landing Page (`.ui_landin_sample/minimal/`)

### Commands
```bash
cd .ui_landin_sample/minimal

npm run dev          # Start dev server (http://localhost:3000)
npm run build        # Production build
npm run lint         # ESLint
npm run lint:fix     # Auto-fix lint errors
npm run format       # Prettier format
npm run typecheck    # TypeScript check (tsc --noEmit)
```

### Architecture
- **Next.js 16 App Router** + TypeScript strict + Tailwind CSS v4
- **Single config file**: `lib/config.ts` — all text content, nav links, feature flags live here
- **Components**: standalone sections (`hero.tsx`, `features.tsx`, `stats.tsx`, `testimonials.tsx`, `pricing.tsx`, `faq.tsx`, `final-cta.tsx`, `footer.tsx`) — each independently modifiable
- **WebGL cursor**: `components/dither-cursor.tsx` via React Three Fiber (`@react-three/fiber`) — GPU-accelerated, disabled on mobile
- **Smooth scroll**: Lenis via `components/smooth-scroll.tsx`
- **Animations**: `motion/react` with reduced-motion support, utilities in `lib/motion.tsx`
- **Theme**: CSS variables in `app/globals.css` (`--accent`, `--background`, `--foreground`), toggled via `next-themes`
- **SEO**: `lib/metadata.ts` generates Open Graph / Twitter card metadata

### Feature Flags
Toggle in `lib/config.ts`:
```ts
export const features = {
  smoothScroll: true,
  darkMode: true,
  ditherCursor: true,
  statsSection: true,
}
```

## Python Swarm Package (`packages/techtide-swarm/`)

Installable package: `pip install -e "packages/techtide-swarm[dev]"`. Source: `packages/techtide-swarm/src/techtide_swarm/`.

### Key Classes (from examples/docs)
| Class | Purpose |
|-------|---------|
| `Agent(AgentConfig)` | Single agent — `await agent.run(task)` |
| `Swarm.from_config(path)` | Full 357-agent swarm — `await swarm.execute(task)` |
| `UltraPlan(UltraPlanConfig)` | Deep Opus planning session |
| `MemoryManager` | Cross-agent knowledge sharing + dream cycles |
| `BashSecurityGate` | 13-pattern bash command validation |

### AgentConfig fields
```python
AgentConfig(
    name="research-market-001",
    layer=LayerType.RESEARCH,   # SALES, SUPPORT, MARKETING, SEO, RESEARCH, OPERATIONS
    role="market_researcher",
    soul="templates/soul/research/trends.md",  # Personality file
    tools=["WebSearch", "Read", "Write"],
    model="sonnet",             # or "opus" / "haiku"
    budget_limit_usd=1.00,
)
```

### CLI (`swarm` command)
```bash
swarm init           # Create project structure + .env + .swarm/MEMORY.md
swarm demo           # 5-agent simulation (or live with ANTHROPIC_API_KEY)
swarm status         # Layer health dashboard
swarm cost           # Model usage cost report
swarm boot           # Boot all 357 agents
swarm run <task>     # Execute task across swarm
swarm dream          # Memory consolidation cycle
swarm plan <task>    # ULTRAPLAN: deep Opus planning
```

### Memory System (3 layers)
1. `.swarm/MEMORY.md` — Pointer index, always in context (max 200 lines × 150 chars)
2. `.swarm/topics/` — Actual knowledge files, fetched on demand
3. `.swarm/transcripts/` — Append-only raw logs, never loaded into context

The `autoDream` background cycle detects contradictions, prunes stale data, and verifies facts.

### Observability
- Agent calls logged to local `.swarm/telemetry.jsonl` (external Opik integration planned)
- Metrics: cost per model, latency, eval scores per agent

### Required env vars
```
ANTHROPIC_API_KEY=sk-ant-...
```

Optional:
```
MEMVID_SWARM_BRIDGE=/path/to/binary
```

### Model IDs (Claude 4.x)

| Short name | Env override | Default model ID |
| ---------- | ------------ | ---------------- |
| `opus` | `SWARM_MODEL_OPUS` | `claude-opus-4-6` |
| `sonnet` | `SWARM_MODEL_SONNET` | `claude-sonnet-4-6` |
| `haiku` | `SWARM_MODEL_HAIKU` | `claude-haiku-4-5-20251001` |

### SOUL.md Templates

Layer personality templates live in `templates/soul/<layer>/`. Each has YAML front-matter (`name`, `layer`, `role`, `model`, `budget_limit_usd`, `skills`, `memory`, `tools`) + a system prompt.

```
templates/soul/
├── sales/
│   ├── crm-operator.md          # Haiku — Composio/HubSpot/Salesforce CRM ops
│   └── outreach-specialist.md   # Sonnet — prospect research + email sequences
├── support/
│   └── tier1-resolver.md        # Haiku — Zendesk/Freshdesk, Courier notifications
├── marketing/
│   └── content-strategist.md    # Sonnet — content, SEO/AEO, brand, Mailchimp
├── seo/
│   └── keyword-researcher.md    # Haiku — Firecrawl, SERP, AEO optimization
├── research/
│   └── market-analyst.md        # Sonnet — Firecrawl, citations, xlsx/pdf output
├── operations/
│   └── project-coordinator.md   # Sonnet — Linear/Notion/Jira, Stripe, Supabase
└── management/
    └── conductor.md             # Opus — orchestrator + self-improvement loop
```

### Skills Ecosystem

Full catalog: `.planning/research/SKILLS-CATALOG.md`. Priority install order:

```bash
# Phase 1 — universal starters (every agent)
npx antigravity-awesome-skills --claude      # @brainstorming, @tdd, @security-auditor, etc.
/plugin install connect-apps-plugin          # Composio 500+ SaaS apps
/plugin marketplace add anthropics/skills    # docx, pptx, xlsx, pdf, brand-guidelines

# Phase 2 — layer specialization
/plugin marketplace add alirezarezvani/claude-skills   # 248 skills: Marketing pod, C-suite, self-improving

# Phase 3 — memory + research
/plugin install claude-mem                   # SQLite+Chroma session memory (complements Memvid)
npm install -g repomix                       # Codebase context packaging

# Phase 4 — infrastructure (verify before adopting)
npx ruflo@latest init --wizard               # 310 meta-agent tools, swarm routing
```

### Memory Architecture (two complementary layers)

| System | Role | Technology |
| ------ | ---- | ---------- |
| **Claude-Mem** | Working memory — auto-captures during sessions | SQLite + Chroma, 5 lifecycle hooks |
| **Memvid `.mv2`** | Long-term memory — consolidated after dream cycles | Rust, HNSW + Tantivy |

3-layer progressive retrieval (10x token savings): broad `search()` → `timeline()` for candidates → `get_observations()` for selected IDs only.

### Code standards

- Python 3.10+ with type hints everywhere
- `ruff check src/` for linting
- `mypy src/` for type checking
- `pytest tests/ -v` for tests
- Functions under 50 lines

## Memvid — Rust Memory Library (`.repos and items/memvid-main/memvid-main/`)

**Memvid** (`memvid-core` v2 on crates.io) is the intended persistent memory backend for Swarm 357 agents. It packs documents, vector embeddings, full-text search, and temporal metadata into a single portable `.mv2` file — no database server required.

### Build & Test Commands

```bash
cd ".repos and items/memvid-main/memvid-main"

cargo build
cargo build --release
cargo test
cargo test --test lifecycle      # Specific integration test
cargo test -- --nocapture        # Show println output
cargo clippy
cargo fmt
cargo bench

cargo run --example basic_usage
cargo run --example pdf_ingestion
cargo run --example text_embedding   # requires --features vec
cargo run --example openai_embedding # requires --features api_embed
```

### File Format (.mv2)

Each `.mv2` is a self-contained memory store:

```
Header (4KB) → WAL (1-64MB) → Data Segments → Lex Index (Tantivy) → Vec Index (HNSW) → Time Index → TOC Footer
```

### Key API

```rust
let mut mem = Memvid::create("agent-memory.mv2")?;
let mut mem = Memvid::open("agent-memory.mv2")?;

mem.put_bytes(content)?;                        // Ingest document
mem.put_bytes_with_options(content, options)?;   // With metadata
mem.commit()?;                                   // Flush WAL → immutable frames

mem.search(SearchRequest { query, top_k, .. })?; // Vector + lex hybrid search
mem.timeline(TimelineQuery::default())?;          // Chronological replay
Memvid::verify("file.mv2", deep)?;               // Integrity check
```

### Feature Flags (`Cargo.toml`)

| Feature | Default | Purpose |
| ------- | ------- | ------- |
| `lex` | ✅ | Full-text search via Tantivy |
| `pdf_extract` | ✅ | Pure-Rust PDF extraction |
| `simd` | ✅ | SIMD-accelerated vector distances |
| `vec` | opt-in | HNSW vector similarity search |
| `clip` | opt-in | CLIP image embeddings |
| `whisper` | opt-in | Audio transcription (Candle) |
| `encryption` | opt-in | AES-256-GCM encrypted `.mv2e` files |
| `api_embed` | opt-in | OpenAI / API-based embeddings |
| `logic_mesh` | opt-in | NER entity-relationship graph |
| `temporal_enrich` | opt-in | Natural-language date parsing |
| `replay` | opt-in | Time-travel agent session replay |

### Architecture (`src/`)

| Path | Purpose |
| ---- | ------- |
| `memvid/` | Core `Memvid` struct — mutation, search, ask (RAG) |
| `io/` | File I/O — header, WAL, time index |
| `lex.rs` | Tantivy full-text search |
| `vec.rs` | HNSW vector search |
| `text_embed.rs` | Local embedding via ONNX |
| `api_embed.rs` | OpenAI / remote embedding |
| `clip.rs` | CLIP image embeddings |
| `whisper.rs` | Whisper audio transcription |
| `encryption/` | AES-256-GCM capsule encryption |
| `reader/` | Document ingestion — PDF, DOCX, XLSX, PPTX |
| `analysis/` | Auto-tagging, NER, temporal enrichment |
| `triplet/` | Subject-predicate-object extraction |
| `replay/` | Session replay engine |
| `types/` | All shared type definitions |

### Design Rules

- **Single-file only** — never create sidecar files
- **Crash-safe** — all writes go through WAL before commit
- **Append-only frames** — immutable once committed
- **Synchronous** — no async; library is sync for simplicity
- Errors via `thiserror`, logging via `tracing`
- `clippy::all + clippy::pedantic` enforced; `unwrap`/`expect` banned outside tests

### Swarm 357 Integration Intent

Replace the current flat-file `.swarm/MEMORY.md + topics/` system with a per-agent or per-layer `.mv2` file. Each agent gets persistent, searchable, versioned memory that travels with it. The `MemoryManager` Python class in the swarm package is the intended bridge layer.
