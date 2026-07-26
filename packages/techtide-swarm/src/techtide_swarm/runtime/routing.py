# file: packages/techtide-swarm/src/techtide_swarm/runtime/routing.py
# description: Validated structured conductor routing (no silent comma-parse fallbacks)
# reference: techtide_swarm.swarm, techtide_swarm.runtime.state
"""Structured routing decisions from the Conductor."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator


class RoutingDecision(BaseModel):
    """Validated role sequence selected by the Conductor."""

    roles: list[str] = Field(min_length=1, max_length=8)
    rationale: str = ""

    @field_validator("roles")
    @classmethod
    def _normalize_roles(cls, roles: list[str]) -> list[str]:
        cleaned = [r.strip() for r in roles if isinstance(r, str) and r.strip()]
        if not cleaned:
            raise ValueError("roles must be a non-empty list")
        return cleaned


class RoutingError(ValueError):
    """Raised when conductor output cannot be validated against available roles."""


_JSON_BLOCK = re.compile(r"\{[\s\S]*\}")


def parse_routing_decision(raw: str, available_roles: set[str]) -> RoutingDecision:
    """Parse conductor output as JSON RoutingDecision; filter to known roles.

    Raises RoutingError on invalid structure or empty intersection with roster.
    """
    text = (raw or "").strip()
    if not text:
        raise RoutingError("empty conductor routing output")

    payload: dict[str, Any] | None = None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = _JSON_BLOCK.search(text)
        if match:
            try:
                payload = json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise RoutingError(f"invalid routing JSON: {exc}") from exc
        else:
            # Legacy comma list — accept only if every token is a known role
            tokens = [t.strip() for t in text.replace("\n", ",").split(",") if t.strip()]
            if tokens and all(t in available_roles for t in tokens):
                payload = {"roles": tokens, "rationale": "legacy_csv"}
            else:
                raise RoutingError(
                    "conductor must return JSON {\"roles\": [...]} with known roles"
                )

    if not isinstance(payload, dict):
        raise RoutingError("routing payload must be a JSON object")

    try:
        decision = RoutingDecision.model_validate(payload)
    except ValidationError as exc:
        raise RoutingError(str(exc)) from exc

    filtered = [r for r in decision.roles if r in available_roles]
    if not filtered:
        raise RoutingError(
            f"no known roles in decision {decision.roles!r}; "
            f"available={sorted(available_roles)[:40]}"
        )
    return RoutingDecision(roles=filtered, rationale=decision.rationale)


def routing_prompt(task: str, available_roles: list[str]) -> str:
    """Prompt that requires strict JSON routing output."""
    roles = ", ".join(sorted(available_roles))
    return (
        "You are the Conductor. Select agent roles needed for the task.\n"
        f"Available roles: {roles}\n\n"
        f"Task: {task}\n\n"
        "Return ONLY valid JSON (no markdown) with this shape:\n"
        '{"roles": ["role_a", "role_b"], "rationale": "one sentence"}\n'
        "Pick 2-5 roles that exist in Available roles."
    )
