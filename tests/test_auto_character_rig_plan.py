from __future__ import annotations

from blender_precision_mcp.auto_character import normalize_prompt_to_character_spec
from blender_precision_mcp.auto_character_rig_plan import build_live_rig_plan


def test_build_live_rig_plan_for_chibi_character():
    character_spec = normalize_prompt_to_character_spec(
        "Create a chibi hero with pink cape and expressive talking face."
    )

    plan = build_live_rig_plan(character_spec)

    assert plan["character_type"] == "chibi"
    assert plan["armature"]["name"] == "RoundBuddy_Rig"
    assert plan["armature"]["template"] == "chibi_standard"
    assert "head" in plan["armature"]["required_bones"]
    assert "mouth_o" in plan["shape_keys"]["supported"]
    assert plan["weight_plan"]["binding_mode"] == "armature_auto_weights"
    assert "balance_hop" not in plan["weight_plan"]["pose_tests"]


def test_build_live_rig_plan_reports_missing_library_entries():
    character_spec = normalize_prompt_to_character_spec(
        "Create a creature beast with green patterned skin."
    )
    character_spec["expression_spec"]["required_expressions"].append("smile")
    character_spec["pose_test_spec"]["required_pose_tests"].append("wings_flap")

    plan = build_live_rig_plan(character_spec)

    assert "smile" in plan["shape_keys"]["missing_from_library"]
    assert "wings_flap" in plan["weight_plan"]["missing_pose_tests"]
