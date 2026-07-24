# Swarm 357 — Skills Ecosystem Catalog

**Researched:** 2026-04-04
**Domain:** Claude Code skills, MCP servers, hooks, and agent patterns
**Confidence:** MEDIUM-HIGH (GitHub READMEs verified; plugin marketplace claims not independently tested)

---

## Source Map

| # | Label | Resolved URL |
|---|-------|-------------|
| 1 | SUPABASE | https://github.com/supabase/cli |
| 2 | NOTEBOOKLM | https://github.com/teng-lin/notebooklm-py |
| 3 | OBSIDIAN | https://github.com/obsidianmd (org page) |
| 4 | LANGCHAIN | https://github.com/langchain-ai/langchain |
| 5 | FLOWISE | https://github.com/FlowiseAI/Flowise |
| 6 | CLAUDE SKILLS | https://github.com/alirezarezvani/claude-skills |
| 7 | AWESOME CLAUDE SKILLS | https://github.com/ComposioHQ/awesome-claude-skills |
| 8 | REPOMIX | https://github.com/yamadashy/repomix |
| 9 | CLAUDE CODE BEST PRACTICE | https://github.com/shanraisshan/claude-code-best-practice |
| 10 | EVERYTHING CLAUDE CODE | https://github.com/affaan-m/everything-claude-code |
| 11 | CLAUDE-MEM | https://github.com/thedotmack/claude-mem |
| 12 | ANTHROPIC SKILLS | https://github.com/anthropics/skills |
| 13 | AWESOME AGENT SKILLS | https://github.com/VoltAgent/awesome-agent-skills |
| 14 | ANTIGRAVITY AWESOME SKILLS | https://github.com/sickn33/antigravity-awesome-skills |
| 15 | CLAUDE CODE SUBAGENTS | https://github.com/VoltAgent/awesome-claude-code-subagents |
| 16 | RUFLO | https://github.com/ruvnet/ruflo |
| 17 | CC-SWITCH | https://github.com/farion1231/cc-switch |

---

## Skills Ready to Install

These are skills with direct `.md` files (or installable plugin packages) that can be copied into
`.claude/skills/` and immediately referenced in agent SOUL.md files.

### Tier 1 — Anthropic Official (highest trust)

