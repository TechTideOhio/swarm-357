import os
import textwrap
from pathlib import Path
import pytest


def test_resolve_env_literal():
    from techtide_swarm.tools.mcp import resolve_env
    assert resolve_env({"KEY": "value"}) == {"KEY": "value"}


def test_resolve_env_interpolation(monkeypatch):
    from techtide_swarm.tools.mcp import resolve_env
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-123")
    assert resolve_env({"FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"}) == {
        "FIRECRAWL_API_KEY": "fc-test-123"
    }


def test_resolve_env_missing_var(monkeypatch):
    from techtide_swarm.tools.mcp import resolve_env
    monkeypatch.delenv("MISSING_VAR", raising=False)
    assert resolve_env({"KEY": "${MISSING_VAR}"}) == {"KEY": ""}


def test_resolve_env_embedded_reference(monkeypatch):
    from techtide_swarm.tools.mcp import resolve_env
    monkeypatch.setenv("TOKEN", "abc123")
    assert resolve_env({"AUTH": "Bearer ${TOKEN}"}) == {"AUTH": "Bearer abc123"}


def test_load_mcp_configs(tmp_path):
    from techtide_swarm.tools.mcp import load_mcp_configs
    (tmp_path / "firecrawl.yaml").write_text(textwrap.dedent("""\
        name: firecrawl
        description: Firecrawl web scraping
        transport: stdio
        command: npx
        args: ["firecrawl-mcp"]
        env:
          FIRECRAWL_API_KEY: "${FIRECRAWL_API_KEY}"
        toolset: research_tools
        enabled: true
    """))
    configs = load_mcp_configs(tmp_path)
    assert len(configs) == 1
    assert configs[0].name == "firecrawl"
    assert configs[0].transport == "stdio"
    assert configs[0].command == "npx"
    assert configs[0].args == ("firecrawl-mcp",)
    assert configs[0].toolset == "research_tools"


def test_load_mcp_configs_skips_disabled(tmp_path):
    from techtide_swarm.tools.mcp import load_mcp_configs
    (tmp_path / "disabled.yaml").write_text("name: disabled\nenabled: false\ntransport: stdio\n")
    configs = load_mcp_configs(tmp_path)
    assert configs == []


def test_load_mcp_configs_empty_dir(tmp_path):
    from techtide_swarm.tools.mcp import load_mcp_configs
    assert load_mcp_configs(tmp_path) == []


def test_load_mcp_configs_missing_dir():
    from techtide_swarm.tools.mcp import load_mcp_configs
    assert load_mcp_configs("/nonexistent/path") == []


def test_mcp_tool_name_with_server_prefix():
    from techtide_swarm.tools.mcp import _mcp_tool_name
    assert _mcp_tool_name("firecrawl", "firecrawl_scrape") == "mcp_firecrawl_scrape"


def test_mcp_tool_name_without_server_prefix():
    from techtide_swarm.tools.mcp import _mcp_tool_name
    assert _mcp_tool_name("github", "create_or_update_file") == "mcp_github_create_or_update_file"


import sys

# A minimal MCP-compliant Python subprocess for testing
FAKE_MCP_SERVER_SCRIPT = '''
import json, sys

def respond(id_, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": id_, "result": result}) + "\\n")
    sys.stdout.flush()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    method = req.get("method", "")
    id_ = req.get("id")
    if method == "initialize":
        respond(id_, {"protocolVersion": "2024-11-05", "capabilities": {}, "serverInfo": {"name": "fake"}})
    elif method == "notifications/initialized":
        pass  # notification - no response
    elif method == "tools/list":
        respond(id_, {"tools": [{"name": "echo_text", "description": "Echoes text", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}}}]})
    elif method == "tools/call":
        args = req.get("params", {}).get("arguments", {})
        respond(id_, {"content": [{"type": "text", "text": args.get("text", "")}]})
'''


def _write_fake_server(tmp_path):
    script = tmp_path / "fake_mcp.py"
    script.write_text(FAKE_MCP_SERVER_SCRIPT)
    return str(script)


def test_stdio_client_list_tools(tmp_path):
    from techtide_swarm.tools.mcp import StdioMCPClient
    script = _write_fake_server(tmp_path)
    client = StdioMCPClient(command=sys.executable, args=[script], env={})
    try:
        client.connect()
        tools = client.list_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "echo_text"
    finally:
        client.close()


