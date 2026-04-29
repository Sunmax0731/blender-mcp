from .ai_suggestion import blender_request_ai_suggestion_tool
from .create_primitive import blender_create_primitive_tool
from .delete_object import blender_delete_object_tool
from .list_objects import blender_list_objects_tool
from .request_status import blender_get_request_status_tool
from .status import blender_status_tool
from .transform_object import blender_transform_object_tool


def build_tool_registry() -> dict[str, object]:
    return {
        "blender_status": blender_status_tool,
        "blender_get_request_status": blender_get_request_status_tool,
        "blender_request_ai_suggestion": blender_request_ai_suggestion_tool,
        "blender_create_primitive": blender_create_primitive_tool,
        "blender_list_objects": blender_list_objects_tool,
        "blender_transform_object": blender_transform_object_tool,
        "blender_delete_object": blender_delete_object_tool,
    }
