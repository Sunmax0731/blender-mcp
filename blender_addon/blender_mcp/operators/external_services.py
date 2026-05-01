from __future__ import annotations

import json
from urllib import error

import bpy

from ..preferences import build_service_overview
from ..preferences import get_addon_preferences
from ..preferences import get_service_settings
from ..service_definitions import get_service_definition
from ..services import asset_import
from ..services import generation
from ..services import polyhaven


class BLENDERMCP_OT_refresh_external_service_overview(bpy.types.Operator):
    bl_idname = "blendermcp.refresh_external_service_overview"
    bl_label = "サービス設定更新"
    bl_description = "Preferences の外部サービス設定を読み直します。"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        preferences = get_addon_preferences(context)
        state.external_service_overview_text = build_service_overview(preferences, bpy)
        state.external_service_last_error = ""
        return {"FINISHED"}


class BLENDERMCP_OT_submit_generation_task(bpy.types.Operator):
    bl_idname = "blendermcp.submit_generation_task"
    bl_label = "生成ジョブ送信"
    bl_description = "選択した外部サービスへ生成ジョブを送信します。"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        preferences = get_addon_preferences(context)
        state.external_service_overview_text = build_service_overview(preferences, bpy)

        try:
            result = generation.submit_generation_task(
                bpy_module=bpy,
                preferences=preferences,
                service_key=state.generation_service_key,
                prompt=state.generation_prompt_text,
                payload_json=state.generation_payload_json,
            )
        except (ValueError, json.JSONDecodeError) as exc:
            state.external_service_last_error = str(exc)
            state.generation_last_response_text = "ジョブ送信に失敗しました。"
            return {"CANCELLED"}
        except error.URLError as exc:
            label = get_service_definition(state.generation_service_key).label
            state.external_service_last_error = f"{label} API error: {exc.reason}"
            state.generation_last_response_text = "API 接続に失敗しました。"
            return {"CANCELLED"}

        state.external_service_last_error = ""
        state.generation_last_task_id = str(result.get("task_id") or "")
        state.generation_last_subscription_key = str(result.get("metadata", {}).get("subscription_key") or "")
        state.generation_last_status = str(result.get("status") or "submitted")
        state.generation_last_result_url = str(result.get("result_url") or "")
        state.generation_last_response_text = _format_generation_result(result)
        return {"FINISHED"}


class BLENDERMCP_OT_poll_generation_task(bpy.types.Operator):
    bl_idname = "blendermcp.poll_generation_task"
    bl_label = "生成ジョブ状態確認"
    bl_description = "選択した外部サービスの生成ジョブ状態を確認します。"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        preferences = get_addon_preferences(context)
        state.external_service_overview_text = build_service_overview(preferences, bpy)

        try:
            result = generation.poll_generation_task(
                preferences=preferences,
                service_key=state.generation_service_key,
                task_id=state.generation_last_task_id,
                payload_json=state.generation_payload_json,
                subscription_key=state.generation_last_subscription_key,
            )
        except (ValueError, json.JSONDecodeError) as exc:
            state.external_service_last_error = str(exc)
            state.generation_last_response_text = "状態確認に失敗しました。"
            return {"CANCELLED"}
        except error.URLError as exc:
            label = get_service_definition(state.generation_service_key).label
            state.external_service_last_error = f"{label} API error: {exc.reason}"
            state.generation_last_response_text = "API 接続に失敗しました。"
            return {"CANCELLED"}

        state.external_service_last_error = ""
        state.generation_last_task_id = str(result.get("task_id") or state.generation_last_task_id)
        state.generation_last_status = str(result.get("status") or "")
        state.generation_last_result_url = str(result.get("result_url") or "")
        state.generation_last_response_text = _format_generation_result(result)
        return {"FINISHED"}


