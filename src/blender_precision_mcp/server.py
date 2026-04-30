from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import ResolvedPrecisionConfig
from .tool_catalog import not_implemented_payload
from .tool_catalog import resolve_public_tool_definitions


def create_mcp_server(resolved: ResolvedPrecisionConfig) -> FastMCP:
    mcp_server = FastMCP(name=resolved.config.server.name)

    @mcp_server.tool(name="precision_status")
    def precision_status() -> dict[str, object]:
        return {
            "success": True,
            "data": resolved.to_summary(),
        }

    @mcp_server.tool(name="precision_get_config_summary")
    def precision_get_config_summary() -> dict[str, object]:
        return {
            "success": True,
            "data": resolved.to_summary(),
        }

    for tool_definition in resolve_public_tool_definitions(resolved.enabled_tools):
        mcp_server.add_tool(
            _make_pending_tool(tool_definition.name),
            name=tool_definition.name,
            description=tool_definition.description,
        )

    return mcp_server


def _make_pending_tool(tool_name: str):
    def pending_tool(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        return not_implemented_payload(tool_name, arguments=arguments)

    pending_tool.__name__ = f"pending_{tool_name}"
    return pending_tool
