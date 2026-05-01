from __future__ import annotations

from .http_utils import get_json
from .http_utils import post_json


TRIPO_BASE_URL = "https://api.tripo3d.ai/v2/openapi"


def _headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def create_text_to_model_task(
    *,
    api_key: str,
    prompt: str,
    base_url: str = TRIPO_BASE_URL,
    model_version: str = "v2.5-20250123",
    texture: bool = True,
    pbr: bool = True,
    texture_quality: str = "standard",
    auto_size: bool = False,
    quad: bool = False,
) -> dict[str, object]:
    payload = {
        "type": "text_to_model",
        "prompt": prompt,
        "model_version": model_version,
        "texture": texture,
        "pbr": pbr,
        "texture_quality": texture_quality,
        "auto_size": auto_size,
        "quad": quad,
    }
    response = post_json(f"{base_url.rstrip('/')}/task", payload, headers=_headers(api_key))
    data = response.get("data", {})
    return {"task_id": data.get("task_id"), "raw": response}


def create_task(
    *,
    api_key: str,
    payload: dict[str, object],
    base_url: str = TRIPO_BASE_URL,
) -> dict[str, object]:
    response = post_json(f"{base_url.rstrip('/')}/task", payload, headers=_headers(api_key))
    data = response.get("data", {})
    return {"task_id": data.get("task_id"), "raw": response}


def get_task(
    *,
    api_key: str,
    task_id: str,
    base_url: str = TRIPO_BASE_URL,
) -> dict[str, object]:
    response = get_json(f"{base_url.rstrip('/')}/task/{task_id}", headers=_headers(api_key))
    data = response.get("data", {})
    output = data.get("output", {}) if isinstance(data, dict) else {}
    return {
        "task_id": data.get("task_id"),
        "status": data.get("status"),
        "progress": data.get("progress"),
        "output": output,
        "raw": response,
    }


def extract_model_url(task_payload: dict[str, object], preferred_field: str = "pbr_model") -> str | None:
    output = task_payload.get("output") or {}
    if not isinstance(output, dict):
        return None
    return output.get(preferred_field) or output.get("model") or output.get("base_model")
