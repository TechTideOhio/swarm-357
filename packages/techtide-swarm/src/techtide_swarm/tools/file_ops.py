"""File read/write tools with path-safety checks.

Registers:
  - Read  (toolset: core_tools)
  - Write (toolset: core_tools)
"""

from __future__ import annotations

import os
from pathlib import Path

from techtide_swarm.tools.registry import registry

# ---------------------------------------------------------------------------
# Write-path deny list — patterns that must not appear in resolved write paths.
# Checked against the absolute, resolved path string.
# ---------------------------------------------------------------------------

_WRITE_DENY_PATTERNS: list[str] = [
    "/.ssh/",
    "\\.ssh\\",
    "/id_rsa",
    "/id_ed25519",
    "/authorized_keys",
    "/.env",
    "\\.env",
    "/etc/passwd",
    "/etc/shadow",
    "/etc/sudoers",
    "/.bashrc",
    "/.zshrc",
    "/.profile",
    "/.bash_profile",
]

# If SWARM_WRITE_SAFE_ROOT is set, all writes must live under that directory.
_SAFE_ROOT = os.getenv("SWARM_WRITE_SAFE_ROOT", "")


def _is_write_allowed(path: Path) -> tuple[bool, str]:
    """Return (allowed, reason).  Reason is empty string when allowed."""
    resolved = str(path.resolve())
    for pattern in _WRITE_DENY_PATTERNS:
        if pattern in resolved:
            return False, f"Write denied: path matches sensitive pattern '{pattern}'"
    if _SAFE_ROOT:
        safe = str(Path(_SAFE_ROOT).resolve())
        if not resolved.startswith(safe):
            return False, f"Write denied: path is outside SWARM_WRITE_SAFE_ROOT ({safe})"
    return True, ""


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def read_file(path: str, offset: int = 1, limit: int = 500) -> str:
    """Read a file, returning up to *limit* lines starting at *offset* (1-based)."""
    try:
        p = Path(path)
        if not p.is_file():
            return f"Error: file not found: {path}"
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        start = max(0, offset - 1)
        chunk = lines[start : start + limit]
        header = f"[Lines {start + 1}–{start + len(chunk)} of {len(lines)}]\n" if len(lines) > limit else ""
        return header + "\n".join(chunk)
    except Exception as exc:
        return f"Error reading file: {exc}"


def write_file(path: str, content: str = "") -> str:
    """Write *content* to *path*, creating parent directories as needed.

    ``content`` defaults to empty string so model calls that omit the field
    still succeed (create/truncate) instead of raising TypeError.
    """
    try:
        if not path:
            return "Error: Write requires a non-empty 'path'"
        p = Path(str(path))
        allowed, reason = _is_write_allowed(p)
        if not allowed:
            return reason
        p.parent.mkdir(parents=True, exist_ok=True)
        text = "" if content is None else str(content)
        p.write_text(text, encoding="utf-8")
        return f"Successfully wrote {len(text)} bytes to {path}"
    except Exception as exc:
        return f"Error writing file: {exc}"


# ---------------------------------------------------------------------------
# Self-registration
# ---------------------------------------------------------------------------

registry.register(
    name="Read",
    schema={
        "description": "Read the contents of a file at the given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file.",
                },
                "offset": {
                    "type": "integer",
                    "description": "1-based line number to start reading from (default 1).",
                    "default": 1,
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of lines to return (default 500).",
                    "default": 500,
                },
            },
            "required": ["path"],
        },
    },
    handler=read_file,
    toolset="core_tools",
)

registry.register(
    name="Write",
    schema={
        "description": (
            "Write content to a file, creating parent directories as needed. "
            "ALWAYS pass both 'path' (string) and 'content' (string) together."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to write.",
                },
                "content": {
                    "type": "string",
                    "description": "Full text content to write into the file.",
                },
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    handler=write_file,
    toolset="core_tools",
)
