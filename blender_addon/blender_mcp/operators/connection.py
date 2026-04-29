import bpy


class BLENDERMCP_OT_connect(bpy.types.Operator):
    bl_idname = "blendermcp.connect"
    bl_label = "Connect"
    bl_description = "Set Blender MCP state to connecting"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        state.ui_state = "connecting"
        state.connection_label = "Connecting to local MCP server..."
        state.last_error = ""
        return {"FINISHED"}


class BLENDERMCP_OT_refresh_status(bpy.types.Operator):
    bl_idname = "blendermcp.refresh_status"
    bl_label = "Refresh Status"
    bl_description = "Refresh the current connection state"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        if state.ui_state == "disconnected":
            state.connection_label = "Disconnected"
        elif state.ui_state == "connecting":
            state.connection_label = "Connecting to local MCP server..."
        elif state.ui_state == "connected_idle":
            state.connection_label = "Connected (idle)"
        elif state.ui_state == "request_running":
            state.connection_label = "Connected (request running)"
        elif state.ui_state == "approval_pending":
            state.connection_label = "Connected (approval pending)"
        else:
            state.connection_label = "Connection error"
        return {"FINISHED"}
