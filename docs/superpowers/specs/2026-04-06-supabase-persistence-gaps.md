# Supabase Persistence Layer — Gap Fixes

**Date:** 2026-04-06  
**Scope:** `packages/techtide-swarm/` + `Dockerfile`  
**Approach:** Option A — surgical fixes to 7 identified gaps; no new files, no schema changes

---

## Context

The Supabase persistence layer (`persistence.py`, `telemetry.py`, `memory.py`,
`database/migrations/001_initial.sql`) was implemented as part of Prompt 5. A
correctness audit against the prompt requirements and against a production Railway
deployment scenario found 7 gaps. This spec covers exactly those gaps — nothing more.

The system must continue to work without Supabase (local-only mode for contributors).
All `SwarmStore` methods remain silent no-ops when `SUPABASE_URL` / `SUPABASE_SERVICE_KEY`
are absent.

---

## Gap Inventory

| # | File | Gap | Fix |
|---|------|-----|-----|
| 1 | `Dockerfile` | `supabase` extra not installed; `create_client` raises `ImportError` on Railway | Install `[supabase]` extra unconditionally |
| 2 | `persistence.py` | `get_total_cost()` fetches `SELECT *` — all columns, all rows | Change to `select("cost_usd")` — single column |
| 3 | `persistence.py` | `get_layer_stats()` fetches all rows — acceptable (3 cols), but verify | Already `select("layer,cost_usd,latency_ms")` — no change needed |
| 4 | `server.py` | `POST /api/swarm/run` never logs the top-level `swarm_run` event | Add `log_telemetry("swarm_run", ...)` after successful full-swarm execution |
| 5 | `persistence.py` | `recall_memory()` passes raw `agent_id` into PostgREST `or_()` filter string | Sanitize `agent_id` to `[a-zA-Z0-9_:-]` before use in filter |
| 6 | `persistence.py` | `recall_memory()` passes raw `query` into `.ilike()` — user-controlled | Truncate `query` to 200 chars, strip `%` and `_` wildcards before ilike |
| 7 | docs | `SUPABASE_SERVICE_KEY` vs Supabase dashboard's `SUPABASE_SERVICE_ROLE_KEY` | Add env var note to `CLAUDE.md` / README so Railway setup is unambiguous |

---

## Architecture (unchanged)

```
Railway deploy
  → Dockerfile installs techtide-swarm[supabase]
  → Server starts → snapshot_config() → Supabase swarm_config
  → Agent run  → telemetry.log_telemetry("agent_run", ...)  → JSONL + agent_runs
  → Swarm run  → telemetry.log_telemetry("swarm_run", ...)  → JSONL + swarm_runs  ← NEW
  → memory share → MemoryManager.share() → .swarm/topics/ + memory_entries
  → dream cycle  → store.log_dream()    → dream_reports
  → GET /api/swarm/cost   → select("cost_usd") → sum in Python  ← FAST
  → GET /api/swarm/status → select("layer,cost_usd,latency_ms") → aggregate in Python
```

---

## File-by-file changes

### `Dockerfile`

```dockerfile
# BEFORE
RUN pip install --no-cache-dir --prefix=/install \
    "./packages/techtide-swarm"

# AFTER
RUN pip install --no-cache-dir --prefix=/install \
    "./packages/techtide-swarm[supabase]"
```

Rationale: Railway is always the production environment; `supabase-py` is a small
dep (~300 KB). Installing unconditionally avoids the silent `ImportError` warning
that would leave the store disabled even when credentials are present.

### `persistence.py` — `get_total_cost()`

```python
# BEFORE
rows = self._client.table("agent_runs").select("*").execute().data
return sum(float(r.get("cost_usd", 0)) for r in (rows or []))

# AFTER
rows = self._client.table("agent_runs").select("cost_usd").execute().data
return sum(float(r.get("cost_usd", 0)) for r in (rows or []))
```

### `persistence.py` — `recall_memory()` sanitization

