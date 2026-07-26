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
| Read redaction | Unauthenticated `GET /api/swarm/runs` and `GET /api/swarm/runs/{id}` return counters and status only. Task text, outputs, errors, and step detail require the write key |
| Health disclosure | Public `/api/health` returns `status`, `version`, `agents`, `auth_required`. Provider, model routing, and config path require the write key |
| CORS | Fail-closed allowlist, never `*`. Extend with `ALLOWED_ORIGINS` |
| Outbound SSRF guard | The `Scrape` tool rejects non-HTTP schemes and any host resolving to loopback, private, link-local, reserved, multicast, or unspecified addresses, and re-validates every redirect hop |
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
- The SSRF guard resolves DNS before the request and again inside the HTTP client, so it does not fully defeat DNS rebinding. Run the API with egress restrictions if that is in your threat model.
- The Firecrawl and Exa scrape backends fetch through a third party. URL validation still applies, but the outbound request itself leaves their infrastructure, not yours.
- Supabase migrations ship without row level security. `SUPABASE_SERVICE_KEY` is a service-role secret for a single-tenant server; do not place it in a client bundle or expose the database directly to browsers.
- Eval and demo deployments should keep `SWARM_API_KEY` set and CORS origins restricted.
- The Rust bridge carries one accepted low-severity advisory: `lru` 0.12.x (`IterMut` violates Stacked Borrows). It reaches us transitively through `tantivy` inside `memvid-core`, which pins `lru ^0.12`, so the 0.16.3 fix is blocked upstream. The issue is a Miri-observable soundness lint in an iterator we do not call, in an optional binary that never handles untrusted input. We will pick it up when `memvid-core` upgrades `tantivy`.
- The interactive API explorer (`/docs`, `/redoc`, `/openapi.json`) is intentionally public. Every route it lists is already public in this repository, writes fail closed without the write key, and reads are redacted. Set `SWARM_DISABLE_API_DOCS=1` to remove the explorer on a deployment where route enumeration matters.

## Disclosure preference

Coordinated disclosure after a fix is available is preferred. Credit will be given unless you request anonymity.
