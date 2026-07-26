# file: packages/techtide-swarm/src/techtide_swarm/runtime/checkpoint.py
# description: Local-first SQLite checkpoint store for durable run/step state
# reference: techtide_swarm.runtime.state, techtide_swarm.swarm
"""SQLite checkpoint persistence with a narrow protocol for adapters."""

from __future__ import annotations

import os
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from techtide_swarm.runtime.state import RunState


class CheckpointStore(ABC):
    """Persistence protocol for run checkpoints."""

    @abstractmethod
    def save(self, state: RunState) -> None: ...

    @abstractmethod
    def load(self, run_id: str) -> RunState | None: ...

    @abstractmethod
    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]: ...

    @abstractmethod
    def delete(self, run_id: str) -> None: ...


class SqliteCheckpointStore(CheckpointStore):
    """Append-friendly SQLite store under .swarm/checkpoints.db by default."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            root = Path(os.getenv("SWARM_CHECKPOINT_DIR", ".swarm"))
            db_path = root / "checkpoints.db"
        self.db_path = Path(db_path)
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Non-writable CWD (e.g. Docker USER without /app write) — fall back to /tmp
            fallback = Path(os.getenv("TMPDIR", "/tmp")) / "swarm357" / "checkpoints.db"
            fallback.parent.mkdir(parents=True, exist_ok=True)
            self.db_path = fallback
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    task TEXT NOT NULL,
                    spent_usd REAL NOT NULL DEFAULT 0,
                    budget_usd REAL NOT NULL DEFAULT 25,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_updated ON runs(updated_at DESC)"
            )
            conn.commit()

    def save(self, state: RunState) -> None:
        state.touch()
        payload = state.model_dump_json()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runs (run_id, status, task, spent_usd, budget_usd, updated_at, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status=excluded.status,
                    task=excluded.task,
                    spent_usd=excluded.spent_usd,
                    budget_usd=excluded.budget_usd,
                    updated_at=excluded.updated_at,
                    payload=excluded.payload
                """,
                (
                    state.run_id,
                    state.status.value,
                    state.task,
                    state.spent_usd,
                    state.budget_usd,
                    state.updated_at.isoformat(),
                    payload,
                ),
            )
            conn.commit()

    def load(self, run_id: str) -> RunState | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        if row is None:
            return None
        return RunState.model_validate_json(row["payload"])

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT run_id, status, task, spent_usd, budget_usd, updated_at
                FROM runs ORDER BY updated_at DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def delete(self, run_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM runs WHERE run_id = ?", (run_id,))
            conn.commit()


class MemoryCheckpointStore(CheckpointStore):
    """In-memory store for tests."""

    def __init__(self) -> None:
        self._runs: dict[str, RunState] = {}

    def save(self, state: RunState) -> None:
        state.touch()
        self._runs[state.run_id] = state.model_copy(deep=True)

    def load(self, run_id: str) -> RunState | None:
        state = self._runs.get(run_id)
        return state.model_copy(deep=True) if state else None

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        items = sorted(
            self._runs.values(), key=lambda s: s.updated_at.isoformat(), reverse=True
        )[:limit]
        return [
            {
                "run_id": s.run_id,
                "status": s.status.value,
                "task": s.task,
                "spent_usd": s.spent_usd,
                "budget_usd": s.budget_usd,
                "updated_at": s.updated_at.isoformat(),
            }
            for s in items
        ]

    def delete(self, run_id: str) -> None:
        self._runs.pop(run_id, None)


_PROCESS_STORE: CheckpointStore | None = None


def default_checkpoint_store() -> CheckpointStore:
    """Factory: SQLite by default; memory when SWARM_CHECKPOINT_BACKEND=memory."""
    backend = os.getenv("SWARM_CHECKPOINT_BACKEND", "sqlite").strip().lower()
    if backend == "memory":
        return MemoryCheckpointStore()
    return SqliteCheckpointStore()


def get_default_store() -> CheckpointStore:
    """Process-wide store shared by Swarm, HITL, and tools."""
    global _PROCESS_STORE
    if _PROCESS_STORE is None:
        _PROCESS_STORE = default_checkpoint_store()
    return _PROCESS_STORE


def set_default_store(store: CheckpointStore) -> None:
    """Bind the process-wide store (called from Swarm.checkpoint)."""
    global _PROCESS_STORE
    _PROCESS_STORE = store
