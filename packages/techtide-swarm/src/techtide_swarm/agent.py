"""Single-agent runner."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from techtide_swarm.core.types import LayerType


class AgentConfig(BaseModel):
    """Configuration for one agent."""

    name: str
    layer: LayerType
    role: str
    soul: str = ""
    tools: list[str] = Field(default_factory=list)
    model: str = "sonnet"
    budget_limit_usd: float = 1.0
    max_turns: int = 10


@dataclass
class AgentResult:
    """Outcome of agent.run."""

    output: str
    cost_usd: float
    latency_ms: int
    status: str
    agent_name: str = ""
    error: str | None = None


class Agent:
    """One Claude-powered agent."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config

    def _load_system_prompt(self) -> str | None:
        """Read the SOUL.md template and return the system prompt body (after YAML front-matter)."""
        soul_path = self.config.soul
        if not soul_path:
            return None
        from techtide_swarm.paths import resolve_soul_path

        path = resolve_soul_path(soul_path)
        if path is None:
            return None
        text = path.read_text(encoding="utf-8")
        # Strip YAML front-matter delimited by ---
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return text.strip()

    async def run(self, task: str) -> AgentResult:
        """Execute task via Anthropic Messages API when API key is set; else deterministic stub."""
        from techtide_swarm.llm import create_async_client, model_id as resolve_model_id, resolve_api_key

        api_key = resolve_api_key()
        if not api_key:
            return self._stub_result(task)

        started = time.perf_counter()
        total_cost = 0.0
        try:
            from techtide_swarm.tools import get_anthropic_tools, execute_tool

            client = create_async_client()
            resolved_model = resolve_model_id(self.config.model)
            system_prompt = self._load_system_prompt()

            messages: list[dict[str, Any]] = [{"role": "user", "content": task}]
            # Eval harness can disable tools when explicitly requested.
            tool_names = (
                []
                if os.getenv("SWARM_EVAL_DISABLE_TOOLS", "").lower() in ("1", "true", "yes")
                else list(self.config.tools)
            )
            tools = get_anthropic_tools(tool_names)

            final_text = ""
            budget = self.config.budget_limit_usd

            for turn in range(self.config.max_turns):
                if total_cost >= budget:
                    final_text = f"Budget limit reached (${budget:.2f}). Stopping."
                    break

                create_kwargs: dict[str, Any] = {
                    "model": resolved_model,
                    "max_tokens": 4096,
                    "messages": messages,
                }
                if system_prompt:
                    create_kwargs["system"] = system_prompt
                if tools:
                    create_kwargs["tools"] = tools

                message = await client.messages.create(**create_kwargs)
                total_cost += self._estimate_cost(message, resolved_model)

                # Serialize to plain dicts — OpenRouter rejects raw SDK block objects
                # on subsequent turns (especially thinking / tool_use blocks).
                assistant_content = self._serialize_content_blocks(message.content)
                if assistant_content:
                    messages.append({"role": "assistant", "content": assistant_content})

                if total_cost >= budget:
                    final_text = self._extract_text(message) or (
                        f"Budget limit reached (${budget:.2f}). Stopping."
                    )
                    break

                tool_uses = [
                    block
                    for block in (message.content or [])
                    if getattr(block, "type", None) == "tool_use"
                ]

                if not tool_uses:
                    final_text = self._extract_text(message)
                    break

                tool_results: list[dict[str, Any]] = []
                for tool_use in tool_uses:
                    name = getattr(tool_use, "name", "") or ""
                    raw_input = getattr(tool_use, "input", None)
                    tool_input: dict[str, Any] = raw_input if isinstance(raw_input, dict) else {}
                    result_text = execute_tool(name, tool_input)
                    is_err = result_text.strip().startswith('{"error"') or result_text.startswith(
                        "Error:"
                    )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": getattr(tool_use, "id", ""),
                            "content": result_text,
                            "is_error": is_err,
                        }
                    )

                messages.append({"role": "user", "content": tool_results})
            else:
                final_text = final_text or "Max turns reached without completion."

            # Prefer last extracted text if tool loop ended without a text turn
            if not final_text.strip():
                final_text = "Completed with tool calls but no final text response."

            elapsed_ms = int((time.perf_counter() - started) * 1000)

            from techtide_swarm.telemetry import log_telemetry

            log_telemetry(
                "agent_run",
                {
                    "agent_name": self.config.name,
                    "layer": self.config.layer.value,
                    "cost_usd": total_cost,
                    "latency_ms": elapsed_ms,
                    "status": "success",
                },
            )

            return AgentResult(
                agent_name=self.config.name,
                output=final_text,
                cost_usd=total_cost,
                latency_ms=elapsed_ms,
                status="success",
            )
        except Exception as exc:  # noqa: BLE001 — surface to CLI
            elapsed_ms = int((time.perf_counter() - started) * 1000)

            from techtide_swarm.telemetry import log_telemetry

            log_telemetry(
                "agent_run",
                {
                    "agent_name": self.config.name,
                    "layer": self.config.layer.value,
                    "cost_usd": total_cost,
                    "latency_ms": elapsed_ms,
                    "status": "error",
                    "error": str(exc),
                },
            )

            return AgentResult(
                agent_name=self.config.name,
                output="",
                cost_usd=total_cost,
                latency_ms=elapsed_ms,
                status="error",
                error=str(exc),
            )

    def _stub_result(self, task: str) -> AgentResult:
        preview = task[:200].replace("\n", " ")
        return AgentResult(
            agent_name=self.config.name,
            output=(
                f"[stub] Agent {self.config.name} ({self.config.layer.value}) would process:\n"
                f"{preview}"
            ),
            cost_usd=0.0,
            latency_ms=0,
            status="success",
        )

    @staticmethod
    def _model_id(short: str) -> str:
        from techtide_swarm.llm import model_id as resolve_model_id

        return resolve_model_id(short)

    @staticmethod
    def _serialize_content_blocks(content: Any) -> list[dict[str, Any]]:
        """Convert SDK content blocks into JSON-safe Anthropic message dicts."""
        if content is None:
            return []
        if isinstance(content, str):
            return [{"type": "text", "text": content}] if content else []

        serialized: list[dict[str, Any]] = []
        for block in content:
            btype = getattr(block, "type", None)
            if btype == "text":
                text = getattr(block, "text", "") or ""
                if text:
                    serialized.append({"type": "text", "text": text})
            elif btype == "tool_use":
                raw_input = getattr(block, "input", None) or {}
                if hasattr(raw_input, "model_dump"):
                    try:
                        raw_input = raw_input.model_dump()
                    except Exception:
                        raw_input = dict(raw_input) if raw_input else {}
                elif not isinstance(raw_input, dict):
                    try:
                        raw_input = dict(raw_input)
                    except Exception:
                        raw_input = {}
                serialized.append(
                    {
                        "type": "tool_use",
                        "id": getattr(block, "id", ""),
                        "name": getattr(block, "name", ""),
                        "input": raw_input,
                    }
                )
            # Skip thinking / redacted_thinking — replaying them breaks OpenRouter turns
            elif btype in ("thinking", "redacted_thinking"):
                continue
            elif isinstance(block, dict):
                if block.get("type") in ("thinking", "redacted_thinking"):
                    continue
                serialized.append(block)
        return serialized

    @staticmethod
    def _extract_text(message: Any) -> str:
        parts: list[str] = []
        for block in getattr(message, "content", []) or []:
            btype = getattr(block, "type", None)
            if btype == "text":
                parts.append(getattr(block, "text", ""))
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "\n".join(parts) if parts else ""

    @staticmethod
    def _estimate_cost(message: Any, model_id: str) -> float:
        usage = getattr(message, "usage", None)
        if usage is None:
            return 0.01
        # Prefer provider-reported cost (OpenRouter attaches usage.cost)
        reported = getattr(usage, "cost", None)
        if reported is not None:
            try:
                return max(0.0, float(reported))
            except (TypeError, ValueError):
                pass
        inp = float(getattr(usage, "input_tokens", 0) or 0)
        out = float(getattr(usage, "output_tokens", 0) or 0)
        # Approximate list pricing snapshot (Claude 4.x, 2026) — override with real billing later
        lower = model_id.lower()
        if "opus" in lower:
            rate_in, rate_out = 15.0 / 1e6, 75.0 / 1e6
        elif "haiku" in lower:
            rate_in, rate_out = 0.80 / 1e6, 4.0 / 1e6
        else:  # sonnet
            rate_in, rate_out = 3.0 / 1e6, 15.0 / 1e6
        return inp * rate_in + out * rate_out
