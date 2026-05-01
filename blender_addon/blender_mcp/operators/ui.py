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
        state.external_service_overview_text = "サービス設定はまだ読み込まれていません。"
        state.external_service_last_error = ""
        state.generation_prompt_text = ""
        state.generation_payload_json = ""
        state.generation_last_task_id = ""
        state.generation_last_subscription_key = ""
        state.generation_last_status = "未実行"
        state.generation_last_result_url = ""
        state.generation_last_response_text = "生成系サービスの実行結果はまだありません。"
        state.generation_import_collection_name = "Generated_External_Assets"
        state.polyhaven_query_text = ""
        state.polyhaven_category_text = ""
        state.polyhaven_results_text = "検索結果はまだありません。"
        return {"FINISHED"}
