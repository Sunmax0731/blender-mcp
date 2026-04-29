import json

import bpy

from ..services.command_executor import execute_command


def _append_history(state, line: str) -> None:
    previous = state.history_text.strip()
    if not previous or previous == "No history yet.":
        state.history_text = line
        return
    state.history_text = f"{previous}\n{line}"


def _clear_pending(state) -> None:
    state.pending_action_label = "No pending actions."
    state.pending_request_id = ""
    state.pending_command_json = ""


class BLENDERMCP_OT_execute_approved_action(bpy.types.Operator):
    bl_idname = "blendermcp.execute_approved_action"
    bl_label = "Execute Approved Action"
    bl_description = "Execute the currently pending approved action inside Blender"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        if not state.pending_command_json:
            state.last_error = "No pending command to execute."
            state.ui_state = "request_failed"
            return {"CANCELLED"}

        try:
            command = json.loads(state.pending_command_json)
        except json.JSONDecodeError:
            state.last_error = "Pending command data is invalid."
            state.ui_state = "request_failed"
            return {"CANCELLED"}

        params = dict(command.get("params", {}) or {})
        params["_approved"] = True
        command["params"] = params
        result = execute_command(command, bpy)
        state.last_result_text = str(result)

        if result.get("success"):
            _append_history(state, f"{command.get('action', 'unknown')}: approved and executed")
            state.ui_state = "connected_idle"
            state.connection_label = "Connected (idle)"
            state.last_error = ""
            _clear_pending(state)
            return {"FINISHED"}

        _append_history(state, f"{command.get('action', 'unknown')}: approval execution failed")
        state.ui_state = "request_failed"
        state.connection_label = "Request failed"
        state.last_error = result.get("error", {}).get("message", "Unknown approval execution failure.")
        return {"CANCELLED"}


class BLENDERMCP_OT_reject_action(bpy.types.Operator):
    bl_idname = "blendermcp.reject_action"
    bl_label = "Reject Action"
    bl_description = "Reject the currently pending action"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        _append_history(state, "pending action: rejected")
        _clear_pending(state)
        state.ui_state = "connected_idle"
        state.connection_label = "Connected (idle)"
        state.last_error = ""
        return {"FINISHED"}
