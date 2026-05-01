import textwrap

import bpy

from ..service_definitions import get_service_definition


class BLENDERMCP_PT_external_services(bpy.types.Panel):
    bl_label = "外部サービス"
    bl_idname = "BLENDERMCP_PT_external_services"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender MCP"

    def draw(self, context):
        layout = self.layout
        state = context.scene.blender_mcp_state

        layout.label(text="設定は Add-ons > Blender MCP > External Services にあります。")
        controls = layout.column(align=True)
        controls.operator("blendermcp.refresh_external_service_overview", text="Preferences 読み込み")

        layout.separator()
        layout.label(text="サービス概要")
        overview_box = layout.box()
        self._draw_multiline(
            overview_box,
            state.external_service_overview_text,
            fallback="サービス設定はまだ読み込まれていません。",
        )

        layout.separator()
        generation_box = layout.box()
        generation_box.label(text="生成系サービス")
        generation_box.prop(state, "generation_service_key", text="Service")
        definition = get_service_definition(state.generation_service_key)
        generation_box.label(text=definition.notes)
        generation_box.prop(state, "generation_prompt_text", text="Prompt")
        generation_box.prop(state, "generation_payload_json", text="JSON")
        generation_box.prop(state, "generation_import_collection_name", text="Collection")
        row = generation_box.row(align=True)
        row.operator("blendermcp.submit_generation_task", text="Submit")
        row.operator("blendermcp.poll_generation_task", text="Poll")
        generation_box.operator("blendermcp.import_generation_result", text="Import")
        self._draw_multiline(
            generation_box.box(),
            state.generation_last_response_text,
            fallback="生成ジョブはまだ実行していません。",
        )

        if state.external_service_last_error:
            layout.separator()
            layout.label(text="外部サービスエラー")
            self._draw_multiline(layout.box(), state.external_service_last_error)

    @staticmethod
    def _draw_multiline(layout, text: str, fallback: str | None = None) -> None:
        lines = text.splitlines() if text else []
        if not lines and fallback:
            lines = [fallback]
        for line in lines:
            wrapped = textwrap.wrap(line, width=32, break_long_words=True) or [line]
            for wrapped_line in wrapped:
                layout.label(text=wrapped_line)
