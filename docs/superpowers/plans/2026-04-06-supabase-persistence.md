# Supabase Persistence Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Supabase as a dual-write persistence backend so Railway deployments survive restarts, while local contributors run unchanged with no credentials required.

**Architecture:** `SwarmStore` (new `persistence.py`) wraps a `supabase-py` client when `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` are present; otherwise every method is a silent no-op. `telemetry.py` and `MemoryManager.share()` call `SwarmStore` *after* their existing file writes so the file system remains authoritative locally. Server endpoints read from Supabase when `store.enabled`, else fall back to local file reads.

**Tech Stack:** Python 3.10+, FastAPI, supabase-py (optional), pytest, existing JSONL/flat-file fallback.

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `database/migrations/001_initial.sql` | Create | DDL for 5 Supabase tables |
| `packages/techtide-swarm/pyproject.toml` | Modify | Add `supabase` optional dep group |
| `packages/techtide-swarm/src/techtide_swarm/persistence.py` | Create | `SwarmStore` class — all Supabase I/O |
| `packages/techtide-swarm/src/techtide_swarm/telemetry.py` | Modify | Dual-write: JSONL + `store.log_run()` |
| `packages/techtide-swarm/src/techtide_swarm/memory.py` | Modify | Dual-write: JSON file + `store.store_memory()` / `store.recall_memory()` |
| `packages/techtide-swarm/src/techtide_swarm/server.py` | Modify | Lifespan startup snapshot; dream endpoint logs; read endpoints use store when enabled |
| `packages/techtide-swarm/src/techtide_swarm/__init__.py` | Modify | Export `SwarmStore` |
| `packages/techtide-swarm/tests/test_server.py` | Modify | Add `SwarmStore` unit tests |

---

## Task 1: SQL Migration

**Files:**
- Create: `database/migrations/001_initial.sql`

- [ ] **Step 1: Write the migration file**

```sql
-- 001_initial.sql
-- UP

create table if not exists agent_runs (
    id          bigserial primary key,
    agent_name  text        not null,
    layer       text        not null default '',
    task        text        not null default '',
    output      text        not null default '',
    cost_usd    numeric(12,8) not null default 0,
    latency_ms  integer     not null default 0,
    status      text        not null default 'success',
    error       text,
    created_at  timestamptz not null default now()
);

create table if not exists swarm_runs (
    id              bigserial primary key,
    pipeline_id     text        not null,
    task            text        not null default '',
    total_cost_usd  numeric(12,8) not null default 0,
    agents_used     jsonb       not null default '[]',
    latency_ms      integer     not null default 0,
    status          text        not null default 'ok',
    created_at      timestamptz not null default now()
);

create table if not exists memory_entries (
    id          bigserial primary key,
    from_agent  text        not null,
    to_agent    text        not null,
    key         text        not null,
    content     text        not null,
    created_at  timestamptz not null default now()
);

create table if not exists dream_reports (
    id          bigserial primary key,
    report      jsonb       not null,
    created_at  timestamptz not null default now()
);

create table if not exists swarm_config (
    id          bigserial primary key,
    config      jsonb       not null,
    created_at  timestamptz not null default now()
);

-- Indexes for common queries
create index if not exists idx_agent_runs_layer     on agent_runs (layer);
create index if not exists idx_agent_runs_created   on agent_runs (created_at desc);
create index if not exists idx_swarm_runs_created   on swarm_runs (created_at desc);
create index if not exists idx_memory_entries_key   on memory_entries (key);
create index if not exists idx_memory_entries_agent on memory_entries (to_agent, from_agent);

-- DOWN
-- drop table if exists swarm_config;
-- drop table if exists dream_reports;
-- drop table if exists memory_entries;
-- drop table if exists swarm_runs;
-- drop table if exists agent_runs;
```

- [ ] **Step 2: Commit**

```bash
git add database/migrations/001_initial.sql
git commit -m "feat(db): add Supabase migration 001_initial"
```

---

## Task 2: Optional Dependency

