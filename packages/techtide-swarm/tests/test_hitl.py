# file: packages/techtide-swarm/tests/test_hitl.py
# description: Bash HITL gate — approve, reject, timeout, and tool integration
# reference: techtide_swarm.runtime.hitl, techtide_swarm.tools.terminal

from __future__ import annotations

import threading
import time

import pytest

from techtide_swarm.runtime.checkpoint import MemoryCheckpointStore, set_default_store
from techtide_swarm.runtime.hitl import ApprovalGate, get_approval_gate
from techtide_swarm.runtime.state import RunState, RunStatus
from techtide_swarm.tools import terminal as terminal_mod


@pytest.fixture()
def gate(monkeypatch: pytest.MonkeyPatch) -> ApprovalGate:
    store = MemoryCheckpointStore()
    set_default_store(store)
    g = ApprovalGate()
    monkeypatch.setattr("techtide_swarm.runtime.hitl._GATE", g)
    monkeypatch.setenv("SWARM_HITL_BASH", "1")
    monkeypatch.setenv("SWARM_ALLOW_BASH", "1")
    monkeypatch.delenv("SWARM_DENY_BASH", raising=False)
    monkeypatch.delenv("SWARM_ENV", raising=False)
    monkeypatch.delenv("SWARM_SERVER_MODE", raising=False)
    return g


def test_hitl_approve_resumes_bash(gate: ApprovalGate, monkeypatch: pytest.MonkeyPatch) -> None:
    store = MemoryCheckpointStore()
    set_default_store(store)
    state = RunState(task="t", status=RunStatus.RUNNING)
    store.save(state)
    monkeypatch.setenv("SWARM_CURRENT_RUN_ID", state.run_id)
    monkeypatch.setenv("SWARM_HITL_TIMEOUT_SEC", "5")

    result_box: list[str] = []

    cmd = 'python -c "print(\'hitl-ok\')"'

    def waiter() -> None:
        result_box.append(terminal_mod.run_bash(cmd))

    t = threading.Thread(target=waiter, daemon=True)
    t.start()
    deadline = time.time() + 3
    approval_id = None
    while time.time() < deadline and approval_id is None:
        loaded = store.load(state.run_id)
        if loaded and loaded.approvals:
            approval_id = loaded.approvals[0].approval_id
            break
        time.sleep(0.05)
    assert approval_id is not None
    assert gate.resolve(approval_id, status="approved", decided_by="test") is True
    t.join(timeout=5)
    assert result_box
    # Approve path must leave HITL; command output may vary by shell/platform.
    assert "BLOCKED by HITL" not in result_box[0]
    assert "rejected" not in result_box[0].lower()
    assert "timeout" not in result_box[0].lower()


def test_hitl_reject_blocks_bash(gate: ApprovalGate, monkeypatch: pytest.MonkeyPatch) -> None:
    store = MemoryCheckpointStore()
    set_default_store(store)
    state = RunState(task="t", status=RunStatus.RUNNING)
    store.save(state)
    monkeypatch.setenv("SWARM_CURRENT_RUN_ID", state.run_id)
    monkeypatch.setenv("SWARM_HITL_TIMEOUT_SEC", "5")

    result_box: list[str] = []

    def waiter() -> None:
        result_box.append(terminal_mod.run_bash('python -c "print(1)"'))

    t = threading.Thread(target=waiter, daemon=True)
    t.start()
    deadline = time.time() + 3
    approval_id = None
    while time.time() < deadline and approval_id is None:
        loaded = store.load(state.run_id)
        if loaded and loaded.approvals:
            approval_id = loaded.approvals[0].approval_id
            break
        time.sleep(0.05)
    assert approval_id is not None
    assert gate.resolve(approval_id, status="rejected", decided_by="test") is True
    t.join(timeout=5)
    assert result_box
    assert "BLOCKED by HITL" in result_box[0]
    assert "rejected" in result_box[0]


def test_hitl_timeout_rejects(gate: ApprovalGate, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWARM_HITL_TIMEOUT_SEC", "0.2")
    store = MemoryCheckpointStore()
    set_default_store(store)
    state = RunState(task="t", status=RunStatus.RUNNING)
    store.save(state)

    approval_id, decision = gate.request_bash_approval(
        command="echo x",
        run_id=state.run_id,
        store=store,
    )
    assert decision == "timeout"
    assert approval_id
    loaded = store.load(state.run_id)
    assert loaded is not None
    assert loaded.approvals[0].status == "rejected"


def test_get_approval_gate_singleton() -> None:
    a = get_approval_gate()
    b = get_approval_gate()
    assert a is b
