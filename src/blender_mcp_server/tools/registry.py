from .status import blender_status_tool


def build_tool_registry() -> dict[str, object]:
    return {
        "blender_status": blender_status_tool,
    }