**Files:**
- Modify: `packages/techtide-swarm/pyproject.toml`

- [ ] **Step 1: Write the failing test** (verifies supabase dep is declared)

Add to `packages/techtide-swarm/tests/test_server.py`:

```python
def test_supabase_optional_dep_declared():
    """supabase must be listed as an optional dependency."""
    import importlib.util
    toml_path = Path(__file__).parent.parent / "pyproject.toml"
    content = toml_path.read_text(encoding="utf-8")
    assert "supabase" in content, "supabase missing from pyproject.toml optional-dependencies"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd packages/techtide-swarm
pytest tests/test_server.py::test_supabase_optional_dep_declared -v
```

Expected: FAIL with AssertionError

- [ ] **Step 3: Add optional dep group to pyproject.toml**

In the `[project.optional-dependencies]` section, add:

```toml
supabase = [
  "supabase>=2.0",
]
```

Full updated block:

```toml
[project.optional-dependencies]
dev = [
  "pytest>=8",
  "pytest-asyncio>=0.24",
  "ruff>=0.8",
  "mypy>=1.13",
]
web = [
  "exa-py>=1.0",
  "firecrawl-py>=0.0.20",
]
supabase = [
  "supabase>=2.0",
]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_server.py::test_supabase_optional_dep_declared -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/techtide-swarm/pyproject.toml packages/techtide-swarm/tests/test_server.py
git commit -m "feat(deps): add supabase optional dependency group"
```

---

## Task 3: Create persistence.py

**Files:**
- Create: `packages/techtide-swarm/src/techtide_swarm/persistence.py`

- [ ] **Step 1: Write failing tests**

Add to `packages/techtide-swarm/tests/test_server.py`:

```python
def test_store_disabled_without_env(monkeypatch):
    """SwarmStore.enabled is False when SUPABASE_URL is absent."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    from techtide_swarm.persistence import SwarmStore
    store = SwarmStore()
    assert store.enabled is False


def test_store_log_run_noop(monkeypatch):
    """log_run() is silent when store is disabled."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    from techtide_swarm.persistence import SwarmStore
    store = SwarmStore()
    # Must not raise
    store.log_run("agent_run", {"agent_name": "x", "cost_usd": 0.0, "latency_ms": 0, "status": "success"})


def test_store_get_runs_empty_when_disabled(monkeypatch):
    """get_runs() returns [] when store is disabled."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    from techtide_swarm.persistence import SwarmStore
    store = SwarmStore()
    assert store.get_runs() == []
    assert store.get_total_cost() == 0.0
    assert store.get_layer_stats() == {}


def test_store_recall_memory_empty_when_disabled(monkeypatch):
    """recall_memory() returns [] when store is disabled."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    from techtide_swarm.persistence import SwarmStore
    store = SwarmStore()
    assert store.recall_memory(query="test", agent_id="agent-001", top_k=5) == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd packages/techtide-swarm
pytest tests/test_server.py::test_store_disabled_without_env tests/test_server.py::test_store_log_run_noop tests/test_server.py::test_store_get_runs_empty_when_disabled tests/test_server.py::test_store_recall_memory_empty_when_disabled -v
```

Expected: FAIL (ModuleNotFoundError on `persistence`)

- [ ] **Step 3: Create persistence.py**

Create `packages/techtide-swarm/src/techtide_swarm/persistence.py`:

