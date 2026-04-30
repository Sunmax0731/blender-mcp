from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image


SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
PROMPT_PRIORITY_FIELDS = [
    "character_type",
    "rig_spec.template",
    "expression_spec.required_expressions",
]
IMAGE_PRIORITY_FIELDS = [
    "body_proportions",
    "parts.hair",
    "look_spec.materials",
    "look_spec.textures",
]
_VIEW_PRIORITY = ["front", "side", "back", "face_closeup"]
_HAIR_KEYWORDS = ("short", "long", "bob", "twintail", "twin tail", "ponytail", "curly", "spiky")


def analyze_image_reference_package(
    package_path: str | Path,
    *,
    prompt: str,
    character_spec: dict[str, Any],
) -> dict[str, Any]:
    package_dir = Path(package_path)
    notes = _load_notes(package_dir / "notes.md")
    images = _discover_images(package_dir)
    if "front" not in images:
        raise ValueError("image reference package must include a front image")

    input_images: list[dict[str, Any]] = []
    detected_views: list[str] = []
    color_hints: list[dict[str, Any]] = []
    shape_hints: list[dict[str, Any]] = []
    expression_hints: list[dict[str, Any]] = []

    for view, image_path in images.items():
        metadata, image = _load_image_metadata(image_path)
        input_images.append(metadata)
        detected_views.append(view)

        if view in {"front", "side", "back", "face_closeup"}:
            color_hints.append(_extract_color_hint(view, image, metadata))
            shape_hints.append(_extract_shape_hint(view, image, metadata))

        if view == "face_closeup" or view.startswith("expression_"):
            expression_hints.append(_extract_expression_hint(view, image, metadata))

    if not expression_hints and notes.get("expression_notes"):
        expression_hints.append(
            {
                "view": "notes",
                "expression": "notes_only",
                "notes": notes["expression_notes"],
            }
        )

    overall_primary_color = _resolve_primary_color(color_hints)
    overall_accent_color = _resolve_accent_color(color_hints)
    dominant_hair_keyword = _detect_hair_keyword(
        " ".join(
            filter(
                None,
                [
                    str(notes.get("hair_silhouette_to_preserve", "")),
                    str(notes.get("extra_notes", "")),
                ],
            )
        )
    )
    conflicts = _detect_prompt_image_conflicts(
        prompt=prompt,
        character_spec=character_spec,
        overall_accent_color=overall_accent_color,
        dominant_hair_keyword=dominant_hair_keyword,
        expression_hints=expression_hints,
    )

    manifest = {
        "schema_version": "0.1",
        "package_path": str(package_dir),
        "input_images": input_images,
        "detected_views": detected_views,
        "extracted_color_hints": color_hints,
        "extracted_shape_hints": shape_hints,
        "extracted_expression_hints": expression_hints,
        "prompt_image_conflicts": conflicts,
        "prompt_priority_fields": PROMPT_PRIORITY_FIELDS,
        "image_priority_fields": IMAGE_PRIORITY_FIELDS,
        "resolved_hints": {
            "primary_color": overall_primary_color,
            "accent_color": overall_accent_color,
            "hair_keyword": dominant_hair_keyword,
            "face_feature_notes": notes.get("face_features_to_preserve"),
            "pattern_notes": notes.get("pattern_or_color_placement_to_preserve"),
            "body_proportion_notes": notes.get("body_proportion_hints"),
        },
        "notes_summary": notes,
    }
    return manifest


