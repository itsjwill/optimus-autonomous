"""
MCP Client - Model Context Protocol integration
Connects to MCP servers for standardized tool access.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .registry import Tool, ToolResult, ToolCategory, ToolRegistry


@dataclass
class MCPServer:
    """An MCP server connection."""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    process: Optional[Any] = None
    connected: bool = False
    tools: List[Dict] = field(default_factory=list)


class MCPClient:
    """
    Client for connecting to MCP (Model Context Protocol) servers.

    MCP provides a standardized way for AI agents to access tools
    like file systems, databases, APIs, and more.

    Supports:
    - stdio-based MCP servers
    - Tool discovery and execution
    - Multiple server connections
    - Automatic reconnection
    """

    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.servers: Dict[str, MCPServer] = {}
        self.registry = registry
        self._initialized = False

    async def connect(self, name: str, command: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None) -> bool:
        """
        Connect to an MCP server.

        Args:
            name: Unique name for this server connection
            command: Command to run the server (e.g., "npx", "python")
            args: Arguments to pass to the command
            env: Environment variables for the server

        Returns:
            True if connection successful
        """
        server = MCPServer(
            name=name,
            command=command,
            args=args or [],
            env=env or {}
        )

        try:
            # Start the MCP server process
            process = await asyncio.create_subprocess_exec(
                command,
                *server.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**dict(__import__('os').environ), **server.env}
            )
            server.process = process
            server.connected = True

            # Initialize the connection
            await self._send_message(server, {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "optimus-autonomous",
                        "version": "0.1.0"
                    }
                }
            })

            # List available tools
            tools_response = await self._send_message(server, {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            })

            if tools_response and "result" in tools_response:
                server.tools = tools_response["result"].get("tools", [])

                # Register tools with the registry
                if self.registry:
                    for tool_def in server.tools:
                        self._register_mcp_tool(server, tool_def)

            self.servers[name] = server
            print(f"[MCP] Connected to {name}: {len(server.tools)} tools available")
            return True

        except Exception as e:
            print(f"[MCP] Failed to connect to {name}: {e}")
            return False

    async def disconnect(self, name: str) -> None:
        """Disconnect from an MCP server."""
        if name in self.servers:
            server = self.servers[name]
            if server.process:
                server.process.terminate()
                await server.process.wait()
            server.connected = False
            del self.servers[name]
            print(f"[MCP] Disconnected from {name}")

    async def disconnect_all(self) -> None:
        """Disconnect from all MCP servers."""
        for name in list(self.servers.keys()):
            await self.disconnect(name)

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        Call a tool on an MCP server.

        Args:
            server_name: Name of the server
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            ToolResult with the output
        """
        if server_name not in self.servers:
            return ToolResult(
                success=False,
                output=None,
                error=f"Server not connected: {server_name}"
            )

        server = self.servers[server_name]
        if not server.connected:
            return ToolResult(
                success=False,
                output=None,
                error=f"Server disconnected: {server_name}"
            )

        start_time = datetime.now()

        try:
            response = await self._send_message(server, {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            })

            duration = (datetime.now() - start_time).total_seconds() * 1000

            if response and "result" in response:
                content = response["result"].get("content", [])
                # Extract text content
                output = ""
                for item in content:
                    if item.get("type") == "text":
                        output += item.get("text", "")

                return ToolResult(
                    success=True,
                    output=output,
                    duration_ms=duration
                )
            elif response and "error" in response:
                return ToolResult(
                    success=False,
                    output=None,
                    error=response["error"].get("message", "Unknown error"),
                    duration_ms=duration
                )
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error="Invalid response from server",
                    duration_ms=duration
                )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def _send_message(self, server: MCPServer, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a JSON-RPC message to an MCP server."""
        if not server.process or not server.process.stdin:
            return None

        try:
            # Send message
            msg_bytes = (json.dumps(message) + "\n").encode()
            server.process.stdin.write(msg_bytes)
            await server.process.stdin.drain()

            # Read response
            if server.process.stdout:
                response_line = await asyncio.wait_for(
                    server.process.stdout.readline(),
                    timeout=30.0
                )
                if response_line:
                    return json.loads(response_line.decode())

        except asyncio.TimeoutError:
            print(f"[MCP] Timeout waiting for response from {server.name}")
        except Exception as e:
            print(f"[MCP] Error communicating with {server.name}: {e}")

        return None

    def _register_mcp_tool(self, server: MCPServer, tool_def: Dict[str, Any]) -> None:
        """Register an MCP tool with the local registry."""
        if not self.registry:
            return

        tool_name = tool_def.get("name", "unknown")
        full_name = f"{server.name}:{tool_name}"

        # Create a wrapper function for this tool
        async def tool_wrapper(**kwargs):
            return await self.call_tool(server.name, tool_name, kwargs)

        # Convert MCP schema to our format
        input_schema = tool_def.get("inputSchema", {})
        parameters = {}
        if "properties" in input_schema:
            for prop_name, prop_def in input_schema["properties"].items():
                parameters[prop_name] = {
                    "type": prop_def.get("type", "string"),
                    "description": prop_def.get("description", ""),
                    "required": prop_name in input_schema.get("required", [])
                }

        tool = Tool(
            name=full_name,
            description=tool_def.get("description", f"MCP tool: {tool_name}"),
            func=tool_wrapper,
            category=ToolCategory.CUSTOM,
            parameters=parameters
        )

        self.registry.register(tool)

    def list_servers(self) -> List[Dict[str, Any]]:
        """List all connected servers."""
        return [
            {
                "name": name,
                "connected": server.connected,
                "tools": len(server.tools)
            }
            for name, server in self.servers.items()
        ]

    def list_tools(self, server_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tools from servers."""
        tools = []
        servers = [self.servers[server_name]] if server_name and server_name in self.servers else self.servers.values()

        for server in servers:
            for tool in server.tools:
                tools.append({
                    "server": server.name,
                    "name": tool.get("name"),
                    "description": tool.get("description")
                })

        return tools

    def get_stats(self) -> Dict[str, Any]:
        """Get MCP client statistics."""
        total_tools = sum(len(s.tools) for s in self.servers.values())
        return {
            "servers_connected": len([s for s in self.servers.values() if s.connected]),
            "total_servers": len(self.servers),
            "total_tools": total_tools,
        }


# Common MCP server configurations
MCP_SERVERS = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    "postgres": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres"]
    },
    "sqlite": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite"]
    },
    "puppeteer": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "brave-search": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"]
    },
    "fetch": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "memory": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "slack": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-slack"]
    },
    "google-drive": {
        "command": "npx",
        "args": ["-y", "@anthropics/mcp-server-google-drive"]
    },
}


async def connect_default_servers(client: MCPClient, servers: Optional[List[str]] = None) -> Dict[str, bool]:
    """
    Connect to common MCP servers.

    Args:
        client: MCPClient instance
        servers: List of server names to connect (defaults to filesystem and fetch)

    Returns:
        Dict of server name to connection success
    """
    servers = servers or ["filesystem", "fetch"]
    results = {}

    for server_name in servers:
        if server_name in MCP_SERVERS:
            config = MCP_SERVERS[server_name]
            success = await client.connect(
                name=server_name,
                command=config["command"],
                args=config.get("args", []),
                env=config.get("env", {})
            )
            results[server_name] = success
        else:
            print(f"[MCP] Unknown server: {server_name}")
            results[server_name] = False

    return results