```python
# BEFORE
def recall_memory(self, query: str, agent_id: str, top_k: int = 5) -> ...
    rows = (
        self._client.table("memory_entries")
        .select("key,content,from_agent,to_agent")
        .or_(f"to_agent.eq.{agent_id},from_agent.eq.{agent_id}")
        .ilike("content", f"%{query}%")
        ...
    )

# AFTER
import re as _re

def recall_memory(self, query: str, agent_id: str, top_k: int = 5) -> ...
    # Sanitize inputs before passing into PostgREST filter strings
    safe_agent_id = _re.sub(r"[^a-zA-Z0-9_:.-]", "", agent_id)[:120]
    safe_query = query[:200].replace("%", "").replace("_", " ")
    rows = (
        self._client.table("memory_entries")
        .select("key,content,from_agent,to_agent")
        .or_(f"to_agent.eq.{safe_agent_id},from_agent.eq.{safe_agent_id}")
        .ilike("content", f"%{safe_query}%")
        ...
    )
```

### `server.py` — log `swarm_run` event after full-swarm execution

In `swarm_run()` (the `POST /api/swarm/run` handler), after `result = await swarm.execute(...)`,
add before the return:

```python
from techtide_swarm.telemetry import log_telemetry
log_telemetry("swarm_run", {
    "pipeline_id":    result.pipeline_id,
    "task":           req.task,
    "total_cost_usd": result.total_cost_usd,
    "agents_used":    [r.agent_name for r in result.agent_results],
    "latency_ms":     sum(r.latency_ms for r in result.agent_results),
    "status":         result.status,
})
```

The layer-specific path (`execute_layer`) already logs individual `agent_run` events
per agent; adding a top-level swarm_run there is optional (out of scope for this fix).

---

## Env var documentation

Add to `CLAUDE.md` (swarm357) under **Required env vars**:

```
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_SERVICE_KEY=<service_role_key>   # In Supabase dashboard: Project Settings → API → service_role
```

Note: Supabase dashboard labels this key `service_role` (or `SUPABASE_SERVICE_ROLE_KEY`
in some docs). The code uses `SUPABASE_SERVICE_KEY` — set Railway env var to that name.

---

## Testing

All existing tests in `test_server.py` must continue to pass unchanged. No new test
files needed — the existing tests already cover:

- `test_store_disabled_without_env` — store is off when no creds
- `test_store_log_run_noop` — no-op when disabled
- `test_store_get_runs_empty_when_disabled` — empty returns when disabled
- `test_store_recall_memory_empty_when_disabled` — empty when disabled
- `test_log_telemetry_calls_store` — dual-write verified
- `test_memory_share_calls_store` — memory dual-write verified
- `test_dream_endpoint_calls_store_log_dream` — dream logging verified

New tests to add (in `test_server.py`):

1. `test_swarm_run_logs_swarm_event` — monkeypatch `log_telemetry`, call
   `POST /api/swarm/run` with a stub config, assert a `swarm_run` event was emitted.
2. `test_recall_memory_sanitizes_agent_id` — instantiate `SwarmStore` with a mock
   client, call `recall_memory(query="test%inject", agent_id="agent;DROP TABLE")`,
   assert the filter string passed to `or_()` contains only safe chars.

---

## Verification (end-to-end on Railway)

1. Push branch to Railway with `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` set.
2. `curl https://<railway-url>/api/health` → `{"status": "ok"}`
3. `curl https://<railway-url>/api/swarm/cost` → `{"total_cost_usd": 0.0, ...}` (no 500)
4. Open Supabase dashboard → Table Editor → `swarm_config` → verify 1 row with
   the config snapshot.
5. `curl -X POST https://<railway-url>/api/swarm/run -d '{"task":"ping","budget_usd":0.01}'`
6. Check `agent_runs` and `swarm_runs` tables in Supabase dashboard → rows appear.
7. `curl -X POST https://<railway-url>/api/swarm/dream`
8. Check `dream_reports` table → row appears.
9. Locally (no Supabase creds): `pytest tests/` → all pass, no warnings about disabled store.
