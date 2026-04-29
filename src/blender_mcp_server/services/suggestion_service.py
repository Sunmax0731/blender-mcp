from __future__ import annotations

import json
import re
from collections.abc import Mapping

from .codex_cli_client import CodexCliError
from .codex_cli_client import load_codex_cli_config
from .codex_cli_client import run_codex_cli_suggestion


def build_ai_suggestion_payload(
    *,
    prompt: str,
    selected_objects: list[dict[str, object]] | None = None,
    scene_summary: dict[str, object] | None = None,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    normalized_constraints = constraints or {}
    user_prompt = _build_user_prompt(
        prompt=prompt,
        selected_objects=selected_objects or [],
        scene_summary=scene_summary or {},
        constraints=normalized_constraints,
    )
    system_prompt = _build_system_prompt()

    try:
        result = run_codex_cli_suggestion(
            config=load_codex_cli_config(),
            user_prompt=user_prompt,
            system_prompt=system_prompt,
        )
    except CodexCliError as exc:
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
                    "summary": _normalize_suggestion_summary(
                        prompt=prompt,
                        content=result["content"],
                        constraints=normalized_constraints,
                    ),
                    "proposedAction": _build_proposed_action(
                        prompt=prompt,
                        selected_objects=selected_objects or [],
                        constraints=normalized_constraints,
                    ),
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
    parts = [f"ユーザーの依頼:\n{prompt.strip()}"]
    if selected_objects:
        parts.append(
            "選択中オブジェクト:\n"
            + json.dumps(selected_objects, ensure_ascii=False, indent=2)
        )
    if scene_summary:
        parts.append(
            "シーン概要:\n"
            + json.dumps(dict(scene_summary), ensure_ascii=False, indent=2)
        )
    if constraints:
        parts.append(
            "制約:\n"
            + json.dumps(dict(constraints), ensure_ascii=False, indent=2)
        )
    parts.append(
        "出力要件:\n"
        "- 必ず日本語で回答すること\n"
        "- ユーザーの依頼と辻褄が合う内容にすること\n"
        "- 制約内で実行可能な具体的な次の一手を 2 文以内で提案すること\n"
        "- 制約のため依頼をそのまま満たせない場合は、その理由と代替案を日本語で短く述べること"
    )
    return "\n\n".join(parts)


def _build_system_prompt() -> str:
    return (
        "あなたは Blender MCP の提案アシスタントです。"
        "必ず日本語で回答してください。"
        "ユーザーの依頼内容と辻褄が合う、具体的で安全な提案だけを返してください。"
        "許可されていない操作を前提にしてはいけません。"
        "英語のみの回答、一般論、依頼と無関係な transform 提案は禁止です。"
        "回答は 2 文以内で簡潔にまとめてください。"
    )


def _normalize_suggestion_summary(
    *,
    prompt: str,
    content: str,
    constraints: Mapping[str, object],
) -> str:
    normalized = " ".join(content.strip().split())
    if normalized and _is_reasonable_japanese_response(prompt=prompt, content=normalized):
        return normalized
    return _build_japanese_fallback(prompt=prompt, constraints=constraints)


def _is_reasonable_japanese_response(*, prompt: str, content: str) -> bool:
    if not content:
        return False
    if _contains_japanese(prompt) and not _contains_japanese(content):
        return False
    if _looks_like_meta_response(content):
        return False

    request_keywords = _extract_request_keywords(prompt)
    if not request_keywords:
        return True

    keyword_hits = sum(1 for keyword in request_keywords if keyword in content)
    return keyword_hits > 0


def _contains_japanese(text: str) -> bool:
    return re.search(r"[\u3040-\u30ff\u3400-\u9fff]", text) is not None


def _looks_like_meta_response(content: str) -> bool:
    blocked_phrases = (
        "内容がまだ見えていません",
        "提案内容を貼って",
        "要件を貼って",
        "必要なら次のどれでも対応します",
        "必要なら次の形式で指示してください",
        "必要なら次の形式で返せます",
        "入力をもらえれば",
        "了解しました。以後",
        "了解。以後",
        "背景提案生成器として振る舞います",
        "背景案生成器として振る舞います",
        "被写体、世界観、用途、画角、時間帯を指定してください",
        "指定がなければこちらで補完します",
        "対応します",
        "貼ってください",
        "指定してください",
    )
    return any(phrase in content for phrase in blocked_phrases)


def _extract_request_keywords(prompt: str) -> list[str]:
    compact = prompt.replace(" ", "")
    keywords: list[str] = []
    if any(token in compact for token in ("カービィ", "kirby", "Kirby")):
        keywords.extend(["カービィ", "球体", "丸"])
    if any(token in compact for token in ("作って", "作成", "モデル", "作り")):
        keywords.extend(["作成", "モデル", "形状"])
    if any(token in compact for token in ("大き", "拡大", "scale")):
        keywords.append("拡大")
    if any(token in compact for token in ("移動", "上", "持ち上げ", "move")):
        keywords.append("移動")
    return list(dict.fromkeys(keywords))


def _build_japanese_fallback(*, prompt: str, constraints: Mapping[str, object]) -> str:
    compact = prompt.replace(" ", "")
    allowed_actions = {str(item) for item in constraints.get("allowActions", [])}
    can_create = "create_primitive" in allowed_actions

    if any(token in compact for token in ("カービィ", "kirby", "Kirby")):
        if can_create:
            return (
                "カービィらしい丸いシルエットを作るため、まず球体を追加して胴体の大きさを整え、"
                "次に小さめの球体や立方体を組み合わせて手足の位置を決めるのが安全です。"
            )
        return (
            "カービィを新規に作るにはプリミティブ追加が必要ですが、現在は作成操作が制限されています。"
            "まず既存オブジェクトを丸いシルエットに近づける拡大・移動から始めてください。"
        )

    if any(token in compact for token in ("大き", "拡大", "scale")):
        return "対象オブジェクトを選択し、全体のバランスを崩さないよう均等拡大で少しずつ大きくしてください。"
    if any(token in compact for token in ("移動", "上", "持ち上げ", "move")):
        return "対象オブジェクトを選択し、他のオブジェクトとの位置関係を見ながら少しずつ移動してください。"

    return (
        f"依頼内容は「{prompt.strip()}」です。まず対象オブジェクトや必要なプリミティブを確認し、"
        "制約内で実行できる小さな形状調整から進めてください。"
    )


def _build_proposed_action(
    *,
    prompt: str,
    selected_objects: list[dict[str, object]],
    constraints: Mapping[str, object],
) -> dict[str, object] | None:
    compact = prompt.replace(" ", "")
    allowed_actions = {str(item) for item in constraints.get("allowActions", [])}
    selected_name = _first_selected_name(selected_objects)

    if "list_objects" in allowed_actions and any(token in compact for token in ("一覧", "リスト", "表示中")):
        return {
            "action": "list_objects",
            "params": {},
            "requiresConfirmation": False,
        }

    if "create_primitive" in allowed_actions:
        if any(token in compact for token in ("カービィ", "kirby", "Kirby")):
            return {
                "action": "create_primitive",
                "params": {
                    "type": "UV_SPHERE",
                    "name": "Kirby_Base",
                    "location": [0.0, 0.0, 1.0],
                    "rotationEuler": [0.0, 0.0, 0.0],
                    "scale": [1.4, 1.4, 1.4],
                },
                "requiresConfirmation": False,
            }
        if any(token in compact for token in ("球", "sphere", "スフィア")):
            return {
                "action": "create_primitive",
                "params": {
                    "type": "UV_SPHERE",
                    "name": "Sphere_A",
                    "location": [0.0, 0.0, 1.0],
                    "rotationEuler": [0.0, 0.0, 0.0],
                    "scale": [1.0, 1.0, 1.0],
                },
                "requiresConfirmation": False,
            }
        if any(token in compact for token in ("立方体", "キューブ", "cube")):
            return {
                "action": "create_primitive",
                "params": {
                    "type": "CUBE",
                    "name": "Cube_A",
                    "location": [0.0, 0.0, 1.0],
                    "rotationEuler": [0.0, 0.0, 0.0],
                    "scale": [1.0, 1.0, 1.0],
                },
                "requiresConfirmation": False,
            }

    if "transform_object" not in allowed_actions or not selected_name:
        return None

    if any(token in compact for token in ("大き", "拡大", "scale")):
        return {
            "action": "transform_object",
            "params": {
                "targetObjectName": selected_name,
                "location": [0.0, 0.0, 0.0],
                "rotationEuler": [0.0, 0.0, 0.0],
                "scale": [1.2, 1.2, 1.2],
                "mode": "delta",
            },
            "requiresConfirmation": False,
        }

    if any(token in compact for token in ("小さ", "縮小")):
        return {
            "action": "transform_object",
            "params": {
                "targetObjectName": selected_name,
                "location": [0.0, 0.0, 0.0],
                "rotationEuler": [0.0, 0.0, 0.0],
                "scale": [0.8, 0.8, 0.8],
                "mode": "delta",
            },
            "requiresConfirmation": False,
        }

    if any(token in compact for token in ("上", "持ち上げ", "移動", "move")):
        return {
            "action": "transform_object",
            "params": {
                "targetObjectName": selected_name,
                "location": [0.0, 0.0, 1.0],
                "rotationEuler": [0.0, 0.0, 0.0],
                "scale": [1.0, 1.0, 1.0],
                "mode": "delta",
            },
            "requiresConfirmation": False,
        }

    return None


def _first_selected_name(selected_objects: list[dict[str, object]]) -> str | None:
    for item in selected_objects:
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return None
