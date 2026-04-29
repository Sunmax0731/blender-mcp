from __future__ import annotations

import json
from urllib import error
from urllib import request

from ..config import AI_SUGGESTION_TIMEOUT_SECONDS
from ..config import DEFAULT_HTTP_TIMEOUT_SECONDS
from ..config import SERVER_URL


def _decode_response(response) -> dict[str, object]:
    return json.loads(response.read().decode("utf-8"))


def _post_json(
    path: str,
    payload: dict[str, object],
    *,
    timeout_seconds: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
) -> dict[str, object]:
    req = request.Request(
        f"{SERVER_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout_seconds) as response:
        return _decode_response(response)


def post_addon_status(addon_version: str, blender_version: str) -> dict[str, object]:
    payload = {
        "blenderRunning": True,
        "addonLoaded": True,
        "addonVersion": addon_version,
        "blenderVersion": blender_version,
        "transportStatus": "connected",
    }
    return _post_json("/api/addon/status", payload)


def fetch_status() -> dict[str, object]:
    with request.urlopen(f"{SERVER_URL}/api/status", timeout=2.0) as response:
        return _decode_response(response)


def poll_next_command(addon_version: str, blender_version: str) -> dict[str, object]:
    payload = {
        "blenderRunning": True,
        "addonLoaded": True,
        "addonVersion": addon_version,
        "blenderVersion": blender_version,
        "transportStatus": "connected",
    }
    return _post_json("/api/addon/command/poll", payload)


def submit_command_result(result: dict[str, object]) -> dict[str, object]:
    return _post_json("/api/addon/command-result", result)


def submit_approval_result(result: dict[str, object]) -> dict[str, object]:
    return _post_json("/api/addon/approval-result", result)


def request_ai_suggestion(
    *,
    prompt: str,
    selected_objects: list[dict[str, object]] | None = None,
    scene_summary: dict[str, object] | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    return _post_json(
        "/api/ai/suggest",
        {
            "prompt": prompt,
            "selectedObjects": selected_objects or [],
            "sceneSummary": scene_summary or {},
            "constraints": constraints or {},
        },
        timeout_seconds=AI_SUGGESTION_TIMEOUT_SECONDS,
    )


def request_connection_status(addon_version: str, blender_version: str) -> dict[str, object]:
    try:
        post_addon_status(addon_version=addon_version, blender_version=blender_version)
        return fetch_status()
    except error.URLError as exc:
        return {
            "success": False,
            "error": {
                "code": "BLENDER_MCP_SERVER_UNREACHABLE",
                "message": str(exc.reason),
            },
        }
