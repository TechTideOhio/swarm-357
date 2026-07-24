# Architecture

## Data and control flow

```
User
  |
  v
swarm CLI (cli.py)
  |
  +-- swarm init     --> create .swarm/ dirs, .env, MEMORY.md
  +-- swarm demo     --> run 5-agent simulation or live pipeline
  +-- swarm boot     --> warm caches, validate agents (placeholder)
  +-- swarm run      --> Swarm.execute(task)
  +-- swarm plan     --> UltraPlan.plan(task)
  +-- swarm dream    --> MemoryManager.run_dream_cycle()
  +-- swarm status   --> layer health dashboard (illustrative)
  +-- swarm cost     --> model cost report (illustrative)
  |
  v
Swarm (swarm.py)
  |
  +-- AgentConfig (per agent: name, layer, role, soul, tools, model, budget)
  +-- Agent.run(task) --> Anthropic Messages API or stub
  +-- CostController --> per-layer spend tracking
  |
  v
MemoryManager (memory.py)
  |
  +-- .swarm/topics/*.json   <-- flat-file persistence (default)
  +-- MemvidBridge            <-- optional .mv2 persistence
  |     |
  |     +-- memvid-swarm-bridge (Rust CLI)
  |           |
  |           +-- memvid-core (Rust library)
  |                 |
  |                 +-- .mv2 file (WAL + lex + vec + time index)
  |
  +-- share()                 --> write to topics + optional .mv2
  +-- recall()                --> search topics + optional .mv2
  +-- migrate_flat_to_memvid() --> bulk copy topics to .mv2
  +-- run_dream_cycle()       --> detect contradictions
  |
  v
Opik (external)
  +-- Agent trace_url per execution
  +-- OPIK_API_KEY / OPIK_WORKSPACE env vars
```

## Package layout

```
swarm357/
  CLAUDE.md                         # Claude Code session bootstrap
  README.md                         # Quick install + component table
  .github/workflows/swarm357-ci.yml # CI: Python + Next.js + Rust
  packages/
    techtide-swarm/                 # Python package
      pyproject.toml
      src/techtide_swarm/
        __init__.py                 # Public API re-exports
        agent.py                    # Agent + AgentConfig + AgentResult
        swarm.py                    # Swarm + CostController
        memory.py                   # MemoryManager
        memvid_bridge.py            # MemvidBridge (subprocess)
        bash_gate.py                # BashSecurityGate
        ultra_plan.py               # UltraPlan
        cli.py                      # swarm CLI entry point
        core/types.py               # LayerType enum
      tests/
        test_memory.py
        test_bash_gate.py
        test_migration_scenario.py
    memvid-swarm-bridge/            # Rust CLI bridge
      Cargo.toml
      src/main.rs
  .ui_landin_sample/minimal/        # Next.js 16 landing page
    package.json
    lib/config.ts                   # Single config source of truth
    components/                     # Section components
  .repos and items/                 # Reference materials
    memvid-main/memvid-main/        # Upstream Memvid Rust library
    workflows.py                    # Example code snippets
    quickstart.py                   # Standalone demo script
    cli.py                          # Legacy CLI shim
  docs/
    ENTERPRISE_CONTROLS.md
    MEMVID_BRIDGE.md
  .planning/research/               # GSD research artifacts (this dir)
```

## Bridge architecture (Python -> Rust)

The MemvidBridge uses subprocess invocation (not FFI, not HTTP sidecar):

1. Python calls `memvid-swarm-bridge <command> <args>` via subprocess.run()
2. Rust binary parses args with clap, calls memvid-core API
3. Results returned as JSON on stdout (search, verify) or exit code (create, put)
4. Python parses JSON response

This design was chosen for:
- Zero Python-Rust build coupling (no maturin/pyo3 dependency)
- Works on all platforms with a prebuilt binary
- Easy to test each side independently
- Graceful degradation: MemoryManager works without the bridge
