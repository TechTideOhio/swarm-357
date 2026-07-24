"""Deep planning session (ULTRAPLAN) — uses Claude when API key present."""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

from pydantic import BaseModel, Field


class UltraPlanConfig(BaseModel):
    """Planner configuration."""

    max_duration_minutes: int = 15
    model: str = "opus"
    max_budget_usd: float = 5.0
    extra: dict[str, Any] = Field(default_factory=dict)


class UltraPlan:
    """Strategic planning with Claude."""

    def __init__(self, config: UltraPlanConfig) -> None:
        self.config = config

    async def plan(self, task: str) -> dict[str, Any]:
        """Return a plan dict; live API when key set."""
        plan_id = str(uuid.uuid4())
        started = time.perf_counter()
        from techtide_swarm.llm import create_async_client, model_id, resolve_api_key

        api_key = resolve_api_key()
        if not api_key:
            body = (
                f"[stub ULTRAPLAN]\n\nObjective:\n{task}\n\n"
                "Phases: (1) Discovery (2) Design (3) Rollout. "
                "Set OPENROUTER_API_KEY or ANTHROPIC_API_KEY for full planning."
            )
        else:
            client = create_async_client()
            model = model_id(self.config.model or "opus")
            message = await client.messages.create(
                model=model,
                max_tokens=8192,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Produce a structured strategic plan with headings and numbered steps.\n\n"
                            f"{task}"
                        ),
                    }
                ],
            )
            body = ""
            for block in getattr(message, "content", []) or []:
                if getattr(block, "type", None) == "text":
                    body += getattr(block, "text", "")
        duration = time.perf_counter() - started
        return {
            "plan_id": plan_id,
            "duration_seconds": duration,
            "plan": body,
        }
