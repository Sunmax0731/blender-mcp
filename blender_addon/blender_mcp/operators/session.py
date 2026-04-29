import bpy


class BLENDERMCP_OT_send_prompt(bpy.types.Operator):
    bl_idname = "blendermcp.send_prompt"
    bl_label = "Send Prompt"
    bl_description = "Append the current prompt to the session history"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        prompt = state.prompt_text.strip()
        if not prompt:
            state.last_error = "プロンプトを入力してください。"
            state.ui_state = "request_failed"
            return {"CANCELLED"}

        state.ui_state = "request_running"
        state.history_text = f"Latest prompt: {prompt}"
        state.connection_label = "Connected (request running)"
        state.last_error = ""
        return {"FINISHED"}
