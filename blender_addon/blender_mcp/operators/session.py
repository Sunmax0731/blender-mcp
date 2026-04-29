import json

import bpy

from ..services.command_runtime import process_next_command
from ..services.http_client import request_ai_suggestion


def _append_history(state, line: str) -> None:
    previous = state.history_text.strip()
    if not previous or previous == "No history yet.":
        state.history_text = line
        return
    state.history_text = f"{previous}\n{line}"


def _build_scene_summary(bpy_module) -> dict[str, object]:
    return {
        "sceneName": getattr(getattr(bpy_module.context, "scene", None), "name", "Scene"),
        "objectCount": len(getattr(bpy_module.data, "objects", [])),
        "selectedObjectCount": len(getattr(bpy_module.context, "selected_objects", [])),
    }


def _build_selected_objects(bpy_module) -> list[dict[str, object]]:
    selected = []
    for obj in getattr(bpy_module.context, "selected_objects", []):
        selected.append(
            {
                "name": getattr(obj, "name", "Unknown"),
                "type": getattr(obj, "type", "UNKNOWN"),
            }
        )
    return selected


class BLENDERMCP_OT_send_prompt(bpy.types.Operator):
    bl_idname = "blendermcp.send_prompt"
    bl_label = "Send Prompt"
    bl_description = "Append the current prompt to the session history"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        prompt = state.prompt_text.strip()
        if not prompt:
            state.last_error = "Prompt is empty."
            state.ui_state = "request_failed"
            return {"CANCELLED"}

        _append_history(state, f"Prompt: {prompt}")
        state.ui_state = "request_running"
        state.connection_label = "Connected (request running)"
        try:
            response = request_ai_suggestion(
                prompt=prompt,
                selected_objects=_build_selected_objects(bpy),
                scene_summary=_build_scene_summary(bpy),
                constraints={
                    "allowActions": ["transform_object"],
                    "disallowActions": ["delete_object"],
                },
            )
        except Exception as exc:  # noqa: BLE001
            state.ui_state = "request_failed"
            state.connection_label = "Connection error"
            state.last_error = str(exc)
            return {"CANCELLED"}

        if response.get("success"):
            suggestion = (
                response.get("data", {})
                .get("suggestions", [{}])[0]
                .get("summary", "No suggestion returned.")
            )
            state.last_result_text = suggestion
            _append_history(state, f"AI: {suggestion}")
            state.ui_state = "connected_idle"
            state.connection_label = "Connected (idle)"
            state.last_error = ""
            return {"FINISHED"}

        state.ui_state = "request_failed"
        state.connection_label = "Request failed"
        state.last_error = response.get("error", {}).get("message", "Unknown AI suggestion error.")
        state.last_result_text = str(response)
        _append_history(state, "AI: request failed")
        return {"CANCELLED"}


class BLENDERMCP_OT_process_next_command(bpy.types.Operator):
    bl_idname = "blendermcp.process_next_command"
    bl_label = "Process Next Command"
    bl_description = "Fetch the next pending command from the local MCP server"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        blender_version = ".".join(str(x) for x in bpy.app.version[:3])
        state.blender_version = blender_version
        state.ui_state = "request_running"
        state.connection_label = "Connected (request running)"
        state.last_error = ""

        response = process_next_command(
            addon_version=state.addon_version,
            blender_version=blender_version,
            bpy_module=bpy,
        )
        if not response.get("success"):
            state.ui_state = "request_failed"
            state.connection_label = "Connection error"
            state.last_error = response.get("error", {}).get("message", "Unknown command error.")
            return {"CANCELLED"}

        data = response.get("data", {})
        if not data.get("commandProcessed"):
            state.ui_state = "connected_idle"
            state.connection_label = "Connected (idle)"
            state.last_result_text = "No pending commands."
            _append_history(state, "System: no pending commands.")
            return {"FINISHED"}

        command = data.get("command", {})
        result = data.get("result", {})
        action = command.get("action", "unknown")
        state.last_result_text = str(result)

        if result.get("executionMode") == "confirm_required":
            state.ui_state = "approval_pending"
            state.pending_action_label = f"Approval required: {action}"
            state.pending_request_id = str(command.get("requestId", ""))
            state.pending_command_json = json.dumps(command)
            state.connection_label = "Approval pending"
            _append_history(state, f"{action}: confirmation required.")
            return {"FINISHED"}

        state.pending_request_id = ""
        state.pending_command_json = ""

        if result.get("success"):
            state.ui_state = "connected_idle"
            state.connection_label = "Connected (idle)"
            state.pending_action_label = "No pending actions."
            _append_history(state, f"{action}: success")
            return {"FINISHED"}

        state.ui_state = "request_failed"
        state.connection_label = "Request failed"
        state.last_error = result.get("error", {}).get("message", "Unknown command failure.")
        _append_history(state, f"{action}: failed")
        return {"CANCELLED"}
