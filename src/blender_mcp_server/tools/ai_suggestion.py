from __future__ import annotations

from ..services.suggestion_service import build_ai_suggestion_payload


def blender_request_ai_suggestion_tool(
    *,
    prompt: str,
    selected_objects: list[dict[str, object]] | None = None,
    scene_summary: dict[str, object] | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    return build_ai_suggestion_payload(
        prompt=prompt,
        selected_objects=selected_objects,
        scene_summary=scene_summary,
        constraints=constraints,
    )
