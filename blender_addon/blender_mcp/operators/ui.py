import bpy


class BLENDERMCP_OT_clear_history(bpy.types.Operator):
    bl_idname = "blendermcp.clear_history"
    bl_label = "履歴消去"
    bl_description = "セッション履歴と結果表示を消去します"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        state.history_text = "履歴はまだありません。"
        state.last_result_text = "まだ結果はありません。"
        state.prompt_plan_text = "実行計画はまだありません。"
        state.prompt_preview_text = "Preview はまだありません。"
        state.prompt_confirmed = False
        state.pending_command_json = ""
        state.last_error = ""
        return {"FINISHED"}
