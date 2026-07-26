# file: packages/techtide-swarm/tests/test_paths_config.py
# description: Tests for resolve_config_path preference order and install_project_config
# reference: techtide_swarm.paths

from __future__ import annotations

from pathlib import Path

import pytest

from techtide_swarm.paths import (
    bundled_compact_config,
    install_project_config,
    resolve_config_path,
)


def test_resolve_config_path_prefers_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_cfg = tmp_path / "from-env.yaml"
    env_cfg.write_text("swarm: {}\n", encoding="utf-8")
    project = tmp_path / "project"
    project.mkdir()
    (project / "config").mkdir()
    (project / "config" / "swarm-compact.yaml").write_text("layers: {}\n", encoding="utf-8")

    monkeypatch.setenv("SWARM_CONFIG_PATH", str(env_cfg))
    monkeypatch.chdir(project)

    assert resolve_config_path() == env_cfg


def test_resolve_config_path_prefers_project_over_bundled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    (project / "config").mkdir(parents=True)
    project_cfg = project / "config" / "swarm-compact.yaml"
    project_cfg.write_text("swarm:\n  version: project\n", encoding="utf-8")

    monkeypatch.delenv("SWARM_CONFIG_PATH", raising=False)
    monkeypatch.chdir(project)

    resolved = resolve_config_path()
    assert resolved == project_cfg
    bundled = bundled_compact_config()
    assert bundled is not None
    assert resolved != bundled


def test_resolve_config_path_falls_back_to_bundled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.delenv("SWARM_CONFIG_PATH", raising=False)
    monkeypatch.chdir(empty)

    bundled = bundled_compact_config()
    assert bundled is not None and bundled.is_file()
    assert resolve_config_path() == bundled


def test_resolve_config_path_explicit_wins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    explicit = tmp_path / "explicit.yaml"
    explicit.write_text("agents: []\n", encoding="utf-8")
    env_cfg = tmp_path / "env.yaml"
    env_cfg.write_text("swarm: {}\n", encoding="utf-8")
    monkeypatch.setenv("SWARM_CONFIG_PATH", str(env_cfg))

    assert resolve_config_path(explicit) == explicit


def test_install_project_config_copies_bundled_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    bundled = bundled_compact_config()
    assert bundled is not None

    dest = install_project_config()
    assert dest == tmp_path / "config" / "swarm-compact.yaml"
    assert dest.is_file()
    assert dest.read_text(encoding="utf-8") == bundled.read_text(encoding="utf-8")

    # Second call without force leaves existing file
    dest.write_text("custom:\n  keep: true\n", encoding="utf-8")
    again = install_project_config(force=False)
    assert again.read_text(encoding="utf-8") == "custom:\n  keep: true\n"

    forced = install_project_config(force=True)
    assert forced.read_text(encoding="utf-8") == bundled.read_text(encoding="utf-8")
