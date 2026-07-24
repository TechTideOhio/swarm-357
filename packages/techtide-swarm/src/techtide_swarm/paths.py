"""Resolve bundled package data (roster + soul templates) for wheel installs."""

from __future__ import annotations

from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
_DATA_DIR = _PKG_DIR / "data"


def bundled_data_dir() -> Path:
    return _DATA_DIR


def bundled_compact_config() -> Path | None:
    path = _DATA_DIR / "swarm-compact.yaml"
    return path if path.is_file() else None


def resolve_soul_path(soul: str) -> Path | None:
    """Resolve a soul template path from CWD, repo, or bundled wheel data."""
    if not soul:
        return None
    path = Path(soul)
    if path.is_file():
        return path

    candidates = [
        Path.cwd() / soul,
        _PKG_DIR.parent.parent.parent.parent / soul,  # Apps/swarm357 when editable
        _PKG_DIR.parent.parent.parent / soul,
        _DATA_DIR / soul.removeprefix("templates/"),
        _DATA_DIR / "soul" / Path(soul).name,
    ]
    # templates/soul/research/x.md -> data/soul/research/x.md
    if soul.startswith("templates/soul/"):
        candidates.insert(0, _DATA_DIR / soul[len("templates/") :])
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None
