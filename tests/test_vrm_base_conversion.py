from __future__ import annotations

from pathlib import Path

from blender_precision_mcp.vrm_base_conversion import VRM_ADDON_MODULE
from blender_precision_mcp.vrm_base_conversion import build_vrm_import_blender_script
from blender_precision_mcp.vrm_base_conversion import select_vrm_addon_asset


def test_select_vrm_addon_asset_prefers_legacy_zip():
    release = {
        "assets": [
            {"name": "VRM_Addon_for_Blender-Extension-3_26_8.zip", "browser_download_url": "https://example.invalid/ext"},
            {"name": "VRM_Addon_for_Blender-3_26_8.zip", "browser_download_url": "https://example.invalid/legacy"},
        ]
    }

    asset = select_vrm_addon_asset(release)

    assert asset["name"] == "VRM_Addon_for_Blender-3_26_8.zip"


def test_build_vrm_import_blender_script_contains_expected_paths_and_module():
    script = build_vrm_import_blender_script(
        addon_zip_path=Path(r"D:\tmp\vrm-addon.zip"),
        vrm_path=Path(r"D:\tmp\BaseAvatar.vrm"),
        blend_path=Path(r"D:\tmp\BaseAvatar.blend"),
        report_path=Path(r"D:\tmp\vrm_conversion_report.json"),
        object_list_path=Path(r"D:\tmp\object_list.json"),
    )

    assert VRM_ADDON_MODULE in script
    assert r"D:\\tmp\\BaseAvatar.vrm" in script
    assert "bpy.ops.import_scene.vrm" in script
