import bpy


class BLENDERMCP_OT_reject_action(bpy.types.Operator):
    bl_idname = "blendermcp.reject_action"
    bl_label = "Reject Action"
    bl_description = "Reject the currently pending action"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        state.pending_action_label = "No pending actions."
        state.ui_state = "connected_idle"
        state.connection_label = "Connected (idle)"
        return {"FINISHED"}
