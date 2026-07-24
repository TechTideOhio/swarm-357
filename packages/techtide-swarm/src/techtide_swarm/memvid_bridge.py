"""Subprocess bridge to `memvid-swarm-bridge` (Rust binary)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, cast


class MemvidBridgeError(RuntimeError):
    """Bridge or memvid binary failed."""


def resolve_bridge_binary() -> Path | None:
    """Return path to bridge executable, or None if not available."""
    env = os.getenv("MEMVID_SWARM_BRIDGE")
    if env:
        p = Path(env)
        if p.is_file():
            return p
    which = shutil.which("memvid-swarm-bridge")
    if which:
        return Path(which)
    return None


class MemvidBridge:
    """Thin wrapper: create, put, search, verify on a `.mv2` path."""

    def __init__(self, mv2_path: Path, *, bridge: Path | None = None) -> None:
        self.mv2_path = mv2_path
        self._bridge = bridge or resolve_bridge_binary()

    @property
    def available(self) -> bool:
        return self._bridge is not None

    def _run(self, args: list[str], *, stdin: bytes | None = None) -> subprocess.CompletedProcess[str]:
        if not self._bridge:
            raise MemvidBridgeError("memvid-swarm-bridge not found; build packages/memvid-swarm-bridge")
        return subprocess.run(
            [str(self._bridge), *args],
            input=stdin,
            capture_output=True,
            text=True,
            check=False,
        )

    def create(self) -> None:
        proc = self._run(["create", str(self.mv2_path)])
        if proc.returncode != 0:
            raise MemvidBridgeError(proc.stderr or proc.stdout or "create failed")

    def put(self, *, uri: str, title: str, body: bytes) -> None:
        proc = self._run(
            ["put", str(self.mv2_path), "--uri", uri, "--title", title],
            stdin=body,
        )
        if proc.returncode != 0:
            raise MemvidBridgeError(proc.stderr or proc.stdout or "put failed")

    def search(self, query: str, top_k: int = 10) -> dict[str, Any]:
        proc = self._run(["search", str(self.mv2_path), query, "--top-k", str(top_k)])
        if proc.returncode != 0:
            raise MemvidBridgeError(proc.stderr or proc.stdout or "search failed")
        return cast(dict[str, Any], json.loads(proc.stdout))

    def verify(self, *, deep: bool = False) -> dict[str, Any]:
        args = ["verify", str(self.mv2_path)]
        if deep:
            args.append("--deep")
        proc = self._run(args)
        if proc.returncode != 0:
            raise MemvidBridgeError(proc.stderr or proc.stdout or "verify failed")
        return cast(dict[str, Any], json.loads(proc.stdout))
