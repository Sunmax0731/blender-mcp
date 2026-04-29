from __future__ import annotations

import json
from urllib import error
from urllib import request

from ..config import SERVER_URL


def post_addon_status(addon_version: str, blender_version: str) -> dict[str, object]:
    payload = {
        "blenderRunning": True,
        "addonLoaded": True,
        "addonVersion": addon_version,
        "blenderVersion": blender_version,
        "transportStatus": "connected",
    }
    req = request.Request(
        f"{SERVER_URL}/api/addon/status",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with request.urlopen(req, timeout=2.0) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_status() -> dict[str, object]:
    with request.urlopen(f"{SERVER_URL}/api/status", timeout=2.0) as response:
        return json.loads(response.read().decode("utf-8"))


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