class BLENDERMCP_OT_import_generation_result(bpy.types.Operator):
    bl_idname = "blendermcp.import_generation_result"
    bl_label = "生成結果 import"
    bl_description = "最後に取得した生成結果 URL を Blender に import します。"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        asset_url = state.generation_last_result_url.strip()
        if not asset_url:
            state.external_service_last_error = "import する result_url がありません。"
            state.generation_last_response_text = "先に submit / poll を実行して result_url を取得してください。"
            return {"CANCELLED"}

        collection_name = state.generation_import_collection_name.strip()
        if not collection_name:
            collection_name = "Generated_External_Assets"

        try:
            result = asset_import.import_asset_from_url(
                bpy_module=bpy,
                asset_url=asset_url,
                service_key=state.generation_service_key,
                collection_name=collection_name,
                download_root=bpy.app.tempdir or str(context.preferences.filepaths.temporary_directory),
            )
        except ValueError as exc:
            state.external_service_last_error = str(exc)
            state.generation_last_response_text = "import に失敗しました。"
            return {"CANCELLED"}
        except error.URLError as exc:
            state.external_service_last_error = f"asset download error: {exc.reason}"
            state.generation_last_response_text = "asset のダウンロードに失敗しました。"
            return {"CANCELLED"}
        except Exception as exc:  # noqa: BLE001
            state.external_service_last_error = str(exc)
            state.generation_last_response_text = "Blender import に失敗しました。"
            return {"CANCELLED"}

        state.external_service_last_error = ""
        state.generation_last_response_text = _format_import_result(result, asset_url)
        return {"FINISHED"}


class BLENDERMCP_OT_polyhaven_search_assets(bpy.types.Operator):
    bl_idname = "blendermcp.polyhaven_search_assets"
    bl_label = "Poly Haven 検索"
    bl_description = "Poly Haven API から asset を検索します。"

    def execute(self, context):
        state = context.scene.blender_mcp_state
        preferences = get_addon_preferences(context)
        settings = get_service_settings(preferences, "polyhaven")
        state.external_service_overview_text = build_service_overview(preferences, bpy)

        if not settings["enabled"]:
            state.external_service_last_error = "Poly Haven は Preferences で有効化してください。"
            state.polyhaven_results_text = "Poly Haven を有効化してから検索してください。"
            return {"CANCELLED"}

        try:
            payload = polyhaven.search_assets(
                base_url=str(settings["endpoint"]),
                asset_type=state.polyhaven_asset_type,
                query_text=state.polyhaven_query_text,
                category_text=state.polyhaven_category_text,
            )
        except ValueError as exc:
            state.external_service_last_error = str(exc)
            state.polyhaven_results_text = "入力内容を見直してください。"
            return {"CANCELLED"}
        except error.URLError as exc:
            state.external_service_last_error = f"Poly Haven API error: {exc.reason}"
            state.polyhaven_results_text = "Poly Haven への接続に失敗しました。"
            return {"CANCELLED"}

        state.external_service_last_error = ""
        state.polyhaven_results_text = polyhaven.format_search_results(payload)
        return {"FINISHED"}


def _format_generation_result(result: dict[str, object]) -> str:
    metadata = result.get("metadata") or {}
    lines = [
        f"service={result.get('service_key')}",
        f"task_id={result.get('task_id') or '-'}",
        f"status={result.get('status') or '-'}",
        f"result_url={result.get('result_url') or '-'}",
    ]
    if isinstance(metadata, dict) and metadata.get("subscription_key"):
        lines.append(f"subscription_key={metadata['subscription_key']}")
    raw_payload = result.get("raw")
    if raw_payload is not None:
        lines.append("raw=" + json.dumps(raw_payload, ensure_ascii=False, sort_keys=True))
    return "\n".join(lines)


def _format_import_result(result: dict[str, object], asset_url: str) -> str:
    lines = [
        f"asset_url={asset_url}",
        f"file_path={result.get('file_path') or '-'}",
        f"collection={result.get('collection_name') or '-'}",
        f"object_count={result.get('object_count') or 0}",
    ]
    object_names = result.get("object_names") or []
    if isinstance(object_names, list) and object_names:
        lines.append("objects=" + ", ".join(str(name) for name in object_names))
    return "\n".join(lines)
