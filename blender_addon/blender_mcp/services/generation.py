from __future__ import annotations

import json

from ..preferences import get_service_settings
from . import plugin_bridge
from . import meshy
from . import rodin
from . import spar3d
from . import tripo


GENERATION_SERVICE_KEYS: tuple[str, ...] = ("meshy", "tripo", "rodin", "spar3d")


def ensure_generation_service_settings(preferences, service_key: str) -> dict[str, object]:
    settings = get_service_settings(preferences, service_key)
    if not settings["enabled"]:
        raise ValueError(f"{settings['label']} は Preferences で有効化されていません。")
    if settings["requires_api_key"] and not settings["api_key"]:
        raise ValueError(f"{settings['label']} の API キーが未設定です。")
    return settings


def parse_optional_json(json_text: str) -> dict[str, object]:
    if not json_text.strip():
        return {}
    payload = json.loads(json_text)
    if not isinstance(payload, dict):
        raise ValueError("追加 JSON はオブジェクト形式で指定してください。")
    return payload


def submit_generation_task(
    *,
    bpy_module=None,
    preferences,
    service_key: str,
    prompt: str,
    payload_json: str = "",
) -> dict[str, object]:
    settings = ensure_generation_service_settings(preferences, service_key)
    base_url = str(settings["endpoint"])
    api_key = str(settings["api_key"])
    payload = parse_optional_json(payload_json)
    mode = str(settings.get("mode", "cloud_api"))

    if mode == "plugin_bridge":
        if bpy_module is None:
            raise ValueError("plugin_bridge 実行には bpy context が必要です。")
        response = plugin_bridge.submit_via_plugin_bridge(
            bpy_module=bpy_module,
            service_key=service_key,
            api_key=api_key,
            prompt=prompt,
            payload_json=payload_json,
        )
        return {
            "service_key": service_key,
            "task_id": None,
            "status": str(response.get("status") or "submitted_via_plugin_bridge"),
            "result_url": None,
            "metadata": {"bridge_mode": True},
            "raw": response.get("raw"),
        }

    if service_key in {"meshy", "tripo", "rodin"} and not prompt.strip():
        if not (service_key == "meshy" and payload.get("mode") == "refine"):
            if not (
                service_key == "tripo"
                and str(payload.get("type", "")).strip()
                in {"refine_model", "texture_model", "convert_model", "stylize_model", "check_riggable", "rig_model", "animate_retarget"}
            ):
                raise ValueError("生成系サービスの submit には prompt が必要です。")

    if service_key == "meshy":
        mode = str(payload.get("mode", "preview"))
        if mode == "refine":
            preview_task_id = str(payload.get("preview_task_id", "")).strip()
            if not preview_task_id:
                raise ValueError("Meshy refine には preview_task_id が必要です。")
            target_formats = payload.get("target_formats")
            if target_formats is not None and not isinstance(target_formats, list):
                raise ValueError("Meshy の target_formats は配列で指定してください。")
            response = meshy.submit_refine_task(
                api_key=api_key,
                preview_task_id=preview_task_id,
                base_url=base_url,
                enable_pbr=bool(payload.get("enable_pbr", True)),
                texture_prompt=str(payload.get("texture_prompt", "")).strip() or None,
                target_formats=target_formats,
            )
        else:
            target_formats = payload.get("target_formats")
            if target_formats is not None and not isinstance(target_formats, list):
                raise ValueError("Meshy の target_formats は配列で指定してください。")
            response = meshy.submit_preview_task(
                api_key=api_key,
                prompt=prompt,
                base_url=base_url,
                ai_model=str(payload.get("ai_model", "latest")),
                model_type=str(payload.get("model_type", "standard")),
                topology=str(payload.get("topology", "triangle")),
                target_formats=target_formats,
            )
        return {
            "service_key": service_key,
            "task_id": response.get("task_id"),
            "status": "submitted",
            "result_url": None,
            "metadata": {"mode": mode},
            "raw": response.get("raw"),
        }

    if service_key == "tripo":
        task_type = str(payload.get("type", "text_to_model")).strip() or "text_to_model"
        if task_type == "text_to_model":
            response = tripo.create_text_to_model_task(
                api_key=api_key,
                prompt=prompt,
                base_url=base_url,
                model_version=str(payload.get("model_version", "v2.5-20250123")),
                texture=bool(payload.get("texture", True)),
                pbr=bool(payload.get("pbr", True)),
                texture_quality=str(payload.get("texture_quality", "standard")),
                auto_size=bool(payload.get("auto_size", False)),
                quad=bool(payload.get("quad", False)),
            )
        else:
            task_payload = dict(payload)
            task_payload["type"] = task_type
            response = tripo.create_task(api_key=api_key, payload=task_payload, base_url=base_url)
        return {
            "service_key": service_key,
            "task_id": response.get("task_id"),
            "status": "submitted",
            "result_url": None,
            "metadata": {"task_type": task_type},
            "raw": response.get("raw"),
        }

    if service_key == "rodin":
        response = rodin.submit_text_generation(api_key=api_key, prompt=prompt, base_url=base_url)
        return {
            "service_key": service_key,
            "task_id": response.get("task_uuid"),
            "status": "submitted",
            "result_url": None,
            "metadata": {"subscription_key": response.get("subscription_key")},
            "raw": response.get("raw"),
        }

    if service_key == "spar3d":
        if prompt.strip() and "prompt" not in payload:
            payload["prompt"] = prompt
        response = spar3d.submit_generation(api_key=api_key, endpoint_url=base_url, payload=payload)
        return {
            "service_key": service_key,
            "task_id": response.get("task_id"),
            "status": response.get("status") or "submitted",
            "result_url": spar3d.extract_model_url(response.get("raw") or {}),
            "metadata": {},
            "raw": response.get("raw"),
        }

    raise ValueError(f"Unsupported generation service: {service_key}")


