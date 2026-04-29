from __future__ import annotations

from urllib import error

from .command_executor import execute_command
from .http_client import poll_next_command
from .http_client import submit_command_result


def process_next_command(*, addon_version: str, blender_version: str, bpy_module) -> dict[str, object]:
    try:
        polled = poll_next_command(
            addon_version=addon_version,
            blender_version=blender_version,
        )
        command = polled.get("data", {}).get("command")
        if not command:
            return {
                "success": True,
                "data": {
                    "commandProcessed": False,
                },
            }

        result = execute_command(command=command, bpy_module=bpy_module)
        submit_command_result(result)
        return {
            "success": True,
            "data": {
                "commandProcessed": True,
                "command": command,
                "result": result,
            },
        }
    except error.URLError as exc:
        return {
            "success": False,
            "error": {
                "code": "BLENDER_MCP_SERVER_UNREACHABLE",
                "message": str(exc.reason),
            },
        }
