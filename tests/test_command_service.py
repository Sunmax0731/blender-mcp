from __future__ import annotations

import json
import threading
import time
from urllib import request

import uvicorn

from blender_mcp_server.server import create_starlette_app
from blender_mcp_server.services.command_service import submit_blender_command
from blender_mcp_server.services.command_store import reset_command_state
from blender_mcp_server.services.status_store import reset_status_state
from blender_mcp_server.services.status_store import update_status_state


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

    app = create_starlette_app(_FakeMcpServer())
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8766, log_level="warning")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    _wait_for_server_startup()

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
        server.should_exit = True
        server_thread.join(timeout=3.0)


class _FakeSessionManager:
    def run(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeMcpServer:
    def __init__(self):
        self.session_manager = _FakeSessionManager()

    def streamable_http_app(self):
        async def app(scope, receive, send):
            if scope["type"] != "http":
                raise RuntimeError("Unsupported scope type")
            body = b'{"jsonrpc":"2.0","result":{"tools":["blender_status"]},"id":1}'
            headers = [(b"content-type", b"application/json")]
            await send({"type": "http.response.start", "status": 200, "headers": headers})
            await send({"type": "http.response.body", "body": body})

        return app


def _wait_for_server_startup():
    deadline = time.time() + 3.0
    while time.time() < deadline:
        try:
            with request.urlopen("http://127.0.0.1:8766/health", timeout=0.2):
                return
        except Exception:  # noqa: BLE001
            time.sleep(0.05)
    raise RuntimeError("ASGI server did not start in time.")


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
