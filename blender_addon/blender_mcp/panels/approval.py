import textwrap

import bpy


class BLENDERMCP_PT_approval(bpy.types.Panel):
    bl_label = "承認"
    bl_idname = "BLENDERMCP_PT_approval"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender MCP"

    def draw(self, context):
        layout = self.layout
        state = context.scene.blender_mcp_state

        layout.label(text="承認待ち操作")
        box = layout.box()
        self._draw_multiline(box, state.pending_action_label, fallback="承認待ちの操作はありません。")
        if state.pending_request_id:
            box.label(text=f"Request ID: {state.pending_request_id}")
        controls = layout.column(align=True)
        controls.operator("blendermcp.execute_approved_action", text="実行")
        controls.operator("blendermcp.reject_action", text="却下")

    @staticmethod
    def _draw_multiline(layout, text: str, fallback: str | None = None) -> None:
        lines = text.splitlines() if text else []
        if not lines and fallback:
            lines = [fallback]
        for line in lines:
            wrapped = textwrap.wrap(line, width=32, break_long_words=True) or [line]
            for wrapped_line in wrapped:
                layout.label(text=wrapped_line)
