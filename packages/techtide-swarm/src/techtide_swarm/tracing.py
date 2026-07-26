# file: packages/techtide-swarm/src/techtide_swarm/tracing.py
# description: Structured traces (local JSONL truth) with optional OpenTelemetry export
# reference: techtide_swarm.telemetry, techtide_swarm.swarm
"""Structured tracing for routing, model/tool calls, checkpoints, and cost."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any

from techtide_swarm.telemetry import redact_secrets

_logger = logging.getLogger(__name__)
TRACE_FILE = Path(os.getenv("SWARM_TRACE_FILE", ".swarm/traces.jsonl"))


def _otel_enabled() -> bool:
    return os.getenv("SWARM_OTEL_EXPORT", "").strip().lower() in {"1", "true", "yes", "on"}


def start_span(name: str, *, attributes: dict[str, Any] | None = None) -> dict[str, Any]:
    """Start a local span dict (and optional OTel span)."""
    span: dict[str, Any] = {
        "span_id": str(uuid.uuid4()),
        "name": name,
        "start_ns": time.time_ns(),
        "attributes": redact_secrets(attributes or {}),
    }
    if _otel_enabled():
        try:
            import importlib

            otel_trace = importlib.import_module("opentelemetry.trace")
            tracer = otel_trace.get_tracer("techtide_swarm")
            otel_span = tracer.start_span(name)
            for k, v in (attributes or {}).items():
                if isinstance(v, (str, int, float, bool)):
                    otel_span.set_attribute(k, v)
            span["_otel"] = otel_span
        except Exception as exc:  # noqa: BLE001
            _logger.debug("OTel span start skipped: %s", exc)
    return span


def end_span(span: dict[str, Any], *, status: str = "ok", attributes: dict[str, Any] | None = None) -> None:
    """End span and append to local JSONL truth."""
    span = dict(span)
    otel = span.pop("_otel", None)
    span["end_ns"] = time.time_ns()
    span["duration_ms"] = int((span["end_ns"] - span["start_ns"]) / 1_000_000)
    span["status"] = status
    if attributes:
        span.setdefault("attributes", {}).update(redact_secrets(attributes))
    try:
        TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(redact_secrets(span), default=str) + "\n")
    except OSError as exc:
        _logger.warning("trace write failed: %s", exc)
    if otel is not None:
        try:
            otel.end()
        except Exception as exc:  # noqa: BLE001
            _logger.debug("OTel span end skipped: %s", exc)


def emit_event(name: str, data: dict[str, Any]) -> None:
    """Emit a point-in-time trace event."""
    end_span(start_span(name, attributes=data), status="ok")
