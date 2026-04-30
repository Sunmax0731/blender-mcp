from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADDON_DIR = ROOT / "blender_addon" / "blender_mcp"
SESSION_PATH = ADDON_DIR / "operators" / "session.py"


def _load_session_module():
    fake_bpy = types.ModuleType("bpy")
    fake_bpy.types = types.SimpleNamespace(Operator=object)
    fake_bpy.app = types.SimpleNamespace(version=(5, 1, 1))
    fake_bpy.context = types.SimpleNamespace(
        selected_objects=[],
        scene=types.SimpleNamespace(name="Scene"),
    )
    fake_bpy.data = types.SimpleNamespace(objects=[])

    executed_commands: list[dict[str, object]] = []

    command_executor_module = types.ModuleType("blender_mcp.services.command_executor")

    def _execute_command(*, command, bpy_module):
        executed_commands.append(command)
        return {
            "success": True,
            "message": "UV_SPHERE created.",
            "data": {"objectName": "Kirby_Base"},
        }

    command_executor_module.execute_command = _execute_command

    command_runtime_module = types.ModuleType("blender_mcp.services.command_runtime")
    command_runtime_module.process_next_command = lambda **_: {"success": True, "data": {"commandProcessed": False}}

    http_client_module = types.ModuleType("blender_mcp.services.http_client")

    def _request_ai_suggestion(**_kwargs):
        return {
            "success": True,
            "data": {
                "suggestions": [
                    {
                        "summary": "球体を追加してカービィの素体を作ります。",
                        "proposedAction": {
                            "action": "create_primitive",
                            "params": {"type": "UV_SPHERE", "name": "Kirby_Base"},
                            "requiresConfirmation": False,
                        },
                    }
                ]
            },
        }

    http_client_module.request_ai_suggestion = _request_ai_suggestion

    sys.modules["bpy"] = fake_bpy
    sys.modules["blender_mcp"] = types.ModuleType("blender_mcp")
    sys.modules["blender_mcp"].__path__ = [str(ADDON_DIR)]
    sys.modules["blender_mcp.operators"] = types.ModuleType("blender_mcp.operators")
    sys.modules["blender_mcp.operators"].__path__ = [str(ADDON_DIR / "operators")]
    sys.modules["blender_mcp.services"] = types.ModuleType("blender_mcp.services")
    sys.modules["blender_mcp.services"].__path__ = [str(ADDON_DIR / "services")]
    sys.modules["blender_mcp.services.command_executor"] = command_executor_module
    sys.modules["blender_mcp.services.command_runtime"] = command_runtime_module
    sys.modules["blender_mcp.services.http_client"] = http_client_module

    spec = importlib.util.spec_from_file_location("blender_mcp.operators.session", SESSION_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["blender_mcp.operators.session"] = module
    spec.loader.exec_module(module)
    return module, executed_commands


class _FakeState:
    def __init__(self):
        self.prompt_text = "カービィを作ってほしいです"
        self.prompt_plan_text = "実行計画はまだありません。"
        self.prompt_preview_text = "Preview はまだありません。"
        self.prompt_confirmed = False
        self.history_text = ""
        self.last_result_text = ""
        self.last_error = ""
        self.ui_state = "connected_idle"
        self.connection_label = "接続済み"
        self.addon_version = "0.1.1"
        self.blender_version = "5.1.1"
        self.pending_action_label = "承認待ちの操作はありません。"
        self.pending_request_id = ""
        self.pending_command_json = ""


class _FakeScene:
    def __init__(self):
        self.blender_mcp_state = _FakeState()
        self.name = "Scene"


class _FakeContext:
    def __init__(self):
        self.scene = _FakeScene()


def test_send_prompt_executes_proposed_action_when_available():
    module, executed_commands = _load_session_module()
    operator = module.BLENDERMCP_OT_send_prompt()
    context = _FakeContext()

    result = operator.execute(context)

    assert result == {"FINISHED"}
    assert executed_commands[0]["action"] == "create_primitive"
    state = context.scene.blender_mcp_state
    assert "AI: 球体を追加してカービィの素体を作ります。" in state.history_text
    assert "実行: UV_SPHERE created." in state.history_text
    assert state.last_result_text == "UV_SPHERE created."
    assert state.last_error == ""


def test_prompt_plan_confirm_execute_flow():
    module, executed_commands = _load_session_module()
    context = _FakeContext()

    plan_result = module.BLENDERMCP_OT_plan_prompt().execute(context)
    state = context.scene.blender_mcp_state

    assert plan_result == {"FINISHED"}
    assert executed_commands == []
    assert "球体を追加してカービィの素体を作ります。" in state.prompt_plan_text
    assert "Action: create_primitive" in state.prompt_preview_text
    assert state.prompt_confirmed is False

    confirm_result = module.BLENDERMCP_OT_confirm_prompt_plan().execute(context)

    assert confirm_result == {"FINISHED"}
    assert state.prompt_confirmed is True

    execute_result = module.BLENDERMCP_OT_execute_prompt_plan().execute(context)

    assert execute_result == {"FINISHED"}
    assert executed_commands[0]["action"] == "create_primitive"
    assert executed_commands[0]["params"]["_approved"] is True
    assert state.prompt_confirmed is False
    assert state.pending_command_json == ""