```python
"""Supabase persistence layer for Swarm 357.

When SUPABASE_URL and SUPABASE_SERVICE_KEY are set, SwarmStore writes agent
runs, memory entries, dream reports, and config snapshots to Supabase.
All methods are silent no-ops when the client is not configured, so local
contributors without credentials are unaffected.
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class SwarmStore:
    """Dual-write persistence: Supabase when configured, silent no-op otherwise."""

    def __init__(self) -> None:
        self._client: Any = None
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if url and key:
            try:
                from supabase import create_client  # type: ignore[import-untyped]
                self._client = create_client(url, key)
            except ImportError:
                logger.warning(
                    "SUPABASE_URL is set but 'supabase' package is not installed. "
                    "Install with: pip install 'techtide-swarm[supabase]'"
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to create Supabase client: %s", exc)

    @property
    def enabled(self) -> bool:
        """True when a Supabase client is active."""
        return self._client is not None

    # ── Telemetry ─────────────────────────────────────────────────────────────

    def log_run(self, event_type: str, data: dict[str, Any]) -> None:
        """Write an agent_run or swarm_run event to Supabase."""
        if not self._client:
            return
        try:
            if event_type == "agent_run":
                self._client.table("agent_runs").insert({
                    "agent_name": data.get("agent_name", ""),
                    "layer":      data.get("layer", ""),
                    "task":       data.get("task", ""),
                    "output":     data.get("output", ""),
                    "cost_usd":   data.get("cost_usd", 0.0),
                    "latency_ms": data.get("latency_ms", 0),
                    "status":     data.get("status", "success"),
                    "error":      data.get("error"),
                }).execute()
            elif event_type == "swarm_run":
                self._client.table("swarm_runs").insert({
                    "pipeline_id":    data.get("pipeline_id", ""),
                    "task":           data.get("task", ""),
                    "total_cost_usd": data.get("total_cost_usd", 0.0),
                    "agents_used":    data.get("agents_used", []),
                    "latency_ms":     data.get("latency_ms", 0),
                    "status":         data.get("status", "ok"),
                }).execute()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Supabase log_run failed: %s", exc)

    def get_runs(self, limit: int = 10) -> list[dict[str, Any]]:
        """Return recent runs from Supabase (agent_runs + swarm_runs combined)."""
        if not self._client:
            return []
        try:
            rows = (
                self._client.table("agent_runs")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
                .data
            )
            return rows or []
        except Exception as exc:  # noqa: BLE001
            logger.warning("Supabase get_runs failed: %s", exc)
            return []

    def get_total_cost(self) -> float:
        """Sum cost_usd from agent_runs in Supabase."""
        if not self._client:
            return 0.0
        try:
            rows = self._client.table("agent_runs").select("cost_usd").execute().data
            return sum(float(r.get("cost_usd", 0)) for r in (rows or []))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Supabase get_total_cost failed: %s", exc)
            return 0.0

    def get_layer_stats(self) -> dict[str, dict[str, Any]]:
        """Aggregate calls/cost/latency by layer from Supabase agent_runs."""
        if not self._client:
            return {}
        try:
            rows = (
                self._client.table("agent_runs")
                .select("layer,cost_usd,latency_ms")
                .execute()
                .data
            ) or []
            stats: dict[str, dict[str, Any]] = {}
            for row in rows:
                layer = row.get("layer", "unknown")
                if layer not in stats:
                    stats[layer] = {"calls": 0, "cost": 0.0, "latency": 0}
                stats[layer]["calls"] += 1
                stats[layer]["cost"] += float(row.get("cost_usd", 0))
                stats[layer]["latency"] += int(row.get("latency_ms", 0))
            return stats
        except Exception as exc:  # noqa: BLE001
            logger.warning("Supabase get_layer_stats failed: %s", exc)
            return {}

    # ── Memory ────────────────────────────────────────────────────────────────

    def store_memory(self, from_agent: str, to_agent: str, key: str, content: str) -> None:
        """Persist a shared memory entry to Supabase."""
        if not self._client:
            return
        try:
            self._client.table("memory_entries").insert({
                "from_agent": from_agent,
                "to_agent":   to_agent,
                "key":        key,
                "content":    content,
            }).execute()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Supabase store_memory failed: %s", exc)

    def recall_memory(
        self,
        query: str,
        agent_id: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Fetch memory entries whose content contains the query string."""
        if not self._client:
            return []
        try:
            rows = (
                self._client.table("memory_entries")
                .select("key,content,from_agent,to_agent")
                .or_(f"to_agent.eq.{agent_id},from_agent.eq.{agent_id}")
                .ilike("content", f"%{query}%")
                .limit(top_k)
                .execute()
                .data
            ) or []
            return [
                {
                    "key":        r["key"],
                    "content":    r["content"],
                    "confidence": 0.7,
                    "note":       "supabase match",
                }
                for r in rows
            ]
        except Exception as exc:  # noqa: BLE001
            logger.warning("Supabase recall_memory failed: %s", exc)
            return []

    # ── Dream ─────────────────────────────────────────────────────────────────

    def log_dream(self, report: dict[str, Any]) -> None:
        """Persist a dream cycle report to Supabase."""
        if not self._client:
            return
        try:
            self._client.table("dream_reports").insert({"report": report}).execute()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Supabase log_dream failed: %s", exc)

    # ── Config snapshot ───────────────────────────────────────────────────────

    def snapshot_config(self, config: dict[str, Any]) -> None:
        """Append a config snapshot row to Supabase on server startup."""
        if not self._client:
            return
        try:
            self._client.table("swarm_config").insert({"config": config}).execute()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Supabase snapshot_config failed: %s", exc)


# Module-level singleton — created once on import.
store = SwarmStore()

__all__ = ["SwarmStore", "store"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd packages/techtide-swarm
pytest tests/test_server.py::test_store_disabled_without_env tests/test_server.py::test_store_log_run_noop tests/test_server.py::test_store_get_runs_empty_when_disabled tests/test_server.py::test_store_recall_memory_empty_when_disabled -v
```

Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add packages/techtide-swarm/src/techtide_swarm/persistence.py packages/techtide-swarm/tests/test_server.py
git commit -m "feat(persistence): add SwarmStore with Supabase dual-write"
```

---

## Task 4: Update telemetry.py (dual-write)

**Files:**
- Modify: `packages/techtide-swarm/src/techtide_swarm/telemetry.py`

- [ ] **Step 1: Write a failing test**

Add to `packages/techtide-swarm/tests/test_server.py`:

```python
def test_log_telemetry_calls_store(monkeypatch, tmp_path):
    """log_telemetry() calls store.log_run() after writing JSONL."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

    calls: list[tuple[str, dict]] = []

    from techtide_swarm import persistence
    monkeypatch.setattr(persistence.store, "log_run", lambda t, d: calls.append((t, d)))

    import techtide_swarm.telemetry as tel
    monkeypatch.setattr(tel, "TELEMETRY_FILE", tmp_path / "telemetry.jsonl")

    tel.log_telemetry("agent_run", {"agent_name": "test", "cost_usd": 0.01, "latency_ms": 100, "status": "success"})
    assert len(calls) == 1
    assert calls[0][0] == "agent_run"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_server.py::test_log_telemetry_calls_store -v
```

Expected: FAIL (calls list is empty)

- [ ] **Step 3: Update telemetry.py**

Replace the full file content:

```python
"""Telemetry logging for Swarm 357."""

import json
import logging
from pathlib import Path
from typing import Any

from techtide_swarm.persistence import store

logger = logging.getLogger(__name__)

TELEMETRY_FILE = Path(".swarm/telemetry.jsonl")


def log_telemetry(event_type: str, data: dict[str, Any]) -> None:
    """Log a telemetry event to JSONL and (when configured) Supabase."""
    try:
        TELEMETRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        event = {"type": event_type, **data}
        with open(TELEMETRY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.warning("Error logging telemetry to file: %s", e)
    # Dual-write to Supabase — never raises
    store.log_run(event_type, data)


def get_total_cost() -> float:
    """Return total cost from Supabase when available, else from local JSONL."""
    if store.enabled:
        return store.get_total_cost()
    return _local_total_cost()


def get_layer_stats() -> dict[str, dict[str, Any]]:
    """Return per-layer stats from Supabase when available, else from local JSONL."""
    if store.enabled:
        return store.get_layer_stats()
    return _local_layer_stats()


def get_recent_runs(limit: int = 10) -> list[dict[str, Any]]:
    """Return recent runs from Supabase when available, else from local JSONL."""
    if store.enabled:
        return store.get_runs(limit)
    return _local_recent_runs(limit)


# ── Local (file-based) fallbacks ──────────────────────────────────────────────

def _local_total_cost() -> float:
    if not TELEMETRY_FILE.exists():
        return 0.0
    total = 0.0
    try:
        with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") == "agent_run":
                    total += event.get("cost_usd", 0.0)
    except OSError:
        pass
    return total


def _local_layer_stats() -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    if not TELEMETRY_FILE.exists():
        return stats
    try:
        with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") == "agent_run":
                    layer = event.get("layer", "unknown")
                    if layer not in stats:
                        stats[layer] = {"calls": 0, "cost": 0.0, "latency": 0}
                    stats[layer]["calls"] += 1
                    stats[layer]["cost"] += event.get("cost_usd", 0.0)
                    stats[layer]["latency"] += event.get("latency_ms", 0)
    except OSError:
        pass
    return stats


def _local_recent_runs(limit: int = 10) -> list[dict[str, Any]]:
    if not TELEMETRY_FILE.exists():
        return []
    events: list[dict[str, Any]] = []
    try:
        with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") in ("swarm_run", "agent_run"):
                    events.append(event)
    except OSError:
        pass
    return events[-limit:][::-1]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_server.py::test_log_telemetry_calls_store -v
```

Expected: PASS

- [ ] **Step 5: Run full test suite to check for regressions**

```bash
pytest tests/ -v
```

Expected: all existing tests pass

- [ ] **Step 6: Commit**

```bash
git add packages/techtide-swarm/src/techtide_swarm/telemetry.py packages/techtide-swarm/tests/test_server.py
git commit -m "feat(telemetry): dual-write to Supabase via SwarmStore"
```

---

## Task 5: Update memory.py (dual-write)

**Files:**
- Modify: `packages/techtide-swarm/src/techtide_swarm/memory.py`

- [ ] **Step 1: Write failing tests**

Add to `packages/techtide-swarm/tests/test_server.py`:

```python
def test_memory_share_calls_store(monkeypatch, tmp_path):
    """MemoryManager.share() calls store.store_memory()."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

    calls: list[dict] = []

    from techtide_swarm import persistence
    monkeypatch.setattr(
        persistence.store,
        "store_memory",
        lambda from_agent, to_agent, key, content: calls.append(
            {"from_agent": from_agent, "to_agent": to_agent, "key": key, "content": content}
        ),
    )

    from techtide_swarm.memory import MemoryManager
    mm = MemoryManager(swarm_root=tmp_path)
    mm.share(from_agent="a", to_agent="b", key="k1", content="hello")
    assert len(calls) == 1
    assert calls[0]["key"] == "k1"


