from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .addons import get_addon_status as get_addon_status_impl
from .addons import inspect_addon_capabilities as inspect_addon_capabilities_impl
from .addons import list_blender_addons as list_blender_addons_impl
from .addons import list_registered_operators as list_registered_operators_impl
from .config import ResolvedPrecisionConfig
from .mesh_quality import analyze_mesh_quality as analyze_mesh_quality_impl
from .mesh_quality import apply_mesh_cleanup as apply_mesh_cleanup_impl
from .mesh_quality import validate_retopology_result as validate_retopology_result_impl
from .operator_execution import apply_retopology as apply_retopology_impl
from .operator_execution import run_approved_addon_operator as run_approved_addon_operator_impl
from .scene_builder import assign_materials_from_spec as assign_materials_from_spec_impl
from .scene_builder import create_or_update_scene_from_spec as create_or_update_scene_from_spec_impl
from .scene_builder import create_parametric_object as create_parametric_object_impl
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
        if tool_definition.name == "create_parametric_object":
            mcp_server.add_tool(
                create_parametric_object,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "create_or_update_scene_from_spec":
            mcp_server.add_tool(
                create_or_update_scene_from_spec,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "assign_materials_from_spec":
            mcp_server.add_tool(
                assign_materials_from_spec,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "validate_scene_against_spec":
            mcp_server.add_tool(
                validate_scene_against_spec,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "analyze_mesh_quality":
            mcp_server.add_tool(
                analyze_mesh_quality,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "apply_mesh_cleanup":
            mcp_server.add_tool(
                apply_mesh_cleanup,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "validate_retopology_result":
            mcp_server.add_tool(
                validate_retopology_result,
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
        if tool_definition.name == "list_blender_addons":
            mcp_server.add_tool(
                list_blender_addons,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "get_addon_status":
            mcp_server.add_tool(
                get_addon_status,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "inspect_addon_capabilities":
            mcp_server.add_tool(
                inspect_addon_capabilities,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "list_registered_operators":
            mcp_server.add_tool(
                list_registered_operators,
                name=tool_definition.name,
                description=tool_definition.description,
            )
            continue
        if tool_definition.name == "apply_retopology":
            mcp_server.add_tool(
                apply_retopology,
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
    live_scene: bool = False,
    live_scene_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = validate_model_spec(
        spec_path=spec_path,
        output_path=output_path,
        live_scene=live_scene,
        live_scene_snapshot=live_scene_snapshot,
    )
    return {
        "success": report["status"] != "failed",
        "data": report,
    }


def create_parametric_object(
    object_spec: dict[str, Any],
    materials: list[dict[str, Any]] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    return create_parametric_object_impl(
        object_spec=object_spec,
        materials=materials,
        dry_run=dry_run,
    )


def create_or_update_scene_from_spec(
    spec_path: str = "templates/precision/model_spec.yaml",
    output_path: str | None = None,
    dry_run: bool = False,
    ensure_camera: bool = True,
    ensure_lights: bool = True,
) -> dict[str, Any]:
    return create_or_update_scene_from_spec_impl(
        spec_path=spec_path,
        output_path=output_path,
        dry_run=dry_run,
        ensure_camera=ensure_camera,
        ensure_lights=ensure_lights,
    )


def assign_materials_from_spec(
    spec_path: str = "templates/precision/model_spec.yaml",
    dry_run: bool = False,
) -> dict[str, Any]:
    return assign_materials_from_spec_impl(spec_path=spec_path, dry_run=dry_run)


def analyze_mesh_quality(
    target_objects: list[str] | None = None,
    spec_path: str = "templates/precision/model_spec.yaml",
    output_path: str | None = None,
) -> dict[str, Any]:
    return analyze_mesh_quality_impl(
        target_objects=target_objects,
        spec_path=spec_path,
        output_path=output_path,
    )


def apply_mesh_cleanup(
    target_object: str,
    operations: list[str] | None = None,
    output_path: str | None = None,
    dry_run: bool = True,
    confirm: bool = False,
    create_backup: bool = True,
) -> dict[str, Any]:
    return apply_mesh_cleanup_impl(
        target_object=target_object,
        operations=operations,
        output_path=output_path,
        dry_run=dry_run,
        confirm=confirm,
        create_backup=create_backup,
    )


def validate_retopology_result(
    target_object: str,
    spec_path: str = "templates/precision/model_spec.yaml",
    output_path: str | None = None,
) -> dict[str, Any]:
    return validate_retopology_result_impl(
        target_object=target_object,
        spec_path=spec_path,
        output_path=output_path,
    )


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


def list_blender_addons(
    registry_path: str = "templates/precision/addon_registry.yaml",
) -> dict[str, Any]:
    return list_blender_addons_impl(registry_path)


def get_addon_status(
    module: str,
    registry_path: str = "templates/precision/addon_registry.yaml",
) -> dict[str, Any]:
    return get_addon_status_impl(module=module, registry_path=registry_path)


def inspect_addon_capabilities(
    module: str | None = None,
    registry_path: str = "templates/precision/addon_registry.yaml",
) -> dict[str, Any]:
    return inspect_addon_capabilities_impl(module=module, registry_path=registry_path)


def list_registered_operators(
    registry_path: str = "templates/precision/addon_registry.yaml",
) -> dict[str, Any]:
    return list_registered_operators_impl(registry_path=registry_path)


def apply_retopology(
    target_object: str,
    target_face_count: int,
    registry_path: str = "templates/precision/addon_registry.yaml",
    dry_run: bool = True,
    confirm: bool = False,
) -> dict[str, Any]:
    return apply_retopology_impl(
        target_object=target_object,
        target_face_count=target_face_count,
        registry_path=registry_path,
        dry_run=dry_run,
        confirm=confirm,
    )


def run_approved_addon_operator(
    operator_idname: str,
    parameters: dict[str, Any] | None = None,
    registry_path: str = "templates/precision/addon_registry.yaml",
    dry_run: bool = True,
    confirm: bool = False,
) -> dict[str, Any]:
    return run_approved_addon_operator_impl(
        operator_idname=operator_idname,
        parameters=parameters,
        registry_path=registry_path,
        dry_run=dry_run,
        confirm=confirm,
    )
