from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import Response

from ..services.approval_store import get_approval_result
from ..services.approval_store import submit_approval_result
from ..services.command_store import claim_next_command
from ..services.command_store import submit_command_result
from ..services.status_service import build_status_payload
from ..services.status_store import update_status_state
from ..services.suggestion_service import build_ai_suggestion_payload
from ..tools.registry import build_tool_registry


async def health_endpoint(request: Request) -> Response:
    return JSONResponse({"ok": True})


async def ai_suggestion_endpoint(request: Request) -> Response:
    payload = await _read_json_body(request)
    if isinstance(payload, Response):
        return payload

    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return JSONResponse(
            {
                "success": False,
                "error": {
                    "code": "INVALID_ARGUMENT",
                    "message": "prompt is required.",
                },
            },
            status_code=400,
        )

    result = build_ai_suggestion_payload(
        prompt=prompt,
        selected_objects=payload.get("selectedObjects"),
        scene_summary=payload.get("sceneSummary"),
        constraints=payload.get("constraints"),
    )
    status_code = 200 if result.get("success") else 400
    return JSONResponse(result, status_code=status_code)


async def status_endpoint(request: Request) -> Response:
    return JSONResponse(build_status_payload())


async def request_status_endpoint(request: Request) -> Response:
    request_id = str(request.path_params.get("request_id", ""))
    result = get_approval_result(request_id)
    if result is None:
        return JSONResponse(
            {
                "success": True,
                "data": {
                    "requestId": request_id,
                    "status": "pending",
                },
            }
        )

    return JSONResponse(
        {
            "success": True,
            "data": {
                "requestId": request_id,
                "status": result.get("finalState", "completed"),
                "result": result,
            },
        }
    )


async def tools_endpoint(request: Request) -> Response:
    return JSONResponse(
        {
            "success": True,
            "data": {
                "tools": sorted(build_tool_registry().keys()),
            },
        }
    )


async def addon_status_endpoint(request: Request) -> Response:
    payload = await _read_json_body(request)
    if isinstance(payload, Response):
        return payload

    updated = update_status_state(payload)
    return JSONResponse({"success": True, "data": updated})


async def addon_command_poll_endpoint(request: Request) -> Response:
    payload = await _read_json_body(request)
    if isinstance(payload, Response):
        return payload

    update_status_state(payload)
    command = claim_next_command()
    return JSONResponse(
        {
            "success": True,
            "data": {
                "command": command,
            },
        }
    )


async def addon_command_result_endpoint(request: Request) -> Response:
    payload = await _read_json_body(request)
    if isinstance(payload, Response):
        return payload

    try:
        result = submit_command_result(payload)
    except ValueError as exc:
        return JSONResponse(
            {
                "success": False,
                "error": {
                    "code": "INVALID_ARGUMENT",
                    "message": str(exc),
                },
            },
            status_code=400,
        )

    return JSONResponse({"success": True, "data": result})


async def addon_approval_result_endpoint(request: Request) -> Response:
    payload = await _read_json_body(request)
    if isinstance(payload, Response):
        return payload

    try:
        result = submit_approval_result(payload)
    except ValueError as exc:
        return JSONResponse(
            {
                "success": False,
                "error": {
                    "code": "INVALID_ARGUMENT",
                    "message": str(exc),
                },
            },
            status_code=400,
        )

    return JSONResponse({"success": True, "data": result})


async def _read_json_body(request: Request) -> dict[str, object] | Response:
    try:
        payload = await request.json()
    except Exception:  # noqa: BLE001
        return JSONResponse(
            {
                "success": False,
                "error": {
                    "code": "INVALID_ARGUMENT",
                    "message": "Request body must be valid JSON.",
                },
            },
            status_code=400,
        )

    if not isinstance(payload, dict):
        return JSONResponse(
            {
                "success": False,
                "error": {
                    "code": "INVALID_ARGUMENT",
                    "message": "Request body must be a JSON object.",
                },
            },
            status_code=400,
        )
    return payload
