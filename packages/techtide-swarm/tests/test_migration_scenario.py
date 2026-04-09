"""Scenario: migrate flat topics to Memvid when bridge missing."""

from pathlib import Path

from techtide_swarm import MemoryManager


def test_migrate_skips_without_bridge(tmp_path: Path):
    mem = MemoryManager(swarm_root=tmp_path)
    mem.share(
        from_agent="x",
        to_agent="y",
        key="test/key",
        content="hello",
    )
    dest = tmp_path / "out.mv2"
    result = mem.migrate_flat_to_memvid(dest)
    assert result["status"] == "skipped"
    assert "not available" in result["reason"]
