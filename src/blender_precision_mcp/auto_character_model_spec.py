from __future__ import annotations

from pathlib import Path
from typing import Any


def build_model_spec_from_character_spec(
    character_spec: dict[str, Any],
    *,
    output_dir: str = "outputs/auto-character/live-run",
) -> dict[str, Any]:
    character_type = str(character_spec.get("character_type", "humanoid"))
    body = character_spec.get("body_proportions", {})
    head_radius = _head_radius(body)
    body_radius = round(head_radius * 0.82, 3)
    eye_radius = round(head_radius * 0.12, 3)

    materials = [
        {
            "name": "mat_skin",
            "type": "principled",
            "color": _color_from_materials(character_spec, "skin", [0.92, 0.78, 0.70, 1.0]),
            "roughness": 0.55,
            "metallic": 0.0,
        },
        {
            "name": "mat_accent",
            "type": "principled",
            "color": _color_from_materials(character_spec, "accent", [0.12, 0.18, 0.32, 1.0]),
            "roughness": 0.7,
            "metallic": 0.0,
        },
        {
            "name": "mat_eye",
            "type": "principled",
            "color": [0.08, 0.08, 0.08, 1.0],
            "roughness": 0.25,
            "metallic": 0.0,
        },
    ]

    objects = _base_round_character_objects(
        character_type=character_type,
        head_radius=head_radius,
        body_radius=body_radius,
        eye_radius=eye_radius,
    )
    if character_type == "creature":
        objects.extend(_creature_extra_objects(body_radius))
    if character_type == "chibi":
        objects.extend(_chibi_extra_objects(body_radius))

    exports_dir = Path(output_dir) / "exports"
    return {
        "schema_version": "0.2",
        "scene": {
            "unit": "meters",
            "blender_unit_scale": 1.0,
            "up_axis": "Z",
            "origin_policy": "main_object_centered",
            "main_collection": "auto_character",
            "output_dir": output_dir,
            "reset_scene_before_build": True,
        },
        "objects": objects,
        "materials": materials,
        "mesh_quality": {
            "defaults": {
                "max_non_manifold_edges": 0,
                "max_loose_vertices": 0,
                "require_normals_outward": True,
                "min_quad_ratio": 0.0,
            },
            "objects": [{"name": obj["name"], "min_quad_ratio": 0.0} for obj in objects],
        },
        "visual_qa": {
            "required": True,
            "views": ["front", "side", "top", "perspective"],
            "resolution": [1280, 1280],
            "wireframe_for_retopology": False,
        },
        "validation": {
            "max_dimension_error_m": 0.03,
            "max_location_error_m": 0.03,
            "require_named_objects": True,
            "require_named_materials": True,
            "require_camera": True,
            "require_lights": True,
            "require_review_images": True,
            "forbid_extra_objects": True,
        },
        "exports": [
            {
                "format": "blend",
                "path": str((exports_dir / "final.blend")).replace("\\", "/"),
            }
        ],
    }


def _base_round_character_objects(
    *,
    character_type: str,
    head_radius: float,
    body_radius: float,
    eye_radius: float,
) -> list[dict[str, Any]]:
    body_height = round(body_radius * 2.0, 3)
    head_z = round(body_height + head_radius * 1.08, 3)
    arm_length = round(body_radius * (0.95 if character_type == "chibi" else 1.15), 3)
    leg_length = round(body_radius * (0.72 if character_type == "chibi" else 0.95), 3)
    foot_radius = round(body_radius * 0.28, 3)
    return [
        _sphere("RoundBuddy_Body", body_radius, [0.0, 0.0, body_radius], "mat_accent", "auto_character/body"),
        _sphere("RoundBuddy_Head", head_radius, [0.0, 0.0, head_z], "mat_skin", "auto_character/body"),
        _cylinder(
            "RoundBuddy_Arm_L",
            [body_radius * 0.16, arm_length, body_radius * 0.16],
            [-body_radius * 1.05, 0.0, body_radius * 1.1],
            [0.0, 0.0, 1.05],
            "mat_skin",
            "auto_character/limbs",
        ),
        _cylinder(
            "RoundBuddy_Arm_R",
            [body_radius * 0.16, arm_length, body_radius * 0.16],
            [body_radius * 1.05, 0.0, body_radius * 1.1],
            [0.0, 0.0, -1.05],
            "mat_skin",
            "auto_character/limbs",
        ),
        _cylinder(
            "RoundBuddy_Leg_L",
            [body_radius * 0.18, leg_length, body_radius * 0.18],
            [-body_radius * 0.42, 0.0, leg_length * 0.5],
            [0.0, 0.0, 0.0],
            "mat_skin",
            "auto_character/limbs",
        ),
        _cylinder(
            "RoundBuddy_Leg_R",
            [body_radius * 0.18, leg_length, body_radius * 0.18],
            [body_radius * 0.42, 0.0, leg_length * 0.5],
            [0.0, 0.0, 0.0],
            "mat_skin",
            "auto_character/limbs",
        ),
        _sphere(
            "RoundBuddy_Foot_L",
            foot_radius,
            [-body_radius * 0.42, body_radius * 0.22, foot_radius],
            "mat_accent",
            "auto_character/limbs",
        ),
        _sphere(
            "RoundBuddy_Foot_R",
            foot_radius,
            [body_radius * 0.42, body_radius * 0.22, foot_radius],
            "mat_accent",
            "auto_character/limbs",
        ),
        _sphere(
            "RoundBuddy_Eye_L",
            eye_radius,
            [-head_radius * 0.32, -head_radius * 0.78, head_z + head_radius * 0.08],
            "mat_eye",
            "auto_character/face",
        ),
        _sphere(
            "RoundBuddy_Eye_R",
            eye_radius,
            [head_radius * 0.32, -head_radius * 0.78, head_z + head_radius * 0.08],
            "mat_eye",
            "auto_character/face",
        ),
        _torus(
            "RoundBuddy_Mouth",
            [eye_radius * 2.2, eye_radius * 0.55, eye_radius * 0.55],
            [0.0, -head_radius * 0.74, head_z - head_radius * 0.24],
            [1.5708, 0.0, 0.0],
            "mat_eye",
            "auto_character/face",
        ),
    ]


