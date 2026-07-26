"""13-pattern bash command validation (regex gate; not an OS sandbox)."""

from __future__ import annotations

import re
import shlex


class BashSecurityGate:
    """Validate shell commands before execution."""

    _BLOCK_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
        (re.compile(r"(?i)\brm\s+(-[rf]*\s*)*[/~]"), "recursive delete toward root or home"),
        (re.compile(r"(?i)\bcurl\b.*\|\s*bash"), "curl pipe to bash"),
        (re.compile(r"(?i)\bwget\b.*\|\s*(?:sh|bash)"), "wget pipe to shell"),
        (re.compile(r"(?i)\b(?:sudo\s+)?chmod\s+777\b"), "dangerous chmod"),
        (re.compile(r"(?i)\$[\w_]*(?:KEY|SECRET|TOKEN|PASSWORD)\b"), "references secret env var"),
        (re.compile(r"(?i)\b(?:ANTHROPIC|OPENAI|AWS|GCP)_(?:API_)?KEY\b"), "API key literal in argv"),
        (re.compile(r"(?i)>\s*/etc/"), "redirect to system config"),
        (re.compile(r"(?i)\bmkfs\b"), "disk format"),
        (re.compile(r"(?i)\bdd\s+if="), "raw disk write"),
        (re.compile(r"(?i)\bpython[23]?\s+-c\s+.*(?:exec|eval|import\s+os)"), "python code exec with os access"),
        (re.compile(r"(?i)\bsudo\s+(?:rm|mv|cp|chown)\b"), "elevated file operation"),
        (re.compile(r"(?i)\bnc\s+-[el]"), "netcat listener"),
        (re.compile(r"(?i)>\s*/dev/(?:sd|hd|nvme)"), "redirect to block device"),
    )

    @classmethod
    def validate(cls, command: str) -> tuple[bool, str]:
        """Return (safe, reason). Safe commands get reason ''."""
        stripped = command.strip()
        if not stripped:
            return False, "empty command"
        try:
            parts = shlex.split(stripped)
        except ValueError as exc:
            return False, f"unparseable shell: {exc}"
        if not parts:
            return False, "empty command"
        joined = " ".join(parts)
        for pattern, reason in cls._BLOCK_PATTERNS:
            if pattern.search(stripped) or pattern.search(joined):
                return False, reason
        return True, ""
