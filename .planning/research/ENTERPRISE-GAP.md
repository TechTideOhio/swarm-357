# Enterprise Gap Analysis

What "enterprise" means to buyers vs what Swarm 357 currently provides.

## Provable controls (in repo today)

| Control | Mechanism | Evidence |
|---------|-----------|----------|
| Command policy | BashSecurityGate (9+ block patterns) | `bash_gate.py` + `test_bash_gate.py` |
| Budget caps | AgentConfig.budget_limit_usd | `agent.py` field; enforcement is TODO |
| Layer spend limits | CostController.set_budget() | `swarm.py`; in-memory demo |
| Memory integrity | memvid-swarm-bridge verify [--deep] | `main.rs` Verify command |
| Trace audit trail | Opik trace URLs per agent run | `agent.py` trace_url field |
| Secret-free execution | BashSecurityGate blocks $KEY patterns | Block pattern in `bash_gate.py` |

## Gaps (not in scope for v0.1)

| Requirement | Status | What buyers expect |
|-------------|--------|--------------------|
| SSO / SAML / OIDC | Not started | Integrate with corporate IdP (Okta, Azure AD) |
| Multi-tenancy | Not started | Tenant isolation for data, agents, and billing |
| RBAC / permissions | Not started | Role-based access to layers, agents, memory |
| Data residency | Not started | Control where .mv2 files and API calls are routed |
| Retention policies | Not started | Auto-expire memory entries after N days |
| Audit logging | Partial (Opik) | Immutable audit log of all agent actions |
| Encryption at rest | Upstream only | Memvid supports .mv2e; not wired in bridge |
| Encryption in transit | Anthropic TLS | No additional layer |
| SOC 2 / ISO 27001 | Not applicable | Certification for hosted offerings |
| SLA / support tiers | Not applicable | Service-level agreements for uptime |
| Disaster recovery | Not started | Backup/restore for .mv2 files and configs |

## Recommended language

Use in marketing and docs:

- "Enterprise controls" (provable: bash gate, budgets, verify)
- "Enterprise-style orchestration" (layered, observable)
- "Compliance-ready memory" (integrity checks, optional encryption path)

Do NOT use:

- "Enterprise-ready" (implies SSO, tenancy, SLAs)
- "Enterprise-grade security" (implies pen-test, SOC 2)
- "Production-hardened" (implies battle-tested at scale)

## Path to enterprise (future milestones)

1. Budget enforcement: CostController rejects tasks when over limit
2. Encrypted .mv2e bridge: add --encrypt flag to memvid-swarm-bridge
3. Audit log: append-only log of all agent actions (separate from Opik)
4. RBAC layer: who can run which agents, access which memory
5. Multi-tenancy: namespace agents and memory per tenant
