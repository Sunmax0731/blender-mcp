from __future__ import annotations

from .http_utils import post_json
from .http_utils import post_multipart


RODIN_BASE_URL = "https://api.hyper3d.com"


def _headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}", "accept": "application/json"}


def submit_text_generation(
    *,
    api_key: str,
    prompt: str,
    base_url: str = RODIN_BASE_URL,
    geometry_file_format: str = "glb",
    material: str = "PBR",
    quality: str = "medium",
    tier: str = "Regular",
    preview_render: bool = False,
) -> dict[str, object]:
    fields = {
        "prompt": prompt,
        "geometry_file_format": geometry_file_format,
        "material": material,
        "quality": quality,
        "tier": tier,
        "preview_render": str(preview_render).lower(),
    }
    response = post_multipart(f"{base_url.rstrip('/')}/api/v2/rodin", fields, headers=_headers(api_key))
    jobs = response.get("jobs", {}) if isinstance(response, dict) else {}
    return {
        "task_uuid": response.get("uuid"),
        "subscription_key": jobs.get("subscription_key") if isinstance(jobs, dict) else None,
        "raw": response,
    }


def check_status(
    *,
    api_key: str,
    subscription_key: str,
    base_url: str = RODIN_BASE_URL,
) -> dict[str, object]:
    response = post_json(
        f"{base_url.rstrip('/')}/api/v2/status",
        {"subscription_key": subscription_key},
        headers=_headers(api_key),
    )
    jobs = response.get("jobs", [])
    primary_status = None
    if isinstance(jobs, list) and jobs:
        primary_status = jobs[0].get("status")
    return {"status": primary_status, "jobs": jobs, "raw": response}


def download_results(
    *,
    api_key: str,
    task_uuid: str,
    base_url: str = RODIN_BASE_URL,
) -> dict[str, object]:
    response = post_json(
        f"{base_url.rstrip('/')}/api/v2/download",
        {"task_uuid": task_uuid},
        headers=_headers(api_key),
    )
    return {"files": response.get("list", []), "raw": response}


def extract_model_url(download_payload: dict[str, object], preferred_name_fragment: str = ".glb") -> str | None:
    files = download_payload.get("files") or []
    if not isinstance(files, list):
        return None
    for item in files:
        if isinstance(item, dict) and preferred_name_fragment.lower() in str(item.get("name", "")).lower():
            return item.get("url")
    for item in files:
        if isinstance(item, dict):
            return item.get("url")
    return None
