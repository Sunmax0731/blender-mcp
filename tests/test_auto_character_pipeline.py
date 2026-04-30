from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from blender_precision_mcp.auto_character import build_pipeline_spec
from blender_precision_mcp.auto_character import normalize_prompt_to_character_spec


ROOT = Path(__file__).resolve().parents[1]
CHARACTER_SPEC_SCHEMA = ROOT / "schemas" / "precision" / "character_spec.schema.json"
PIPELINE_SPEC_SCHEMA = ROOT / "schemas" / "precision" / "pipeline_spec.schema.json"


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def test_normalize_prompt_defaults_to_humanoid_and_matches_schema():
    character_spec = normalize_prompt_to_character_spec(
        "Create a stylized human character with blue jacket and short hair."
    )

    schema = _load_json(CHARACTER_SPEC_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=character_spec, schema=schema)

    assert character_spec["character_type"] == "humanoid"
    assert character_spec["rig_spec"]["template"] == "humanoid_standard"
    assert any(part["name"] == "jacket" for part in character_spec["parts"])
    assert character_spec["look_spec"]["materials"][1]["base_color"] == [0.12, 0.24, 0.68, 1.0]
    assert character_spec["hair_spec"]["preset"] == "short"


def test_normalize_prompt_builds_chibi_variant():
    character_spec = normalize_prompt_to_character_spec(
        "Create a chibi hero with pink cape and expressive talking face."
    )

    assert character_spec["character_type"] == "chibi"
    assert character_spec["body_proportions"]["head_count"] == 2.5
    assert character_spec["rig_spec"]["template"] == "chibi_standard"
    assert "mouth_o" in character_spec["expression_spec"]["required_expressions"]
    assert character_spec["pose_test_spec"]["base_pose"] == "t_pose"
    assert character_spec["hair_spec"]["preset"] == "short"


def test_normalize_prompt_builds_creature_variant():
    character_spec = normalize_prompt_to_character_spec(
        "Create a green creature beast with striped tail for animation."
    )

    assert character_spec["character_type"] == "creature"
    assert character_spec["rig_spec"]["template"] == "creature_quadruped"
    assert any(part["name"] == "tail" for part in character_spec["parts"])
    assert "tail" in character_spec["rig_spec"]["required_bones"]
    assert character_spec["pose_test_spec"]["base_pose"] == "a_pose"
    assert character_spec["hair_spec"]["preset"] == "crest"


def test_build_pipeline_spec_matches_schema_and_adds_type_specific_inputs():
    prompt = "Create a creature beast with green patterned skin and talking face."
    character_spec = normalize_prompt_to_character_spec(prompt)
    pipeline_spec = build_pipeline_spec(
        prompt,
        character_spec,
        run_directory="outputs/auto-character/creature-run",
    )

    schema = _load_json(PIPELINE_SPEC_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=pipeline_spec, schema=schema)

    assert pipeline_spec["normalized_character_spec"]["character_type"] == "creature"
    assert "creature_shape_template" in pipeline_spec["shape_stage"]["inputs"]
    assert "creature_pose_library" in pipeline_spec["weight_stage"]["inputs"]
    assert "creature_balance_final" in pipeline_spec["validation_plan"]["final_validators"]
    assert "review/back.png" in pipeline_spec["artifact_plan"]["required_artifacts"]
    assert "validation/retry_trace.json" in pipeline_spec["artifact_plan"]["required_artifacts"]


def test_build_pipeline_spec_adds_base_asset_branching_when_manifest_is_present():
    prompt = "Create a humanoid hero using an existing base avatar."
    character_spec = normalize_prompt_to_character_spec(prompt)
    pipeline_spec = build_pipeline_spec(
        prompt,
        character_spec,
        run_directory="outputs/base-asset-run",
        character_spec_ref="character_spec.yaml",
        base_asset_inputs={
            "manifest": {"source_file_path": "D:/base/BaseAvatar.blend"},
            "adaptation_plan": {
                "reuse_targets": ["mesh", "rig", "shape_keys", "materials_and_textures"],
                "regenerate_targets": [],
                "target_objects": {
                    "main_mesh_object": "Body",
                    "face_mesh_object": "Face",
                    "armature_objects": ["Armature"],
                    "material_names": ["Skin"],
                },
            },
            "artifact_refs": {
                "base_asset_manifest": "validation/base_asset_manifest.json",
                "adaptation_plan": "validation/adaptation_plan.json",
            },
        },
    )

    assert pipeline_spec["normalized_character_spec"]["base_asset"]["source_file_path"] == "D:/base/BaseAvatar.blend"
    assert pipeline_spec["shape_stage"]["base_asset_mode"] == "reuse_base_mesh"
    assert pipeline_spec["rig_stage"]["base_asset_mode"] == "reuse_base_rig"
    assert pipeline_spec["expression_stage"]["base_asset_mode"] == "reuse_base_shape_keys"
    assert pipeline_spec["look_stage"]["base_asset_mode"] == "reuse_base_materials"
    assert "validation/base_asset_manifest.json" in pipeline_spec["artifact_plan"]["required_artifacts"]


def test_build_pipeline_spec_adds_image_reference_inputs_when_manifest_is_present():
    prompt = "Create a humanoid hero with blue jacket and short hair."
    character_spec = normalize_prompt_to_character_spec(prompt)
    pipeline_spec = build_pipeline_spec(
        prompt,
        character_spec,
        run_directory="outputs/image-reference-run",
        character_spec_ref="character_spec.yaml",
        image_reference_manifest={
            "detected_views": ["front", "side", "face_closeup", "expression_smile"],
            "prompt_image_conflicts": [{"field": "look_spec.materials.accent"}],
            "image_priority_fields": ["body_proportions", "parts.hair"],
        },
    )

    assert pipeline_spec["normalized_character_spec"]["image_reference"]["manifest_ref"] == "validation/image_reference_manifest.json"
    assert pipeline_spec["shape_stage"]["image_reference_mode"] == "guided_shape"
    assert "image_reference_front" in pipeline_spec["shape_stage"]["inputs"]
    assert "image_reference_side" in pipeline_spec["shape_stage"]["inputs"]
    assert pipeline_spec["look_stage"]["image_reference_mode"] == "guided_look"
    assert "image_reference_palette" in pipeline_spec["look_stage"]["inputs"]
    assert pipeline_spec["expression_stage"]["image_reference_mode"] == "guided_expression"
    assert "image_reference_face" in pipeline_spec["expression_stage"]["inputs"]
    assert "image_reference_expression_set" in pipeline_spec["expression_stage"]["inputs"]
    assert "validation/image_reference_manifest.json" in pipeline_spec["artifact_plan"]["required_artifacts"]