def poll_generation_task(
    *,
    preferences,
    service_key: str,
    task_id: str,
    payload_json: str = "",
    subscription_key: str = "",
) -> dict[str, object]:
    settings = ensure_generation_service_settings(preferences, service_key)
    base_url = str(settings["endpoint"])
    api_key = str(settings["api_key"])
    payload = parse_optional_json(payload_json)

    if service_key != "rodin" and not task_id.strip():
        raise ValueError("poll には task_id が必要です。")

    if service_key == "meshy":
        response = meshy.get_task(api_key=api_key, task_id=task_id, base_url=base_url)
        return {
            "service_key": service_key,
            "task_id": response.get("task_id") or task_id,
            "status": response.get("status"),
            "result_url": meshy.extract_model_url(response),
            "metadata": {},
            "raw": response.get("raw"),
        }

    if service_key == "tripo":
        response = tripo.get_task(api_key=api_key, task_id=task_id, base_url=base_url)
        return {
            "service_key": service_key,
            "task_id": response.get("task_id") or task_id,
            "status": response.get("status"),
            "result_url": tripo.extract_model_url(response),
            "metadata": {},
            "raw": response.get("raw"),
        }

    if service_key == "rodin":
        if not subscription_key.strip():
            raise ValueError("Rodin の poll には subscription_key が必要です。")
        status_response = rodin.check_status(api_key=api_key, subscription_key=subscription_key, base_url=base_url)
        status = status_response.get("status")
        result_url = None
        raw_payload: object = status_response.get("raw")
        if status in {"Done", "done", "SUCCEEDED", "succeeded", "Completed", "completed"}:
            download_response = rodin.download_results(api_key=api_key, task_uuid=task_id, base_url=base_url)
            result_url = rodin.extract_model_url(download_response)
            raw_payload = {
                "status_response": status_response.get("raw"),
                "download_response": download_response.get("raw"),
            }
        return {
            "service_key": service_key,
            "task_id": task_id,
            "status": status,
            "result_url": result_url,
            "metadata": {"subscription_key": subscription_key},
            "raw": raw_payload,
        }

    if service_key == "spar3d":
        response = spar3d.poll_generation_status(
            api_key=api_key,
            endpoint_url=base_url,
            task_id=task_id,
            payload=payload,
        )
        return {
            "service_key": service_key,
            "task_id": response.get("task_id") or task_id,
            "status": response.get("status"),
            "result_url": spar3d.extract_model_url(response.get("raw") or {}),
            "metadata": {},
            "raw": response.get("raw"),
        }

    raise ValueError(f"Unsupported generation service: {service_key}")