def test_memory_recall_uses_store_when_enabled(monkeypatch, tmp_path):
    """MemoryManager.recall() merges Supabase results when store is enabled."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

    from techtide_swarm import persistence
    monkeypatch.setattr(persistence.store, "_client", object())  # fake client to enable store
    monkeypatch.setattr(
        persistence.store,
        "recall_memory",
        lambda query, agent_id, top_k: [{"key": "remote", "content": "supabase result", "confidence": 0.7, "note": "supabase match"}],
    )

    from techtide_swarm.memory import MemoryManager
    mm = MemoryManager(swarm_root=tmp_path)
    results = mm.recall("agent-001", "supabase")
    assert any(r["note"] == "supabase match" for r in results)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_server.py::test_memory_share_calls_store tests/test_server.py::test_memory_recall_uses_store_when_enabled -v
```

Expected: FAIL

- [ ] **Step 3: Update memory.py**

Add `from techtide_swarm.persistence import store` after the existing imports, then modify `share()` and `recall()`.

In `share()`, add after `topic_file.write_text(...)` (line 55) and before the `if self._memvid` block:

```python
        store.store_memory(
            from_agent=from_agent,
            to_agent=to_agent,
            key=key,
            content=content,
        )
```

In `recall()`, after building the initial `out` list from `self._shared` and before the `if self._memvid` block, add:

```python
        if store.enabled:
            out.extend(store.recall_memory(query=query, agent_id=agent_id, top_k=5))
```

Full updated `memory.py` (only the changed sections shown — apply as targeted edits):

**Import addition** (after line 10 `from techtide_swarm.memvid_bridge ...`):
```python
from techtide_swarm.persistence import store
```

**`share()` updated body** (replace from `self._shared.append(entry)` through end of method):
```python
        self._shared.append(entry)
        topic_file = self._topics / f"{self._safe_key(key)}.json"
        topic_file.write_text(json.dumps(entry, indent=2), encoding="utf-8")
        store.store_memory(
            from_agent=from_agent,
            to_agent=to_agent,
            key=key,
            content=content,
        )
        if self._memvid and self._memvid.available:
            uri = f"swarm://{key}"
            title = f"{from_agent}->{to_agent}"
            body = f"{content}\n\nmeta: {json.dumps(entry)}".encode("utf-8")
            try:
                self._memvid.put(uri=uri, title=title, body=body)
            except MemvidBridgeError:
                pass
```

**`recall()` updated body** (replace from `out: list[dict[str, Any]] = []` through end of method):
```python
        q = query.lower()
        out: list[dict[str, Any]] = []
        for e in self._shared:
            if e["to"] != agent_id and e["from"] != agent_id:
                continue
            blob = f"{e['key']} {e['content']}".lower()
            if q in blob:
                out.append(
                    {
                        "key": e["key"],
                        "content": e["content"],
                        "confidence": 0.9,
                        "note": "matched shared memory",
                    }
                )
        if store.enabled:
            out.extend(store.recall_memory(query=query, agent_id=agent_id, top_k=5))
        if self._memvid and self._memvid.available:
            try:
                raw = self._memvid.search(query, top_k=5)
                for hit in raw.get("hits", [])[:5]:
                    text = hit.get("text") or hit.get("chunk_text") or ""
                    out.append(
                        {
                            "key": hit.get("uri", "memvid"),
                            "content": text[:2000],
                            "confidence": float(hit.get("score") or 0.5),
                            "note": "memvid search",
                        }
                    )
            except MemvidBridgeError:
                pass
        return out
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_server.py::test_memory_share_calls_store tests/test_server.py::test_memory_recall_uses_store_when_enabled -v
```

Expected: 2 PASS

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add packages/techtide-swarm/src/techtide_swarm/memory.py packages/techtide-swarm/tests/test_server.py
git commit -m "feat(memory): dual-write to Supabase via SwarmStore"
```

---

## Task 6: Update server.py (startup snapshot + dream logging)

**Files:**
- Modify: `packages/techtide-swarm/src/techtide_swarm/server.py`

- [ ] **Step 1: Write failing test**

Add to `packages/techtide-swarm/tests/test_server.py`:

```python
@pytest.mark.asyncio
async def test_dream_endpoint_calls_store_log_dream(monkeypatch):
    """POST /api/swarm/dream calls store.log_dream() with the report."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

    logged: list[dict] = []

    from techtide_swarm import persistence
    monkeypatch.setattr(persistence.store, "log_dream", lambda r: logged.append(r))

    from techtide_swarm.server import create_app
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/swarm/dream")
    assert resp.status_code == 200
    assert len(logged) == 1
    assert "status" in logged[0]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_server.py::test_dream_endpoint_calls_store_log_dream -v
