from blender_mcp_server.services.status_service import build_status_payload
from blender_mcp_server.services.status_store import reset_status_state
from blender_mcp_server.services.status_store import update_status_state


def test_build_status_payload_returns_disconnected_shape():
    reset_status_state()
    payload = build_status_payload()

    assert payload["success"] is True
    assert payload["data"]["transportStatus"] == "disconnected"


def test_update_status_state_persists_connected_status():
    reset_status_state()
    updated = update_status_state(
        {
            "blenderRunning": True,
            "addonLoaded": True,
            "addonVersion": "0.1.0",
            "blenderVersion": "4.5.0",
            "transportStatus": "connected",
        }
    )

    assert updated["blenderRunning"] is True
    assert updated["addonLoaded"] is True
    assert updated["transportStatus"] == "connected"
