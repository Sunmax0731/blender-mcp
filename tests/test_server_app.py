from __future__ import annotations

from starlette.testclient import TestClient

from blender_mcp_server.server import create_starlette_app
from blender_mcp_server.server import create_server


def test_create_server_builds_starlette_app():
    server = create_server()

    assert server.name == "blender-mcp-server"
    assert server.host == "127.0.0.1"
    assert server.port == 8765
    assert server.app is not None


def test_tools_endpoint_returns_registered_tool_names():
    app = create_starlette_app(_FakeMcpServer())

    with TestClient(app) as client:
        response = client.get("/api/tools")

    payload = response.json()
    assert payload["success"] is True
    assert "blender_status" in payload["data"]["tools"]
    assert "blender_create_primitive" in payload["data"]["tools"]


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
            body = b'{"ok": true}'
            headers = [(b"content-type", b"application/json")]
            await send({"type": "http.response.start", "status": 200, "headers": headers})
            await send({"type": "http.response.body", "body": body})

        return app
