# Database Setup

## Apply Migrations

Run in the Supabase SQL editor (Dashboard → SQL Editor):

```sql
-- Paste the full contents of migrations/001_initial.sql
```

Or via the Supabase CLI:

```bash
supabase db push
```

## Tables

| Table | Purpose |
|-------|---------|
| `agent_runs` | Individual agent execution records (name, task, cost, latency, status) |
| `swarm_runs` | Multi-agent pipeline records (pipeline_id, total_cost, agents_used) |
| `memory_entries` | Cross-agent shared knowledge (from_agent, to_agent, key, content) |
| `dream_reports` | Memory consolidation cycle reports (JSONB) |
| `swarm_config` | Config snapshots on server startup (JSONB) |

## Environment Variables

Set in Railway (or `.env` locally):

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your project URL, e.g. `https://xxxx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Service role key from Project Settings → API |

When these vars are absent, the system falls back to local JSONL files in `.swarm/`.

## Row Level Security (RLS)

The bundled migration creates tables without RLS for simplicity. The Python server uses the **service role** key (`SUPABASE_SERVICE_KEY`), which bypasses RLS.

- **Recommended**: keep service role secrets only on the API server (Railway), never in the browser.
- If you need **read-only public access** (e.g. a dashboard), create a dedicated Postgres role or Supabase **anon** policies on views that expose only non-sensitive columns — do not expose the service key to clients.

For a typical deployment, only the FastAPI backend talks to Supabase with the service key; end users call the REST API, which enforces `SWARM_API_KEY` on POST routes.
