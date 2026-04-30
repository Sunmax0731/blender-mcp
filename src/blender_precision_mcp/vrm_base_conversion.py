from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any


VRM_ADDON_REPO = "saturday06/VRM-Addon-for-Blender"
VRM_ADDON_MODULE = "VRM_Addon_for_Blender-release"


def select_vrm_addon_asset(release: dict[str, Any]) -> dict[str, Any]:
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise ValueError("release assets are missing")

    for asset in assets:
        if not isinstance(asset, dict):
            continue
        name = str(asset.get("name", ""))
        if name.endswith(".zip") and "Extension" not in name and name.startswith(
            "VRM_Addon_for_Blender-"
        ):
            return asset

    raise ValueError("VRM add-on zip asset was not found in the release payload")


def build_vrm_import_blender_script(
    *,
    addon_zip_path: Path,
    vrm_path: Path,
    blend_path: Path,
    report_path: Path,
    object_list_path: Path,
) -> str:
    return textwrap.dedent(
        f"""
        import json
        from pathlib import Path

        import addon_utils
        import bpy

        addon_zip_path = Path({json.dumps(str(addon_zip_path))})
        vrm_path = Path({json.dumps(str(vrm_path))})
        blend_path = Path({json.dumps(str(blend_path))})
        report_path = Path({json.dumps(str(report_path))})
        object_list_path = Path({json.dumps(str(object_list_path))})
        addon_module = {json.dumps(VRM_ADDON_MODULE)}

        report_path.parent.mkdir(parents=True, exist_ok=True)
        object_list_path.parent.mkdir(parents=True, exist_ok=True)
        blend_path.parent.mkdir(parents=True, exist_ok=True)

        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

        installed, enabled = addon_utils.check(addon_module)
        if not installed:
            bpy.ops.preferences.addon_install(
                filepath=str(addon_zip_path),
                overwrite=True,
                enable_on_install=True,
            )
        else:
            bpy.ops.preferences.addon_enable(module=addon_module)

        installed, enabled = addon_utils.check(addon_module)
        if not enabled:
            bpy.ops.preferences.addon_enable(module=addon_module)
        installed, enabled = addon_utils.check(addon_module)

        result = bpy.ops.import_scene.vrm(
            filepath=str(vrm_path),
            extract_textures_into_folder=False,
            make_new_texture_folder=False,
        )
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

        objects = []
        armatures = []
        materials = []
        images = []

        for obj in bpy.data.objects:
            materials_for_object = [
                slot.material.name
                for slot in getattr(obj, "material_slots", [])
                if getattr(slot, "material", None) is not None
            ]
            shape_key_names = []
            if getattr(obj.data, "shape_keys", None):
                shape_key_names = [key_block.name for key_block in obj.data.shape_keys.key_blocks]

            object_info = {{
                "name": obj.name,
                "type": obj.type,
                "materials": materials_for_object,
                "shape_keys": shape_key_names,
            }}
            objects.append(object_info)
            if obj.type == "ARMATURE":
                armatures.append(obj.name)

        for material in bpy.data.materials:
            materials.append(material.name)

        for image in bpy.data.images:
            images.append(image.name)

        report = {{
            "status": "ok",
            "addon_module": addon_module,
            "addon_installed": bool(installed),
            "addon_enabled": bool(enabled),
            "import_result": list(result),
            "source_vrm": str(vrm_path),
            "blend_path": str(blend_path),
            "object_count": len(objects),
            "objects": objects,
            "armatures": armatures,
            "materials": materials,
            "images": images,
        }}

        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
        object_list_path.write_text(json.dumps(objects, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        """
    ).strip() + "\n"
