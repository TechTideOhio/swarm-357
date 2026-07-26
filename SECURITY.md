# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.2.x | Yes |
| 0.1.x | Best effort |
| < 0.1 | No |

## Reporting a vulnerability

Please report security issues privately via GitHub Security Advisories on
[TechTideOhio/swarm-357](https://github.com/TechTideOhio/swarm-357/security/advisories/new)
or email `ai@techtide.ai` with subject `[SECURITY] Swarm 357`.

Do not open public issues for exploitable vulnerabilities.

We aim to acknowledge reports within 72 hours and provide a remediation timeline after triage.

## Security posture (what we claim)

| Control | Behavior |
|---------|----------|
| HTTP write auth | When `SWARM_API_KEY` is set, POST routes require `X-SWARM-API-KEY` |
| Rate limiting | Per-IP sliding window via `SWARM_RATE_LIMIT_PER_MINUTE` (`0` disables) |
| Run budget cap | Request `budget_usd` capped by `SWARM_MAX_RUN_BUDGET_USD` |
| BashSecurityGate | 13-pattern regex validator on the `Bash` tool - blocks destructive and exfiltration-shaped commands |
| Bash HITL | When Bash is enabled, `SWARM_HITL_BASH` (default on in server/production) requires approve/reject before execution |
| Write sandbox | Workspace root confinement for Read/Write (CWD by default; `SWARM_UNSAFE_FS=1` opt-out) |
| File deny-list | Path deny patterns in file ops |
| Model mapping | OpenRouter does **not** silently map opus/sonnet → Haiku unless `SWARM_OPENROUTER_CHEAP=1` |
| Cost downgrade | `CostController` may force Haiku at 80% layer spend; this is **logged** (`model_downgrade`), not a silent provider remap |

## Non-scope / limitations

- BashSecurityGate is **pattern-based**, not a sandboxed OS. Do not treat it as a container or seccomp jail.
- API key auth is a **shared secret**, not multi-tenant IAM / SSO.
- Agents that can call external tools inherit those tools' trust boundaries (Exa, Firecrawl, MCP servers).
- Eval and demo deployments should keep `SWARM_API_KEY` set and CORS origins restricted.

## Disclosure preference

Coordinated disclosure after a fix is available is preferred. Credit will be given unless you request anonymity.
