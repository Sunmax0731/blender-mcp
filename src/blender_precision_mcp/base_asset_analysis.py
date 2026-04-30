from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any


def build_base_asset_manifest(snapshot: dict[str, Any], source_file_path: str) -> dict[str, Any]:
    objects = snapshot.get("objects", [])
    materials = snapshot.get("materials", [])
    images = snapshot.get("images", [])

    main_mesh_object = _select_main_mesh_name(objects)
    face_mesh_object = _select_face_mesh_name(objects)
    hair_objects = _select_hair_objects(objects)
    armatures = [obj["name"] for obj in objects if obj.get("type") == "ARMATURE"]
    mesh_objects = [obj["name"] for obj in objects if obj.get("type") == "MESH"]
    shape_key_objects = [
        obj["name"]
        for obj in objects
        if obj.get("type") == "MESH" and len(obj.get("shape_keys", [])) > 1
    ]

    reusable_uv = any(obj.get("type") == "MESH" and obj.get("has_uv") for obj in objects)
    reusable_shape_keys = bool(shape_key_objects)
    reusable_rig = bool(armatures)
    reusable_face_topology = face_mesh_object is not None and reusable_shape_keys
    relevant_images = [
        image
        for image in images
        if isinstance(image, dict) and image.get("name") not in {"Render Result", "Viewer Node"}
    ]
    texture_paths_resolved = all(
        image.get("packed") or image.get("filepath_exists") for image in relevant_images
    )

    return {
        "status": "ok",
        "source_file_path": source_file_path,
        "imported_object_list": [obj["name"] for obj in objects],
        "imported_armature_list": armatures,
        "imported_material_list": list(materials),
        "mesh_objects": mesh_objects,
        "main_mesh_object": main_mesh_object,
        "face_mesh_object": face_mesh_object,
        "reusable_uv": reusable_uv,
        "reusable_face_topology": reusable_face_topology,
        "reusable_rig": reusable_rig,
        "reusable_shape_keys": reusable_shape_keys,
        "reusable_hair_objects": hair_objects,
        "shape_key_objects": shape_key_objects,
        "texture_paths_resolved": texture_paths_resolved,
        "image_count": len(images),
    }


def build_adaptation_plan(manifest: dict[str, Any]) -> dict[str, Any]:
    reuse_targets = []
    regenerate_targets = []

    if manifest.get("main_mesh_object"):
        reuse_targets.append("mesh")
    else:
        regenerate_targets.append("mesh")

    if manifest.get("reusable_uv"):
        reuse_targets.append("uv")
    else:
        regenerate_targets.append("uv")

    if manifest.get("reusable_face_topology"):
        reuse_targets.append("face_topology")
    else:
        regenerate_targets.append("face_topology")

    if manifest.get("reusable_rig"):
        reuse_targets.append("rig")
    else:
        regenerate_targets.append("rig")

    if manifest.get("reusable_shape_keys"):
        reuse_targets.append("shape_keys")
    else:
        regenerate_targets.append("shape_keys")

    if manifest.get("reusable_hair_objects"):
        reuse_targets.append("hair_objects")
    else:
        regenerate_targets.append("hair_objects")

    if manifest.get("texture_paths_resolved"):
        reuse_targets.append("materials_and_textures")
    else:
        regenerate_targets.append("materials_and_textures")

    return {
        "status": "ok",
        "reuse_targets": reuse_targets,
        "regenerate_targets": regenerate_targets,
        "target_objects": {
            "main_mesh_object": manifest.get("main_mesh_object"),
            "face_mesh_object": manifest.get("face_mesh_object"),
            "hair_objects": manifest.get("reusable_hair_objects", []),
            "armature_objects": manifest.get("imported_armature_list", []),
            "material_names": manifest.get("imported_material_list", []),
        },
        "notes": {
            "shape_key_objects": manifest.get("shape_key_objects", []),
            "texture_paths_resolved": manifest.get("texture_paths_resolved", False),
        },
    }


