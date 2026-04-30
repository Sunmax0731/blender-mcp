from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
CHARACTER_SPEC_TEMPLATE_PATH = ROOT / "templates" / "precision" / "character_spec.yaml"
PIPELINE_SPEC_TEMPLATE_PATH = ROOT / "templates" / "precision" / "pipeline_spec.yaml"

_CHARACTER_TYPE_HINTS: tuple[tuple[str, str], ...] = (
    ("chibi", "chibi"),
    ("super deformed", "chibi"),
    ("creature", "creature"),
    ("monster", "creature"),
    ("beast", "creature"),
    ("animal", "creature"),
    ("humanoid", "humanoid"),
    ("human", "humanoid"),
)

_COLOR_HINTS: tuple[tuple[str, tuple[float, float, float, float]], ...] = (
    ("red", (0.75, 0.16, 0.14, 1.0)),
    ("blue", (0.12, 0.24, 0.68, 1.0)),
    ("green", (0.17, 0.52, 0.24, 1.0)),
    ("yellow", (0.92, 0.74, 0.18, 1.0)),
    ("black", (0.08, 0.08, 0.1, 1.0)),
    ("white", (0.9, 0.9, 0.9, 1.0)),
    ("pink", (0.92, 0.56, 0.7, 1.0)),
    ("purple", (0.44, 0.28, 0.63, 1.0)),
)


def normalize_prompt_to_character_spec(prompt: str) -> dict[str, Any]:
    normalized_prompt = " ".join(prompt.split())
    prompt_lower = normalized_prompt.lower()
    spec = _load_yaml_template(CHARACTER_SPEC_TEMPLATE_PATH)

    spec["character_type"] = _detect_character_type(prompt_lower)
    spec["body_proportions"] = _body_proportions_for_type(spec["character_type"])
    spec["parts"] = _parts_for_type(spec["character_type"], prompt_lower)
    spec["look_spec"] = _look_spec_for_prompt(prompt_lower)
    spec["rig_spec"] = _rig_spec_for_type(spec["character_type"])
    spec["expression_spec"] = _expression_spec_for_prompt(prompt_lower)
    spec["pose_test_spec"] = _pose_test_spec_for_type(spec["character_type"])
    spec["hair_spec"] = _hair_spec_for_prompt(prompt_lower, spec["character_type"])
    spec["source_prompt"] = normalized_prompt
    return spec


