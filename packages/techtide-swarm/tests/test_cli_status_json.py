"""Tests for swarm status --json (issue #17)."""
from __future__ import annotations
import json, types
from unittest.mock import MagicMock, patch

def _args(json_flag=True):
    a = types.SimpleNamespace(); a.json = json_flag; return a

class TestBuildStatusDict:
    def test_required_keys(self):
        from techtide_swarm.cli import _build_status_dict
        r = _build_status_dict(config_path="nonexistent.yaml")
        assert "layers" in r and "total_agents" in r and "healthy_layers" in r
    def test_layer_fields(self):
        from techtide_swarm.cli import _build_status_dict
        for l in _build_status_dict(config_path="nonexistent.yaml")["layers"]:
            assert {"name","agent_count","model","status"} <= l.keys()
    def test_totals_consistent(self):
        from techtide_swarm.cli import _build_status_dict
        r = _build_status_dict(config_path="nonexistent.yaml")
        assert r["total_agents"] == sum(l["agent_count"] for l in r["layers"])
        assert r["healthy_layers"] == sum(1 for l in r["layers"] if l["status"]=="healthy")
    def test_seven_layers(self):
        from techtide_swarm.cli import _build_status_dict
        assert len(_build_status_dict(config_path="nonexistent.yaml")["layers"]) == 7
    def test_status_values(self):
        from techtide_swarm.cli import _build_status_dict
        for l in _build_status_dict(config_path="nonexistent.yaml")["layers"]:
            assert l["status"] in ("healthy","degraded")

class TestCmdStatusJson:
    def test_valid_json(self, capsys):
        from techtide_swarm.cli import cmd_status
        cmd_status(_args(True))
        data = json.loads(capsys.readouterr().out)
        assert "layers" in data and "total_agents" in data
    def test_seven_layers(self, capsys):
        from techtide_swarm.cli import cmd_status
        cmd_status(_args(True))
        assert len(json.loads(capsys.readouterr().out)["layers"]) == 7
    def test_pipeable(self, capsys):
        from techtide_swarm.cli import cmd_status
        cmd_status(_args(True))
        data = json.loads(capsys.readouterr().out)
        assert isinstance(data["total_agents"], int)
        for l in data["layers"]: assert l["status"] in ("healthy","degraded")
    def test_no_flag_uses_rich_path(self, capsys):
        from techtide_swarm.cli import cmd_status
        with patch("techtide_swarm.cli.console") as mc:
            mc.print = MagicMock()
            cmd_status(_args(False))
