"""Tests for the tool registry, toolset resolution, and individual tool modules."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from techtide_swarm.tools.registry import TOOLSET_MAP, ToolRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_registry() -> ToolRegistry:
    """Fresh, empty registry for isolation."""
    return ToolRegistry()


# ---------------------------------------------------------------------------
# ToolRegistry — core behaviour
# ---------------------------------------------------------------------------

class TestToolRegistryCore:
    def test_register_and_lookup(self):
        reg = _make_registry()
        reg.register(
            name="Foo",
            schema={"description": "Foo tool", "input_schema": {"type": "object", "properties": {}}},
            handler=lambda: "ok",
            toolset="test_tools",
        )
        assert "Foo" in reg.get_all_tool_names()

    def test_unknown_tool_returns_error_json(self):
        reg = _make_registry()
        result = reg.execute_tool("NonExistent", {})
        parsed = json.loads(result)
        assert "error" in parsed

    def test_check_fn_gates_tool(self):
        reg = _make_registry()
        reg.register(
            name="Gated",
            schema={"description": "gated", "input_schema": {"type": "object", "properties": {}}},
            handler=lambda: "reached",
            toolset="test",
            check_fn=lambda: False,  # always unavailable
        )
        schemas = reg.get_anthropic_tools(["Gated"])
        assert schemas == []

    def test_check_fn_passes_when_true(self):
        reg = _make_registry()
        reg.register(
            name="Open",
            schema={"description": "open", "input_schema": {"type": "object", "properties": {}}},
            handler=lambda: "reached",
            toolset="test",
            check_fn=lambda: True,
        )
        schemas = reg.get_anthropic_tools(["Open"])
        assert len(schemas) == 1

    def test_check_fn_exception_treated_as_false(self):
        reg = _make_registry()

        def bad_check() -> bool:
            raise RuntimeError("boom")

        reg.register(
            name="Exploding",
            schema={"description": "x", "input_schema": {"type": "object", "properties": {}}},
            handler=lambda: "nope",
            toolset="test",
            check_fn=bad_check,
        )
        schemas = reg.get_anthropic_tools(["Exploding"])
        assert schemas == []

    def test_anthropic_schema_format(self):
        """Every returned schema must have name, description, input_schema keys."""
        reg = _make_registry()
        reg.register(
            name="Ping",
            schema={
                "description": "A ping tool.",
                "input_schema": {
                    "type": "object",
                    "properties": {"msg": {"type": "string"}},
                    "required": ["msg"],
                },
            },
            handler=lambda msg: f"pong: {msg}",
            toolset="test",
        )
        schemas = reg.get_anthropic_tools(["Ping"])
        assert len(schemas) == 1
        s = schemas[0]
        assert s["name"] == "Ping"
        assert "description" in s
        assert "input_schema" in s
        # Must NOT have OpenAI-style type/function wrapper
        assert "type" not in s
        assert "function" not in s

    def test_get_all_tool_names_sorted(self):
        reg = _make_registry()
        for name in ["Zebra", "Alpha", "Mango"]:
            reg.register(
                name=name,
                schema={"description": "", "input_schema": {"type": "object", "properties": {}}},
                handler=lambda: "",
                toolset="test",
            )
        names = reg.get_all_tool_names()
        assert names == sorted(names)

    def test_collision_warning_logged(self, caplog):
        import logging
        reg = _make_registry()
        schema: dict[str, Any] = {"description": "", "input_schema": {"type": "object", "properties": {}}}
        reg.register("Dup", schema=schema, handler=lambda: "", toolset="ts_a")
        with caplog.at_level(logging.WARNING, logger="techtide_swarm.tools.registry"):
            reg.register("Dup", schema=schema, handler=lambda: "", toolset="ts_b")
        assert any("collision" in r.message.lower() or "Dup" in r.message for r in caplog.records)

    def test_execute_tool_by_schema_name(self):
        """execute_tool must find the handler by its schema 'name' field (Anthropic name)."""
        reg = _make_registry()
        reg.register(
            name="MyTool",
            schema={
                "description": "d",
                "input_schema": {"type": "object", "properties": {"x": {"type": "integer"}}},
            },
            handler=lambda x: str(x * 2),
            toolset="test",
        )
        # Anthropic sends back the "name" field, which is "MyTool"
        result = reg.execute_tool("MyTool", {"x": 21})
        assert result == "42"


# ---------------------------------------------------------------------------
# TOOLSET_MAP
# ---------------------------------------------------------------------------

class TestToolsetMap:
    def test_all_layers_present(self):
        expected = {
            "core_tools", "research_tools", "sales_tools", "support_tools",
            "marketing_tools", "seo_tools", "ops_tools", "management_tools",
        }
        assert expected.issubset(TOOLSET_MAP.keys())

    def test_get_tools_for_toolset(self):
        reg = _make_registry()
        tools = reg.get_tools_for_toolset("research_tools")
        assert "WebSearch" in tools
        assert "Scrape" in tools
        assert "Read" in tools

    def test_unknown_toolset_returns_empty(self):
        reg = _make_registry()
        assert reg.get_tools_for_toolset("does_not_exist") == []

    def test_check_toolset_requirements_returns_dict(self):
        # Use the real module-level registry (tools are registered).
        from techtide_swarm.tools import registry as real_reg
        result = real_reg.check_toolset_requirements()
        assert isinstance(result, dict)
        for key, val in result.items():
            assert isinstance(val, bool), f"{key} must be bool, got {type(val)}"


# ---------------------------------------------------------------------------
# file_ops
# ---------------------------------------------------------------------------

class TestFileOps:
    def test_read_existing_file(self, tmp_path: Path):
        f = tmp_path / "hello.txt"
        f.write_text("line1\nline2\nline3", encoding="utf-8")
        from techtide_swarm.tools.file_ops import read_file
        result = read_file(str(f))
        assert "line1" in result
        assert "line2" in result

    def test_read_missing_file(self, tmp_path: Path):
        from techtide_swarm.tools.file_ops import read_file
        result = read_file(str(tmp_path / "nope.txt"))
        assert "Error" in result or "not found" in result.lower()

    def test_write_and_read_roundtrip(self, tmp_path: Path):
        from techtide_swarm.tools.file_ops import read_file, write_file
        target = str(tmp_path / "sub" / "out.txt")
        write_result = write_file(target, "hello world")
        assert "Successfully" in write_result
        read_result = read_file(target)
        assert "hello world" in read_result

    def test_write_deny_list_blocks_ssh_key(self, tmp_path: Path):
        from techtide_swarm.tools.file_ops import write_file
        # Create a path that contains the deny pattern
        bad_path = str(tmp_path / ".ssh" / "authorized_keys")
        result = write_file(bad_path, "evil key")
        # Must return an error string, NOT raise an exception
        assert "denied" in result.lower() or "blocked" in result.lower() or "Error" in result

    def test_write_safe_root_blocks_escape(self, tmp_path: Path):
        safe_dir = tmp_path / "safe"
        safe_dir.mkdir()
        outside = tmp_path / "outside.txt"
        with patch.dict(os.environ, {"SWARM_WRITE_SAFE_ROOT": str(safe_dir)}):
            # Force reload so _SAFE_ROOT is re-evaluated
            import importlib
            from techtide_swarm.tools import file_ops
            importlib.reload(file_ops)
            result = file_ops.write_file(str(outside), "oops")
        # Clean up env side-effect
        importlib.reload(file_ops)
        assert "denied" in result.lower() or "outside" in result.lower() or "Error" in result

    def test_read_pagination(self, tmp_path: Path):
        from techtide_swarm.tools.file_ops import read_file
        f = tmp_path / "big.txt"
        f.write_text("\n".join(str(i) for i in range(1, 21)), encoding="utf-8")
        result = read_file(str(f), offset=5, limit=3)
        # Should contain lines 5, 6, 7 (values "5", "6", "7")
        assert "5" in result
        assert "6" in result
        assert "7" in result


# ---------------------------------------------------------------------------
# web_search
# ---------------------------------------------------------------------------

class TestWebSearch:
    def test_no_api_key_returns_stub(self, monkeypatch):
        monkeypatch.delenv("EXA_API_KEY", raising=False)
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        from techtide_swarm.tools.web_search import web_search
        result = web_search("test query")
        # Must not crash; must return a string
        assert isinstance(result, str)
        assert len(result) > 0

    def test_stub_contains_helpful_message(self, monkeypatch):
        monkeypatch.delenv("EXA_API_KEY", raising=False)
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        from techtide_swarm.tools.web_search import web_search
        result = web_search("Python AI frameworks")
        # Stub should mention how to configure a real key
        assert "EXA_API_KEY" in result or "FIRECRAWL_API_KEY" in result or "stub" in result.lower()

    def test_check_fn_false_without_keys(self, monkeypatch):
        monkeypatch.delenv("EXA_API_KEY", raising=False)
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        from techtide_swarm.tools.web_search import check_web_search
        assert check_web_search() is False

    def test_registered_in_registry(self):
        from techtide_swarm.tools import registry as real_reg
        assert "WebSearch" in real_reg.get_all_tool_names()


# ---------------------------------------------------------------------------
# web_scrape
# ---------------------------------------------------------------------------

class TestWebScrape:
    def test_no_api_key_uses_httpx_fallback(self, monkeypatch, respx_mock=None):
        """Without API keys, Scrape falls back to httpx; should not crash."""
        monkeypatch.delenv("EXA_API_KEY", raising=False)
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        # No real network call - just verify no ImportError / crash when the
        # function is invoked against a mocked httpx client.
        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.text = "<html><body>Hello world</body></html>"
        mock_response.headers = {"content-type": "text/html"}
        mock_response.is_redirect = False
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get = MagicMock(return_value=mock_response)

        with patch("httpx.Client", return_value=mock_client):
            from techtide_swarm.tools.web_scrape import web_scrape
            result = web_scrape("https://example.com")
        assert "Hello world" in result

    def test_check_fn_always_true(self):
        from techtide_swarm.tools.web_scrape import check_web_scrape
        assert check_web_scrape() is True

    def test_registered_in_registry(self):
        from techtide_swarm.tools import registry as real_reg
        assert "Scrape" in real_reg.get_all_tool_names()


# ---------------------------------------------------------------------------
# memory_tool
# ---------------------------------------------------------------------------

class TestMemoryTool:
    def setup_method(self):
        # Reset the singleton so each test gets its own tmp dir
        from techtide_swarm.tools import memory_tool
        memory_tool.reset_memory_manager()

    def test_share_and_recall(self, tmp_path: Path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from techtide_swarm.tools import memory_tool
        memory_tool.reset_memory_manager()

        from techtide_swarm.tools.memory_tool import memory_recall, memory_share
        share_result = json.loads(
            memory_share("insight_001", "The sky is blue", from_agent="agent-a", to_agent="agent-b")
        )
        assert share_result.get("status") == "ok"

        recall_result = json.loads(memory_recall("sky color", agent_id="agent-a"))
        # Should return something without erroring
        assert "error" not in recall_result

    def test_registered_in_registry(self):
        from techtide_swarm.tools import registry as real_reg
        names = real_reg.get_all_tool_names()
        assert "Memory" in names
        assert "MemoryShare" in names


# ---------------------------------------------------------------------------
# Backward-compat shims
# ---------------------------------------------------------------------------

class TestBackwardCompat:
    def test_get_anthropic_tools_shim(self):
        from techtide_swarm.tools import get_anthropic_tools
        schemas = get_anthropic_tools(["Read", "Write", "Bash"])
        assert len(schemas) == 3
        names = {s["name"] for s in schemas}
        assert "Read" in names
        assert "Write" in names
        assert "Bash" in names

    def test_execute_tool_shim(self, tmp_path: Path):
        from techtide_swarm.tools import execute_tool
        # Write a temp file then read it back via the tool
        target = str(tmp_path / "out.txt")
        write_res = execute_tool("Write", {"path": target, "content": "hello shim"})
        assert "Successfully" in write_res
        read_res = execute_tool("Read", {"path": target})
        assert "hello shim" in read_res

    def test_unknown_tool_via_shim(self):
        from techtide_swarm.tools import execute_tool
        result = execute_tool("UnknownTool", {})
        assert "error" in result.lower() or "Unknown" in result

    def test_registry_exported_from_tools(self):
        from techtide_swarm.tools import registry
        assert hasattr(registry, "get_all_tool_names")
        assert len(registry.get_all_tool_names()) >= 7  # Read Write Bash WebSearch Scrape Memory MemoryShare
