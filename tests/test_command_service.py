from __future__ import annotations

import json
import threading
import time
from urllib import request

from blender_mcp_server.services.command_service import submit_blender_command
from blender_mcp_server.services.command_store import reset_command_state
from blender_mcp_server.services.status_store import reset_status_state
from blender_mcp_server.services.status_store import update_status_state
from blender_mcp_server.transport.http_app import create_http_server


def test_submit_blender_command_requires_connected_addon():
    reset_status_state()
    reset_command_state()

    result = submit_blender_command(
        action="list_objects",
        params={"selectedOnly": False},
        timeout_seconds=0.1,
    )

    assert result["success"] is False
    assert result["error"]["code"] == "ADDON_NOT_READY"


def test_submit_blender_command_round_trip_over_http():
    reset_status_state()
    reset_command_state()
    update_status_state(
        {
            "blenderRunning": True,
            "addonLoaded": True,
            "addonVersion": "0.1.0",
            "blenderVersion": "4.5.0",
            "transportStatus": "connected",
        }
    )

    server = create_http_server(host="127.0.0.1", port=8766)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        addon_thread = threading.Thread(target=_fake_addon_worker, daemon=True)
        addon_thread.start()

        result = submit_blender_command(
            action="list_objects",
            params={"selectedOnly": False},
            timeout_seconds=2.0,
        )

        assert result["success"] is True
        assert result["data"]["objects"][0]["name"] == "Cube"
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=2.0)


def _fake_addon_worker():
    payload = {
        "blenderRunning": True,
        "addonLoaded": True,
        "addonVersion": "0.1.0",
        "blenderVersion": "4.5.0",
        "transportStatus": "connected",
    }
    deadline = time.time() + 2.0
    while time.time() < deadline:
        req = request.Request(
            "http://127.0.0.1:8766/api/addon/command/poll",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with request.urlopen(req, timeout=1.0) as response:
            polled = json.loads(response.read().decode("utf-8"))

        command = polled.get("data", {}).get("command")
        if not command:
            time.sleep(0.05)
            continue

        result_req = request.Request(
            "http://127.0.0.1:8766/api/addon/command-result",
            data=json.dumps(
                {
                    "success": True,
                    "requestId": command["requestId"],
                    "data": {
                        "objects": [
                            {
                                "name": "Cube",
                                "type": "MESH",
                                "selected": False,
                                "visible": True,
                            }
                        ]
                    },
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with request.urlopen(result_req, timeout=1.0):
            return