```

Expected: FAIL (logged list is empty)

- [ ] **Step 3: Update server.py**

Three changes:

**A) Add lifespan for startup config snapshot.** Replace the `create_app` signature and add a lifespan:

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator
import yaml  # already available via pyyaml

@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Snapshot current swarm config to Supabase on startup."""
    from techtide_swarm.persistence import store
    cfg_path = _DEFAULT_CONFIG
    if store.enabled and cfg_path.exists():
        try:
            with open(cfg_path, encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
            store.snapshot_config(config_data)
        except Exception as exc:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).warning("Config snapshot failed: %s", exc)
    yield
```

Then pass `lifespan=_lifespan` to `FastAPI(...)` in `create_app()`:

```python
app = FastAPI(
    title="TechTide Swarm 357 API",
    description="357 Claude AI agents organized into 6 business layers",
    version="0.1.0",
    lifespan=_lifespan,
)
```

**B) Update `swarm_dream` endpoint** to call `store.log_dream()`:

```python
    @app.post("/api/swarm/dream")
    async def swarm_dream() -> dict[str, Any]:
        from techtide_swarm.memory import MemoryManager
        from techtide_swarm.persistence import store
        mem = MemoryManager()
        try:
            report = await mem.run_dream_cycle()
            store.log_dream(report)
            return report
        except Exception as exc:
            return {"status": "error", "error": str(exc)}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_server.py::test_dream_endpoint_calls_store_log_dream -v
```