Source: `anthropics/skills` (repo #12) and `VoltAgent/awesome-agent-skills` (repo #13)

Install via plugin marketplace:
```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

Or copy individual skills from `https://officialskills.sh/<publisher>/skills/<skill-name>`.

| Skill ID | Publisher | What It Does | Swarm 357 Layer |
|----------|-----------|-------------|-----------------|
| `anthropics/docx` | Anthropic | Create, edit, analyze Word documents | Operations, Management |
| `anthropics/pptx` | Anthropic | Create, edit PowerPoint decks | Marketing, Management |
| `anthropics/xlsx` | Anthropic | Create, edit Excel spreadsheets | Operations, Research |
| `anthropics/pdf` | Anthropic | Extract text, create PDFs, handle forms | All layers |
| `anthropics/internal-comms` | Anthropic | Write status reports and company newsletters | Management, Operations |
| `anthropics/mcp-builder` | Anthropic | Guide to creating new MCP servers | Operations (meta) |
| `anthropics/webapp-testing` | Anthropic | Test web apps via Playwright | Operations |
| `anthropics/skill-creator` | Anthropic | Meta-skill: guidance for creating new skills | Management |
| `anthropics/brand-guidelines` | Anthropic | Apply brand standards to artifacts | Marketing |
| `anthropics/frontend-design` | Anthropic | Frontend design and UI/UX tooling | Marketing |

### Tier 2 — Composio Connect-Apps (broad SaaS automation)

Source: `ComposioHQ/awesome-claude-skills` (repo #7)

Install:
```
/plugin install connect-apps-plugin
/connect-apps:setup
```

The `composiohq/composio` skill connects to 500+ applications. Key sub-skills for Swarm 357:

| Skill ID | What It Does | Swarm 357 Layer |
|----------|-------------|-----------------|
| `hubspot-automation` | Contacts, deals, companies, tickets, email engagement | Sales |
| `salesforce-automation` | Objects, records, SOQL queries, bulk ops | Sales |
| `pipedrive-automation` | Deals, contacts, orgs, activities, pipelines | Sales |
| `close-automation` | Leads, contacts, opportunities, activities | Sales |
| `lead-research-assistant` | Identifies + qualifies prospects, outreach strategy | Sales, Research |
| `competitive-ads-extractor` | Extracts/analyzes competitor ads from ad libraries | Marketing, Research |
| `zendesk-automation` | Tickets, users, orgs, search, macros | Support |
| `freshdesk-automation` | Tickets, contacts, agents, groups, canned responses | Support |
| `helpdesk-automation` | Help Scout conversations, customers, mailboxes | Support |
| `slack-automation` | Messages, channels, search, reactions, scheduling | All layers |
| `gmail-automation` | Send/reply, search, labels, drafts, attachments | Sales, Support |
| `mailchimp-automation` | Audiences, campaigns, templates, segments, reports | Marketing |
| `google-analytics-automation` | Reports, dimensions, metrics, property management | SEO, Marketing |
| `notion-automation` | Pages, databases, blocks, comments, search | Operations |
| `linear-automation` | Issues, projects, cycles, teams, workflows | Operations |
| `jira-automation` | Issues, projects, boards, sprints, JQL | Operations |
| `content-research-writer` | Research, citations, hooks, content feedback | Marketing, Research |
| `meeting-insights-analyzer` | Transcript analysis: speaking ratios, patterns | Management |
| `domain-name-brainstormer` | Domain ideas + availability checks | Marketing |
| `twitter-algorithm-optimizer` | Tweet optimization via algorithm insights | Marketing |
| `lead-research-assistant` | Prospect qualification + outreach strategies | Sales |

### Tier 3 — alirezarezvani/claude-skills (248 production skills)

Source: repo #6

Install:
```
/plugin marketplace add alirezarezvani/claude-skills
/plugin install engineering-skills@claude-code-skills
```

Most relevant to Swarm 357 business layers:

**Marketing Pod (45 skills across 7 sub-pods):**
- Content Pod (8): content creation + strategy
- SEO Pod (5): search optimization
- CRO Pod (6): conversion rate optimization
- Channels Pod (6): multi-channel marketing
- Growth Pod (4): growth strategy
- Intelligence Pod (4): market + competitive analysis
- Sales Pod (2): sales enablement

**C-Level Advisory (34 skills):**
- Full C-suite: CEO, CTO, CFO, CMO + 6 other roles
- Board meeting preparation
- Culture + collaboration frameworks
- Orchestration routing across executive perspectives

**Product (15 skills):**
- PM toolkit, UX researcher, SaaS scaffolder
- Roadmap communicator, analytics expert
- Code-to-PRD converter

**Self-Improving Agent (7 skills):**
- `auto-memory-curation`: curates memory entries without manual intervention
- `pattern-promotion`: elevates frequently-used patterns to formal skills
- `skill-extraction`: extracts new skills from session behavior
- `memory-health`: monitors memory store quality
- These 7 skills enable agents to improve themselves autonomously

**Regulatory & QM (14 skills):**
- ISO 13485, MDR 2017/745, FDA, GDPR compliance
- CAPA processes
- Useful for enterprise sales (compliance narrative layer)

### Tier 4 — Platform + Integration Skills (from VoltAgent awesome list)

Source: repo #13 (`VoltAgent/awesome-agent-skills`)

| Skill | Publisher | Layer Fit |
|-------|-----------|-----------|
| `stripe/stripe-best-practices` | Stripe | Operations |
| `stripe/upgrade-stripe` | Stripe | Operations |
| `supabase/postgres-best-practices` | Supabase | Operations |
| `firecrawl/firecrawl-scrape` | Firecrawl | Research, SEO |
| `firecrawl/firecrawl-crawl` | Firecrawl | Research, SEO |
| `firecrawl/firecrawl-search` | Firecrawl | Research, SEO |
| `trycourier/courier-skills` | Courier | Support, Marketing |
| `typefully/typefully` | Typefully | Marketing |
| `sanity-io/seo-aeo-best-practices` | Sanity | SEO |
| `sanity-io/content-modeling-best-practices` | Sanity | Marketing |
| `cloudflare/agents-sdk` | Cloudflare | Operations (infra) |
| `vercel-labs/next-best-practices` | Vercel | Operations |
| `sentry/*` | Sentry | Operations |
| `google-gemini/gemini-api-dev` | Google | Research |

### Tier 5 — Antigravity Universal Starter Skills

Source: repo #14 (`sickn33/antigravity-awesome-skills`)

These 8 skills are recommended as baseline context for every agent:

```
@brainstorming              — planning before implementation
@test-driven-development    — TDD-oriented work
@debugging-strategies       — systematic troubleshooting
@lint-and-validate          — lightweight quality checks
@security-auditor           — security-focused reviews
@frontend-design            — UI and interaction quality
@api-design-principles      — API shape and consistency
@create-pr                  — packaging work into pull requests
```

Install via: `npx antigravity-awesome-skills --claude`
Full catalog browsable at: https://sickn33.github.io/antigravity-awesome-skills/

### Tier 6 — NotebookLM Research Skill

Source: repo #2 (`teng-lin/notebooklm-py`)

Install:
```
npx skills add teng-lin/notebooklm-py
# or
notebooklm skill install
```

Capabilities for Research and Marketing layers:
- Create/manage notebooks programmatically
- Generate podcasts, videos, quizzes, flashcards, slide decks, infographics, mind maps
- Bulk-import sources + execute web/Drive research with auto-import
- Batch download artifacts (MP3, MP4, PDF, JSON, CSV)
- Exports quiz/flashcard JSON and mind map data unavailable in web UI

**Caveat:** Unofficial Google API — subject to breaking changes. LOW confidence on stability.

---

## MCP Servers to Configure

These MCP servers provide tool integrations that all 357 agents can access through the
tool-use permission layer.

### High Priority

**1. Composio MCP (500+ app integrations)**
- Source: `ComposioHQ/awesome-claude-skills` connect-apps plugin
- Provides: HubSpot, Salesforce, Zendesk, Slack, Gmail, Notion, Linear, Jira, Google Analytics, Mailchimp and 490+ more
- Install: Plugin system handles MCP registration automatically
- Agent value: Eliminates hand-rolled API clients for every SaaS tool
- Confidence: MEDIUM (plugin-based, not raw MCP config)

**2. Ruflo MCP (310+ meta-agent tools)**
- Source: repo #16 (`ruvnet/ruflo`)
- Provides: Multi-agent swarm orchestration, 100+ specialist agents, 27-hook routing system
- Install: `curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/ruflo@main/scripts/install.sh | bash`
- MCP config: Auto-registers on install; Claude Code discovers it
- Agent value: Intelligent task routing, swarm coordination, self-learning pipeline
- Relevant tools: 310 MCP tools for agent management, routing, coordination
- Confidence: MEDIUM (complex system, verify against current docs before adopting)

**3. Firecrawl MCP (web scraping)**
- Source: `VoltAgent/awesome-agent-skills` (firecrawl skills)
- Provides: `firecrawl-scrape`, `firecrawl-crawl`, `firecrawl-search`, `firecrawl-map`, browser automation
- Agent value: Research and SEO layers need production web scraping
- Confidence: HIGH (official Firecrawl skills, well documented)

**4. Supabase MCP**
- Source: repo #1 (`supabase/cli`) — the CLI itself, not a dedicated skill
- Reality check: The supabase/cli repo has NO Claude Code skill or MCP server built in.
  The skill that exists is `supabase/postgres-best-practices` (a guidelines skill, not an MCP server).
  For actual Supabase MCP: use the separately published `@supabase/mcp-server-supabase`.
- Agent value: Operations layer for database management
- Install: `npm install @supabase/mcp-server-supabase` (verify current package name)
- Confidence: MEDIUM (supabase publishes MCP server separately from CLI)

**5. Claude-Mem MCP (cross-session memory)**
- Source: repo #11 (`thedotmack/claude-mem`)
- Provides: SQLite + Chroma vector search memory system with 5 lifecycle hooks
- Install: `/plugin marketplace add thedotmack/claude-mem && /plugin install claude-mem`
- MCP tools exposed: `search` (compact index), `timeline` (chronological context), `get_observations` (full details)
- Architecture: Hybrid keyword + semantic search, 10x token savings via 3-layer retrieval
- Agent value: Persistent cross-session memory that complements Memvid .mv2
- Confidence: MEDIUM

### Medium Priority

**6. NotebookLM Python MCP**
- Source: repo #2 (`teng-lin/notebooklm-py`)
- Agent value: Research layer's content generation (podcasts, slides, mind maps)
- Caveat: Unofficial API — evaluate stability before production use

**7. Repomix MCP**
- Source: repo #8 (`yamadashy/repomix`)
- Provides: Pack entire repositories into single AI-friendly files
- Install: `npm install -g repomix` then `repomix --mcp` (check current docs for MCP mode)
- Has `.claude/` and `.agents/` directories suggesting Claude ecosystem integration
- Agent value: Research and Operations agents that need full codebase context
- Confidence: MEDIUM

---

## Hook Patterns to Adopt

### Pattern 1: Lifecycle Memory Hooks (from claude-mem, everything-claude-code)

The canonical 5-hook memory lifecycle:

```
SessionStart       → Load prior context, inject relevant memories
UserPromptSubmit   → Capture user intent before Claude processes
PostToolUse        → Record observations after every tool execution (primary data collection)
Stop               → Handle session pause (persist partial state)
SessionEnd / Stop  → Finalize session: compress learnings, update memory store
```

Implementation approach for Swarm 357:
- Each agent's `stop_sequence` or session-end event should trigger `MemoryManager.share()`
- PostToolUse hook: record tool result + agent reasoning for pattern extraction
- SessionStart hook: load Memvid `.mv2` search results for relevant prior context

Environment-driven gating (from everything-claude-code):
```
ECC_HOOK_PROFILE=minimal|standard|strict
ECC_DISABLED_HOOKS=hook1,hook2
```
This prevents hook overhead during development without editing config files.

### Pattern 2: Intelligence Learning Cycle (from Ruflo)

Ruflo's RETRIEVE → JUDGE → DISTILL → CONSOLIDATE → ROUTE cycle maps cleanly
to Swarm 357's dream cycle concept:

```
RETRIEVE    → Search Memvid .mv2 for prior patterns matching task
JUDGE       → Evaluate pattern relevance and confidence score
DISTILL     → Extract reusable insight from current session
CONSOLIDATE → Write distilled insight back to Memvid .mv2
ROUTE       → Update routing weights based on success/failure
```

This is the self-improving loop. Ruflo implements it with Q-Learning + MoE routing.
For Swarm 357, a simplified version in Python using confidence scoring is sufficient.

### Pattern 3: 3-Layer Progressive Retrieval (from claude-mem)

Avoid dumping full memory context. Use staged retrieval:

```
Layer 1: search() → compact index with IDs (~50-100 tokens/result)
Layer 2: timeline() → chronological context around candidates (~200 tokens)
Layer 3: get_observations() → full details only for selected IDs (~500-1000 tokens)
```

This achieves ~10x token savings. Apply to Memvid `.mv2` search:
- First call: broad search, get URIs
- Second call: fetch only the 2-3 most relevant entries

### Pattern 4: PreToolUse Security Gate (from everything-claude-code)

The `BashSecurityGate` in Swarm 357 already implements this pattern.
The broader pattern from everything-claude-code (AgentShield integration):

```python
# PreToolUse hook pattern
def pre_tool_use(tool_name, tool_input):
    if tool_name == "Bash":
        result = security_gate.validate(tool_input["command"])
        if not result.safe:
            return {"block": True, "reason": result.violation}
    return {"allow": True}
```

Reference: `@security-auditor` skill (antigravity) + AgentShield integration (everything-claude-code).

### Pattern 5: Content-Hash Caching (from everything-claude-code)

For Research and SEO agents that process web pages repeatedly:

```python
import hashlib

def should_process(url: str, content: str, cache: dict) -> bool:
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    if cache.get(url) == content_hash:
        return False  # Skip re-processing
    cache[url] = content_hash
    return True
```

Store hashes in Memvid `.mv2` metadata. Prevents redundant LLM calls on unchanged pages.

### Pattern 6: Stop-Phase Session Summary

From everything-claude-code and claude-mem Stop hooks:

```python
# Stop hook: compress session into summary before context is lost
async def on_session_stop(agent, session):
    summary = await agent.run(
        f"Summarize the 3 most important things learned in this session "
        f"as bullet points for future reference."
    )
    agent.memory.share(summary, uri=f"session/{session.id}", title="Session Summary")
```

This is the Swarm 357 equivalent of the "dream cycle" — lightweight consolidation
at the end of every agent session rather than a separate nightly process.

### Pattern 7: Skill Evolution via Confidence Gates

From alirezarezvani/claude-skills self-improving agent:

```
Pattern extracted from session
    → confidence < 0.6: store as observation only
    → confidence 0.6-0.8: promote to candidate skill
    → confidence > 0.8: promote to active skill
    → used 3+ times: promote to memory-health monitored skill
```

Implement in `MemoryManager` as a `promote_to_skill()` method that writes
a new SOUL.md snippet when confidence threshold is crossed.

---

## Architecture Patterns

### Pattern A: Command → Agent → Skill (from shanraisshan/claude-code-best-practice)

The canonical three-tier architecture:

```
Command         = knowledge injected into existing context (user-invoked prompt templates)
Agent           = autonomous actor in isolated fresh context (custom tools, permissions, model)
Skill           = configurable, preloadable, auto-discoverable knowledge module
```

**Application to Swarm 357:**
- Each of the 357 agents maps to the Agent tier
- SOUL.md files ARE the Skill tier (per-role knowledge modules)
- The `swarm` CLI commands map to the Command tier

### Pattern B: Layer-Based Orchestration Topology

From Ruflo's swarm architecture and VoltAgent subagents:

```
Management Layer (10 meta-agents)
    ↓ routes tasks to
Specialist Layers (Sales 62 / Support 55 / Marketing 68 / SEO 47 / Research 58 / Operations 57)
    ↓ delegate atomic tasks to
Tool-Use (WebSearch, Read, Write, Bash via security gate)
```

Ruflo's topologies map directly:
- **Hierarchical** (queen/workers) = Management layer orchestrating specialist layers
- **Mesh** (peer-to-peer) = agents within the same layer collaborating
- **Star** (hub and spoke) = single orchestrator dispatching to specialists

For Swarm 357: use Hierarchical for cross-layer orchestration, Mesh for same-layer
collaboration on complex tasks (e.g., 3 Research agents on same question).

### Pattern C: Iterative Context Retrieval (from everything-claude-code)

The "context problem" for large agent swarms: don't dump full state to subagents.
Use staged information extraction:

```
Step 1: Give subagent compact task brief (< 500 tokens)
Step 2: Subagent requests specific context via tool calls
Step 3: Orchestrator answers only what was asked
Step 4: Subagent completes task, returns structured result
```

This maps to Memvid's search-first pattern: agents query `.mv2` for what they need,
not load the entire memory store.

### Pattern D: SOUL.md Skill-Referenced Agent Identity

From the Command → Agent → Skill pattern, a SOUL.md file should reference installed skills:

```markdown
---
name: marketing-content-001
layer: marketing
role: content_strategist
skills:
  - composiohq/composio          # SaaS integrations
  - content-research-writer       # Research + citations
  - twitter-algorithm-optimizer   # Social distribution
  - @brainstorming               # Universal starter
  - @create-pr                   # Output packaging
memory: .swarm/marketing.mv2
model: sonnet
budget_limit_usd: 2.00
---

You are a content strategist focused on [domain].
...
```

The `skills:` field in SOUL.md tells the agent which knowledge modules to load.

### Pattern E: Multi-Agent Git Worktrees (from claude-code-best-practice)

For parallel agent work on the same codebase:

```bash
git worktree add .worktrees/agent-sales main
git worktree add .worktrees/agent-marketing main
```

Each agent gets isolated branch. Results merged by Management layer orchestrator.
Enables true parallel execution without merge conflicts during research phases.

### Pattern F: Autonomous Loop with PM2 (from everything-claude-code)

For long-running agent processes:

```bash
# Start multiple agents as PM2 processes
pm2 start "python -m techtide_swarm.agent --config agents/sales-001.yaml" --name sales-001
pm2 start "python -m techtide_swarm.agent --config agents/research-001.yaml" --name research-001

# Monitor
pm2 status
pm2 logs sales-001
```

The `/multi-plan`, `/multi-execute` commands from everything-claude-code provide
orchestration templates for coordinating PM2-managed agent fleets.

### Pattern G: Cross-Harness Hook Abstraction (from everything-claude-code)

Write hooks once, run across Claude Code, Cursor, OpenCode, Codex:

```python
# hooks/post_tool_use.py — harness-agnostic
import os

def handle_post_tool_use(tool_name, tool_result):
    """Works in any agent harness that supports PostToolUse hooks."""
    if tool_name in ("WebSearch", "Read"):
        log_observation(tool_name, tool_result)
```

This is valuable if Swarm 357 agents ever need to run in non-Claude-Code environments.

---

## Per-Layer Recommendations

### Sales (62 agents)

**Priority skills:**
1. `hubspot-automation` / `salesforce-automation` / `pipedrive-automation` / `close-automation` — CRM operations
2. `lead-research-assistant` — prospect qualification
3. `competitive-ads-extractor` — competitor intelligence
4. `gmail-automation` — outreach automation
5. `slack-automation` — team communication
6. alirezarezvani Marketing/Sales Pod (2 skills): sales enablement + strategy
7. alirezarezvani C-Level Advisory: CEO/CRO perspective for strategic deals

**SOUL.md skill references:** composio (CRM), lead-research-assistant, gmail-automation
**Hook pattern:** PostToolUse to log every prospect interaction to Memvid
**Model guidance:** Haiku for routine CRM ops, Sonnet for complex deal strategy

### Support (55 agents)

**Priority skills:**
1. `zendesk-automation` / `freshdesk-automation` / `helpdesk-automation` — ticket management
2. `trycourier/courier-skills` — multi-channel notifications (email, SMS, push, chat)
3. `slack-automation` — agent-customer async communication
4. `gmail-automation` — email support threads
5. `anthropics/internal-comms` — escalation writeups, status reports

**SOUL.md skill references:** zendesk-automation (or freshdesk), courier-skills, slack-automation
**Hook pattern:** SessionStart to load recent customer context from Memvid
**Model guidance:** Haiku for ticket triage, Sonnet for complex resolution paths

### Marketing (68 agents)

**Priority skills:**
1. alirezarezvani Marketing Pod full suite (45 skills: Content, SEO, CRO, Channels, Growth, Intelligence, Sales)
2. `competitive-ads-extractor` — competitor ad intelligence
3. `mailchimp-automation` — campaign management
4. `twitter-algorithm-optimizer` — social media optimization
5. `typefully/typefully` — cross-platform social scheduling
6. `content-research-writer` — research-backed content
7. `domain-name-brainstormer` — brand and campaign naming
8. `anthropics/brand-guidelines` — brand consistency
9. `anthropics/pptx` — pitch decks, client presentations
10. `sanity-io/seo-aeo-best-practices` — content optimization patterns

**SOUL.md skill references:** composio (Mailchimp), content-research-writer, twitter-algorithm-optimizer, brand-guidelines
**Hook pattern:** Content-hash caching (Pattern 5) to avoid re-analyzing unchanged competitor pages
**Model guidance:** Haiku for content drafts/variations, Sonnet for strategy and campaign planning

### SEO (47 agents)

**Priority skills:**
1. `firecrawl/firecrawl-scrape` + `firecrawl-crawl` + `firecrawl-search` — web data extraction
2. `sanity-io/seo-aeo-best-practices` — SEO guidelines with AEO (AI engine optimization)
3. `google-analytics-automation` — analytics access
4. `cloudflare/web-perf` — Core Web Vitals audit
5. alirezarezvani SEO Pod (5 skills) — search optimization expertise
6. `content-research-writer` — research for topical authority content
7. `firecrawl/firecrawl-map` — site structure mapping

**SOUL.md skill references:** firecrawl-scrape, firecrawl-search, seo-aeo-best-practices, google-analytics-automation
**Hook pattern:** Content-hash caching for SERP monitoring (avoid redundant crawls)
**Model guidance:** Haiku for bulk crawl/extraction, Sonnet for strategy and content gap analysis

### Research (58 agents)

**Priority skills:**
1. `firecrawl/*` (full suite, 8 skills) — web research extraction
2. `teng-lin/notebooklm-py` — notebooks, podcasts, mind maps from research (with stability caveat)
3. `content-research-writer` — citations + structured output
4. `meeting-insights-analyzer` — transcript/interview analysis
5. `google-gemini/gemini-api-dev` — multi-model research (cross-validate with Gemini)
6. `replicate/replicate` — run specialized AI models for research tasks
7. alirezarezvani Intelligence Pod (4 skills) — market + competitive analysis
8. `anthropics/xlsx` + `anthropics/pdf` — structured research output

**SOUL.md skill references:** firecrawl-scrape, content-research-writer, notebooklm (optional), xlsx/pdf
**Hook pattern:** 3-layer progressive retrieval (Pattern 3) for memory lookups before web searches
**Model guidance:** Haiku for bulk extraction, Opus for deep analysis and synthesis

### Operations (57 agents)

**Priority skills:**
1. `notion-automation` / `linear-automation` / `jira-automation` — project tracking
2. `stripe/stripe-best-practices` + `stripe/upgrade-stripe` — payment operations
3. `supabase/postgres-best-practices` — database patterns
4. `anthropics/docx` + `anthropics/xlsx` — documentation and reporting
5. `hashicorp/terraform-style-guide` — infrastructure management
6. `cloudflare/wrangler` — serverless deployments
7. `sentry/*` — error tracking integration
8. `anthropics/mcp-builder` — build new MCP servers as needed
9. `anthropics/webapp-testing` — automated testing

**SOUL.md skill references:** notion-automation (or linear), stripe-best-practices, postgres-best-practices, docx/xlsx
**Hook pattern:** Stop-phase session summary (Pattern 6) to capture ops learnings
**Model guidance:** Haiku for routine ops tasks, Sonnet for complex infrastructure decisions

### Management (10 meta-agents)

**Priority skills:**
1. alirezarezvani C-Level Advisory (34 skills) — full C-suite perspective
2. `meeting-insights-analyzer` — analyze cross-agent coordination patterns
3. `anthropics/internal-comms` — status reports, escalations
4. alirezarezvani Self-Improving Agent (7 skills) — autonomous memory curation and skill promotion
5. alirezarezvani Project Management (9 skills) — scrum master, senior PM, Jira/Confluence
6. `anthropics/pptx` — executive presentations
7. alirezarezvani Regulatory & QM (14 skills) — compliance for enterprise customers

**SOUL.md skill references:** c-level-advisory (appropriate role), self-improving-agent, internal-comms
**Hook pattern:** Skill evolution confidence gates (Pattern 7) — Management agents decide when patterns become skills
**Model guidance:** Opus for strategic decisions, Sonnet for coordination tasks

---

## Repomix Integration

Repomix (repo #8) deserves special treatment as a cross-cutting utility rather than
a layer-specific skill.

**What it does:** Packs entire repositories into a single AI-friendly file, with:
- Token counting per file and per repository
- Security scanning (Secretlint) to prevent secret exposure
- Git-aware filtering (respects `.gitignore`, `.repomixignore`)
- Code compression via Tree-sitter

**Swarm 357 use cases:**
- Research agents: `repomix --remote <competitor-github-repo>` to analyze competitor codebases
- Operations agents: `repomix --compress` to feed full project context to planning agents
- Management agents: `repomix --stdin` with curated file lists for architectural review

**Install:** `npm install -g repomix`

**Pattern:**
```bash
# Give Research agent full context of a repo they're analyzing
repomix --remote https://github.com/competitor/repo --style xml --compress > /tmp/context.xml
# Then pass as context to agent
```

---

## Memory Architecture Decision

The research reveals two complementary memory systems:

**Memvid `.mv2`** (existing Swarm 357 system):
- Single-file, portable, Rust-based
- Semantic video codec compression
- Bridge: `memvid-swarm-bridge` CLI
- Best for: long-term archival, cross-session knowledge persistence, "deep memory"

**Claude-Mem** (repo #11):
- SQLite + Chroma vector search
- 5 lifecycle hooks (automatic capture)
- 3-layer progressive retrieval (10x token savings)
- Web UI at localhost:37777
- Best for: real-time session capture, automatic observation logging, "working memory"

**Recommendation:** Use both in complementary roles:
- Claude-Mem as "working memory" — automatic capture during active sessions
- Memvid `.mv2` as "long-term memory" — consolidated knowledge after dream cycles
- Migration path: `MemoryManager.migrate_flat_to_memvid()` already handles flat → Memvid
- Add: export from Claude-Mem SQLite → import to Memvid `.mv2` as a nightly consolidation step

---

## Skip List

These resources don't add direct value for Swarm 357 or duplicate what's already in the stack:

| Resource | Reason to Skip |
|----------|---------------|
| **Supabase CLI** (repo #1) | CLI for database management only. No Claude Code skill or MCP integration built in. For Supabase MCP, use the separately published `@supabase/mcp-server-supabase` instead. |
| **Obsidian** (repo #3) | The obsidianmd GitHub org has NO MCP server, no Claude integration, no AI agent tools. Plain plugin SDK only. |
| **LangChain** (repo #4) | LangChain is a Python orchestration framework. It has a `.mcp.json` but no Claude Code skills. Swarm 357 uses the Anthropic SDK directly; LangChain would add complexity without value. Skip unless a specific LangGraph workflow is needed. |
| **Flowise** (repo #5) | Visual no-code AI builder. No Claude Code skills, no hooks, no MCP server. Redundant with Swarm 357's existing orchestration. |
| **CC-Switch** (repo #17) | Desktop app for switching between CLI AI tools (Claude Code, Codex, Gemini CLI, etc.). Not relevant for server-side agent deployment. Useful only for local developer workstations. |

---

## Installation Priority Order

Based on impact/effort for the 357 agents:

**Phase 1 (immediate, high value):**
```bash
# 1. Universal starter skills for all agents
npx antigravity-awesome-skills --claude

# 2. Composio connect-apps (covers 500+ SaaS integrations in one install)
/plugin install connect-apps-plugin

# 3. Anthropic official document skills
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

**Phase 2 (business layer specialization):**
```bash
# alirezarezvani/claude-skills — marketing, C-suite, product, self-improvement
/plugin marketplace add alirezarezvani/claude-skills
/plugin install engineering-skills@claude-code-skills  # adjust per plugin set

# VoltAgent subagents — 130+ specialists
claude plugin marketplace add VoltAgent/awesome-claude-code-subagents
```

**Phase 3 (memory + research enhancement):**
```bash
# Claude-Mem for automatic session capture
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem

# Repomix for codebase context packaging
npm install -g repomix

# NotebookLM skill (Research layer only, verify stability first)
npx skills add teng-lin/notebooklm-py
```

**Phase 4 (infrastructure, when ready):**
```bash
# Ruflo for advanced swarm orchestration (complex setup, verify first)
npx ruflo@latest init --wizard

# Supabase MCP (when database management agents needed)
npm install @supabase/mcp-server-supabase
```

---

## Sources

### Primary (HIGH confidence)
- `github.com/anthropics/skills` — Official Anthropic skills (17 skills documented)
- `github.com/ComposioHQ/awesome-claude-skills` — 31 SaaS automation skills
- `github.com/VoltAgent/awesome-agent-skills` — 1,060+ skills, official publishers
- `github.com/VoltAgent/awesome-claude-code-subagents` — 130+ subagents

### Secondary (MEDIUM confidence)
- `github.com/alirezarezvani/claude-skills` — 248 production skills, installation verified
- `github.com/thedotmack/claude-mem` — Plugin with 5-hook lifecycle, SQLite+Chroma
- `github.com/sickn33/antigravity-awesome-skills` — 8 universal starter skills
- `github.com/yamadashy/repomix` — Codebase packing tool
- `github.com/shanraisshan/claude-code-best-practice` — Architecture patterns
- `github.com/affaan-m/everything-claude-code` — 156+ skills, 38 agents, hook patterns
- `github.com/ruvnet/ruflo` — Enterprise orchestration (complex, verify before adopting)

### Tertiary (LOW confidence — needs validation before production use)
- `github.com/teng-lin/notebooklm-py` — Unofficial Google API, stability unknown
- `github.com/farion1231/cc-switch` — Desktop tool, not relevant for server deployment

---

## Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| Anthropic official skills | HIGH | Direct github.com/anthropics/skills verification |
| Composio SaaS skills | MEDIUM | GitHub README verified; plugin system not live-tested |
| alirezarezvani/claude-skills | MEDIUM | README verified, 248 skills claimed, not all spot-checked |
| Hook lifecycle patterns | HIGH | Consistent across 3+ sources (claude-mem, everything-claude-code, ruflo) |
| Ruflo MCP integration | LOW-MEDIUM | Complex system, claims ambitious; verify current docs before adopting |
| NotebookLM skill | LOW | Unofficial Google API explicitly flagged as unstable by author |
| Memory complementarity | MEDIUM | Architectural reasoning; actual integration not tested |

**Research date:** 2026-04-04
**Valid until:** 2026-05-04 (plugin ecosystem moves fast; re-verify Composio and alirezarezvani versions)
