"""Tests for MemoryManager.for_layer factory and per-layer memory."""

from pathlib import Path

from techtide_swarm import MemoryManager


def test_for_layer_creates_manager(tmp_path: Path):
    mem = MemoryManager.for_layer("research", swarm_root=tmp_path, use_memvid=False)
    assert mem.swarm_root == tmp_path
    assert mem._memvid is None


def test_for_layer_with_memvid_path(tmp_path: Path):
    mem = MemoryManager.for_layer("sales", swarm_root=tmp_path, use_memvid=True)
    expected = tmp_path / ".swarm" / "layer-sales.mv2"
    assert mem._memvid is not None
    assert mem._memvid.mv2_path == expected


def test_for_layer_share_and_recall(tmp_path: Path):
    mem = MemoryManager.for_layer("marketing", swarm_root=tmp_path, use_memvid=False)
    mem.share(
        from_agent="mktg-content-001",
        to_agent="mktg-social-001",
        key="campaign/q2",
        content="Q2 campaign launches June 1",
    )
    results = mem.recall("mktg-social-001", "campaign")
    assert len(results) >= 1
    assert "Q2" in results[0]["content"]