Expected: PASS

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add packages/techtide-swarm/src/techtide_swarm/server.py packages/techtide-swarm/tests/test_server.py
git commit -m "feat(server): snapshot config on startup, log dream reports to Supabase"
```

---

## Task 7: Export SwarmStore from \_\_init\_\_.py

**Files:**
- Modify: `packages/techtide-swarm/src/techtide_swarm/__init__.py`

- [ ] **Step 1: Write failing test**

Add to `packages/techtide-swarm/tests/test_server.py`:

```python
def test_swarm_store_exported():
    """SwarmStore must be importable from the top-level package."""
    from techtide_swarm import SwarmStore
    assert hasattr(SwarmStore, "enabled")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_server.py::test_swarm_store_exported -v
```

Expected: FAIL (ImportError)

- [ ] **Step 3: Update \_\_init\_\_.py**

Replace content with:

```python
"""TechTide Swarm 357 — public API."""

from techtide_swarm.agent import Agent, AgentConfig, AgentResult
from techtide_swarm.bash_gate import BashSecurityGate
from techtide_swarm.memory import MemoryManager
from techtide_swarm.memvid_bridge import MemvidBridge, MemvidBridgeError, resolve_bridge_binary
from techtide_swarm.persistence import SwarmStore
from techtide_swarm.swarm import CostController, Swarm, SwarmExecutionResult
from techtide_swarm.tools.registry import TOOLSET_MAP, ToolRegistry, registry
from techtide_swarm.ultra_plan import UltraPlan, UltraPlanConfig

