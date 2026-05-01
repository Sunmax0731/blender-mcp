from __future__ import annotations

from pathlib import Path

from .http_utils import post_json
from .http_utils import post_multipart


SPAR3D_DEFAULT_ENDPOINT = "https://platform.stability.ai/v1/3d/stable-point-aware-3d"


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
    }


def submit_generation(
    *,
    api_key: str,
    endpoint_url: str = SPAR3D_DEFAULT_ENDPOINT,
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    request_payload = payload or {}
    image_path = request_payload.pop("image_path", None)
    if image_path:
        response = post_multipart(
            endpoint_url,
            _build_multipart_fields(request_payload, Path(str(image_path))),
            headers=_headers(api_key),
        )
    else:
        response = post_json(endpoint_url, request_payload, headers=_headers(api_key))
    return {
        "task_id": response.get("id") or response.get("task_id"),
        "status": response.get("status"),
        "raw": response,
    }


def poll_generation_status(
    *,
    api_key: str,
    endpoint_url: str,
    task_id: str,
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    response = post_json(endpoint_url, payload or {"task_id": task_id}, headers=_headers(api_key))
    return {
        "task_id": response.get("id") or response.get("task_id") or task_id,
        "status": response.get("status"),
        "raw": response,
    }


def extract_model_url(response_payload: dict[str, object]) -> str | None:
    candidates = [
        response_payload.get("model_url"),
        response_payload.get("glb_url"),
        response_payload.get("asset_url"),
    ]
    output = response_payload.get("output")
    if isinstance(output, dict):
        candidates.extend([output.get("model_url"), output.get("glb_url"), output.get("asset_url")])
    for candidate in candidates:
        if isinstance(candidate, str) and candidate:
            return candidate
    return None


def _build_multipart_fields(payload: dict[str, object], image_path: Path) -> dict[str, object]:
    if not image_path.exists():
        raise ValueError(f"SPAR3D image_path not found: {image_path}")

    file_field_name = str(payload.pop("image_field_name", "image"))
    content_type = str(payload.pop("image_content_type", "image/png"))
    filename = image_path.name
    fields = dict(payload)
    fields[file_field_name] = (filename, image_path.read_bytes(), content_type)
    return fields
