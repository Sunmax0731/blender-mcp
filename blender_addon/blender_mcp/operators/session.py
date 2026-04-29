import json

import bpy

from ..services.command_runtime import process_next_command
from ..services.http_client import request_ai_suggestion


def _append_history(state, line: str) -> None:
    previous = state.history_text.strip()
    if not previous or previous == "履歴はまだありません。":
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
    bl_label = "送信"
    bl_description = "現在のプロンプトを送信して提案を取得します"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        prompt = state.prompt_text.strip()
        if not prompt:
            state.last_error = "プロンプトが空です。"
            state.ui_state = "request_failed"
            return {"CANCELLED"}

        _append_history(state, f"入力: {prompt}")
        state.ui_state = "request_running"
        state.connection_label = "リクエスト処理中"
        try:
            response = request_ai_suggestion(
                prompt=prompt,
                selected_objects=_build_selected_objects(bpy),
                scene_summary=_build_scene_summary(bpy),
                constraints={
                    "allowActions": ["create_primitive", "list_objects", "transform_object"],
                    "disallowActions": ["delete_object"],
                },
            )
        except Exception as exc:  # noqa: BLE001
            state.ui_state = "request_failed"
            state.connection_label = "接続エラー"
            state.last_error = str(exc)
            return {"CANCELLED"}

        if response.get("success"):
            suggestion = (
                response.get("data", {})
                .get("suggestions", [{}])[0]
                .get("summary", "提案は返されませんでした。")
            )
            state.last_result_text = suggestion
            _append_history(state, f"AI: {suggestion}")
            state.ui_state = "connected_idle"
            state.connection_label = "接続済み"
            state.last_error = ""
            return {"FINISHED"}

        state.ui_state = "request_failed"
        state.connection_label = "リクエスト失敗"
        state.last_error = response.get("error", {}).get("message", "AI 提案の取得に失敗しました。")
        state.last_result_text = str(response)
        _append_history(state, "AI: 提案取得に失敗しました。")
        return {"CANCELLED"}


class BLENDERMCP_OT_process_next_command(bpy.types.Operator):
    bl_idname = "blendermcp.process_next_command"
    bl_label = "取得"
    bl_description = "ローカル MCP サーバーから次のコマンドを取得します"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        blender_version = ".".join(str(x) for x in bpy.app.version[:3])
        state.blender_version = blender_version
        state.ui_state = "request_running"
        state.connection_label = "リクエスト処理中"
        state.last_error = ""

        response = process_next_command(
            addon_version=state.addon_version,
            blender_version=blender_version,
            bpy_module=bpy,
        )
        if not response.get("success"):
            state.ui_state = "request_failed"
            state.connection_label = "接続エラー"
            state.last_error = response.get("error", {}).get("message", "コマンド取得に失敗しました。")
            return {"CANCELLED"}

        data = response.get("data", {})
        if not data.get("commandProcessed"):
            state.ui_state = "connected_idle"
            state.connection_label = "接続済み"
            state.last_result_text = "処理待ちのコマンドはありません。"
            _append_history(state, "システム: 処理待ちコマンドはありません。")
            return {"FINISHED"}

        command = data.get("command", {})
        result = data.get("result", {})
        action = command.get("action", "unknown")
        state.last_result_text = str(result)

        if result.get("executionMode") == "confirm_required":
            state.ui_state = "approval_pending"
            state.pending_action_label = f"承認が必要です: {action}"
            state.pending_request_id = str(command.get("requestId", ""))
            state.pending_command_json = json.dumps(command)
            state.connection_label = "承認待ち"
            _append_history(state, f"{action}: 承認待ちです。")
            return {"FINISHED"}

        state.pending_request_id = ""
        state.pending_command_json = ""

        if result.get("success"):
            state.ui_state = "connected_idle"
            state.connection_label = "接続済み"
            state.pending_action_label = "承認待ちの操作はありません。"
            _append_history(state, f"{action}: 成功")
            return {"FINISHED"}

        state.ui_state = "request_failed"
        state.connection_label = "リクエスト失敗"
        state.last_error = result.get("error", {}).get("message", "コマンド実行に失敗しました。")
        _append_history(state, f"{action}: 失敗")
        return {"CANCELLED"}
