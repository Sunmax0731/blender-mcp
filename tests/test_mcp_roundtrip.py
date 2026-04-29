from __future__ import annotations

import asyncio
import json
import threading
import time
from urllib import request

import uvicorn

from blender_mcp_server.server import create_server
from blender_mcp_server.services.command_store import reset_command_state
from blender_mcp_server.services.status_store import reset_status_state
from blender_mcp_server.services.status_store import update_status_state
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client


def test_mcp_tool_round_trip_over_streamable_http():
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

    server_app = create_server()
    config = uvicorn.Config(app=server_app.app, host="127.0.0.1", port=8767, log_level="warning")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    _wait_for_server_startup()

    try:
        addon_thread = threading.Thread(target=_fake_addon_worker, daemon=True)
        addon_thread.start()
        result = asyncio.run(_call_list_objects_tool())

        assert result["success"] is True
        assert result["data"]["objects"][0]["name"] == "Cube"
    finally:
        server.should_exit = True
        server_thread.join(timeout=3.0)


async def _call_list_objects_tool() -> dict[str, object]:
    async with streamable_http_client("http://127.0.0.1:8767/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "blender_list_objects",
                {
                    "name_prefix": "",
                    "selected_only": False,
                    "type_filter": ["MESH"],
                },
            )

    texts = []
    for item in result.content:
        text = getattr(item, "text", None)
        if isinstance(text, str):
            texts.append(text)
    return json.loads("".join(texts))


def _wait_for_server_startup():
    deadline = time.time() + 3.0
    while time.time() < deadline:
        try:
            with request.urlopen("http://127.0.0.1:8767/health", timeout=0.2):
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
    deadline = time.time() + 3.0
    while time.time() < deadline:
        req = request.Request(
            "http://127.0.0.1:8767/api/addon/command/poll",
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
            "http://127.0.0.1:8767/api/addon/command-result",
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