def test_stdio_client_call_tool(tmp_path):
    from techtide_swarm.tools.mcp import StdioMCPClient
    script = _write_fake_server(tmp_path)
    client = StdioMCPClient(command=sys.executable, args=[script], env={})
    try:
        client.connect()
        result = client.call_tool("echo_text", {"text": "hello mcp"})
        assert result == "hello mcp"
    finally:
        client.close()


def test_http_client_list_tools(monkeypatch):
    from techtide_swarm.tools.mcp import HttpMCPClient
    import httpx

    RESPONSES = {
        "initialize": {"protocolVersion": "2024-11-05", "capabilities": {}, "serverInfo": {"name": "test"}},
        "tools/list": {"tools": [{"name": "search_repos", "description": "Search repos", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}}}]},
    }

    def mock_post(url, json, headers, timeout):
        method = json.get("method")
        result = RESPONSES.get(method, {})
        request = httpx.Request("POST", url, json=json, headers=headers)
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": json.get("id"), "result": result}, request=request)

    monkeypatch.setattr("techtide_swarm.tools.mcp.httpx.post", mock_post)
    client = HttpMCPClient(url="https://example.com/mcp", headers={"Authorization": "Bearer tok"})
    client.connect()
    tools = client.list_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "search_repos"


def test_http_client_call_tool(monkeypatch):
    from techtide_swarm.tools.mcp import HttpMCPClient
    import httpx

    def mock_post(url, json, headers, timeout):
        method = json.get("method")
        if method == "initialize":
            result = {"protocolVersion": "2024-11-05", "capabilities": {}}
        elif method == "tools/call":
            result = {"content": [{"type": "text", "text": "found 5 repos"}]}
        else:
            result = {}
        request = httpx.Request("POST", url, json=json, headers=headers)
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": json.get("id"), "result": result}, request=request)

    monkeypatch.setattr("techtide_swarm.tools.mcp.httpx.post", mock_post)
    client = HttpMCPClient(url="https://example.com/mcp", headers={})
    client.connect()
    result = client.call_tool("search_repos", {"query": "anthropic"})
    assert result == "found 5 repos"


def test_mcp_registry_connect_registers_tools(tmp_path):
    """Connecting via MCPRegistry registers MCP tools in the given ToolRegistry."""
    import sys
    from techtide_swarm.tools.mcp import MCPRegistry, MCPServerConfig
    from techtide_swarm.tools.registry import ToolRegistry

    isolated = ToolRegistry()
    script = _write_fake_server(tmp_path)
    cfg = MCPServerConfig(
        name="fake",
        transport="stdio",
        command=sys.executable,
        args=(script,),
        toolset="core_tools",
    )

    reg = MCPRegistry(target_registry=isolated)
    registered = reg.connect(cfg)

    assert "mcp_fake_echo_text" in registered
    result = isolated.execute_tool("mcp_fake_echo_text", {"text": "ping"})
    assert result == "ping"


def test_mcp_registry_get_status(tmp_path):
    import sys
    from techtide_swarm.tools.mcp import MCPRegistry, MCPServerConfig
    from techtide_swarm.tools.registry import ToolRegistry

    script = _write_fake_server(tmp_path)
    cfg = MCPServerConfig(name="fake", transport="stdio", command=sys.executable, args=(script,))
    reg = MCPRegistry(target_registry=ToolRegistry())
    reg.connect(cfg)

    status = reg.get_status()
    assert "fake" in status
    assert status["fake"]["connected"] is True
    assert status["fake"]["tool_count"] == 1
    assert "mcp_fake_echo_text" in status["fake"]["tools"]


def test_mcp_registry_disconnect_all(tmp_path):
    import sys
    from techtide_swarm.tools.mcp import MCPRegistry, MCPServerConfig
    from techtide_swarm.tools.registry import ToolRegistry

    script = _write_fake_server(tmp_path)
    cfg = MCPServerConfig(name="fake", transport="stdio", command=sys.executable, args=(script,))
    reg = MCPRegistry(target_registry=ToolRegistry())
    reg.connect(cfg)
    reg.disconnect_all()

    assert reg.get_status() == {}
