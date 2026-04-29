import bpy


class BLENDERMCP_OT_clear_history(bpy.types.Operator):
    bl_idname = "blendermcp.clear_history"
    bl_label = "Clear History"
    bl_description = "Clear session history and result display"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        state.history_text = "No history yet."
        state.last_result_text = "No command processed yet."
        state.last_error = ""
        return {"FINISHED"}
