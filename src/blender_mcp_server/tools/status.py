from ..services.status_service import build_status_payload


def blender_status_tool() -> dict[str, object]:
    return build_status_payload()
