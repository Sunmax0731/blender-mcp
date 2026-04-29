import bpy


class BLENDERMCP_PT_connection(bpy.types.Panel):
    bl_label = "接続"
    bl_idname = "BLENDERMCP_PT_connection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender MCP"

    def draw(self, context):
        layout = self.layout
        state = context.scene.blender_mcp_state

        layout.label(text=f"サーバー: {state.server_url}")
        layout.label(text=f"状態: {self._state_label(state.ui_state)}")
        layout.label(text=state.connection_label)
        if state.blender_version:
            layout.label(text=f"Blender: {state.blender_version}")
        layout.label(text=f"アドオン: {state.addon_version}")

        row = layout.row(align=True)
        row.operator("blendermcp.connect", text="接続")
        row.operator("blendermcp.refresh_status", text="状態更新")

        if state.last_error:
            layout.separator()
            layout.label(text="最新エラー")
            box = layout.box()
            box.label(text=state.last_error)

    @staticmethod
    def _state_label(ui_state: str) -> str:
        return {
            "disconnected": "未接続",
            "connecting": "接続中",
            "connected_idle": "接続済み",
            "request_running": "処理中",
            "approval_pending": "承認待ち",
            "request_failed": "失敗",
        }.get(ui_state, ui_state)
