import bpy

from ..services.http_client import request_connection_status


class BLENDERMCP_OT_connect(bpy.types.Operator):
    bl_idname = "blendermcp.connect"
    bl_label = "Connect"
    bl_description = "Set Blender MCP state to connecting"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        state.ui_state = "connecting"
        state.connection_label = "Connecting to local MCP server..."
        state.last_error = ""
        blender_version = ".".join(str(x) for x in bpy.app.version[:3])
        state.blender_version = blender_version

        response = request_connection_status(
            addon_version=state.addon_version,
            blender_version=blender_version,
        )
        if response.get("success"):
            state.ui_state = "connected_idle"
            state.connection_label = "Connected (idle)"
            state.history_text = "Local MCP server connection established."
            return {"FINISHED"}

        error_message = response.get("error", {}).get("message", "Unknown connection error.")
        state.ui_state = "request_failed"
        state.connection_label = "Connection error"
        state.last_error = error_message
        return {"CANCELLED"}


class BLENDERMCP_OT_refresh_status(bpy.types.Operator):
    bl_idname = "blendermcp.refresh_status"
    bl_label = "Refresh Status"
    bl_description = "Refresh the current connection state"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        blender_version = ".".join(str(x) for x in bpy.app.version[:3])
        state.blender_version = blender_version
        response = request_connection_status(
            addon_version=state.addon_version,
            blender_version=blender_version,
        )

        if response.get("success"):
            transport_status = response.get("data", {}).get("transportStatus", "disconnected")
            if transport_status == "connected":
                state.ui_state = "connected_idle"
                state.connection_label = "Connected (idle)"
                state.last_error = ""
            else:
                state.ui_state = "disconnected"
                state.connection_label = "Disconnected"
        else:
            state.ui_state = "request_failed"
            state.connection_label = "Connection error"
            state.last_error = response.get("error", {}).get("message", "Unknown connection error.")
        return {"FINISHED"}
