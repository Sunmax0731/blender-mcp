from src.blender_mcp_server.services.status_service import build_status_payload


def test_build_status_payload_returns_disconnected_shape():
    payload = build_status_payload()

    assert payload["success"] is True
    assert payload["data"]["transportStatus"] == "disconnected"