def build_base_asset_blender_script(
    *,
    blend_path: Path,
    manifest_path: Path,
    adaptation_plan_path: Path,
    object_list_path: Path,
    snapshot_path: Path,
) -> str:
    return textwrap.dedent(
        f"""
        import json
        import sys
        from pathlib import Path

        sys.path.insert(0, {json.dumps(str(Path(__file__).resolve().parents[1]))})

        import bpy
        from blender_precision_mcp.base_asset_analysis import build_adaptation_plan
        from blender_precision_mcp.base_asset_analysis import build_base_asset_manifest

        blend_path = Path({json.dumps(str(blend_path))})
        manifest_path = Path({json.dumps(str(manifest_path))})
        adaptation_plan_path = Path({json.dumps(str(adaptation_plan_path))})
        object_list_path = Path({json.dumps(str(object_list_path))})
        snapshot_path = Path({json.dumps(str(snapshot_path))})

        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        adaptation_plan_path.parent.mkdir(parents=True, exist_ok=True)
        object_list_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)

        bpy.ops.wm.open_mainfile(filepath=str(blend_path))

        objects = []
        for obj in bpy.data.objects:
            material_names = [
                slot.material.name
                for slot in getattr(obj, "material_slots", [])
                if getattr(slot, "material", None) is not None
            ]
            shape_keys = []
            data = getattr(obj, "data", None)
            if getattr(data, "shape_keys", None):
                shape_keys = [key_block.name for key_block in data.shape_keys.key_blocks]
            uv_layer_count = 0
            vertex_count = 0
            polygon_count = 0
            if obj.type == "MESH" and data is not None:
                uv_layer_count = len(getattr(data, "uv_layers", []))
                vertex_count = len(getattr(data, "vertices", []))
                polygon_count = len(getattr(data, "polygons", []))

            objects.append({{
                "name": obj.name,
                "type": obj.type,
                "materials": material_names,
                "shape_keys": shape_keys,
                "has_uv": uv_layer_count > 0,
                "uv_layer_count": uv_layer_count,
                "vertex_count": vertex_count,
                "polygon_count": polygon_count,
            }})

        materials = sorted(material.name for material in bpy.data.materials)
        images = []
        for image in bpy.data.images:
            raw_path = image.filepath_from_user()
            filepath = bpy.path.abspath(raw_path) if raw_path else ""
            images.append({{
                "name": image.name,
                "filepath": filepath,
                "filepath_exists": bool(filepath) and Path(filepath).exists(),
                "packed": image.packed_file is not None,
            }})

        snapshot = {{
            "status": "ok",
            "blend_path": str(blend_path),
            "objects": objects,
            "materials": materials,
            "images": images,
        }}
        manifest = build_base_asset_manifest(snapshot, str(blend_path))
        adaptation_plan = build_adaptation_plan(manifest)

        snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
        object_list_path.write_text(json.dumps(objects, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
        adaptation_plan_path.write_text(json.dumps(adaptation_plan, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")

        print(json.dumps({{
            "snapshot_path": str(snapshot_path),
            "manifest_path": str(manifest_path),
            "adaptation_plan_path": str(adaptation_plan_path),
            "object_list_path": str(object_list_path),
            "main_mesh_object": manifest.get("main_mesh_object"),
            "face_mesh_object": manifest.get("face_mesh_object"),
        }}, ensure_ascii=False, indent=2))
        """
    ).strip() + "\n"


def _select_main_mesh_name(objects: list[dict[str, Any]]) -> str | None:
    mesh_objects = [obj for obj in objects if obj.get("type") == "MESH"]
    if not mesh_objects:
        return None

    preferred = [obj for obj in mesh_objects if "body" in obj.get("name", "").lower()]
    if preferred:
        return preferred[0]["name"]

    fallback = sorted(
        mesh_objects,
        key=lambda obj: (int(obj.get("vertex_count", 0)), int(obj.get("polygon_count", 0))),
        reverse=True,
    )
    return fallback[0]["name"]


def _select_face_mesh_name(objects: list[dict[str, Any]]) -> str | None:
    for obj in objects:
        if obj.get("type") == "MESH" and "face" in obj.get("name", "").lower():
            return obj["name"]
    return None


def _select_hair_objects(objects: list[dict[str, Any]]) -> list[str]:
    hair_objects = []
    for obj in objects:
        if obj.get("type") != "MESH":
            continue
        name = obj.get("name", "").lower()
        materials = [material.lower() for material in obj.get("materials", [])]
        if "hair" in name or any("hair" in material for material in materials):
            hair_objects.append(obj["name"])
    return hair_objects
