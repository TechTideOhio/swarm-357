# file: packages/techtide-swarm/tests/test_tool_normalize.py
# description: Tests for tool input alias normalization and Write resilience.
# reference: techtide_swarm.tools.input_normalize, techtide_swarm.tools.registry

"""Tool input normalization — platform-critical for OpenRouter tool calls."""

from __future__ import annotations

from pathlib import Path

from techtide_swarm.tools import execute_tool
from techtide_swarm.tools.input_normalize import (
    coerce_to_dict,
    filter_handler_kwargs,
    normalize_tool_input,
)


def test_coerce_none_and_dict() -> None:
    assert coerce_to_dict(None) == {}
    assert coerce_to_dict({"a": 1}) == {"a": 1}


def test_coerce_json_string() -> None:
    assert coerce_to_dict('{"path": "/tmp/x", "content": "hi"}') == {
        "path": "/tmp/x",
        "content": "hi",
    }


def test_write_aliases_file_path_and_contents() -> None:
    out = normalize_tool_input(
        "Write",
        {"file_path": "/tmp/a.txt", "contents": "hello"},
    )
    assert out["path"] == "/tmp/a.txt"
    assert out["content"] == "hello"


def test_write_defaults_missing_content() -> None:
    out = normalize_tool_input("Write", {"path": "/tmp/a.txt"})
    assert out["path"] == "/tmp/a.txt"
    assert out["content"] == ""


def test_bash_cmd_alias() -> None:
    out = normalize_tool_input("Bash", {"cmd": "echo hi"})
    assert out["command"] == "echo hi"


def test_websearch_q_alias() -> None:
    out = normalize_tool_input("WebSearch", {"q": "swarm agents"})
    assert out["query"] == "swarm agents"


def test_filter_handler_kwargs_drops_unknown() -> None:
    def handler(path: str, content: str = "") -> str:
        return path + content

    filtered = filter_handler_kwargs(handler, {"path": "a", "content": "b", "extra": 1})
    assert filtered == {"path": "a", "content": "b"}


def test_execute_write_with_file_path_alias(tmp_path: Path) -> None:
    target = str(tmp_path / "alias.txt")
    result = execute_tool("Write", {"file_path": target, "text": "via alias"})
    assert "Successfully" in result
    assert Path(target).read_text(encoding="utf-8") == "via alias"


def test_execute_write_missing_content_does_not_crash(tmp_path: Path) -> None:
    target = str(tmp_path / "empty.txt")
    result = execute_tool("Write", {"path": target})
    assert "error" not in result.lower() or "Successfully" in result
    assert Path(target).exists()


def test_execute_write_file_handler_name(tmp_path: Path) -> None:
    """Backward-compat: models sometimes emit write_file instead of Write."""
    target = str(tmp_path / "snake.txt")
    result = execute_tool("write_file", {"path": target, "content": "snake"})
    assert "Successfully" in result
    assert Path(target).read_text(encoding="utf-8") == "snake"
