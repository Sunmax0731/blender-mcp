import bpy


class BLENDERMCP_PT_connection(bpy.types.Panel):
    bl_label = "Connection"
    bl_idname = "BLENDERMCP_PT_connection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender MCP"

    def draw(self, context):
        layout = self.layout
        state = context.scene.blender_mcp_state

        layout.label(text=f"State: {state.ui_state}")
        layout.label(text=state.connection_label)

        row = layout.row(align=True)
        row.operator("blendermcp.connect", text="Connect")
        row.operator("blendermcp.refresh_status", text="Refresh Status")

        if state.last_error:
            layout.label(text=f"Error: {state.last_error}")
