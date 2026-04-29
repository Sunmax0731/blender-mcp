from __future__ import annotations

from ..services.command_service import submit_blender_command


def blender_list_objects_tool(
    *,
    name_prefix: str | None = None,
    selected_only: bool = False,
    type_filter: list[str] | None = None,
) -> dict[str, object]:
    return submit_blender_command(
        action="list_objects",
        params={
            "namePrefix": name_prefix,
            "selectedOnly": selected_only,
            "typeFilter": type_filter or [],
        },
    )
