"""Bash execution tool, gated by BashSecurityGate.

Registers:
  - Bash  (toolset: core_tools)
"""

from __future__ import annotations

import subprocess

from techtide_swarm.bash_gate import BashSecurityGate
from techtide_swarm.tools.registry import registry


def run_bash(command: str, timeout: int = 30) -> str:
    """Execute a shell command after BashSecurityGate validation.

    Returns stdout (and stderr on non-zero exit).  Output is capped at
    8 000 characters so it stays comfortably inside a Claude context window.
    """
    safe, reason = BashSecurityGate.validate(command)
    if not safe:
        return f"BLOCKED by BashSecurityGate: {reason}"
    try:
        result = subprocess.run(
            command,
            shell=True,
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
            "before execution to block destructive or dangerous operations."
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
