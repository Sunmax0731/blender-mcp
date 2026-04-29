from .create_primitive import blender_create_primitive_tool
from .delete_object import blender_delete_object_tool
from .list_objects import blender_list_objects_tool
from .status import blender_status_tool


def build_tool_registry() -> dict[str, object]:
    return {
        "blender_status": blender_status_tool,
        "blender_create_primitive": blender_create_primitive_tool,
        "blender_list_objects": blender_list_objects_tool,
        "blender_delete_object": blender_delete_object_tool,
    }
