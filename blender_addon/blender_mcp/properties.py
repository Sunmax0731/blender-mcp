import bpy


UI_STATE_ITEMS = (
    ("disconnected", "未接続", "Blender MCP is not connected"),
    ("connecting", "接続中", "Blender MCP is connecting"),
    ("connected_idle", "接続済み", "Blender MCP is connected and idle"),
    ("request_running", "処理中", "A request is running"),
    ("approval_pending", "承認待ち", "An approval is pending"),
    ("request_failed", "失敗", "The last request failed"),
)


class BLENDERMCP_PG_state(bpy.types.PropertyGroup):
    ui_state: bpy.props.EnumProperty(
        name="UI State",
        items=UI_STATE_ITEMS,
        default="disconnected",
    )
    connection_label: bpy.props.StringProperty(
        name="Connection Label",
        default="未接続",
    )
    server_url: bpy.props.StringProperty(
        name="Server URL",
        default="http://127.0.0.1:8765",
    )
    prompt_text: bpy.props.StringProperty(
        name="Prompt",
        default="",
    )
    prompt_plan_text: bpy.props.StringProperty(
        name="Prompt Plan",
        default="実行計画はまだありません。",
    )
    prompt_preview_text: bpy.props.StringProperty(
        name="Prompt Preview",
        default="Preview はまだありません。",
    )
    prompt_confirmed: bpy.props.BoolProperty(
        name="Prompt Confirmed",
        default=False,
    )
    history_text: bpy.props.StringProperty(
        name="History",
        default="履歴はまだありません。",
    )
    last_result_text: bpy.props.StringProperty(
        name="Last Result",
        default="まだ結果はありません。",
    )
    last_error: bpy.props.StringProperty(
        name="Last Error",
        default="",
    )
    pending_action_label: bpy.props.StringProperty(
        name="Pending Action",
        default="承認待ちの操作はありません。",
    )
    pending_request_id: bpy.props.StringProperty(
        name="Pending Request ID",
        default="",
    )
    pending_command_json: bpy.props.StringProperty(
        name="Pending Command JSON",
        default="",
    )
    blender_version: bpy.props.StringProperty(
        name="Blender Version",
        default="",
    )
    addon_version: bpy.props.StringProperty(
        name="Add-on Version",
        default="0.1.1",
    )
