# file: packages/techtide-swarm/src/techtide_swarm/tools/terminal.py
# description: Bash tool with explicit argv execution policy and optional HITL
# reference: techtide_swarm.bash_gate, techtide_swarm.runtime.hitl
"""Bash execution tool, gated by BashSecurityGate, execution policy, and HITL.

Registers:
  - Bash  (toolset: core_tools)
"""

from __future__ import annotations

import os
import shlex
import subprocess

from techtide_swarm.bash_gate import BashSecurityGate
from techtide_swarm.runtime.hitl import (
    current_run_id,
    get_approval_gate,
    hitl_bash_enabled,
)
from techtide_swarm.tools.registry import registry


def bash_denied() -> bool:
    """Default-deny Bash in server/production unless explicitly allowed."""
    if os.getenv("SWARM_ALLOW_BASH", "").strip().lower() in {"1", "true", "yes", "on"}:
        return False
    if os.getenv("SWARM_DENY_BASH", "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    env = os.getenv("SWARM_ENV", "").strip().lower()
    if env in {"prod", "production", "server"}:
        return True
    if os.getenv("SWARM_SERVER_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    return False


def allow_shell_true() -> bool:
    """Unsafe local opt-in for shell=True (never default)."""
    return os.getenv("SWARM_ALLOW_UNSAFE_BASH", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def run_bash(command: str, timeout: int = 30) -> str:
    """Execute a command after BashSecurityGate validation and optional HITL."""
    if bash_denied():
        return (
            "BLOCKED by execution policy: Bash is disabled in server/production. "
            "Set SWARM_ALLOW_BASH=1 to enable (still gated)."
        )
    safe, reason = BashSecurityGate.validate(command)
    if not safe:
        return f"BLOCKED by BashSecurityGate: {reason}"

    if hitl_bash_enabled():
        approval_id, decision = get_approval_gate().request_bash_approval(
            command=command,
            run_id=current_run_id(),
        )
        if decision != "approved":
            return (
                f"BLOCKED by HITL: Bash approval {approval_id} "
                f"status={decision}. Use `swarm approve {approval_id}` to allow."
            )

    try:
        if allow_shell_true():
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        else:
            try:
                argv = shlex.split(command, posix=os.name != "nt")
            except ValueError as exc:
                return f"Error: invalid command quoting: {exc}"
            if not argv:
                return "Error: empty command"
            result = subprocess.run(
                argv,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        output = result.stdout or ""
        if result.returncode != 0:
            if result.stderr:
                output += f"\n[stderr] {result.stderr}"
            output += f"\n[exit code: {result.returncode}]"
        output = output.strip()
        return output[:8000] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout} seconds"
    except Exception as exc:
        return f"Error executing command: {exc}"


registry.register(
    name="Bash",
    schema={
        "description": (
            "Execute a shell command. Commands are validated by BashSecurityGate "
            "and an explicit execution policy before execution. Side-effecting "
            "calls may require human approval when HITL is enabled."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default 30).",
                    "default": 30,
                },
            },
            "required": ["command"],
        },
    },
    handler=run_bash,
    toolset="core_tools",
)
