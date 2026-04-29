from __future__ import annotations

import subprocess
from pathlib import Path

from starlette.testclient import TestClient

from blender_mcp_server.server import create_starlette_app
from blender_mcp_server.services.codex_cli_client import CodexCliConfig
from blender_mcp_server.services.codex_cli_client import CodexCliError
from blender_mcp_server.services.codex_cli_client import run_codex_cli_suggestion
from blender_mcp_server.services.suggestion_service import build_ai_suggestion_payload
from blender_mcp_server.services.suggestion_service import _build_proposed_action
from blender_mcp_server.services.suggestion_service import _build_user_prompt


J_KIRBY_PROMPT = "\u30ab\u30fc\u30d3\u30a3\u3092\u4f5c\u3063\u3066\u307b\u3057\u3044\u3067\u3059"
J_SAFE_SUMMARY = "\u5b89\u5168\u306a\u63d0\u6848\u3067\u3059\u3002"
J_CUBE_PROMPT = "Cube \u3092\u5c11\u3057\u5927\u304d\u304f\u3057\u3066\u304f\u3060\u3055\u3044\u3002"
J_USER_REQUEST = "\u30e6\u30fc\u30b6\u30fc\u306e\u4f9d\u983c"
J_SELECTED_OBJECTS = "\u9078\u629e\u4e2d\u30aa\u30d6\u30b8\u30a7\u30af\u30c8"
J_SCENE_SUMMARY = "\u30b7\u30fc\u30f3\u6982\u8981"
J_CONSTRAINTS = "\u5236\u7d04"
J_OUTPUT_RULE = "\u5fc5\u305a\u65e5\u672c\u8a9e\u3067\u56de\u7b54\u3059\u308b\u3053\u3068"
J_SPHERE = "\u7403\u4f53"
J_KIRBY = "\u30ab\u30fc\u30d3\u30a3"


def test_run_codex_cli_suggestion_reads_plain_text_output(monkeypatch, tmp_path):
    def fake_run(command, cwd, capture_output, text, encoding, timeout, check):
        assert command[0] == "codex.cmd"
        output_index = command.index("--output-last-message") + 1
        written_output_path = Path(command[output_index])
        written_output_path.write_text(J_SAFE_SUMMARY, encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", fake_run)
    result = run_codex_cli_suggestion(
        config=CodexCliConfig(
            command="codex.cmd",
            model="gpt-5",
            timeout_seconds=5.0,
            working_directory=tmp_path,
        ),
        user_prompt=J_USER_REQUEST,
        system_prompt=J_CONSTRAINTS,
    )

    assert result["provider"] == "codex-cli"
    assert result["model"] == "gpt-5"
    assert result["content"] == J_SAFE_SUMMARY


def test_run_codex_cli_suggestion_raises_when_command_fails(tmp_path, monkeypatch):
    def fake_run(command, cwd, capture_output, text, encoding, timeout, check):
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="login required")

    monkeypatch.setattr("subprocess.run", fake_run)

    try:
        run_codex_cli_suggestion(
            config=CodexCliConfig(
                command="codex.cmd",
                model="",
                timeout_seconds=5.0,
                working_directory=tmp_path,
            ),
            user_prompt="prompt",
            system_prompt="system",
        )
    except CodexCliError as exc:
        assert exc.code == "CODEX_CLI_ERROR"
        assert "login required" in exc.message
    else:
        raise AssertionError("Expected CodexCliError to be raised.")


def test_ai_suggestion_endpoint_returns_codex_cli_error(monkeypatch):
    monkeypatch.setattr(
        "blender_mcp_server.services.suggestion_service.run_codex_cli_suggestion",
        lambda **_: (_ for _ in ()).throw(
            CodexCliError("CODEX_CLI_NOT_FOUND", "Codex CLI command was not found: codex.cmd")
        ),
    )
    app = create_starlette_app(_FakeMcpServer())

    with TestClient(app) as client:
        response = client.post(
            "/api/ai/suggest",
            json={
                "prompt": J_CUBE_PROMPT,
                "selectedObjects": [],
                "sceneSummary": {"objectCount": 1},
                "constraints": {"allowActions": ["transform_object"]},
            },
        )

    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "CODEX_CLI_NOT_FOUND"


