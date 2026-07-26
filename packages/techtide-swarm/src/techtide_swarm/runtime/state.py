# file: packages/techtide-swarm/src/techtide_swarm/runtime/state.py
# description: Typed run/step state models with stable UUID identifiers
# reference: techtide_swarm.runtime.checkpoint, techtide_swarm.swarm
"""Explicit run and step state for durable swarm execution."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid.uuid4())


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SIMULATED = "simulated"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class StepState(BaseModel):
    step_id: str = Field(default_factory=new_id)
    run_id: str
    index: int = 0
    role: str = ""
    agent_name: str = ""
    layer: str = ""
    status: StepStatus = StepStatus.PENDING
    input_text: str = ""
    output_text: str = ""
    error: str | None = None
    cost_usd: float = 0.0
    latency_ms: int = 0
    model_resolved: str = ""
    idempotency_key: str = ""
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = _utc_now()


class ApprovalRecord(BaseModel):
    approval_id: str = Field(default_factory=new_id)
    run_id: str
    step_id: str
    tool_name: str
    tool_input: dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"  # pending | approved | rejected | edited
    edited_input: dict[str, Any] | None = None
    decided_by: str = ""
    reason: str = ""
    created_at: datetime = Field(default_factory=_utc_now)
    decided_at: datetime | None = None


class RunState(BaseModel):
    run_id: str = Field(default_factory=new_id)
    task: str
    status: RunStatus = RunStatus.PENDING
    budget_usd: float = 25.0
    spent_usd: float = 0.0
    layer: str | None = None
    simulate: bool = False
    parent_run_id: str | None = None
    roles: list[str] = Field(default_factory=list)
    steps: list[StepState] = Field(default_factory=list)
    approvals: list[ApprovalRecord] = Field(default_factory=list)
    final_output: str = ""
    error: str | None = None
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = _utc_now()

    def add_step(self, step: StepState) -> StepState:
        step.run_id = self.run_id
        step.index = len(self.steps)
        if not step.idempotency_key:
            step.idempotency_key = f"{self.run_id}:{step.index}:{step.role}:{step.agent_name}"
        self.steps.append(step)
        self.touch()
        return step
