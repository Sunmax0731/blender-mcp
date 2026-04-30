from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CONTROL_TOOLS = (
    "precision_status",
    "precision_get_config_summary",
)


@dataclass(frozen=True, slots=True)
class PrecisionToolDefinition:
    name: str
    description: str
    implemented: bool = False


TOOL_CATALOG: dict[str, PrecisionToolDefinition] = {
    "get_scene_snapshot": PrecisionToolDefinition(
        name="get_scene_snapshot",
        description="Return a normalized summary of the current Blender scene.",
    ),
    "create_parametric_object": PrecisionToolDefinition(
        name="create_parametric_object",
        description="Create a parameterized Blender object from structured arguments.",
    ),
    "create_or_update_scene_from_spec": PrecisionToolDefinition(
        name="create_or_update_scene_from_spec",
        description="Create or update a Blender scene from model_spec data.",
    ),
    "assign_materials_from_spec": PrecisionToolDefinition(
        name="assign_materials_from_spec",
        description="Assign Blender materials from model_spec definitions.",
    ),
    "export_scene": PrecisionToolDefinition(
        name="export_scene",
        description="Export the scene using an approved output profile.",
    ),
    "validate_scene_against_spec": PrecisionToolDefinition(
        name="validate_scene_against_spec",
        description="Validate scene objects, transforms, materials, and evidence against model_spec.",
    ),
    "analyze_mesh_quality": PrecisionToolDefinition(
        name="analyze_mesh_quality",
        description="Analyze mesh quality metrics such as loose geometry and non-manifold edges.",
    ),
    "validate_retopology_result": PrecisionToolDefinition(
        name="validate_retopology_result",
        description="Validate retopology output against quality thresholds.",
    ),
    "capture_review_views": PrecisionToolDefinition(
        name="capture_review_views",
        description="Capture standard viewport review images for human visual QA.",
    ),
    "list_blender_addons": PrecisionToolDefinition(
        name="list_blender_addons",
        description="List installed Blender add-ons and their enabled status.",
    ),
    "get_addon_status": PrecisionToolDefinition(
        name="get_addon_status",
        description="Return status for a specific Blender add-on module.",
    ),
    "inspect_addon_capabilities": PrecisionToolDefinition(
        name="inspect_addon_capabilities",
        description="Inspect approved add-on operators and public Python API capabilities.",
    ),
    "list_registered_operators": PrecisionToolDefinition(
        name="list_registered_operators",
        description="List registered Blender operators relevant to approved add-on workflows.",
    ),
    "enable_approved_addon": PrecisionToolDefinition(
        name="enable_approved_addon",
        description="Enable an add-on only when it is listed in the approved add-on registry.",
    ),
    "backup_object": PrecisionToolDefinition(
        name="backup_object",
        description="Create a backup before destructive object operations.",
    ),
    "restore_object_backup": PrecisionToolDefinition(
        name="restore_object_backup",
        description="Restore a previously created object backup.",
    ),
    "apply_mesh_cleanup": PrecisionToolDefinition(
        name="apply_mesh_cleanup",
        description="Apply an approved mesh cleanup workflow.",
    ),
    "apply_retopology": PrecisionToolDefinition(
        name="apply_retopology",
        description="Apply an approved retopology workflow.",
    ),
    "apply_uv_unwrap": PrecisionToolDefinition(
        name="apply_uv_unwrap",
        description="Apply an approved UV unwrap workflow.",
    ),
    "transfer_mesh_data": PrecisionToolDefinition(
        name="transfer_mesh_data",
        description="Transfer mesh data between approved source and target objects.",
    ),
}


def resolve_public_tool_definitions(enabled_tool_names: tuple[str, ...]) -> list[PrecisionToolDefinition]:
    definitions: list[PrecisionToolDefinition] = []
    for tool_name in enabled_tool_names:
        definitions.append(
            TOOL_CATALOG.get(
                tool_name,
                PrecisionToolDefinition(
                    name=tool_name,
                    description="Configured precision tool. Implementation is pending.",
                ),
            )
        )
    return definitions


def not_implemented_payload(tool_name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": "not_implemented",
            "message": f"{tool_name} is exposed by the active profile but is not implemented yet.",
        },
        "data": {
            "tool": tool_name,
            "arguments": arguments or {},
        },
    }
