from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import ResolvedPrecisionConfig
from .tool_catalog import not_implemented_payload
from .tool_catalog import resolve_public_tool_definitions
from .validation import validate_model_spec
from .visual_qa import capture_review_views as capture_review_views_impl


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
        if tool_definition.name == "validate_scene_against_spec":
            mcp_server.add_tool(
                validate_scene_against_spec,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "capture_review_views":
            mcp_server.add_tool(
                capture_review_views,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
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


def validate_scene_against_spec(
    spec_path: str = "templates/precision/model_spec.yaml",
    output_path: str | None = None,
) -> dict[str, Any]:
    report = validate_model_spec(spec_path=spec_path, output_path=output_path)
    return {
        "success": report["status"] != "failed",
        "data": report,
    }


def capture_review_views(
    spec_path: str = "templates/precision/model_spec.yaml",
    output_dir: str | None = None,
    views: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    result = capture_review_views_impl(
        spec_path=spec_path,
        output_dir=output_dir,
        views=tuple(views) if views else None,
        dry_run=dry_run,
    )
    return {
        "success": result["status"] == "captured",
        "data": result,
    }
