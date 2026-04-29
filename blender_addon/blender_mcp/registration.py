from .operators.approval import BLENDERMCP_OT_reject_action
from .operators.connection import BLENDERMCP_OT_connect
from .operators.connection import BLENDERMCP_OT_refresh_status
from .operators.session import BLENDERMCP_OT_send_prompt
from .panels.approval import BLENDERMCP_PT_approval
from .panels.connection import BLENDERMCP_PT_connection
from .panels.session import BLENDERMCP_PT_session
from .properties import BLENDERMCP_PG_state


CLASSES = (
    BLENDERMCP_PG_state,
    BLENDERMCP_OT_connect,
    BLENDERMCP_OT_refresh_status,
    BLENDERMCP_OT_send_prompt,
    BLENDERMCP_OT_reject_action,
    BLENDERMCP_PT_connection,
    BLENDERMCP_PT_session,
    BLENDERMCP_PT_approval,
)


def register_addon():
    import bpy

    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.blender_mcp_state = bpy.props.PointerProperty(type=BLENDERMCP_PG_state)


def unregister_addon():
    import bpy

    del bpy.types.Scene.blender_mcp_state

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