def build_pipeline_spec(
    prompt: str,
    character_spec: dict[str, Any],
    *,
    run_directory: str = "outputs/auto-character/generated-run",
    character_spec_ref: str = "character_spec.generated.yaml",
    base_asset_inputs: dict[str, Any] | None = None,
    image_reference_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_prompt = " ".join(prompt.split())
    pipeline = _load_yaml_template(PIPELINE_SPEC_TEMPLATE_PATH)

    pipeline["source_prompt"] = normalized_prompt
    pipeline["normalized_character_spec"] = {
        "ref": character_spec_ref,
        "character_type": character_spec["character_type"],
        "required_parts": [part["name"] for part in character_spec["parts"]],
        "required_expressions": character_spec["expression_spec"]["required_expressions"],
        "rig_template": character_spec["rig_spec"]["template"],
        "hair_preset": character_spec.get("hair_spec", {}).get("preset", "none"),
    }
    if base_asset_inputs:
        pipeline["normalized_character_spec"]["base_asset"] = {
            "source_file_path": base_asset_inputs["manifest"].get("source_file_path"),
            "reuse_targets": base_asset_inputs["adaptation_plan"].get("reuse_targets", []),
            "regenerate_targets": base_asset_inputs["adaptation_plan"].get("regenerate_targets", []),
        }
    if image_reference_manifest:
        pipeline["normalized_character_spec"]["image_reference"] = {
            "manifest_ref": "validation/image_reference_manifest.json",
            "detected_views": image_reference_manifest.get("detected_views", []),
            "conflict_count": len(image_reference_manifest.get("prompt_image_conflicts", [])),
        }

    for stage_name in ("shape_stage", "look_stage", "rig_stage", "expression_stage", "weight_stage"):
        pipeline[stage_name] = _stage_for_type(
            stage_name,
            pipeline[stage_name],
            character_spec["character_type"],
        )
        if base_asset_inputs:
            pipeline[stage_name] = _apply_base_asset_stage_plan(
                stage_name,
                pipeline[stage_name],
                base_asset_inputs["adaptation_plan"],
                base_asset_inputs["artifact_refs"],
            )
        if image_reference_manifest:
            pipeline[stage_name] = _apply_image_reference_stage_plan(
                stage_name,
                pipeline[stage_name],
                image_reference_manifest,
            )

    pipeline["artifact_plan"]["run_directory"] = run_directory
    pipeline["artifact_plan"]["required_artifacts"] = _required_artifacts_for_type(
        character_spec["character_type"]
    )
    if "validation/retry_trace.json" not in pipeline["artifact_plan"]["required_artifacts"]:
        pipeline["artifact_plan"]["required_artifacts"].append("validation/retry_trace.json")
    if base_asset_inputs:
        pipeline["artifact_plan"]["required_artifacts"].extend(
            [
                "validation/base_asset_manifest.json",
                "validation/adaptation_plan.json",
            ]
        )
    if image_reference_manifest:
        pipeline["artifact_plan"]["required_artifacts"].append(
            "validation/image_reference_manifest.json"
        )
    pipeline["validation_plan"]["final_validators"] = _final_validators_for_type(
        character_spec["character_type"]
    )
    pipeline["fallback_plan"]["alternate_routes"] = [
        "official_mcp_scene_snapshot",
        "template_rebuild_retry",
    ]
    return pipeline


def _load_yaml_template(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"template must be a mapping: {path}")
    return deepcopy(loaded)


def _detect_character_type(prompt_lower: str) -> str:
    for hint, character_type in _CHARACTER_TYPE_HINTS:
        if hint in prompt_lower:
            return character_type
    return "humanoid"


def _body_proportions_for_type(character_type: str) -> dict[str, Any]:
    if character_type == "chibi":
        return {
            "head_count": 2.5,
            "shoulder_width": 1.4,
            "torso_length": 1.1,
            "arm_length": 1.3,
            "leg_length": 1.5,
            "hand_size": "small",
            "foot_size": "small",
        }
    if character_type == "creature":
        return {
            "head_count": 4.0,
            "shoulder_width": 2.2,
            "torso_length": 2.4,
            "arm_length": 2.0,
            "leg_length": 2.6,
            "hand_size": "large",
            "foot_size": "large",
        }
    return {
        "head_count": 6.5,
        "shoulder_width": 1.8,
        "torso_length": 2.2,
        "arm_length": 2.6,
        "leg_length": 3.4,
        "hand_size": "medium",
        "foot_size": "medium",
    }


def _parts_for_type(character_type: str, prompt_lower: str) -> list[dict[str, str]]:
    parts: list[dict[str, str]] = [
        {"name": "head", "category": "anatomy", "notes": "prompt-normalized primary silhouette"},
        {"name": "torso", "category": "anatomy", "notes": "prompt-normalized core volume"},
    ]
    if "hair" in prompt_lower or character_type != "creature":
        parts.append({"name": "hair", "category": "style", "notes": "derived from prompt keywords"})
    if "jacket" in prompt_lower:
        parts.append({"name": "jacket", "category": "costume", "notes": "cropped jacket silhouette"})
    if "cape" in prompt_lower:
        parts.append({"name": "cape", "category": "costume", "notes": "secondary cloth silhouette"})
    if character_type == "chibi":
        parts.append({"name": "face", "category": "expression", "notes": "large face area for expressions"})
    if character_type == "creature":
        parts.extend(
            [
                {"name": "tail", "category": "anatomy", "notes": "balance appendage for creature pose tests"},
                {"name": "horns", "category": "style", "notes": "optional creature accent"},
            ]
        )
    return parts


def _look_spec_for_prompt(prompt_lower: str) -> dict[str, Any]:
    accent_color = [0.12, 0.18, 0.32, 1.0]
    for color_name, rgba in _COLOR_HINTS:
        if color_name in prompt_lower:
            accent_color = list(rgba)
            break

    texture_mode = "image"
    if "striped" in prompt_lower or "stripe" in prompt_lower:
        texture_notes = "striped pattern from prompt"
    elif "spotted" in prompt_lower or "dot" in prompt_lower:
        texture_notes = "spotted pattern from prompt"
    else:
        texture_notes = "single accent texture derived from prompt"

    return {
        "materials": [
            {
                "part": "skin",
                "base_color": [0.92, 0.78, 0.70, 1.0],
                "roughness": 0.55,
            },
            {
                "part": "accent",
                "base_color": accent_color,
                "roughness": 0.7,
            },
        ],
        "textures": [
            {
                "part": "accent",
                "mode": texture_mode,
                "symmetry": "mirrored",
                "notes": texture_notes,
            }
        ],
    }


def _rig_spec_for_type(character_type: str) -> dict[str, Any]:
    if character_type == "chibi":
        template = "chibi_standard"
    elif character_type == "creature":
        template = "creature_quadruped"
    else:
        template = "humanoid_standard"

    required_bones = ["root", "hips", "spine", "chest", "neck", "head"]
    if character_type == "creature":
        required_bones.extend(["foreleg_l", "foreleg_r", "hindleg_l", "hindleg_r", "tail"])
    else:
        required_bones.extend(["arm_l", "arm_r", "leg_l", "leg_r"])

    return {
        "template": template,
        "required_bones": required_bones,
    }


def _expression_spec_for_prompt(prompt_lower: str) -> dict[str, Any]:
    expressions = ["smile", "angry", "surprised", "blink"]
    if "talk" in prompt_lower or "speaking" in prompt_lower or "voice" in prompt_lower:
        expressions.extend(["mouth_a", "mouth_i", "mouth_u", "mouth_e", "mouth_o"])
    else:
        expressions.append("mouth_a")
    return {"required_expressions": expressions}


def _pose_test_spec_for_type(character_type: str) -> dict[str, Any]:
    if character_type == "creature":
        return {
            "base_pose": "a_pose",
            "required_pose_tests": [
                "foreleg_bend",
                "hindleg_bend",
                "neck_turn",
                "tail_swing",
            ],
        }
    return {
        "base_pose": "t_pose",
        "required_pose_tests": [
            "arms_raise",
            "elbows_bend",
            "knees_bend",
            "neck_turn",
        ],
    }


def _hair_spec_for_prompt(prompt_lower: str, character_type: str) -> dict[str, Any]:
    preset = "none"
    if "twin tail" in prompt_lower or "twintail" in prompt_lower:
        preset = "twin_tail"
    elif "bob" in prompt_lower:
        preset = "bob"
    elif "long" in prompt_lower:
        preset = "long"
    elif "hair" in prompt_lower or character_type in {"humanoid", "chibi"}:
        preset = "short"
    elif character_type == "creature":
        preset = "crest"

    return {
        "preset": preset,
        "generation_mode": "mesh_preset",
        "allow_approved_addon_extension": True,
    }


def _stage_for_type(stage_name: str, stage: dict[str, Any], character_type: str) -> dict[str, Any]:
    stage_copy = deepcopy(stage)
    if stage_name == "shape_stage":
        stage_copy["inputs"] = stage_copy["inputs"] + [f"{character_type}_shape_template"]
    elif stage_name == "look_stage":
        stage_copy["inputs"] = stage_copy["inputs"] + [f"{character_type}_material_library"]
    elif stage_name == "rig_stage":
        stage_copy["inputs"] = stage_copy["inputs"] + [f"{character_type}_rig_template"]
    elif stage_name == "expression_stage":
        stage_copy["inputs"] = stage_copy["inputs"] + [f"{character_type}_expression_library"]
    elif stage_name == "weight_stage":
        stage_copy["inputs"] = stage_copy["inputs"] + [f"{character_type}_pose_library"]
    return stage_copy


def _required_artifacts_for_type(character_type: str) -> list[str]:
    artifacts = [
        "prompt.txt",
        "character_spec.yaml",
        "pipeline_spec.yaml",
        "validation/final_validation_report.json",
        "validation/object_list.json",
        "review/front.png",
        "review/side.png",
        "exports/final.blend",
    ]
    if character_type == "creature":
        artifacts.append("review/back.png")
    return artifacts


def _final_validators_for_type(character_type: str) -> list[str]:
    validators = [
        "shape_final",
        "look_final",
        "rig_final",
        "expression_final",
        "weight_final",
    ]
    if character_type == "creature":
        validators.append("creature_balance_final")
    return validators


def _apply_base_asset_stage_plan(
    stage_name: str,
    stage: dict[str, Any],
    adaptation_plan: dict[str, Any],
    artifact_refs: dict[str, str],
) -> dict[str, Any]:
    stage_copy = deepcopy(stage)
    reuse_targets = set(adaptation_plan.get("reuse_targets", []))
    target_objects = adaptation_plan.get("target_objects", {})

    stage_copy["base_asset_mode"] = "generate_new"
    stage_copy["base_asset_refs"] = {
        "base_asset_manifest": artifact_refs["base_asset_manifest"],
        "adaptation_plan": artifact_refs["adaptation_plan"],
    }

    if stage_name == "shape_stage" and "mesh" in reuse_targets:
        stage_copy["base_asset_mode"] = "reuse_base_mesh"
        stage_copy["inputs"] = stage_copy["inputs"] + ["base_asset_mesh"]
        stage_copy["outputs"] = ["mesh_objects", "shape_snapshot", "base_asset_mesh_reuse_report"]
        stage_copy["base_asset_targets"] = {
            "main_mesh_object": target_objects.get("main_mesh_object"),
        }
    elif stage_name == "look_stage" and "materials_and_textures" in reuse_targets:
        stage_copy["base_asset_mode"] = "reuse_base_materials"
        stage_copy["inputs"] = stage_copy["inputs"] + ["base_asset_materials"]
        stage_copy["outputs"] = ["materials", "textures", "review_images", "base_asset_material_reuse_report"]
        stage_copy["base_asset_targets"] = {
            "material_names": target_objects.get("material_names", []),
        }
    elif stage_name == "rig_stage" and "rig" in reuse_targets:
        stage_copy["base_asset_mode"] = "reuse_base_rig"
        stage_copy["inputs"] = stage_copy["inputs"] + ["base_asset_armature"]
        stage_copy["outputs"] = ["armature", "bone_map", "base_asset_rig_reuse_report"]
        stage_copy["base_asset_targets"] = {
            "armature_objects": target_objects.get("armature_objects", []),
        }
    elif stage_name == "expression_stage" and "shape_keys" in reuse_targets:
        stage_copy["base_asset_mode"] = "reuse_base_shape_keys"
        stage_copy["inputs"] = stage_copy["inputs"] + ["base_asset_shape_keys"]
        stage_copy["outputs"] = ["shape_keys", "expression_preview", "base_asset_expression_reuse_report"]
        stage_copy["base_asset_targets"] = {
            "face_mesh_object": target_objects.get("face_mesh_object"),
        }
    elif stage_name == "weight_stage" and "rig" in reuse_targets and "mesh" in reuse_targets:
        stage_copy["base_asset_mode"] = "reuse_base_weights"
        stage_copy["inputs"] = stage_copy["inputs"] + ["base_asset_skinning"]
        stage_copy["outputs"] = ["weight_data", "pose_test_report", "base_asset_weight_reuse_report"]
        stage_copy["base_asset_targets"] = {
            "main_mesh_object": target_objects.get("main_mesh_object"),
            "armature_objects": target_objects.get("armature_objects", []),
        }

    return stage_copy


def _apply_image_reference_stage_plan(
    stage_name: str,
    stage: dict[str, Any],
    image_reference_manifest: dict[str, Any],
) -> dict[str, Any]:
    stage_copy = deepcopy(stage)
    detected_views = set(image_reference_manifest.get("detected_views", []))
    stage_copy["image_reference_mode"] = "unguided"
    stage_copy["image_reference_refs"] = {
        "image_reference_manifest": "validation/image_reference_manifest.json",
    }

    if stage_name == "shape_stage":
        stage_copy["image_reference_mode"] = "guided_shape"
        if "front" in detected_views:
            stage_copy["inputs"] = stage_copy["inputs"] + ["image_reference_front"]
        if "side" in detected_views:
            stage_copy["inputs"] = stage_copy["inputs"] + ["image_reference_side"]
    elif stage_name == "look_stage":
        stage_copy["image_reference_mode"] = "guided_look"
        stage_copy["inputs"] = stage_copy["inputs"] + ["image_reference_palette"]
    elif stage_name == "expression_stage":
        stage_copy["image_reference_mode"] = "guided_expression"
        if "face_closeup" in detected_views:
            stage_copy["inputs"] = stage_copy["inputs"] + ["image_reference_face"]
        if any(view.startswith("expression_") for view in detected_views):
            stage_copy["inputs"] = stage_copy["inputs"] + ["image_reference_expression_set"]

    stage_copy["image_priority_fields"] = image_reference_manifest.get("image_priority_fields", [])
    stage_copy["prompt_image_conflicts"] = image_reference_manifest.get("prompt_image_conflicts", [])
    return stage_copy
