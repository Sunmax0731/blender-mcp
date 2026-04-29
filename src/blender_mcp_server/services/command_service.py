from __future__ import annotations

from collections.abc import Mapping

from .command_store import enqueue_command
from .command_store import wait_for_command_result
from .status_store import get_status_state


def submit_blender_command(
    *,
    action: str,
    params: Mapping[str, object] | None = None,
    requires_confirmation: bool = False,
    timeout_seconds: float = 5.0,
) -> dict[str, object]:
    status = get_status_state()
    if status.get("transportStatus") != "connected" or not status.get("addonLoaded"):
        return {
            "success": False,
            "error": {
                "code": "ADDON_NOT_READY",
                "message": "Blender add-on is not connected to the local MCP server.",
                "retryable": True,
                "details": {
                    "transportStatus": status.get("transportStatus", "disconnected"),
                },
            },
        }

    command = enqueue_command(
        action=action,
        params=params,
        requires_confirmation=requires_confirmation,
    )
    result = wait_for_command_result(
        request_id=str(command["requestId"]),
        timeout_seconds=timeout_seconds,
    )
    if result is None:
        return {
            "success": False,
            "requestId": command["requestId"],
            "error": {
                "code": "BLENDER_COMMAND_TIMEOUT",
                "message": "Timed out while waiting for the Blender add-on to return a result.",
                "retryable": True,
            },
        }
    return result
