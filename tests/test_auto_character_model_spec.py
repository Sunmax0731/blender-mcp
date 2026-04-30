from __future__ import annotations

from blender_precision_mcp.auto_character import normalize_prompt_to_character_spec
from blender_precision_mcp.auto_character_model_spec import build_model_spec_from_character_spec


def test_build_model_spec_from_humanoid_character_spec():
    character_spec = normalize_prompt_to_character_spec(
        "Create a stylized human character with blue jacket and short hair."
    )

    model_spec = build_model_spec_from_character_spec(
        character_spec,
        output_dir="outputs/auto-character/humanoid-live",
    )

    assert model_spec["schema_version"] == "0.2"
    assert model_spec["scene"]["main_collection"] == "auto_character"
    assert model_spec["scene"]["reset_scene_before_build"] is True
    assert any(obj["name"] == "RoundBuddy_Body" and obj["type"] == "sphere" for obj in model_spec["objects"])
    assert any(obj["name"] == "RoundBuddy_Mouth" and obj["type"] == "torus" for obj in model_spec["objects"])
    assert model_spec["validation"]["forbid_extra_objects"] is True
    assert "RoundBuddy_Rig" in model_spec["validation"]["allowed_extra_objects"]
    assert model_spec["exports"][0]["path"].endswith("outputs/auto-character/humanoid-live/exports/final.blend")


def test_build_model_spec_adds_type_specific_parts():
    creature_spec = normalize_prompt_to_character_spec(
        "Create a green creature beast with striped tail for animation."
    )
    creature_model_spec = build_model_spec_from_character_spec(creature_spec)

    chibi_spec = normalize_prompt_to_character_spec(
        "Create a chibi hero with pink cape and expressive talking face."
    )
    chibi_model_spec = build_model_spec_from_character_spec(chibi_spec)

    creature_names = {obj["name"] for obj in creature_model_spec["objects"]}
    chibi_names = {obj["name"] for obj in chibi_model_spec["objects"]}

    assert "RoundBuddy_Tail" in creature_names
    assert "RoundBuddy_Horn_L" in creature_names
    assert "RoundBuddy_Cheek_L" in chibi_names
    assert "RoundBuddy_Cheek_R" in chibi_names
