"""Read-only boundary around a Notion MCP client.

The agent must receive tools through this adapter instead of using an MCP client
directly. That makes write access impossible by construction, rather than merely
discouraging it in a system prompt.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol


# Tool names exposed by Notion's hosted MCP server. Keep this deliberately small:
# a newly added server tool is unavailable until it has been reviewed and added.
READ_ONLY_TOOL_NAMES = frozenset({"notion-fetch", "notion-search"})


class UnsafeToolError(ValueError):
    """Raised when code attempts to invoke a non-allow-listed MCP tool."""


@dataclass(frozen=True, slots=True)
class MCPTool:
    """The tool metadata needed by the agent's tool-binding layer."""

    name: str
    description: str = ""
    input_schema: Mapping[str, Any] | None = None


class MCPClient(Protocol):
    """Minimal client interface used by the adapter.

    A concrete MCP SDK client can satisfy this protocol without inheritance.
    """

    async def list_tools(self) -> Sequence[MCPTool]: ...

    async def call_tool(self, name: str, arguments: Mapping[str, Any]) -> Any: ...


class ReadOnlyNotionAdapter:
    """Expose and execute only reviewed Notion read operations."""

    def __init__(self, client: MCPClient) -> None:
        self._client = client

    async def list_tools(self) -> tuple[MCPTool, ...]:
        """Return the intersection of server tools and the fixed allow-list."""
        tools = await self._client.list_tools()
        return tuple(tool for tool in tools if tool.name in READ_ONLY_TOOL_NAMES)

    async def call_tool(self, name: str, arguments: Mapping[str, Any]) -> Any:
        """Invoke a read tool, rejecting every other name before network access."""
        if name not in READ_ONLY_TOOL_NAMES:
            raise UnsafeToolError(f"Notion MCP tool is not allowed: {name!r}")
        return await self._client.call_tool(name, arguments)
