import bpy

from ..services.http_client import request_connection_status


class BLENDERMCP_OT_connect(bpy.types.Operator):
    bl_idname = "blendermcp.connect"
    bl_label = "接続"
    bl_description = "ローカル MCP サーバーへ接続します"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        state.ui_state = "connecting"
        state.connection_label = "ローカル MCP サーバーへ接続中..."
        state.last_error = ""
        blender_version = ".".join(str(x) for x in bpy.app.version[:3])
        state.blender_version = blender_version

        response = request_connection_status(
            addon_version=state.addon_version,
            blender_version=blender_version,
        )
        if response.get("success"):
            state.ui_state = "connected_idle"
            state.connection_label = "接続済み"
            state.history_text = "ローカル MCP サーバーへ接続しました。"
            return {"FINISHED"}

        error_message = response.get("error", {}).get("message", "接続エラーが発生しました。")
        state.ui_state = "request_failed"
        state.connection_label = "接続エラー"
        state.last_error = error_message
        return {"CANCELLED"}


class BLENDERMCP_OT_refresh_status(bpy.types.Operator):
    bl_idname = "blendermcp.refresh_status"
    bl_label = "状態更新"
    bl_description = "現在の接続状態を更新します"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        blender_version = ".".join(str(x) for x in bpy.app.version[:3])
        state.blender_version = blender_version
        response = request_connection_status(
            addon_version=state.addon_version,
            blender_version=blender_version,
        )

        if response.get("success"):
            transport_status = response.get("data", {}).get("transportStatus", "disconnected")
            if transport_status == "connected":
                state.ui_state = "connected_idle"
                state.connection_label = "接続済み"
                state.last_error = ""
            else:
                state.ui_state = "disconnected"
                state.connection_label = "未接続"
        else:
            state.ui_state = "request_failed"
            state.connection_label = "接続エラー"
            state.last_error = response.get("error", {}).get("message", "接続エラーが発生しました。")
        return {"FINISHED"}
