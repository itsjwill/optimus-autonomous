"""
Optimus Tools - MCP and tool integrations
by itsJWill (BillyCoder)
"""

from .registry import ToolRegistry, Tool, ToolResult, ToolCategory, get_registry
from .mcp_client import MCPClient, MCP_SERVERS, connect_default_servers
from .browser import BrowserTool
from .file_tools import FileTools
from .web_tools import WebTools

__all__ = [
    "ToolRegistry",
    "Tool",
    "ToolResult",
    "ToolCategory",
    "get_registry",
    "MCPClient",
    "MCP_SERVERS",
    "connect_default_servers",
    "BrowserTool",
    "FileTools",
    "WebTools",
]
