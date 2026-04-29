import bpy


class BLENDERMCP_PT_approval(bpy.types.Panel):
    bl_label = "Approval"
    bl_idname = "BLENDERMCP_PT_approval"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender MCP"

    def draw(self, context):
        layout = self.layout
        state = context.scene.blender_mcp_state

        layout.label(text="Pending Action")
        box = layout.box()
        box.label(text=state.pending_action_label)
        layout.operator("blendermcp.reject_action", text="Reject Action")
