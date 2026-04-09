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

    # ── Telemetry ────────────────────────────────────────────────────────────

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
        """Return recent agent_run rows from Supabase."""
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

    # ── Memory ───────────────────────────────────────────────────────────────

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
            base = (
                self._client.table("memory_entries")
                .select("key,content,from_agent,to_agent")
                .ilike("content", f"%{query}%")
                .limit(top_k)
            )
            to_rows = base.eq("to_agent", agent_id).execute().data or []
            from_rows = base.eq("from_agent", agent_id).execute().data or []
            seen: set[str] = set()
            rows: list[dict[str, Any]] = []
            for r in to_rows + from_rows:
                if r["key"] not in seen:
                    seen.add(r["key"])
                    rows.append(r)
            return [
                {
                    "key":        r["key"],
                    "content":    r["content"],
                    "confidence": 0.7,
                    "note":       "supabase match",
                }
                for r in rows[:top_k]
            ]
        except Exception as exc:  # noqa: BLE001
            logger.warning("Supabase recall_memory failed: %s", exc)
            return []

    # ── Dream ────────────────────────────────────────────────────────────────

    def log_dream(self, report: dict[str, Any]) -> None:
        """Persist a dream cycle report to Supabase."""
        if not self._client:
            return
        try:
            self._client.table("dream_reports").insert({"report": report}).execute()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Supabase log_dream failed: %s", exc)

    # ── Config snapshot ──────────────────────────────────────────────────────

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
