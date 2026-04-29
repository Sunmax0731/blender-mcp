from __future__ import annotations

from ..services.command_service import submit_blender_command


def blender_delete_object_tool(*, target_object_name: str) -> dict[str, object]:
    return submit_blender_command(
        action="delete_object",
        params={
            "targetObjectName": target_object_name,
        },
        requires_confirmation=True,
    )
