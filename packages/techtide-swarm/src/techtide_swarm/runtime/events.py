# file: packages/techtide-swarm/src/techtide_swarm/runtime/events.py
# description: Typed run/step/tool/cost event bus with bounded buffering for SSE
# reference: techtide_swarm.server, techtide_swarm.swarm
"""In-process event bus for streaming swarm execution."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator


class EventType(str, Enum):
    RUN_STARTED = "run.started"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    RUN_CANCELLED = "run.cancelled"
    STEP_STARTED = "step.started"
    STEP_COMPLETED = "step.completed"
    STEP_FAILED = "step.failed"
    TOOL_CALL = "tool.call"
    TOOL_RESULT = "tool.result"
    COST = "cost.update"
    APPROVAL_REQUIRED = "approval.required"
    APPROVAL_RESOLVED = "approval.resolved"
    CHECKPOINT = "checkpoint.saved"
    LOG = "log"


@dataclass
class SwarmEvent:
    type: EventType
    run_id: str
    data: dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)

    def to_sse(self) -> str:
        payload = {
            "type": self.type.value,
            "run_id": self.run_id,
            "ts": self.ts,
            "data": self.data,
        }
        import json

        return f"event: {self.type.value}\ndata: {json.dumps(payload, default=str)}\n\n"


class EventBus:
    """Per-run fan-out with bounded buffer; drop-oldest under pressure."""

    def __init__(self, max_buffer: int = 256) -> None:
        self._max_buffer = max_buffer
        self._queues: dict[str, list[asyncio.Queue[SwarmEvent | None]]] = defaultdict(list)
        self._history: dict[str, deque[SwarmEvent]] = defaultdict(
            lambda: deque(maxlen=max_buffer)
        )
        self._lock = asyncio.Lock()

    async def publish(self, event: SwarmEvent) -> None:
        async with self._lock:
            self._history[event.run_id].append(event)
            dead: list[asyncio.Queue[SwarmEvent | None]] = []
            for q in self._queues.get(event.run_id, []):
                try:
                    q.put_nowait(event)
                except asyncio.QueueFull:
                    try:
                        q.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    try:
                        q.put_nowait(event)
                    except asyncio.QueueFull:
                        dead.append(q)
            for q in dead:
                if q in self._queues[event.run_id]:
                    self._queues[event.run_id].remove(q)

    async def subscribe(self, run_id: str) -> AsyncIterator[SwarmEvent]:
        q: asyncio.Queue[SwarmEvent | None] = asyncio.Queue(maxsize=self._max_buffer)
        async with self._lock:
            for past in self._history.get(run_id, []):
                try:
                    q.put_nowait(past)
                except asyncio.QueueFull:
                    break
            self._queues[run_id].append(q)
        try:
            while True:
                item = await q.get()
                if item is None:
                    break
                yield item
        finally:
            async with self._lock:
                if q in self._queues.get(run_id, []):
                    self._queues[run_id].remove(q)

    async def close(self, run_id: str) -> None:
        async with self._lock:
            for q in self._queues.get(run_id, []):
                try:
                    q.put_nowait(None)
                except asyncio.QueueFull:
                    pass
            self._queues.pop(run_id, None)


_GLOBAL_BUS: EventBus | None = None


def get_event_bus() -> EventBus:
    global _GLOBAL_BUS
    if _GLOBAL_BUS is None:
        _GLOBAL_BUS = EventBus()
    return _GLOBAL_BUS
