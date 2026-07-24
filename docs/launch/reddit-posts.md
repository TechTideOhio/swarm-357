# Reddit Posts

Two posts: one for r/LocalLLaMA, one for r/MachineLearning. Different audiences, different angles.

---

## r/LocalLLaMA Post

### Title
```
I built a 357-agent Claude AI system organized as a business org chart. Open source. Here's the architecture.
```

### Body

Built and open-sourcing a 357-agent orchestration framework: https://github.com/TechTideOhio/swarm357

**The org chart:**
- Management (10 agents) u2014 Conductor routes tasks; Chief Strategist, Cost Controller, Memory Curator, QA Auditor handle meta-level operations
- Sales (62), Support (55), Marketing (68), SEO (47), Research (58), Operations (57)

**Why org-chart instead of flat agent graph?**

Most multi-agent failures happen at handoffs. When you model agents as "do whatever the LLM decides," you get chaotic routing and unpredictable costs. When you model them as a business org chart, you get: defined roles, predictable routing, clear accountability when something fails.

**Memory (this is the part I want feedback on):**

Three-layer system:
1. `MEMORY.md` u2014 pointer index, max 200 lines u00d7 150 chars, always in context
2. `topics/` u2014 knowledge files fetched on demand
3. Optional: Memvid `.mv2` u2014 portable single-file store with WAL crash safety, Tantivy full-text search, HNSW vector search

`swarm dream` runs memory consolidation u2014 loads all topics, detects contradictions via string overlap, prunes stale entries.

The `.mv2` format is interesting because it has no external dependencies. The file contains its own indexes (lex + vector + time). You can copy it between machines, attach it to an agent, and it travels with no server needed.

**Cost controls (enforced in code, not just documented):**

- Per-agent budget caps checked during `Agent.run()` u2014 execution halts when limit is hit
- Per-layer daily limits (Sales: $500, Support: $300, SEO: $200, etc.)
- `CostController.should_downgrade_model()` returns True at 80% utilization u2014 agent switches Opus u2192 Sonnet or Sonnet u2192 Haiku automatically
- Full GTM campaign (8 agents, 43s): $0.12 in testing

**BashSecurityGate:**

13 regex patterns compiled into a validator that every Bash tool call passes through. Blocks: recursive deletes, curl|bash, secret env var references in argv, writes to system paths, chmod 777, sudo destructive ops, netcat listeners. 50+ tests. Built after a near-miss during development.

**Install:**
```bash
pip install techtide-swarm
swarm demo  # works without API key for architecture view
swarm run "write a market analysis for X"
swarm cost  # see what it cost
```

Python 3.10+. Rust binary for the Memvid bridge (optional; flat-file memory works without it).

Looking for feedback on: the routing architecture, whether the memory system is the right abstraction, and what you'd add to BashSecurityGate.

**Edit:** Replying to all questions. Ask anything.

---

## r/MachineLearning Post

### Title
```
[Project] TechTide Swarm 357: Layered multi-agent orchestration with portable memory and enforced cost controls
```

*(r/ML requires [Project] tag for project posts)*

### Body

**TL;DR:** 357-agent orchestration framework modeled as a business org chart. Open source (Apache 2.0). Key contributions: business-layer ontology for agent routing, three-layer memory architecture with portable .mv2 files, enforced (not documented) cost controls.

https://github.com/TechTideOhio/swarm357

---

**Motivation**

Existing multi-agent frameworks (LangGraph, CrewAI, OpenAI Agents SDK) treat agents as nodes in a task graph. This works well for workflow automation but breaks down at organizational scale: you get chaotic routing, no memory persistence across sessions, and cost overruns that are hard to bound.

Swarm 357 models agents as an org chart instead. Six domain layers + a management meta-layer. The Conductor agent routes every task based on role taxonomy, not ad-hoc LLM routing decisions.

---

**Architecture**

Layer structure (357 agents total):

```
          Management (10)
               |
+------+-------+--------+-----+---------+------+
Sales  Support Marketing SEO  Research  Operations
(62)    (55)    (68)     (47)    (58)      (57)
```

Model distribution is role-based:
- Opus: management agents only (highest reasoning requirement)
- Sonnet: senior domain agents (strategy, synthesis, complex analysis)
- Haiku: high-frequency workers (CRM writes, keyword lookups, tier-1 triage)

Each agent has a u201csoulu201d file u2014 YAML front-matter + system prompt with decision rules, worked examples, and confidence gates.

---

**Memory Architecture**

Three-layer progressive retrieval system designed to minimize context token usage:

1. `MEMORY.md` (always loaded) u2014 pointer index only, max 200 lines, ~150 chars each
2. `topics/*.json` (fetched on demand) u2014 actual knowledge files retrieved by semantic key
3. `agent-memory.mv2` (optional, Rust-backed) u2014 single-file store with WAL, Tantivy full-text, HNSW vector search

The `.mv2` format (Memvid v2) is the interesting piece: it packs the WAL, data segments, lex index, vector index, and time index into one portable file with no external database dependency. `swarm migrate` converts flat-file memory to `.mv2`.

The dream cycle (`swarm dream`) runs memory consolidation: loads all topic files, detects contradictions via string-overlap heuristics, and prunes entries older than a configurable TTL.

---

**Cost Enforcement**

Cost controls are enforced in code, not documented as guidelines:

- `Agent.run()` checks remaining budget before each API call; raises `BudgetExceeded` if the estimated cost would exceed the cap
- `CostController` tracks cumulative spend per model, per layer, per day
- At 80% layer utilization, `should_downgrade_model()` returns True and the Conductor switches subsequent agent calls to a cheaper model tier
- Cost estimation uses token counts u00d7 per-model pricing snapshots (not real-time API queries)

Observed cost for 8-agent GTM campaign task: $0.12, 43 seconds.

---

**Security**

`BashSecurityGate` is a 13-pattern regex validator wired into the Bash tool. Every shell command passes through it before execution. Blocked patterns include recursive deletes, shell injection via curl/wget, secret env var references in argv, writes to system paths, and privilege escalation. The test suite has 50+ scenario-based tests; each new pattern gets a failing test written before the regex is added.

---

**Limitations (honest)**

- WebSearch and WebScrape tools are stubs; they need Exa/Firecrawl API keys wired in
- Dream cycle contradiction detection is heuristic (string overlap), not semantic
- Eval harness uses keyword overlap scoring, not LLM-based evaluation
- Cost estimation is offline (pricing snapshots, not live API rates)
- 357 agents with soul files takes ~2s to boot; first-run latency is noticeable

**Open questions I'm interested in:**

1. Is the business-layer ontology the right abstraction for agent routing, or are there better taxonomies?
2. Is the three-layer memory architecture too complex? Would a single vector store be better?
3. BashSecurityGate uses regex patterns u2014 is there a better approach that doesn't require manual pattern addition?

All code and tests are in the repo. Happy to discuss any of the design decisions.

---

## Reddit Posting Notes

- **r/LocalLLaMA:** More casual, builder-focused audience. They want to try it. Lead with install command.
- **r/MachineLearning:** More academic, interested in architecture and limitations. Lead with the problem statement and be honest about limitations.
- Post both on the same day (Tuesdayu2013Thursday, 10 AMu20132 PM ET works well)
- Don't cross-post the same text u2014 use different angles as shown above
- Reply to comments within 2 hours on both subs; early engagement boosts visibility
- If anyone asks about comparison to other frameworks, be specific: point to actual code, not claims
