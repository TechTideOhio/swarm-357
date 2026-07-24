"""
MCP (Model Context Protocol) client integration for TechTide Swarm 357.

Connects to any MCP server via stdio subprocess or HTTP and exposes
its tools through the central ToolRegistry under mcp_{server}_{tool} names.

Transports supported:
  stdio - launches a local subprocess (e.g. npx firecrawl-mcp)
  http  - sends JSON-RPC 2.0 POST requests to a remote URL

Usage:
    from techtide_swarm.tools.mcp import mcp_registry, load_mcp_configs
    configs = load_mcp_configs("config/mcp")
    for cfg in configs:
        mcp_registry.connect(cfg)
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, cast

import httpx
import yaml

from techtide_swarm.tools.registry import ToolRegistry, registry

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MCPServerConfig:
    """Parsed MCP server configuration from a YAML file."""
    name: str
    description: str = ""
    transport: str = "stdio"
    command: str = ""
    args: tuple[str, ...] = field(default_factory=tuple)
    env: dict[str, str] = field(default_factory=dict)
    url: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    toolset: str = "core_tools"
    enabled: bool = True


def resolve_env(env: dict[str, str]) -> dict[str, str]:
    """Resolve ${VAR} references in env values from os.environ."""
    def _replace(m: re.Match[str]) -> str:
        return os.environ.get(m.group(1), "")

    return {key: re.sub(r"\$\{([^}]+)\}", _replace, str(val)) for key, val in env.items()}


def _mcp_tool_name(server_name: str, tool_name: str) -> str:
    """Build a registry tool name for an MCP tool, avoiding double-prefixing.

    Examples::

        _mcp_tool_name("firecrawl", "firecrawl_scrape")     -> "mcp_firecrawl_scrape"
        _mcp_tool_name("github", "create_or_update_file")   -> "mcp_github_create_or_update_file"
    """
    if tool_name.startswith(server_name + "_"):
        return f"mcp_{tool_name}"
    return f"mcp_{server_name}_{tool_name}"


def load_mcp_configs(config_dir: str | Path = "config/mcp") -> list[MCPServerConfig]:
    """Load all enabled MCP server configs from config_dir/*.yaml."""
    config_path = Path(config_dir)
    if not config_path.is_dir():
        return []
    configs: list[MCPServerConfig] = []
    for yaml_file in sorted(config_path.glob("*.yaml")):
        try:
            raw: dict[str, Any] = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or {}
            cfg = MCPServerConfig(
                name=raw.get("name", yaml_file.stem),
                description=raw.get("description", ""),
                transport=raw.get("transport", "stdio"),
                command=raw.get("command", ""),
                args=tuple(str(a) for a in raw.get("args", [])),
                env={str(k): str(v) for k, v in raw.get("env", {}).items()},
                url=raw.get("url", ""),
                headers={str(k): str(v) for k, v in raw.get("headers", {}).items()},
                toolset=raw.get("toolset", "core_tools"),
                enabled=bool(raw.get("enabled", True)),
            )
            if cfg.enabled:
                configs.append(cfg)
        except Exception as exc:
            logger.warning("Failed to load MCP config %s: %s", yaml_file, exc)
    return configs


# ---------------------------------------------------------------------------
# Stdio transport
# ---------------------------------------------------------------------------

class StdioMCPClient:
    """MCP client over a stdio subprocess (JSON-RPC 2.0 on stdin/stdout)."""

    def __init__(self, command: str, args: list[str], env: dict[str, str]) -> None:
        self._command = command
        self._args = args
        self._env = env
        self._proc: subprocess.Popen[bytes] | None = None
        self._next_id = 1
        self._lock = threading.Lock()

    def connect(self) -> None:
        """Launch subprocess and run MCP initialize handshake."""
        merged_env = {**os.environ, **self._env}
        self._proc = subprocess.Popen(
            [self._command] + self._args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=merged_env,
        )
        # initialize handshake
        self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "techtide-swarm", "version": "1.0.0"},
        })
        # send initialized notification (no id = notification, no response expected)
        notif = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        assert self._proc.stdin is not None
        self._proc.stdin.write(notif.encode())
        self._proc.stdin.flush()

    def _send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a JSON-RPC request and return the response dict."""
        assert self._proc is not None, "Call connect() before sending"
        assert self._proc.stdin is not None
        assert self._proc.stdout is not None

        with self._lock:
            msg_id = self._next_id
            self._next_id += 1
            request: dict[str, Any] = {"jsonrpc": "2.0", "id": msg_id, "method": method}
            if params is not None:
                request["params"] = params
            self._proc.stdin.write((json.dumps(request) + "\n").encode())
            self._proc.stdin.flush()
            # Read lines until we find our response (skip notifications)
            while True:
                raw = self._proc.stdout.readline()
                if not raw:
                    raise RuntimeError("MCP subprocess closed stdout unexpectedly")
                try:
                    resp: dict[str, Any] = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if resp.get("id") == msg_id:
                    if "error" in resp:
                        raise RuntimeError(f"MCP error: {resp['error']}")
                    return resp
                # else: notification or different id - skip

    def list_tools(self) -> list[dict[str, Any]]:
        """Return the tool definitions from the MCP server."""
        resp = self._send("tools/list", {})
        return cast(
            list[dict[str, Any]],
            resp.get("result", {}).get("tools", []),
        )

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Call a named tool and return its output as a plain string."""
        resp = self._send("tools/call", {"name": name, "arguments": arguments})
        content = cast(list[dict[str, Any]], resp.get("result", {}).get("content", []))
        texts = [block.get("text", "") for block in content if block.get("type") == "text"]
        if texts:
            return "\n".join(texts)
        return json.dumps(resp.get("result", {}))

    def close(self) -> None:
        """Terminate the subprocess."""
        if self._proc is not None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None


# ---------------------------------------------------------------------------
# HTTP transport
# ---------------------------------------------------------------------------

class HttpMCPClient:
    """MCP client over HTTP (JSON-RPC 2.0 POST)."""

    def __init__(self, url: str, headers: dict[str, str]) -> None:
        self._url = url
        self._headers = {"Content-Type": "application/json", **headers}
        self._next_id = 1

    def connect(self) -> None:
        """Run MCP initialize handshake over HTTP."""
        self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "techtide-swarm", "version": "1.0.0"},
        })

    def _send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send JSON-RPC 2.0 POST request, return response dict."""
        msg_id = self._next_id
        self._next_id += 1
        request: dict[str, Any] = {"jsonrpc": "2.0", "id": msg_id, "method": method}
        if params is not None:
            request["params"] = params
        resp = httpx.post(self._url, json=request, headers=self._headers, timeout=30)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        if "error" in data:
            raise RuntimeError(f"MCP HTTP error: {data['error']}")
        return data

    def list_tools(self) -> list[dict[str, Any]]:
        """Return the tool definitions from the MCP server."""
        resp = self._send("tools/list", {})
        return cast(
            list[dict[str, Any]],
            resp.get("result", {}).get("tools", []),
        )

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Call a named tool and return its output as a plain string."""
        resp = self._send("tools/call", {"name": name, "arguments": arguments})
        content = cast(list[dict[str, Any]], resp.get("result", {}).get("content", []))
        texts = [block.get("text", "") for block in content if block.get("type") == "text"]
        if texts:
            return "\n".join(texts)
        return json.dumps(resp.get("result", {}))

    def close(self) -> None:
        """No-op: stateless HTTP transport has nothing to tear down."""
        pass


# ---------------------------------------------------------------------------
# Registry - manages active connections + tool auto-registration
# ---------------------------------------------------------------------------

class MCPRegistry:
    """Manages MCP server connections and auto-registers their tools in ToolRegistry.

    Args:
        target_registry: Which ToolRegistry to register tools into.
            Defaults to the module-level singleton ``registry``.
    """

    def __init__(self, target_registry: ToolRegistry | None = None) -> None:
        self._reg = target_registry if target_registry is not None else registry
        self._clients: dict[str, StdioMCPClient | HttpMCPClient] = {}
        self._server_tools: dict[str, list[str]] = {}

    def connect(self, config: MCPServerConfig) -> list[str]:
        """Connect to an MCP server, register its tools, return registered tool names."""
        resolved_env = resolve_env(config.env)
        resolved_headers = resolve_env(config.headers)

        if config.transport == "http":
            client: StdioMCPClient | HttpMCPClient = HttpMCPClient(
                url=config.url, headers=resolved_headers
            )
        else:
            client = StdioMCPClient(
                command=config.command, args=list(config.args), env=resolved_env
            )

        try:
            client.connect()
        except Exception as exc:
            raise RuntimeError(f"MCP connect failed for '{config.name}': {exc}") from exc

        try:
            tools = client.list_tools()
        except Exception as exc:
            client.close()
            raise RuntimeError(f"MCP tools/list failed for '{config.name}': {exc}") from exc

        registered: list[str] = []
        for tool_def in tools:
            raw_name: str = tool_def.get("name", "")
            if not raw_name:
                continue
            tool_name = _mcp_tool_name(config.name, raw_name)
            description: str = tool_def.get(
                "description", f"MCP tool {raw_name} from {config.name}"
            )
            input_schema: dict[str, Any] = tool_def.get(
                "inputSchema", {"type": "object", "properties": {}}
            )

            def _make_handler(
                c: StdioMCPClient | HttpMCPClient, rn: str, tn: str
            ) -> Callable[..., str]:
                def handler(**kwargs: Any) -> str:
                    return c.call_tool(rn, kwargs)
                handler.__name__ = tn
                return handler

            self._reg.register(
                name=tool_name,
                schema={"description": description, "input_schema": input_schema},
                handler=_make_handler(client, raw_name, tool_name),
                toolset=config.toolset,
                description=description,
            )
            registered.append(tool_name)
            logger.info("Registered MCP tool: %s (server=%s)", tool_name, config.name)

        self._clients[config.name] = client
        self._server_tools[config.name] = registered
        logger.info(
            "MCP server '%s' connected: %d tools registered", config.name, len(registered)
        )
        return registered

    def get_status(self) -> dict[str, dict[str, Any]]:
        """Return connection status for all connected servers."""
        return {
            name: {
                "connected": name in self._clients,
                "tools": tools,
                "tool_count": len(tools),
            }
            for name, tools in self._server_tools.items()
        }

    def disconnect_all(self) -> None:
        """Close all active MCP connections."""
        for client in self._clients.values():
            try:
                client.close()
            except Exception as exc:
                logger.warning("Error closing MCP client: %s", exc)
        self._clients.clear()
        self._server_tools.clear()


# Module-level singleton - CLI and boot code import this.
mcp_registry = MCPRegistry()