def _creature_extra_objects(body_radius: float) -> list[dict[str, Any]]:
    return [
        _cylinder(
            "RoundBuddy_Tail",
            [body_radius * 0.14, body_radius * 1.1, body_radius * 0.14],
            [0.0, body_radius * 0.9, body_radius * 0.9],
            [0.7, 0.0, 0.0],
            "mat_accent",
            "auto_character/extras",
        ),
        _cone(
            "RoundBuddy_Horn_L",
            [body_radius * 0.18, body_radius * 0.18, body_radius * 0.4],
            [-body_radius * 0.32, 0.0, body_radius * 2.42],
            [0.0, 0.0, 0.0],
            "mat_accent",
            "auto_character/extras",
        ),
        _cone(
            "RoundBuddy_Horn_R",
            [body_radius * 0.18, body_radius * 0.18, body_radius * 0.4],
            [body_radius * 0.32, 0.0, body_radius * 2.42],
            [0.0, 0.0, 0.0],
            "mat_accent",
            "auto_character/extras",
        ),
    ]


def _chibi_extra_objects(body_radius: float) -> list[dict[str, Any]]:
    cheek_radius = round(body_radius * 0.11, 3)
    head_z = round(body_radius * 2.0 + _head_radius({"head_count": 2.5}) * 1.08, 3)
    return [
        _sphere(
            "RoundBuddy_Cheek_L",
            cheek_radius,
            [-body_radius * 0.26, -body_radius * 0.88, head_z - body_radius * 0.12],
            "mat_accent",
            "auto_character/face",
        ),
        _sphere(
            "RoundBuddy_Cheek_R",
            cheek_radius,
            [body_radius * 0.26, -body_radius * 0.88, head_z - body_radius * 0.12],
            "mat_accent",
            "auto_character/face",
        ),
    ]


def _head_radius(body: dict[str, Any]) -> float:
    head_count = float(body.get("head_count", 6.5))
    if head_count <= 3.0:
        return 0.42
    if head_count <= 4.5:
        return 0.38
    return 0.34


def _color_from_materials(
    character_spec: dict[str, Any],
    part: str,
    fallback: list[float],
) -> list[float]:
    look_spec = character_spec.get("look_spec", {})
    for material in look_spec.get("materials", []):
        if isinstance(material, dict) and material.get("part") == part:
            color = material.get("base_color")
            if isinstance(color, list) and len(color) == 4:
                return [float(value) for value in color]
    return fallback


def _sphere(name: str, radius: float, location: list[float], material: str, collection: str) -> dict[str, Any]:
    diameter = round(radius * 2.0, 3)
    return {
        "name": name,
        "type": "sphere",
        "collection": collection,
        "dimensions": [diameter, diameter, diameter],
        "location": [round(float(value), 3) for value in location],
        "rotation": [0.0, 0.0, 0.0],
        "material": material,
        "requirements": {"apply_scale": True, "must_touch_ground": False},
    }


def _cylinder(
    name: str,
    dimensions: list[float],
    location: list[float],
    rotation: list[float],
    material: str,
    collection: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "type": "cylinder",
        "collection": collection,
        "dimensions": [round(float(value), 3) for value in dimensions],
        "location": [round(float(value), 3) for value in location],
        "rotation": [round(float(value), 4) for value in rotation],
        "material": material,
        "requirements": {"apply_scale": True, "must_touch_ground": False},
    }


def _torus(
    name: str,
    dimensions: list[float],
    location: list[float],
    rotation: list[float],
    material: str,
    collection: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "type": "torus",
        "collection": collection,
        "dimensions": [round(float(value), 3) for value in dimensions],
        "location": [round(float(value), 3) for value in location],
        "rotation": [round(float(value), 4) for value in rotation],
        "material": material,
        "requirements": {"apply_scale": True, "must_touch_ground": False},
    }


def _cone(
    name: str,
    dimensions: list[float],
    location: list[float],
    rotation: list[float],
    material: str,
    collection: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "type": "cone",
        "collection": collection,
        "dimensions": [round(float(value), 3) for value in dimensions],
        "location": [round(float(value), 3) for value in location],
        "rotation": [round(float(value), 4) for value in rotation],
        "material": material,
        "requirements": {"apply_scale": True, "must_touch_ground": False},
    }
