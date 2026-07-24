# Pitfalls and Risks

## 1. Bridge risk (critical path)

**Risk:** The Python-to-Memvid bridge is the single integration point. If it breaks, the "durable memory" story is dead.

**Mitigation:**
- CI builds the bridge on every push (already in `swarm357-ci.yml`)
- MemoryManager gracefully degrades to flat-file when bridge is missing
- test_migration_scenario.py verifies the skip path
- TODO: add integration test that builds the bridge and runs a full put/search cycle

## 2. 357-scope creep

**Risk:** Promising 357 named agents creates maintenance burden. Each agent needs a SOUL.md, tests, and eval criteria.

**Mitigation:**
- Use codegen: `scripts/generate-agents.py --layer <layer> --role <role> --count N`
- Template-based SOUL.md with variables (layer, role, tools, tone)
- Test one representative agent per layer, not all 357
- Agent count is a product story, not a testing matrix

## 3. Enterprise washing

**Risk:** Calling the product "enterprise" without RBAC, tenancy, retention policies, or SLAs undermines credibility with security and procurement reviewers.

**Mitigation:**
- `docs/ENTERPRISE_CONTROLS.md` maps product claims to concrete mechanisms
- `.planning/research/ENTERPRISE-GAP.md` lists what is NOT in scope
- Landing page and README use "enterprise-style" or "enterprise controls" (not "enterprise-ready")
- BashSecurityGate, budget caps, and Memvid verify are the provable claims

## 4. Documentation and onboarding gaps

**Risk:** "Top GitHub repo" outcomes require: quickstart < 5 min, works on Win/Mac/Linux, architecture diagrams, and clear contributor guide.

**Mitigation:**
- quickstart.py runs without API key (simulation mode)
- `pip install -e "packages/techtide-swarm[dev]" && swarm demo` is the golden path
- CONTRIBUTING.md exists with 5 easy contribution paths
- CLAUDE.md is the architecture document

## 5. Test coverage

**Risk:** Only 3 test files. No integration tests with the bridge. No eval/regression tests for agent outputs.

**Mitigation:**
- Add test_agent.py (stub mode), test_swarm.py (pipeline), test_bridge_integration.py (if bridge available)
- Golden trace tests: known input -> expected output shape (not exact text)
- CI runs pytest on every push

## 6. Positioning collision

**Risk:** OpenClaw, LangChain, CrewAI, and Claude Code subagents all compete in the "multi-agent" space. Generic "we have more agents" does not differentiate.

**Mitigation:**
- Lead with the unique combination: layered business ontology + portable .mv2 memory + observability
- Comparison table in `.planning/research/COMPARISON.md`
- Landing config already uses this positioning
