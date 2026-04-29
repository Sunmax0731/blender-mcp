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
    server_url: bpy.props.StringProperty(
        name="Server URL",
        default="http://127.0.0.1:8765",
    )
    prompt_text: bpy.props.StringProperty(
        name="Prompt",
        default="",
    )
    history_text: bpy.props.StringProperty(
        name="History",
        default="No history yet.",
    )
    last_result_text: bpy.props.StringProperty(
        name="Last Result",
        default="No command processed yet.",
    )
    last_error: bpy.props.StringProperty(
        name="Last Error",
        default="",
    )
    pending_action_label: bpy.props.StringProperty(
        name="Pending Action",
        default="No pending actions.",
    )
    blender_version: bpy.props.StringProperty(
        name="Blender Version",
        default="",
    )
    addon_version: bpy.props.StringProperty(
        name="Add-on Version",
        default="0.1.0",
    )
