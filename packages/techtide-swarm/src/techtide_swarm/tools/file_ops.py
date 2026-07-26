# file: packages/techtide-swarm/src/techtide_swarm/tools/file_ops.py
# description: File read/write tools with workspace-root confinement for server mode
# reference: techtide_swarm.tools.registry
"""File read/write tools with path-safety checks.

Registers:
  - Read  (toolset: core_tools)
  - Write (toolset: core_tools)
"""

from __future__ import annotations

import os
from pathlib import Path

from techtide_swarm.tools.registry import registry

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


def _workspace_root() -> Path | None:
    """Immutable workspace root for Read/Write.

    Default: confine to CWD (Steinberger local-first). Escape with SWARM_UNSAFE_FS=1.
    """
    if os.getenv("SWARM_UNSAFE_FS", "").strip().lower() in {"1", "true", "yes", "on"}:
        return None
    explicit = os.getenv("SWARM_WORKSPACE_ROOT", "").strip() or os.getenv(
        "SWARM_WRITE_SAFE_ROOT", ""
    ).strip()
    if explicit:
        return Path(explicit).resolve()
    # Default confine for CLI and server unless explicitly disabled
    return Path.cwd().resolve()


def _is_path_allowed(path: Path, *, for_write: bool) -> tuple[bool, str]:
    """Return (allowed, reason)."""
    try:
        resolved = path.resolve()
    except OSError as exc:
        return False, f"Path denied: {exc}"
    resolved_s = str(resolved)
    if for_write:
        for pattern in _WRITE_DENY_PATTERNS:
            if pattern in resolved_s:
                return False, f"Write denied: path matches sensitive pattern '{pattern}'"
    root = _workspace_root()
    if root is not None:
        try:
            resolved.relative_to(root)
        except ValueError:
            return False, f"Path denied: outside workspace root ({root})"
    return True, ""


def read_file(path: str, offset: int = 1, limit: int = 500) -> str:
    """Read a file, returning up to *limit* lines starting at *offset* (1-based)."""
    try:
        p = Path(path)
        allowed, reason = _is_path_allowed(p, for_write=False)
        if not allowed:
            return reason
        if not p.is_file():
            return f"Error: file not found: {path}"
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        start = max(0, offset - 1)
        chunk = lines[start : start + limit]
        header = (
            f"[Lines {start + 1}–{start + len(chunk)} of {len(lines)}]\n"
            if len(lines) > limit
            else ""
        )
        return header + "\n".join(chunk)
    except Exception as exc:
        return f"Error reading file: {exc}"


def write_file(path: str, content: str = "") -> str:
    """Write *content* to *path*, creating parent directories as needed."""
    try:
        if not path:
            return "Error: Write requires a non-empty 'path'"
        p = Path(str(path))
        allowed, reason = _is_path_allowed(p, for_write=True)
        if not allowed:
            return reason
        p.parent.mkdir(parents=True, exist_ok=True)
        text = "" if content is None else str(content)
        p.write_text(text, encoding="utf-8")
        return f"Successfully wrote {len(text)} bytes to {path}"
    except Exception as exc:
        return f"Error writing file: {exc}"


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
        "description": "Write content to a file at the given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file.",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write.",
                    "default": "",
                },
            },
            "required": ["path"],
        },
    },
    handler=write_file,
    toolset="core_tools",
)
