"""Integration test: full put/search cycle via MemvidBridge (skipped if binary missing)."""

import json
from pathlib import Path

import pytest

from techtide_swarm.memvid_bridge import MemvidBridge, resolve_bridge_binary


bridge_available = resolve_bridge_binary() is not None
skip_reason = "memvid-swarm-bridge binary not on PATH or MEMVID_SWARM_BRIDGE not set"


@pytest.mark.skipif(not bridge_available, reason=skip_reason)
def test_create_put_search_verify(tmp_path: Path):
    mv2 = tmp_path / "test-layer.mv2"
    bridge = MemvidBridge(mv2)

    bridge.create()
    assert mv2.exists()

    bridge.put(
        uri="swarm://test/key",
        title="research-001->sales-001",
        body=b"Acme Corp raised enterprise pricing 20% in Q1 2026.",
    )

    results = bridge.search("Acme pricing", top_k=5)
    assert "hits" in results or "results" in results

    report = bridge.verify()
    assert isinstance(report, dict)


@pytest.mark.skipif(not bridge_available, reason=skip_reason)
def test_verify_deep(tmp_path: Path):
    mv2 = tmp_path / "deep-test.mv2"
    bridge = MemvidBridge(mv2)
    bridge.create()
    bridge.put(uri="swarm://deep", title="test", body=b"deep verify content")

    report = bridge.verify(deep=True)
    assert isinstance(report, dict)