def test_build_user_prompt_uses_japanese_sections():
    prompt = _build_user_prompt(
        prompt=J_KIRBY_PROMPT,
        selected_objects=[{"name": "Cube", "type": "MESH"}],
        scene_summary={"objectCount": 1},
        constraints={"allowActions": ["create_primitive", "transform_object"]},
    )

    assert J_USER_REQUEST in prompt
    assert J_SELECTED_OBJECTS in prompt
    assert J_SCENE_SUMMARY in prompt
    assert J_CONSTRAINTS in prompt
    assert J_OUTPUT_RULE in prompt


def test_build_ai_suggestion_payload_falls_back_to_japanese_when_model_returns_english(monkeypatch):
    monkeypatch.setattr(
        "blender_mcp_server.services.suggestion_service.load_codex_cli_config",
        lambda: CodexCliConfig(
            command="codex.cmd",
            model="gpt-5",
            timeout_seconds=5.0,
            working_directory=Path.cwd(),
        ),
    )
    monkeypatch.setattr(
        "blender_mcp_server.services.suggestion_service.run_codex_cli_suggestion",
        lambda **_: {
            "provider": "codex-cli",
            "model": "gpt-5",
            "content": "Move the selected object slightly upward.",
        },
    )

    result = build_ai_suggestion_payload(
        prompt=J_KIRBY_PROMPT,
        selected_objects=[],
        scene_summary={"objectCount": 1},
        constraints={"allowActions": ["create_primitive", "transform_object"]},
    )

    assert result["success"] is True
    summary = result["data"]["suggestions"][0]["summary"]
    assert J_KIRBY in summary
    assert J_SPHERE in summary
    assert "Move the selected object" not in summary


def test_build_ai_suggestion_payload_falls_back_when_model_returns_meta_response(monkeypatch):
    monkeypatch.setattr(
        "blender_mcp_server.services.suggestion_service.load_codex_cli_config",
        lambda: CodexCliConfig(
            command="codex.cmd",
            model="gpt-5",
            timeout_seconds=5.0,
            working_directory=Path.cwd(),
        ),
    )
    monkeypatch.setattr(
        "blender_mcp_server.services.suggestion_service.run_codex_cli_suggestion",
        lambda **_: {
            "provider": "codex-cli",
            "model": "gpt-5",
            "content": "\u63d0\u6848\u5185\u5bb9\u3092\u8cbc\u3063\u3066\u304f\u3060\u3055\u3044\u3002",
        },
    )

    result = build_ai_suggestion_payload(
        prompt=J_KIRBY_PROMPT,
        selected_objects=[],
        scene_summary={"objectCount": 1},
        constraints={"allowActions": ["create_primitive", "transform_object"]},
    )

    assert result["success"] is True
    summary = result["data"]["suggestions"][0]["summary"]
    assert J_KIRBY in summary
    assert J_SPHERE in summary


def test_build_ai_suggestion_payload_falls_back_when_model_returns_background_meta(monkeypatch):
    monkeypatch.setattr(
        "blender_mcp_server.services.suggestion_service.load_codex_cli_config",
        lambda: CodexCliConfig(
            command="codex.cmd",
            model="gpt-5",
            timeout_seconds=5.0,
            working_directory=Path.cwd(),
        ),
    )
    monkeypatch.setattr(
        "blender_mcp_server.services.suggestion_service.run_codex_cli_suggestion",
        lambda **_: {
            "provider": "codex-cli",
            "model": "gpt-5",
            "content": (
                "了解。以後、Blender MCP 向けの背景案生成器として振る舞います。"
                " 必要なら次の形式で返せます。"
                " 被写体、世界観、用途、画角、時間帯を指定してください。"
            ),
        },
    )

    result = build_ai_suggestion_payload(
        prompt=J_KIRBY_PROMPT,
        selected_objects=[],
        scene_summary={"objectCount": 1},
        constraints={"allowActions": ["create_primitive", "transform_object"]},
    )

    assert result["success"] is True
    summary = result["data"]["suggestions"][0]["summary"]
    assert J_KIRBY in summary
    assert J_SPHERE in summary


def test_build_proposed_action_creates_kirby_base():
    action = _build_proposed_action(
        prompt=J_KIRBY_PROMPT,
        selected_objects=[],
        constraints={"allowActions": ["create_primitive", "transform_object"]},
    )

    assert action is not None
    assert action["action"] == "create_primitive"
    assert action["params"]["type"] == "UV_SPHERE"
    assert action["params"]["name"] == "Kirby_Base"


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
