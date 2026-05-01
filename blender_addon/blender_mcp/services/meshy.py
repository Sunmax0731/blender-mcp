from __future__ import annotations

from .http_utils import get_json
from .http_utils import post_json


MESHY_BASE_URL = "https://api.meshy.ai"


def _headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def submit_preview_task(
    *,
    api_key: str,
    prompt: str,
    base_url: str = MESHY_BASE_URL,
    ai_model: str = "latest",
    model_type: str = "standard",
    topology: str = "triangle",
    target_formats: list[str] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "mode": "preview",
        "prompt": prompt,
        "ai_model": ai_model,
        "model_type": model_type,
        "topology": topology,
    }
    if target_formats:
        payload["target_formats"] = target_formats
    response = post_json(f"{base_url.rstrip('/')}/openapi/v2/text-to-3d", payload, headers=_headers(api_key))
    return {"task_id": response.get("result"), "raw": response}


def submit_refine_task(
    *,
    api_key: str,
    preview_task_id: str,
    base_url: str = MESHY_BASE_URL,
    enable_pbr: bool = True,
    texture_prompt: str | None = None,
    target_formats: list[str] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "mode": "refine",
        "preview_task_id": preview_task_id,
        "enable_pbr": enable_pbr,
    }
    if texture_prompt:
        payload["texture_prompt"] = texture_prompt
    if target_formats:
        payload["target_formats"] = target_formats
    response = post_json(f"{base_url.rstrip('/')}/openapi/v2/text-to-3d", payload, headers=_headers(api_key))
    return {"task_id": response.get("result"), "raw": response}


def get_task(
    *,
    api_key: str,
    task_id: str,
    base_url: str = MESHY_BASE_URL,
) -> dict[str, object]:
    response = get_json(f"{base_url.rstrip('/')}/openapi/v2/text-to-3d/{task_id}", headers=_headers(api_key))
    return {
        "task_id": response.get("id"),
        "status": response.get("status"),
        "progress": response.get("progress"),
        "model_urls": response.get("model_urls", {}),
        "thumbnail_url": response.get("thumbnail_url"),
        "raw": response,
    }


def extract_model_url(task_payload: dict[str, object], preferred_format: str = "glb") -> str | None:
    model_urls = task_payload.get("model_urls") or {}
    if not isinstance(model_urls, dict):
        return None
    return model_urls.get(preferred_format) or next(iter(model_urls.values()), None)
