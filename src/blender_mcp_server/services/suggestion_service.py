from __future__ import annotations

from collections.abc import Mapping

from .ai_client import OpenAICompatibleError
from .ai_client import create_chat_completion
from .ai_config import load_openai_compatible_config


def build_ai_suggestion_payload(
    *,
    prompt: str,
    selected_objects: list[dict[str, object]] | None = None,
    scene_summary: dict[str, object] | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    user_prompt = _build_user_prompt(
        prompt=prompt,
        selected_objects=selected_objects or [],
        scene_summary=scene_summary or {},
        constraints=constraints or {},
    )
    system_prompt = (
        "You are an assistant that proposes safe Blender modeling steps. "
        "Return concise suggestions in Japanese. "
        "Do not assume destructive actions are allowed. "
        "Prefer non-destructive transform suggestions."
    )

    try:
        result = create_chat_completion(
            config=load_openai_compatible_config(),
            user_prompt=user_prompt,
            system_prompt=system_prompt,
        )
    except OpenAICompatibleError as exc:
        return {
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "retryable": exc.retryable,
            },
        }

    return {
        "success": True,
        "data": {
            "provider": result["provider"],
            "model": result["model"],
            "suggestions": [
                {
                    "summary": result["content"],
                    "proposedAction": None,
                }
            ],
        },
    }


def _build_user_prompt(
    *,
    prompt: str,
    selected_objects: list[dict[str, object]],
    scene_summary: Mapping[str, object],
    constraints: Mapping[str, object],
) -> str:
    parts = [f"User request:\n{prompt.strip()}"]
    if selected_objects:
        parts.append(f"Selected objects:\n{selected_objects}")
    if scene_summary:
        parts.append(f"Scene summary:\n{dict(scene_summary)}")
    if constraints:
        parts.append(f"Constraints:\n{dict(constraints)}")
    parts.append("Return one safe Blender modeling suggestion in Japanese.")
    return "\n\n".join(parts)
