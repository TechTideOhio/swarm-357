# file: packages/techtide-swarm/src/techtide_swarm/runtime/hitl.py
# description: Bash HITL approval gate with durable records and sync wait
# reference: techtide_swarm.tools.terminal, techtide_swarm.runtime.state
"""Human-in-the-loop approvals for side-effecting Bash tool calls."""

from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timezone
from techtide_swarm.runtime.checkpoint import CheckpointStore, get_default_store
from techtide_swarm.runtime.state import ApprovalRecord, RunStatus


def hitl_bash_enabled() -> bool:
    """HITL for Bash: default on in server/production; opt-in/out via env."""
    flag = os.getenv("SWARM_HITL_BASH", "").strip().lower()
    if flag in {"0", "false", "no", "off"}:
        return False
    if flag in {"1", "true", "yes", "on"}:
        return True
    env = os.getenv("SWARM_ENV", "").strip().lower()
    if env in {"prod", "production", "server"}:
        return True
    if os.getenv("SWARM_SERVER_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    return False


def hitl_timeout_sec() -> float:
    raw = os.getenv("SWARM_HITL_TIMEOUT_SEC", "300").strip()
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 300.0


class ApprovalGate:
    """In-process waiters keyed by approval_id; decisions persist to checkpoints."""

    def __init__(self) -> None:
        self._events: dict[str, threading.Event] = {}
        self._decisions: dict[str, str] = {}
        self._lock = threading.Lock()
        self._run_bindings: dict[str, str] = {}  # approval_id -> run_id

    def request_bash_approval(
        self,
        *,
        command: str,
        run_id: str | None = None,
        step_id: str | None = None,
        store: CheckpointStore | None = None,
    ) -> tuple[str, str]:
        """Create pending approval and block until resolved.

        Returns (approval_id, decision) where decision is approved|rejected|timeout.
        """
        record = ApprovalRecord(
            run_id=run_id or "local",
            step_id=step_id or "bash",
            tool_name="Bash",
            tool_input={"command": command},
            status="pending",
        )
        event = threading.Event()
        with self._lock:
            self._events[record.approval_id] = event
            self._run_bindings[record.approval_id] = record.run_id

        ckpt = store or get_default_store()
        if run_id:
            state = ckpt.load(run_id)
            if state is not None:
                state.approvals.append(record)
                state.status = RunStatus.WAITING_APPROVAL
                state.touch()
                ckpt.save(state)

        timed_out = not event.wait(timeout=hitl_timeout_sec())
        with self._lock:
            decision = self._decisions.pop(record.approval_id, None)
            self._events.pop(record.approval_id, None)
            self._run_bindings.pop(record.approval_id, None)

        if timed_out and decision is None:
            decision = "timeout"
            self._persist_decision(
                record.approval_id,
                "rejected",
                decided_by="system",
                reason="HITL timeout",
                store=ckpt,
                run_id=run_id,
            )
        return record.approval_id, decision or "rejected"

    def resolve(
        self,
        approval_id: str,
        *,
        status: str,
        decided_by: str = "",
        reason: str = "",
        store: CheckpointStore | None = None,
    ) -> bool:
        """Approve or reject a pending approval. Returns False if unknown/already resolved."""
        if status not in {"approved", "rejected"}:
            raise ValueError(f"Invalid approval status: {status}")
        with self._lock:
            event = self._events.get(approval_id)
            if event is None:
                # Still try checkpoint-only update for API callers
                pass
            else:
                self._decisions[approval_id] = status
        self._persist_decision(
            approval_id,
            status,
            decided_by=decided_by,
            reason=reason,
            store=store or get_default_store(),
            run_id=self._run_bindings.get(approval_id),
        )
        if event is not None:
            event.set()
            return True
        # Checkpoint-only resolution (waiter may be in another process — still record)
        return self._checkpoint_has_approval(approval_id, store or get_default_store())

    def _checkpoint_has_approval(
        self, approval_id: str, store: CheckpointStore
    ) -> bool:
        for item in store.list_runs(limit=200):
            state = store.load(str(item.get("run_id", "")))
            if state is None:
                continue
            for appr in state.approvals:
                if appr.approval_id == approval_id:
                    return True
        return False

    def _persist_decision(
        self,
        approval_id: str,
        status: str,
        *,
        decided_by: str,
        reason: str,
        store: CheckpointStore,
        run_id: str | None,
    ) -> None:
        candidates: list[str] = []
        if run_id and run_id != "local":
            candidates.append(run_id)
        else:
            for item in store.list_runs(limit=100):
                rid = str(item.get("run_id", ""))
                if rid:
                    candidates.append(rid)
        now = datetime.now(timezone.utc)
        for rid in candidates:
            state = store.load(rid)
            if state is None:
                continue
            for appr in state.approvals:
                if appr.approval_id != approval_id:
                    continue
                appr.status = status
                appr.decided_by = decided_by
                appr.reason = reason
                appr.decided_at = now
                if state.status == RunStatus.WAITING_APPROVAL:
                    state.status = RunStatus.RUNNING
                state.touch()
                store.save(state)
                return


_GATE: ApprovalGate | None = None


def get_approval_gate() -> ApprovalGate:
    global _GATE
    if _GATE is None:
        _GATE = ApprovalGate()
    return _GATE


def current_run_id() -> str | None:
    return os.getenv("SWARM_CURRENT_RUN_ID", "").strip() or None


def set_current_run_id(run_id: str | None) -> None:
    if run_id:
        os.environ["SWARM_CURRENT_RUN_ID"] = run_id
    else:
        os.environ.pop("SWARM_CURRENT_RUN_ID", None)
