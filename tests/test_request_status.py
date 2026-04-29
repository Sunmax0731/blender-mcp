from __future__ import annotations

from starlette.testclient import TestClient

from blender_mcp_server.server import create_starlette_app
from blender_mcp_server.services.approval_store import reset_approval_state
from blender_mcp_server.services.approval_store import submit_approval_result
from blender_mcp_server.tools.request_status import blender_get_request_status_tool


def test_request_status_tool_returns_pending_then_completed():
    reset_approval_state()

    pending = blender_get_request_status_tool(request_id="req-00042")
    assert pending["success"] is True
    assert pending["data"]["status"] == "pending"

    submit_approval_result(
        {
            "requestId": "req-00042",
            "finalState": "approved_executed",
            "success": True,
        }
    )
    completed = blender_get_request_status_tool(request_id="req-00042")
    assert completed["success"] is True
    assert completed["data"]["status"] == "approved_executed"


def test_request_status_http_endpoint_returns_stored_result():
    reset_approval_state()
    submit_approval_result(
        {
            "requestId": "req-00999",
            "finalState": "rejected",
            "success": False,
        }
    )
    app = create_starlette_app(_FakeMcpServer())

    with TestClient(app) as client:
        response = client.get("/api/requests/req-00999")

    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "rejected"
    assert payload["data"]["result"]["requestId"] == "req-00999"


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
