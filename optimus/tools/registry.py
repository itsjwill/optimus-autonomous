"""
Tool Registry - Central registry for all available tools
"""

from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json


class ToolCategory(Enum):
    """Categories of tools."""
    FILE = "file"
    WEB = "web"
    CODE = "code"
    DATA = "data"
    COMMUNICATION = "communication"
    SYSTEM = "system"
    CUSTOM = "custom"


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    duration_ms: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tool:
    """
    A tool that can be used by agents.

    Tools are functions that agents can call to perform actions
    like reading files, making web requests, or executing code.
    """
    name: str
    description: str
    func: Callable
    category: ToolCategory = ToolCategory.CUSTOM
    parameters: Dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    enabled: bool = True

    def to_schema(self) -> Dict[str, Any]:
        """Convert tool to JSON schema for LLM function calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters,
                "required": [k for k, v in self.parameters.items() if v.get("required", False)]
            }
        }

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given arguments."""
        start_time = datetime.now()

        try:
            if asyncio.iscoroutinefunction(self.func):
                result = await self.func(**kwargs)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: self.func(**kwargs))

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=result,
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


class ToolRegistry:
    """
    Central registry for all tools available to agents.

    Provides:
    - Tool registration and discovery
    - Category-based filtering
    - Tool execution with logging
    - MCP server integration
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._execution_log: List[Dict] = []
        self._mcp_servers: Dict[str, Any] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool

    def register_function(
        self,
        name: str,
        description: str,
        func: Callable,
        category: ToolCategory = ToolCategory.CUSTOM,
        parameters: Optional[Dict[str, Any]] = None,
        requires_confirmation: bool = False
    ) -> Tool:
        """Register a function as a tool."""
        tool = Tool(
            name=name,
            description=description,
            func=func,
            category=category,
            parameters=parameters or {},
            requires_confirmation=requires_confirmation
        )
        self.register(tool)
        return tool

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self, category: Optional[ToolCategory] = None) -> List[Tool]:
        """List all tools, optionally filtered by category."""
        tools = list(self.tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return [t for t in tools if t.enabled]

    def get_schemas(self, category: Optional[ToolCategory] = None) -> List[Dict[str, Any]]:
        """Get JSON schemas for all tools (for LLM function calling)."""
        tools = self.list_tools(category)
        return [t.to_schema() for t in tools]

    async def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool not found: {tool_name}"
            )

        if not tool.enabled:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool is disabled: {tool_name}"
            )

        result = await tool.execute(**kwargs)

        # Log execution
        self._execution_log.append({
            "tool": tool_name,
            "args": kwargs,
            "success": result.success,
            "duration_ms": result.duration_ms,
            "timestamp": datetime.now().isoformat()
        })

        return result

    def disable(self, tool_name: str) -> bool:
        """Disable a tool."""
        tool = self.get(tool_name)
        if tool:
            tool.enabled = False
            return True
        return False

    def enable(self, tool_name: str) -> bool:
        """Enable a tool."""
        tool = self.get(tool_name)
        if tool:
            tool.enabled = True
            return True
        return False

    def get_execution_log(self, limit: int = 100) -> List[Dict]:
        """Get recent tool execution log."""
        return self._execution_log[-limit:]

    def clear_log(self) -> None:
        """Clear the execution log."""
        self._execution_log.clear()

    def register_mcp_server(self, name: str, server: Any) -> None:
        """Register an MCP server."""
        self._mcp_servers[name] = server

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        categories = {}
        for tool in self.tools.values():
            cat = tool.category.value
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_tools": len(self.tools),
            "enabled_tools": len([t for t in self.tools.values() if t.enabled]),
            "categories": categories,
            "mcp_servers": len(self._mcp_servers),
            "total_executions": len(self._execution_log),
        }


# Global registry instance
_global_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get the global tool registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry
