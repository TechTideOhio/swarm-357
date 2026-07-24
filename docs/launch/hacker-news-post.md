# Hacker News u2014 Show HN Post

## Title

```
Show HN: TechTide Swarm 357 u2013 357-agent Claude AI system organized as a business org chart
```

*(HN title limit: 80 chars. This is 75.)*

---

## Body (5 paragraphs)

---

I spent the last several months building a 357-agent Claude AI system and am open-sourcing it today under Apache 2.0: https://github.com/TechTideOhio/swarm357

The core idea: instead of ad-hoc agents that talk to each other, model the whole thing as a business org chart. Six domain layers (Sales 62, Support 55, Marketing 68, SEO 47, Research 58, Operations 57) plus a management layer of ten Opus agents u2014 a Conductor, Chief Strategist, Memory Curator, QA Auditor, Cost Controller, and five others. The Conductor routes every task to the right agents based on role and layer. I found that most multi-agent failures happen at the handoff, not inside the agent itself. The routing problem is harder than the agent problem.

The two things Iu2019m most interested in feedback on: (1) Memory. Each agent gets a three-layer memory system u2014 a MEMORY.md pointer index always in context, a topics/ directory of knowledge files fetched on demand, and optionally a portable Memvid .mv2 file for long-term storage. The .mv2 format is a single file with a WAL, full-text search (Tantivy), and HNSW vector search. No database server needed. A `swarm dream` command runs memory consolidation across the whole swarm. (2) Cost controls. Per-agent budget caps are enforced in code during Agent.run(), not just documented. Per-layer daily limits total $2,500/day. The CostController automatically downgrades models at 80% utilization. A full GTM campaign (routing through 8 agents, 67 seconds) costs $0.0773 in testing.

BashSecurityGate is worth calling out separately because giving 357 agents access to a Bash tool without controls is a bad idea. Itu2019s a 13-pattern regex validator that blocks recursive deletes toward root, curl-pipe-to-bash patterns, secret env var references in argv, writes to /etc/ and block devices, chmod 777, sudo destructive operations, and netcat listeners. There are 50+ tests. I added every pattern after an actual near-miss during development.

Install: `pip install techtide-swarm`, then `swarm demo` (works without an API key for the architecture view, runs live agents with one set). The CLI has 11 commands: init, demo, boot, run, status, cost, dream, plan, eval, serve, and agent. Everything is documented in the README. The package is Python 3.10+ and the memory bridge is a Rust binary (source in packages/memvid-swarm-bridge/). Interested in feedback on the routing logic, the memory architecture, and whether the business-layer ontology is the right abstraction for multi-agent orchestration.

---

## HN Submission Tips

- Submit between 9u201311 AM ET on a Tuesday, Wednesday, or Thursday
- Reply to every early comment within 30 minutes u2014 HN surfaces posts with fast author engagement
- If asked about security/costs, point to `BashSecurityGate` in the code and the `CostController` class u2014 show real code, not explanations
- Common critical questions to prepare for:
  - "How is this different from CrewAI?" u2192 Cost enforcement in code + BashSecurityGate + Memvid .mv2 memory
  - "357 agents seems arbitrary" u2192 Explain the org-chart ontology; the number reflects real business role counts
  - "Is the memory actually useful?" u2192 Show the `swarm dream` output and the .mv2 format spec
  - "What's the latency?" u2192 67 seconds for 14-agent GTM task in testing; Haiku agents average ~1.5s
  - "Does the security gate actually work?" u2192 Link to test_bash_gate_scenarios.py u2014 50+ tests
- Avoid: calling it "game-changing" or "revolutionary" u2014 HN readers respond to technical specifics, not marketing language
