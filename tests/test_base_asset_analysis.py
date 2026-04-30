from __future__ import annotations

from pathlib import Path

from blender_precision_mcp.base_asset_analysis import build_adaptation_plan
from blender_precision_mcp.base_asset_analysis import build_base_asset_blender_script
from blender_precision_mcp.base_asset_analysis import build_base_asset_manifest


def test_build_base_asset_manifest_detects_reusable_assets():
    snapshot = {
        "objects": [
            {
                "name": "Armature",
                "type": "ARMATURE",
                "materials": [],
                "shape_keys": [],
                "has_uv": False,
                "vertex_count": 0,
                "polygon_count": 0,
            },
            {
                "name": "Body",
                "type": "MESH",
                "materials": ["Skin", "Hair_Main"],
                "shape_keys": [],
                "has_uv": True,
                "vertex_count": 100,
                "polygon_count": 50,
            },
            {
                "name": "Face",
                "type": "MESH",
                "materials": ["Face"],
                "shape_keys": ["Basis", "Smile"],
                "has_uv": True,
                "vertex_count": 40,
                "polygon_count": 20,
            },
        ],
        "materials": ["Skin", "Hair_Main", "Face"],
        "images": [
            {"name": "tex", "packed": True, "filepath_exists": False},
            {"name": "Render Result", "packed": False, "filepath_exists": False},
        ],
    }

    manifest = build_base_asset_manifest(snapshot, "D:/tmp/BaseAvatar.blend")

    assert manifest["main_mesh_object"] == "Body"
    assert manifest["face_mesh_object"] == "Face"
    assert manifest["reusable_uv"] is True
    assert manifest["reusable_face_topology"] is True
    assert manifest["reusable_rig"] is True
    assert manifest["reusable_shape_keys"] is True
    assert manifest["reusable_hair_objects"] == ["Body"]
    assert manifest["texture_paths_resolved"] is True


def test_build_adaptation_plan_uses_manifest_flags():
    manifest = {
        "main_mesh_object": "Body",
        "face_mesh_object": "Face",
        "reusable_uv": True,
        "reusable_face_topology": True,
        "reusable_rig": True,
        "reusable_shape_keys": False,
        "reusable_hair_objects": [],
        "texture_paths_resolved": False,
        "imported_armature_list": ["Armature"],
        "imported_material_list": ["Skin"],
        "shape_key_objects": [],
    }

    adaptation_plan = build_adaptation_plan(manifest)

    assert "mesh" in adaptation_plan["reuse_targets"]
    assert "shape_keys" in adaptation_plan["regenerate_targets"]
    assert "hair_objects" in adaptation_plan["regenerate_targets"]
    assert adaptation_plan["target_objects"]["main_mesh_object"] == "Body"


def test_build_base_asset_blender_script_references_expected_artifacts():
    script = build_base_asset_blender_script(
        blend_path=Path(r"D:\tmp\BaseAvatar.blend"),
        manifest_path=Path(r"D:\tmp\base_asset_manifest.json"),
        adaptation_plan_path=Path(r"D:\tmp\adaptation_plan.json"),
        object_list_path=Path(r"D:\tmp\object_list.json"),
        snapshot_path=Path(r"D:\tmp\base_asset_snapshot.json"),
    )

    assert r"D:\\tmp\\BaseAvatar.blend" in script
    assert "build_base_asset_manifest" in script
    assert "adaptation_plan_path" in script
