import bpy


class BLENDERMCP_PT_session(bpy.types.Panel):
    bl_label = "Session"
    bl_idname = "BLENDERMCP_PT_session"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender MCP"

    def draw(self, context):
        layout = self.layout
        state = context.scene.blender_mcp_state

        layout.prop(state, "prompt_text", text="Prompt")
        layout.operator("blendermcp.send_prompt", text="Send Prompt")
        layout.separator()
        layout.label(text="History")
        box = layout.box()
        box.label(text=state.history_text)
