from __future__ import annotations

import httpx
from starlette.testclient import TestClient

from blender_mcp_server.server import create_starlette_app
from blender_mcp_server.services.ai_client import OpenAICompatibleError
from blender_mcp_server.services.ai_client import create_chat_completion
from blender_mcp_server.services.ai_config import OpenAICompatibleConfig


def test_create_chat_completion_returns_text_from_mock_transport():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/chat/completions")
        return httpx.Response(
            200,
            json={
                "model": "mock-model",
                "choices": [
                    {
                        "message": {
                            "content": "安全な提案です。",
                        }
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    config = OpenAICompatibleConfig(
        base_url="https://example.com/v1",
        api_key="test-key",
        model="mock-model",
        timeout_seconds=5.0,
    )

    result = create_chat_completion(
        config=config,
        user_prompt="Move the cube upward.",
        system_prompt="safe suggestion",
        client=client,
    )

    assert result["content"] == "安全な提案です。"


def test_create_chat_completion_requires_api_key():
    config = OpenAICompatibleConfig(
        base_url="https://example.com/v1",
        api_key="",
        model="mock-model",
        timeout_seconds=5.0,
    )

    try:
        create_chat_completion(
            config=config,
            user_prompt="prompt",
            system_prompt="system",
        )
    except OpenAICompatibleError as exc:
        assert exc.code == "AI_PROVIDER_NOT_CONFIGURED"
    else:
        raise AssertionError("Expected OpenAICompatibleError to be raised.")


def test_ai_suggestion_endpoint_returns_configuration_error_when_key_missing(monkeypatch):
    monkeypatch.delenv("BLENDER_MCP_OPENAI_API_KEY", raising=False)
    app = create_starlette_app(_FakeMcpServer())

    with TestClient(app) as client:
        response = client.post(
            "/api/ai/suggest",
            json={
                "prompt": "Cube を少し大きくしてください。",
                "selectedObjects": [],
                "sceneSummary": {"objectCount": 1},
                "constraints": {"allowActions": ["transform_object"]},
            },
        )

    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "AI_PROVIDER_NOT_CONFIGURED"


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