__all__ = [
    "Agent",
    "AgentConfig",
    "AgentResult",
    "BashSecurityGate",
    "CostController",
    "MemvidBridge",
    "MemvidBridgeError",
    "MemoryManager",
    "Swarm",
    "SwarmExecutionResult",
    "SwarmStore",
    "TOOLSET_MAP",
    "ToolRegistry",
    "UltraPlan",
    "UltraPlanConfig",
    "registry",
    "resolve_bridge_binary",
]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_server.py::test_swarm_store_exported -v
```

Expected: PASS

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add packages/techtide-swarm/src/techtide_swarm/__init__.py packages/techtide-swarm/tests/test_server.py
git commit -m "feat: export SwarmStore from public API"
```

---

## Verification

After all tasks are complete:

```bash
# Full test suite — all must pass
cd packages/techtide-swarm
pytest tests/ -v

# Local mode smoke test (no Supabase)
unset SUPABASE_URL
unset SUPABASE_SERVICE_KEY
uvicorn techtide_swarm.server:app --port 8001 &
curl -s http://localhost:8001/api/health | python3 -m json.tool
curl -s http://localhost:8001/api/swarm/status | python3 -m json.tool
curl -s http://localhost:8001/api/swarm/runs | python3 -m json.tool
# Expect: all return valid JSON, no errors

# Railway / Supabase mode (set real creds)
export SUPABASE_URL=https://xxxx.supabase.co
export SUPABASE_SERVICE_KEY=service_role_key
# Apply migration in Supabase SQL editor: database/migrations/001_initial.sql
# Then start the server and run an agent task:
curl -X POST http://localhost:8001/api/swarm/dream
# Check Supabase dashboard → Table Editor → dream_reports: should have 1 row
```
