from __future__ import annotations

from ..services.approval_store import get_approval_result


def blender_get_request_status_tool(*, request_id: str) -> dict[str, object]:
    result = get_approval_result(request_id)
    if result is None:
        return {
            "success": True,
            "data": {
                "requestId": request_id,
                "status": "pending",
            },
        }

    return {
        "success": True,
        "data": {
            "requestId": request_id,
            "status": result.get("finalState", "completed"),
            "result": result,
        },
    }
