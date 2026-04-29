import bpy


UI_STATE_ITEMS = (
    ("disconnected", "Disconnected", "Blender MCP is not connected"),
    ("connecting", "Connecting", "Blender MCP is connecting"),
    ("connected_idle", "Connected", "Blender MCP is connected and idle"),
    ("request_running", "Running", "A request is running"),
    ("approval_pending", "Approval Pending", "An approval is pending"),
    ("request_failed", "Failed", "The last request failed"),
)


class BLENDERMCP_PG_state(bpy.types.PropertyGroup):
    ui_state: bpy.props.EnumProperty(
        name="UI State",
        items=UI_STATE_ITEMS,
        default="disconnected",
    )
    connection_label: bpy.props.StringProperty(
        name="Connection Label",
        default="Disconnected",
    )
    prompt_text: bpy.props.StringProperty(
        name="Prompt",
        default="",
    )
    history_text: bpy.props.StringProperty(
        name="History",
        default="No history yet.",
    )
    last_error: bpy.props.StringProperty(
        name="Last Error",
        default="",
    )
    pending_action_label: bpy.props.StringProperty(
        name="Pending Action",
        default="No pending actions.",
    )
