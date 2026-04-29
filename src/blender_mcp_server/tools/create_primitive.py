from __future__ import annotations

from ..services.command_service import submit_blender_command


def blender_create_primitive_tool(
    *,
    primitive_type: str,
    name: str | None = None,
    location: list[float] | None = None,
    rotation_euler: list[float] | None = None,
    scale: list[float] | None = None,
) -> dict[str, object]:
    return submit_blender_command(
        action="create_primitive",
        params={
            "type": primitive_type,
            "name": name,
            "location": location or [0.0, 0.0, 0.0],
            "rotationEuler": rotation_euler or [0.0, 0.0, 0.0],
            "scale": scale or [1.0, 1.0, 1.0],
        },
    )
