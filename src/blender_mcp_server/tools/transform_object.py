from __future__ import annotations

from ..services.command_service import submit_blender_command


def blender_transform_object_tool(
    *,
    target_object_name: str,
    location: list[float] | None = None,
    rotation_euler: list[float] | None = None,
    scale: list[float] | None = None,
    mode: str = "absolute",
) -> dict[str, object]:
    return submit_blender_command(
        action="transform_object",
        params={
            "targetObjectName": target_object_name,
            "location": location or [0.0, 0.0, 0.0],
            "rotationEuler": rotation_euler or [0.0, 0.0, 0.0],
            "scale": scale or [1.0, 1.0, 1.0],
            "mode": mode,
        },
    )
