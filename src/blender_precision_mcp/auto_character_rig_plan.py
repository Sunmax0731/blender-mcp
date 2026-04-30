from __future__ import annotations

from typing import Any

from .auto_character_library import load_character_library


def build_live_rig_plan(character_spec: dict[str, Any]) -> dict[str, Any]:
    character_type = str(character_spec.get("character_type", "humanoid"))
    bundle = load_character_library(character_type)
    rig_spec = character_spec.get("rig_spec", {})
    expression_spec = character_spec.get("expression_spec", {})
    pose_test_spec = character_spec.get("pose_test_spec", {})

    library_expression_names = {
        item["name"]
        for item in bundle.expression_library.get("expressions", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    required_expressions = [
        expression
        for expression in expression_spec.get("required_expressions", [])
        if isinstance(expression, str)
    ]
    required_pose_tests = [
        pose_test
        for pose_test in pose_test_spec.get("required_pose_tests", [])
        if isinstance(pose_test, str)
    ]
    library_pose_tests = {
        item["name"]
        for item in bundle.pose_test_library.get("pose_tests", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }

    return {
        "character_type": character_type,
        "armature": {
            "name": "RoundBuddy_Rig",
            "template": rig_spec.get("template", bundle.rig_template.get("template_name")),
            "required_bones": list(rig_spec.get("required_bones", bundle.rig_template.get("required_bones", []))),
            "bone_groups": bundle.rig_template.get("bone_groups", {}),
        },
        "shape_keys": {
            "target_object": "RoundBuddy_Head",
            "required": required_expressions,
            "supported": sorted(expression for expression in required_expressions if expression in library_expression_names),
            "missing_from_library": sorted(
                expression for expression in required_expressions if expression not in library_expression_names
            ),
        },
        "weight_plan": {
            "binding_mode": "armature_auto_weights",
            "base_pose": pose_test_spec.get("base_pose", bundle.pose_test_library.get("base_pose")),
            "pose_tests": required_pose_tests,
            "supported_pose_tests": sorted(test for test in required_pose_tests if test in library_pose_tests),
            "missing_pose_tests": sorted(test for test in required_pose_tests if test not in library_pose_tests),
        },
    }
