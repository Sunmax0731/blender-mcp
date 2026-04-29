import bpy


class BLENDERMCP_OT_clear_history(bpy.types.Operator):
    bl_idname = "blendermcp.clear_history"
    bl_label = "履歴をクリア"
    bl_description = "セッション履歴と結果表示を消去します"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        state.history_text = "履歴はまだありません。"
        state.last_result_text = "まだ結果はありません。"
        state.last_error = ""
        return {"FINISHED"}
