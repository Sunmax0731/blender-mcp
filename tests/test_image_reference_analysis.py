from __future__ import annotations

from pathlib import Path

from PIL import Image

from blender_precision_mcp.auto_character import normalize_prompt_to_character_spec
from blender_precision_mcp.image_reference_analysis import analyze_image_reference_package
from blender_precision_mcp.image_reference_analysis import apply_image_reference_to_character_spec


def test_analyze_image_reference_package_extracts_views_and_conflicts(tmp_path):
    package_dir = tmp_path / "image-reference-package"
    package_dir.mkdir(parents=True, exist_ok=True)
    _write_reference_image(package_dir / "front.png", body_color=(32, 64, 196, 255), hair_color=(220, 90, 120, 255))
    _write_reference_image(package_dir / "side.png", body_color=(32, 64, 196, 255), hair_color=(220, 90, 120, 255))
    _write_reference_image(package_dir / "face_closeup.png", body_color=(240, 220, 200, 255), hair_color=(220, 90, 120, 255))
    _write_reference_image(package_dir / "expression_smile.png", body_color=(240, 220, 200, 255), hair_color=(220, 90, 120, 255))
    (package_dir / "notes.md").write_text(
        "\n".join(
            [
                "Hair silhouette to preserve: long layered hair",
                "Body proportion hints: compact torso and wide head",
                "Face features to preserve: large eyes and rounded mouth",
                "Pattern or color placement to preserve: blue jacket with pink trim",
            ]
        ),
        encoding="utf-8",
    )

    prompt = "Create a humanoid hero with blue jacket and short hair."
    character_spec = normalize_prompt_to_character_spec(prompt)
    manifest = analyze_image_reference_package(package_dir, prompt=prompt, character_spec=character_spec)

    assert manifest["detected_views"] == ["front", "side", "face_closeup", "expression_smile"]
    assert manifest["resolved_hints"]["hair_keyword"] == "long"
    assert manifest["resolved_hints"]["accent_color"] is not None
    assert any(conflict["field"] == "parts.hair" for conflict in manifest["prompt_image_conflicts"])
    assert any(hint["view"] == "expression_smile" for hint in manifest["extracted_expression_hints"])


def test_apply_image_reference_to_character_spec_overrides_image_priority_fields(tmp_path):
    package_dir = tmp_path / "image-reference-package"
    package_dir.mkdir(parents=True, exist_ok=True)
    _write_reference_image(package_dir / "front.png", body_color=(32, 64, 196, 255), hair_color=(220, 90, 120, 255))
    _write_reference_image(package_dir / "face_closeup.png", body_color=(240, 220, 200, 255), hair_color=(220, 90, 120, 255))
    (package_dir / "notes.md").write_text(
        "\n".join(
            [
                "Hair silhouette to preserve: long layered hair",
                "Pattern or color placement to preserve: blue jacket with pink trim",
            ]
        ),
        encoding="utf-8",
    )

    prompt = "Create a humanoid hero with blue jacket and short hair."
    character_spec = normalize_prompt_to_character_spec(prompt)
    manifest = analyze_image_reference_package(package_dir, prompt=prompt, character_spec=character_spec)
    enriched = apply_image_reference_to_character_spec(character_spec, manifest)

    accent_material = next(material for material in enriched["look_spec"]["materials"] if material["part"] == "accent")
    hair_part = next(part for part in enriched["parts"] if part["name"] == "hair")

    assert enriched["image_reference"]["enabled"] is True
    assert accent_material["color_source"] == "image_reference"
    assert "image hair hint: long" in hair_part["notes"]
    assert enriched["look_spec"]["textures"][0]["reference_pattern_notes"] == "blue jacket with pink trim"


def _write_reference_image(path: Path, *, body_color: tuple[int, int, int, int], hair_color: tuple[int, int, int, int]) -> None:
    image = Image.new("RGBA", (128, 192), (255, 255, 255, 0))
    pixels = image.load()
    for y in range(36, 170):
        for x in range(34, 96):
            pixels[x, y] = body_color
    for y in range(10, 52):
        for x in range(28, 102):
            pixels[x, y] = hair_color
    image.save(path)
