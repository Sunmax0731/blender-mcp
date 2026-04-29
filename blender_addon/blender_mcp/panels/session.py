import textwrap

import bpy


class BLENDERMCP_PT_session(bpy.types.Panel):
    bl_label = "セッション"
    bl_idname = "BLENDERMCP_PT_session"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender MCP"

    def draw(self, context):
        layout = self.layout
        state = context.scene.blender_mcp_state

        layout.prop(state, "prompt_text", text="プロンプト")
        controls = layout.column(align=True)
        controls.operator("blendermcp.send_prompt", text="提案を送信")
        controls.operator("blendermcp.process_next_command", text="次のコマンドを取得")
        controls.operator("blendermcp.clear_history", text="履歴をクリア")
        layout.separator()
        layout.label(text="履歴")
        box = layout.box()
        self._draw_multiline(box, state.history_text, fallback="履歴はまだありません。")
        layout.separator()
        layout.label(text="最新結果")
        result_box = layout.box()
        self._draw_multiline(result_box, state.last_result_text, fallback="まだ結果はありません。")
        if state.last_error:
            layout.separator()
            layout.label(text="エラー")
            error_box = layout.box()
            self._draw_multiline(error_box, state.last_error)

    @staticmethod
    def _draw_multiline(layout, text: str, fallback: str | None = None) -> None:
        lines = text.splitlines() if text else []
        if not lines and fallback:
            lines = [fallback]
        for line in lines:
            wrapped = textwrap.wrap(line, width=32, break_long_words=True) or [line]
            for wrapped_line in wrapped:
                layout.label(text=wrapped_line)
