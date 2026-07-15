from typing import Any

import pytest

from secondbrain.notion import MCPTool, ReadOnlyNotionAdapter, UnsafeToolError


class FakeMCPClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def list_tools(self) -> list[MCPTool]:
        return [
            MCPTool("notion-search"),
            MCPTool("notion-fetch"),
            MCPTool("notion-create-pages"),
            MCPTool("notion-update-page"),
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, bool]:
        self.calls.append((name, arguments))
        return {"ok": True}


@pytest.mark.asyncio
async def test_only_read_tools_are_exposed() -> None:
    adapter = ReadOnlyNotionAdapter(FakeMCPClient())

    tools = await adapter.list_tools()

    assert {tool.name for tool in tools} == {"notion-search", "notion-fetch"}


@pytest.mark.asyncio
async def test_read_tool_is_forwarded() -> None:
    client = FakeMCPClient()
    adapter = ReadOnlyNotionAdapter(client)

    result = await adapter.call_tool("notion-search", {"query": "PTO"})

    assert result == {"ok": True}
    assert client.calls == [("notion-search", {"query": "PTO"})]


@pytest.mark.asyncio
async def test_write_tool_is_rejected_without_calling_client() -> None:
    client = FakeMCPClient()
    adapter = ReadOnlyNotionAdapter(client)

    with pytest.raises(UnsafeToolError, match="notion-update-page"):
        await adapter.call_tool("notion-update-page", {"page_id": "secret"})

    assert client.calls == []