def apply_image_reference_to_character_spec(
    character_spec: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    spec = json.loads(json.dumps(character_spec))
    accent_color = manifest.get("resolved_hints", {}).get("accent_color")
    primary_color = manifest.get("resolved_hints", {}).get("primary_color")
    hair_keyword = manifest.get("resolved_hints", {}).get("hair_keyword")
    body_notes = manifest.get("resolved_hints", {}).get("body_proportion_notes")
    face_notes = manifest.get("resolved_hints", {}).get("face_feature_notes")
    pattern_notes = manifest.get("resolved_hints", {}).get("pattern_notes")

    spec["image_reference"] = {
        "enabled": True,
        "manifest_ref": "validation/image_reference_manifest.json",
        "detected_views": manifest.get("detected_views", []),
        "prompt_image_conflicts": manifest.get("prompt_image_conflicts", []),
        "priority_fields": {
            "prompt": manifest.get("prompt_priority_fields", []),
            "image": manifest.get("image_priority_fields", []),
        },
    }
    spec["body_proportions"]["image_reference_hints"] = manifest.get("extracted_shape_hints", [])
    if body_notes:
        spec["body_proportions"]["reference_notes"] = body_notes

    if primary_color:
        spec["look_spec"]["primary_reference_color"] = primary_color
    if accent_color:
        for material in spec.get("look_spec", {}).get("materials", []):
            if material.get("part") == "accent":
                material["base_color"] = accent_color
                material["color_source"] = "image_reference"
                break
    if pattern_notes and spec.get("look_spec", {}).get("textures"):
        spec["look_spec"]["textures"][0]["reference_pattern_notes"] = pattern_notes

    spec["expression_spec"]["image_reference_hints"] = manifest.get("extracted_expression_hints", [])

    for part in spec.get("parts", []):
        if part.get("name") == "hair" and hair_keyword:
            part["notes"] = f"{part.get('notes', '').strip()} | image hair hint: {hair_keyword}".strip(" |")
        if part.get("name") == "face" and face_notes:
            part["notes"] = f"{part.get('notes', '').strip()} | image face hint: {face_notes}".strip(" |")

    return spec


def _discover_images(package_dir: Path) -> dict[str, Path]:
    search_roots = [package_dir]
    previews_dir = package_dir / "previews"
    if previews_dir.exists():
        search_roots.append(previews_dir)

    images: dict[str, Path] = {}
    for root in search_roots:
        for image_path in root.iterdir():
            if image_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
                continue
            view = _detect_view_name(image_path.stem)
            if view is None or view in images:
                continue
            images[view] = image_path

    ordered: dict[str, Path] = {}
    for view in _VIEW_PRIORITY:
        if view in images:
            ordered[view] = images[view]
    for view in sorted(key for key in images if key not in ordered):
        ordered[view] = images[view]
    return ordered


def _detect_view_name(stem: str) -> str | None:
    normalized = stem.lower().replace("-", "_").replace(" ", "_")
    if normalized.startswith("expression_"):
        return normalized
    for candidate in ("front", "side", "back", "face_closeup", "face"):
        if normalized == candidate:
            return "face_closeup" if candidate == "face" else candidate
    return None


def _load_notes(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    parsed: dict[str, str] = {}
    key_map = {
        "highest_priority_image": "highest_priority_image",
        "secondary_image": "secondary_image",
        "same_character_across_all_images": "same_character_across_all_images",
        "same_outfit_across_all_images": "same_outfit_across_all_images",
        "same_hairstyle_across_all_images": "same_hairstyle_across_all_images",
        "face_features_to_preserve": "face_features_to_preserve",
        "hair_silhouette_to_preserve": "hair_silhouette_to_preserve",
        "body_proportion_hints": "body_proportion_hints",
        "pattern_or_color_placement_to_preserve": "pattern_or_color_placement_to_preserve",
        "any_intentional_difference_from_the_prompt": "prompt_difference_notes",
        "expression_notes": "expression_notes",
        "areas_that_may_be_ambiguous": "ambiguous_areas",
        "extra_notes": "extra_notes",
    }
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*[-*]?\s*([^:]+):\s*(.+?)\s*$", raw_line)
        if not match:
            continue
        raw_key = re.sub(r"[^a-z0-9]+", "_", match.group(1).strip().lower()).strip("_")
        key = key_map.get(raw_key, raw_key)
        parsed[key] = match.group(2).strip()
    return parsed


def _load_image_metadata(image_path: Path) -> tuple[dict[str, Any], Image.Image]:
    image = Image.open(image_path).convert("RGBA")
    metadata = {
        "view": _detect_view_name(image_path.stem),
        "path": str(image_path),
        "width": image.width,
        "height": image.height,
    }
    return metadata, image


def _extract_color_hint(view: str, image: Image.Image, metadata: dict[str, Any]) -> dict[str, Any]:
    palette = _dominant_palette(image)
    return {
        "view": view,
        "path": metadata["path"],
        "dominant_palette": palette,
        "primary_color": palette[0] if palette else None,
    }


def _extract_shape_hint(view: str, image: Image.Image, metadata: dict[str, Any]) -> dict[str, Any]:
    bbox = _foreground_bbox(image)
    width = metadata["width"]
    height = metadata["height"]
    if bbox is None:
        return {
            "view": view,
            "path": metadata["path"],
            "coverage_ratio": 0.0,
            "silhouette_aspect_ratio": round(height / max(width, 1), 3),
            "hair_volume_hint": "unknown",
        }

    left, top, right, bottom = bbox
    box_width = max(right - left, 1)
    box_height = max(bottom - top, 1)
    coverage_ratio = round((box_width * box_height) / max(width * height, 1), 4)
    silhouette_aspect_ratio = round(box_height / box_width, 3)
    top_band = _dark_pixel_ratio(image.crop((left, top, right, min(bottom, top + max(box_height // 3, 1)))))
    hair_volume_hint = "large" if top_band > 0.42 else "medium" if top_band > 0.22 else "small"
    return {
        "view": view,
        "path": metadata["path"],
        "coverage_ratio": coverage_ratio,
        "silhouette_aspect_ratio": silhouette_aspect_ratio,
        "hair_volume_hint": hair_volume_hint,
        "foreground_bbox": [left, top, right, bottom],
    }


def _extract_expression_hint(view: str, image: Image.Image, metadata: dict[str, Any]) -> dict[str, Any]:
    expression_name = "face_closeup"
    if view.startswith("expression_"):
        expression_name = view.removeprefix("expression_")
    grayscale = image.convert("L")
    upper = grayscale.crop((0, 0, grayscale.width, grayscale.height // 2))
    lower = grayscale.crop((0, grayscale.height // 2, grayscale.width, grayscale.height))
    return {
        "view": view,
        "path": metadata["path"],
        "expression": expression_name,
        "upper_feature_density": round(_dark_pixel_ratio(upper), 4),
        "lower_feature_density": round(_dark_pixel_ratio(lower), 4),
    }


def _dominant_palette(image: Image.Image, max_colors: int = 3) -> list[list[float]]:
    foreground = image.copy()
    foreground.thumbnail((64, 64))
    counter: Counter[tuple[int, int, int, int]] = Counter()
    for pixel in foreground.getdata():
        rgba = tuple(pixel)
        if _is_background_pixel(rgba):
            continue
        bucket = tuple(channel // 32 * 32 for channel in rgba[:3]) + (255,)
        counter[bucket] += 1

    palette: list[list[float]] = []
    for rgba, _count in counter.most_common(max_colors):
        palette.append([round(channel / 255, 3) for channel in rgba])
    return palette


def _foreground_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    alpha = image.getchannel("A")
    bbox = alpha.point(lambda value: 255 if value > 10 else 0).getbbox()
    if bbox is not None:
        return bbox

    width, height = image.size
    pixels = image.load()
    min_x, min_y = width, height
    max_x, max_y = -1, -1
    for y in range(height):
        for x in range(width):
            if _is_background_pixel(pixels[x, y]):
                continue
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
    if max_x < 0 or max_y < 0:
        return None
    return (min_x, min_y, max_x + 1, max_y + 1)


def _dark_pixel_ratio(image: Image.Image) -> float:
    grayscale = image.convert("L")
    values = list(grayscale.getdata())
    if not values:
        return 0.0
    dark_pixels = sum(1 for value in values if value < 120)
    return dark_pixels / len(values)


def _is_background_pixel(rgba: tuple[int, int, int, int]) -> bool:
    if rgba[3] <= 10:
        return True
    return rgba[0] >= 245 and rgba[1] >= 245 and rgba[2] >= 245


def _resolve_primary_color(color_hints: list[dict[str, Any]]) -> list[float] | None:
    for preferred_view in ("front", "face_closeup", "side", "back"):
        for hint in color_hints:
            if hint["view"] == preferred_view and hint.get("primary_color") is not None:
                return hint["primary_color"]
    return None


def _resolve_accent_color(color_hints: list[dict[str, Any]]) -> list[float] | None:
    candidates: list[list[float]] = []
    for hint in color_hints:
        candidates.extend(hint.get("dominant_palette", []))
    if not candidates:
        return None
    return max(candidates, key=_color_saturation)


def _color_saturation(rgba: list[float]) -> float:
    rgb = rgba[:3]
    return max(rgb) - min(rgb)


def _detect_prompt_image_conflicts(
    *,
    prompt: str,
    character_spec: dict[str, Any],
    overall_accent_color: list[float] | None,
    dominant_hair_keyword: str | None,
    expression_hints: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    prompt_lower = prompt.lower()

    if overall_accent_color is not None:
        prompt_accent = None
        for material in character_spec.get("look_spec", {}).get("materials", []):
            if material.get("part") == "accent":
                prompt_accent = material.get("base_color")
                break
        if isinstance(prompt_accent, list):
            diff = sum(abs(prompt_accent[index] - overall_accent_color[index]) for index in range(3))
            if diff > 0.45:
                conflicts.append(
                    {
                        "field": "look_spec.materials.accent",
                        "prompt_value": prompt_accent,
                        "image_value": overall_accent_color,
                        "winner": "image",
                        "reason": "major color hint is image-priority",
                    }
                )

    prompt_hair_keyword = _detect_hair_keyword(prompt_lower)
    if prompt_hair_keyword and dominant_hair_keyword and prompt_hair_keyword != dominant_hair_keyword:
        conflicts.append(
            {
                "field": "parts.hair",
                "prompt_value": prompt_hair_keyword,
                "image_value": dominant_hair_keyword,
                "winner": "image",
                "reason": "hair silhouette is image-priority",
            }
        )

    prompt_requires_talk = any(keyword in prompt_lower for keyword in ("talk", "speaking", "voice"))
    image_expressions = {hint.get("expression") for hint in expression_hints}
    if prompt_requires_talk and image_expressions and "talk" not in image_expressions:
        conflicts.append(
            {
                "field": "expression_spec.required_expressions",
                "prompt_value": "talking mouth shapes",
                "image_value": sorted(expression for expression in image_expressions if expression),
                "winner": "prompt",
                "reason": "required expressions remain prompt-priority",
            }
        )

    return conflicts


def _detect_hair_keyword(text: str) -> str | None:
    normalized = text.lower()
    for keyword in _HAIR_KEYWORDS:
        if keyword in normalized:
            return keyword.replace(" ", "_")
    return None
