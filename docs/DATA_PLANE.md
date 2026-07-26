# Data plane (Supabase)

Optional persistence uses the same schema as [`SwarmStore`](../packages/techtide-swarm/src/techtide_swarm/persistence.py).

## Apply migration

1. Open your Supabase project → **SQL Editor**.
2. Run [`database/migrations/001_initial.sql`](../database/migrations/001_initial.sql) in order (single file is self-contained).
3. Tables created: `agent_runs`, `swarm_runs`, `memory_entries`, `dream_reports`, `swarm_config`.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Project URL |
| `SUPABASE_SERVICE_KEY` | Service role key (server-side only; never expose to browsers) |

When either variable is missing, `SwarmStore` stays disabled: the API continues to work using local `.swarm/telemetry.jsonl` only.

## Failure mode

Supabase insert failures are logged with `logger.warning` and **do not** fail HTTP requests. The primary API response path remains available if the database is down or misconfigured.

## RLS

The migration does not enable Row Level Security by default (server uses service role). If you expose Supabase directly to clients, add RLS policies separately. This project expects the Python service to be the only writer.
