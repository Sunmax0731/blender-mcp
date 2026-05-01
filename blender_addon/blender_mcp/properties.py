import bpy


GENERATION_SERVICE_ITEMS = (
    ("meshy", "Meshy", "Meshy を使って 3D 生成します。"),
    ("tripo", "Tripo AI", "Tripo AI を使って 3D 生成します。"),
    ("rodin", "Hyper3D Rodin", "Hyper3D Rodin を使って 3D 生成します。"),
    ("spar3d", "Stability API SPAR3D", "Stability API SPAR3D を使って 3D 生成します。"),
)


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
    external_service_overview_text: bpy.props.StringProperty(
        name="External Service Overview",
        default="サービス設定はまだ読み込まれていません。",
    )
    external_service_last_error: bpy.props.StringProperty(
        name="External Service Error",
        default="",
    )
    generation_service_key: bpy.props.EnumProperty(
        name="Generation Service",
        items=GENERATION_SERVICE_ITEMS,
        default="meshy",
    )
    generation_prompt_text: bpy.props.StringProperty(
        name="Generation Prompt",
        default="",
    )
    generation_payload_json: bpy.props.StringProperty(
        name="Generation Payload JSON",
        default="",
    )
    generation_last_task_id: bpy.props.StringProperty(
        name="Generation Last Task ID",
        default="",
    )
    generation_last_subscription_key: bpy.props.StringProperty(
        name="Generation Last Subscription Key",
        default="",
    )
    generation_last_status: bpy.props.StringProperty(
        name="Generation Last Status",
        default="未実行",
    )
    generation_last_result_url: bpy.props.StringProperty(
        name="Generation Last Result URL",
        default="",
    )
    generation_last_response_text: bpy.props.StringProperty(
        name="Generation Last Response",
        default="生成系サービスの実行結果はまだありません。",
    )
    generation_import_collection_name: bpy.props.StringProperty(
        name="Generation Import Collection",
        default="Generated_External_Assets",
    )
    polyhaven_query_text: bpy.props.StringProperty(
        name="Poly Haven Query",
        default="",
    )
    polyhaven_category_text: bpy.props.StringProperty(
        name="Poly Haven Category",
        default="",
    )
    polyhaven_asset_type: bpy.props.EnumProperty(
        name="Poly Haven Asset Type",
        items=(
            ("all", "All", "すべての asset を対象にします。"),
            ("hdris", "HDRIs", "HDRI のみを対象にします。"),
            ("textures", "Textures", "Texture のみを対象にします。"),
            ("models", "Models", "Model のみを対象にします。"),
        ),
        default="all",
    )
    polyhaven_results_text: bpy.props.StringProperty(
        name="Poly Haven Results",
        default="検索結果はまだありません。",
    )
