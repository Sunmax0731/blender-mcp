from __future__ import annotations

from blender_precision_mcp.auto_character_library import load_all_character_libraries
from blender_precision_mcp.auto_character_library import load_character_library


def test_load_character_library_reads_humanoid_bundle():
    bundle = load_character_library("humanoid")

    assert bundle.character_type == "humanoid"
    assert bundle.shape_template["template_name"] == "humanoid_base_shape"
    assert bundle.rig_template["template_name"] == "humanoid_standard"
    assert bundle.expression_library["library_name"] == "humanoid_basic_expressions"
    assert bundle.pose_test_library["base_pose"] == "t_pose"
    assert bundle.material_preset["preset_name"] == "humanoid_default_materials"


def test_load_all_character_libraries_reads_all_types():
    bundles = load_all_character_libraries()

    assert set(bundles) == {"humanoid", "chibi", "creature"}
    assert bundles["chibi"].shape_template["shape_guides"]["default_head_count"] == 2.5
    assert "tail" in bundles["creature"].rig_template["required_bones"]
    assert any(
        expression["name"] == "mouth_o"
        for expression in bundles["chibi"].expression_library["expressions"]
    )
