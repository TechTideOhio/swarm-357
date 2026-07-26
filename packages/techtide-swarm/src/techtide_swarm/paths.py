# file: packages/techtide-swarm/src/techtide_swarm/paths.py
# description: Resolve bundled package data and unified swarm config path resolution
# reference: techtide_swarm.cli, techtide_swarm.server, techtide_swarm.swarm
"""Resolve bundled package data (roster + soul templates) for wheel installs."""

from __future__ import annotations

import os
import shutil
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


def resolve_config_path(explicit: str | Path | None = None) -> Path:
    """Resolve swarm YAML: explicit/env → project compact → bundled compact.

    Search order:
    1. Explicit CLI/API argument (if provided and exists, or non-empty string)
    2. SWARM_CONFIG_PATH env
    3. ./config/swarm-compact.yaml
    4. ./config/swarm.yaml
    5. Docker /app/config/swarm-compact.yaml
    6. Bundled wheel data/swarm-compact.yaml
    7. Repo-relative config/swarm-compact.yaml (editable installs)

    Returns the first existing path, or the first preferred path even if missing
    (callers check ``.exists()``).
    """
    candidates: list[Path] = []
    if explicit is not None and str(explicit).strip():
        candidates.append(Path(str(explicit)))
    env = os.getenv("SWARM_CONFIG_PATH", "").strip()
    if env:
        candidates.append(Path(env))
    candidates.extend(
        [
            Path.cwd() / "config" / "swarm-compact.yaml",
            Path.cwd() / "config" / "swarm.yaml",
            Path("/app/config/swarm-compact.yaml"),
        ]
    )
    bundled = bundled_compact_config()
    if bundled is not None:
        candidates.append(bundled)
    # Editable / monorepo layouts
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidates.append(parent / "config" / "swarm-compact.yaml")
        candidates.append(parent / "config" / "swarm.yaml")

    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        if path.is_file():
            return path
    # Prefer project compact path for error messages when nothing exists
    return candidates[0] if candidates else Path("config/swarm-compact.yaml")


def install_project_config(*, force: bool = False) -> Path:
    """Copy bundled compact roster into ./config/swarm-compact.yaml for swarm init."""
    dest_dir = Path.cwd() / "config"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "swarm-compact.yaml"
    if dest.exists() and not force:
        return dest
    src = bundled_compact_config()
    if src is None:
        raise FileNotFoundError("bundled swarm-compact.yaml missing from package data")
    shutil.copyfile(src, dest)
    return dest


def install_project_souls(*, force: bool = False) -> Path:
    """Copy bundled soul templates into ./templates/soul for local editing."""
    dest_root = Path.cwd() / "templates" / "soul"
    src_root = _DATA_DIR / "soul"
    if not src_root.is_dir():
        raise FileNotFoundError("bundled soul templates missing from package data")
    for src in src_root.rglob("*.md"):
        rel = src.relative_to(src_root)
        dest = dest_root / rel
        if dest.exists() and not force:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    return dest_root
