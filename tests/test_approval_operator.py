from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADDON_DIR = ROOT / "blender_addon" / "blender_mcp"
APPROVAL_PATH = ADDON_DIR / "operators" / "approval.py"


def _load_approval_module():
    fake_bpy = types.ModuleType("bpy")
    fake_bpy.types = types.SimpleNamespace(Operator=object)

    command_executor_module = types.ModuleType("blender_mcp.services.command_executor")

    def _execute_command(_command, _bpy_module):
        return {"success": True}

    command_executor_module.execute_command = _execute_command

    http_client_module = types.ModuleType("blender_mcp.services.http_client")
    submitted_payloads: list[dict[str, object]] = []

    def _submit_approval_result(payload: dict[str, object]) -> dict[str, object]:
        submitted_payloads.append(payload)
        return payload

    http_client_module.submit_approval_result = _submit_approval_result

    sys.modules["bpy"] = fake_bpy
    sys.modules["blender_mcp"] = types.ModuleType("blender_mcp")
    sys.modules["blender_mcp"].__path__ = [str(ADDON_DIR)]
    sys.modules["blender_mcp.operators"] = types.ModuleType("blender_mcp.operators")
    sys.modules["blender_mcp.operators"].__path__ = [str(ADDON_DIR / "operators")]
    sys.modules["blender_mcp.services"] = types.ModuleType("blender_mcp.services")
    sys.modules["blender_mcp.services"].__path__ = [str(ADDON_DIR / "services")]
    sys.modules["blender_mcp.services.command_executor"] = command_executor_module
    sys.modules["blender_mcp.services.http_client"] = http_client_module

    spec = importlib.util.spec_from_file_location("blender_mcp.operators.approval", APPROVAL_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["blender_mcp.operators.approval"] = module
    spec.loader.exec_module(module)
    return module, submitted_payloads


class _FakeState:
    def __init__(self):
        self.history_text = ""
        self.pending_action_label = "delete_object: Cube"
        self.pending_request_id = "req-reject-1"
        self.pending_command_json = '{"action":"delete_object"}'
        self.ui_state = "approval_pending"
        self.connection_label = "承認待ち"
        self.last_error = "old"


class _FakeScene:
    def __init__(self):
        self.blender_mcp_state = _FakeState()


class _FakeContext:
    def __init__(self):
        self.scene = _FakeScene()


def test_reject_action_clears_pending_and_submits_result():
    module, submitted_payloads = _load_approval_module()
    operator = module.BLENDERMCP_OT_reject_action()
    context = _FakeContext()

    result = operator.execute(context)

    assert result == {"FINISHED"}
    assert submitted_payloads == [
        {
            "requestId": "req-reject-1",
            "action": "delete_object: Cube",
            "success": False,
            "finalState": "rejected",
        }
    ]
    state = context.scene.blender_mcp_state
    assert state.pending_action_label == "承認待ちの操作はありません。"
    assert state.pending_request_id == ""
    assert state.pending_command_json == ""
    assert state.ui_state == "connected_idle"
    assert state.connection_label == "接続済み"
    assert state.last_error == ""
    assert "却下しました" in state.history_text
