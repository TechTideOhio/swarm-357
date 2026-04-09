# Enterprise Controls

Concrete mechanisms in the repo that map to enterprise product language.

## 1. Command execution policy

**`BashSecurityGate`** ([`packages/techtide-swarm/src/techtide_swarm/bash_gate.py`](../packages/techtide-swarm/src/techtide_swarm/bash_gate.py)) validates shell commands before execution against 13 block patterns:

| Category | What it blocks |
|----------|---------------|
| Destructive filesystem | `rm -rf /`, `rm -rf ~` |
| Remote code execution | `curl ... \| bash`, `wget ... \| sh` |
| Dangerous permissions | `chmod 777`, `sudo chmod 777` |
| Secret exfiltration | `$ANTHROPIC_API_KEY`, `$OPENAI_API_KEY`, `$AWS_SECRET`, `$DB_PASSWORD` |
| System config writes | Redirects to `/etc/` |
| Disk operations | `mkfs`, `dd if=`, redirects to `/dev/sd*` |
| Code injection | `python -c '...exec/eval/import os...'` |
| Elevated operations | `sudo rm`, `sudo mv`, `sudo cp`, `sudo chown` |
| Network listeners | `nc -l`, `nc -e` |

Extend `_BLOCK_PATTERNS` as your policy tightens. Every pattern has a corresponding test in [`tests/test_bash_gate.py`](../packages/techtide-swarm/tests/test_bash_gate.py) and [`tests/test_bash_gate_scenarios.py`](../packages/techtide-swarm/tests/test_bash_gate_scenarios.py).

## 2. Budgets and cost control

- **`AgentConfig.budget_limit_usd`** — per-agent intent cap (enforcement during runtime planned for v0.2).
- **`CostController`** ([`swarm.py`](../packages/techtide-swarm/src/techtide_swarm/swarm.py)) — tracks per-layer daily limits, computes utilization percentage, and signals when to downgrade models.
- **`swarm cost`** CLI — surfaces model-level cost tables. Replace with Opik or warehouse aggregates in production.
- **`Agent._estimate_cost()`** — computes approximate cost from token usage and model pricing snapshots.

Tests: [`tests/test_swarm.py`](../packages/techtide-swarm/tests/test_swarm.py) covers `CostController.set_budget()`, `get_swarm_cost_report()`, and `should_downgrade_model()`.

## 3. Memory integrity and compliance

- **Flat-file layer** — `.swarm/topics/*.json` are human-readable, auditable JSON files.
- **Memvid `.mv2`** — WAL-based crash-safe store with `Memvid::verify()` for integrity checks.
- **`memvid-swarm-bridge verify [--deep]`** — runs integrity checks from CLI. JSON `VerificationReport` on stdout. See [`docs/MEMVID_BRIDGE.md`](MEMVID_BRIDGE.md).
- **Optional encryption** — upstream Memvid supports AES-256-GCM encrypted capsules (`.mv2e`). Not yet wired in the bridge; reference upstream feature flags for regulated use cases.
- **Migration** — `MemoryManager.migrate_flat_to_memvid(dest)` bulk-copies `.swarm/topics/` to `.mv2`. `swarm migrate` CLI command available.

Tests: [`tests/test_migration_scenario.py`](../packages/techtide-swarm/tests/test_migration_scenario.py), [`tests/test_bridge_integration.py`](../packages/techtide-swarm/tests/test_bridge_integration.py), [`tests/test_layer_memory.py`](../packages/techtide-swarm/tests/test_layer_memory.py).

## 4. Observability

- **Opik tracing** — `Agent.run()` returns `trace_url` when `OPIK_WORKSPACE` is set.
- **Structured results** — `AgentResult` and `SwarmExecutionResult` dataclasses carry cost, latency, status, and error fields.
- **CLI dashboards** — `swarm status` (layer health), `swarm cost` (model spend).

## 5. What is outside this repository

SSO, multi-tenancy, data residency, retention policies, SLA/support tiers, and SOC 2 certification are **not in scope** for the open-source package. See [`.planning/research/ENTERPRISE-GAP.md`](../.planning/research/ENTERPRISE-GAP.md) for the full gap analysis and recommended language.
