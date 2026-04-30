from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_SPEC_PATH = Path("templates/precision/model_spec.yaml")
SUPPORTED_OBJECT_TYPES = ("box", "sphere", "cylinder", "cone", "torus")


def create_parametric_object(
    object_spec: dict[str, Any],
    materials: list[dict[str, Any]] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    if not isinstance(object_spec, dict):
        return _failure("invalid_object_spec", "object_spec must be a mapping.")

    validation_error = _validate_object_spec(object_spec)
    if validation_error is not None:
        return validation_error

    plan = _object_plan(object_spec)
    if dry_run:
        return {"success": True, "data": {"dry_run": True, "operations": [plan]}}

    bpy_module = _try_load_bpy()
    if bpy_module is None:
        return _failure(
            "blender_unavailable",
            "Blender Python module bpy is not available.",
            data={"operations": [plan]},
        )

    material_map = _material_specs_by_name(materials or [])
    try:
        obj = _create_or_update_object(bpy_module, object_spec, material_map)
    except Exception as exc:
        return _failure("object_creation_failed", str(exc), data={"operations": [plan]})

    return {
        "success": True,
        "data": {
            "dry_run": False,
            "objects": [_object_result(obj)],
            "operations": [plan],
        },
    }


def assign_materials_from_spec(
    spec_path: str | Path = DEFAULT_SPEC_PATH,
    dry_run: bool = False,
) -> dict[str, Any]:
    try:
        spec = load_scene_spec(spec_path)
    except Exception as exc:
        return _failure("model_spec_load_failed", str(exc))

    materials = spec.get("materials", [])
    objects = spec.get("objects", [])
    operations = [
        {
            "action": "assign_material",
            "object": obj.get("name"),
            "material": obj.get("material"),
        }
        for obj in objects
        if isinstance(obj, dict) and isinstance(obj.get("material"), str)
    ]
    if dry_run:
        return {"success": True, "data": {"dry_run": True, "operations": operations}}

    bpy_module = _try_load_bpy()
    if bpy_module is None:
        return _failure(
            "blender_unavailable",
            "Blender Python module bpy is not available.",
            data={"operations": operations},
        )

    material_map = _material_specs_by_name(materials)
    assigned: list[dict[str, str]] = []
    missing_objects: list[str] = []
    try:
        for obj_spec in objects:
            if not isinstance(obj_spec, dict) or not isinstance(obj_spec.get("name"), str):
                continue
            obj = bpy_module.data.objects.get(obj_spec["name"])
            if obj is None:
                missing_objects.append(obj_spec["name"])
                continue
            material_name = obj_spec.get("material")
            if isinstance(material_name, str):
                material = _ensure_material(bpy_module, material_name, material_map.get(material_name))
                _assign_material(obj, material)
                assigned.append({"object": obj.name, "material": material.name})
    except Exception as exc:
        return _failure("material_assignment_failed", str(exc), data={"assigned": assigned})

    return {
        "success": not missing_objects,
        "data": {
            "dry_run": False,
            "assigned": assigned,
            "missing_objects": missing_objects,
        },
        **(
            {}
            if not missing_objects
            else {
                "error": {
                    "code": "object_not_found",
                    "message": "Some target objects were not found.",
                }
            }
        ),
    }


def create_or_update_scene_from_spec(
    spec_path: str | Path = DEFAULT_SPEC_PATH,
    dry_run: bool = False,
    output_path: str | Path | None = None,
    ensure_camera: bool = True,
    ensure_lights: bool = True,
) -> dict[str, Any]:
    try:
        spec = load_scene_spec(spec_path)
    except Exception as exc:
        return _failure("model_spec_load_failed", str(exc))

    objects = [obj for obj in spec.get("objects", []) if isinstance(obj, dict)]
    materials = [mat for mat in spec.get("materials", []) if isinstance(mat, dict)]
    operations = [_object_plan(obj) for obj in objects if _validate_object_spec(obj) is None]

    validation = spec.get("validation", {}) if isinstance(spec.get("validation"), dict) else {}
    scene_config = spec.get("scene", {}) if isinstance(spec.get("scene"), dict) else {}
    reset_scene_before_build = bool(scene_config.get("reset_scene_before_build", False))
    should_create_camera = ensure_camera and bool(validation.get("require_camera", True))
    should_create_lights = ensure_lights and bool(validation.get("require_lights", True))
    if reset_scene_before_build:
        operations.append({"action": "reset_scene"})
    if should_create_camera:
        operations.append({"action": "ensure_camera", "name": "Precision_Camera"})
    if should_create_lights:
        operations.append({"action": "ensure_light", "name": "Precision_Key_Light", "type": "AREA"})

    if dry_run:
        payload = _scene_result_payload(
            dry_run=True,
            spec_path=spec_path,
            operations=operations,
            objects=[],
            materials=[],
            camera=None,
            lights=[],
        )
        _write_optional_json(output_path, payload)
        return {"success": True, "data": payload}

    bpy_module = _try_load_bpy()
    if bpy_module is None:
        return _failure(
            "blender_unavailable",
            "Blender Python module bpy is not available.",
            data={"operations": operations},
        )

    material_map = _material_specs_by_name(materials)
    created_objects = []
    try:
        if reset_scene_before_build:
            _reset_scene_objects(bpy_module)
        for material in materials:
            name = material.get("name")
            if isinstance(name, str):
                _ensure_material(bpy_module, name, material)
        for obj_spec in objects:
            validation_error = _validate_object_spec(obj_spec)
            if validation_error is not None:
                return validation_error
            created_objects.append(_create_or_update_object(bpy_module, obj_spec, material_map))
        camera = _ensure_standard_camera(bpy_module) if should_create_camera else None
        lights = [_ensure_standard_light(bpy_module)] if should_create_lights else []
    except Exception as exc:
        return _failure("scene_update_failed", str(exc), data={"operations": operations})

    payload = _scene_result_payload(
        dry_run=False,
        spec_path=spec_path,
        operations=operations,
        objects=[_object_result(obj) for obj in created_objects],
        materials=[mat.name for mat in bpy_module.data.materials],
        camera=camera.name if camera else None,
        lights=[light.name for light in lights],
    )
    _write_optional_json(output_path, payload)
    return {"success": True, "data": payload}


def load_scene_spec(path: str | Path) -> dict[str, Any]:
    spec_path = Path(path)
    if not spec_path.exists():
        raise FileNotFoundError(f"model_spec not found: {spec_path}")
    text = spec_path.read_text(encoding="utf-8")
    if spec_path.suffix.lower() == ".json":
        loaded = json.loads(text)
    else:
        loaded = _load_yaml(text)
    if not isinstance(loaded, dict):
        raise ValueError(f"model_spec must be a mapping: {spec_path}")
    return loaded


def _load_yaml(text: str) -> Any:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyYAML is required to load YAML model_spec files.") from exc
    return yaml.safe_load(text)


def _validate_object_spec(object_spec: dict[str, Any]) -> dict[str, Any] | None:
    name = object_spec.get("name")
    object_type = object_spec.get("type")
    if not isinstance(name, str) or not name.strip():
        return _failure("invalid_object_name", "object_spec.name must be a non-empty string.")
    if object_type not in SUPPORTED_OBJECT_TYPES:
        return _failure(
            "unsupported_object_type",
            f"Unsupported object type: {object_type}",
            data={"supported_types": list(SUPPORTED_OBJECT_TYPES)},
        )
    for field in ("dimensions", "location", "rotation"):
        value = object_spec.get(field)
        if value is not None and not _is_number_list(value, 3):
            return _failure(f"invalid_{field}", f"object_spec.{field} must be a 3-number list.")
    return None


def _object_plan(object_spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "action": "create_or_update_object",
        "name": object_spec.get("name"),
        "type": object_spec.get("type"),
        "collection": object_spec.get("collection"),
        "dimensions": object_spec.get("dimensions"),
        "location": object_spec.get("location"),
        "rotation": object_spec.get("rotation"),
        "material": object_spec.get("material"),
        "bevel_radius": (object_spec.get("requirements") or {}).get("bevel_radius")
        if isinstance(object_spec.get("requirements"), dict)
        else None,
    }


def _create_or_update_object(
    bpy_module: Any,
    object_spec: dict[str, Any],
    material_specs: dict[str, dict[str, Any]],
) -> Any:
    name = str(object_spec["name"])
    obj = bpy_module.data.objects.get(name)
    if obj is None:
        obj = _create_primitive(bpy_module, object_spec)
        obj.name = name
    _move_to_collection(bpy_module, obj, object_spec.get("collection"))
    _apply_transform(bpy_module, obj, object_spec)
    material_name = object_spec.get("material")
    if isinstance(material_name, str):
        material = _ensure_material(bpy_module, material_name, material_specs.get(material_name))
        _assign_material(obj, material)
    requirements = object_spec.get("requirements", {})
    if isinstance(requirements, dict) and requirements.get("bevel_radius") is not None:
        _ensure_bevel_modifier(obj, float(requirements["bevel_radius"]))
    return obj


def _reset_scene_objects(bpy_module: Any) -> None:
    scene = bpy_module.context.scene
    for obj in list(scene.objects):
        bpy_module.data.objects.remove(obj, do_unlink=True)


def _create_primitive(bpy_module: Any, object_spec: dict[str, Any]) -> Any:
    object_type = object_spec["type"]
    location = _vector(object_spec.get("location"), (0.0, 0.0, 0.0))
    if object_type == "box":
        bpy_module.ops.mesh.primitive_cube_add(size=1.0, location=location)
    elif object_type == "sphere":
        bpy_module.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=location)
    elif object_type == "cylinder":
        bpy_module.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.5, depth=1.0, location=location)
    elif object_type == "cone":
        bpy_module.ops.mesh.primitive_cone_add(vertices=32, radius1=0.5, depth=1.0, location=location)
    elif object_type == "torus":
        bpy_module.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.125, location=location)
    else:
        raise ValueError(f"Unsupported object type: {object_type}")
    return bpy_module.context.object


def _apply_transform(bpy_module: Any, obj: Any, object_spec: dict[str, Any]) -> None:
    obj.location = _vector(object_spec.get("location"), (0.0, 0.0, 0.0))
    obj.rotation_euler = _vector(object_spec.get("rotation"), (0.0, 0.0, 0.0))
    if object_spec.get("dimensions") is not None:
        obj.dimensions = _vector(object_spec["dimensions"], (1.0, 1.0, 1.0))
        _update_view_layer(bpy_module)
        requirements = object_spec.get("requirements", {})
        if isinstance(requirements, dict) and requirements.get("apply_scale"):
            bpy_module.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy_module.ops.object.transform_apply(location=False, rotation=False, scale=True)
            _update_view_layer(bpy_module)
    else:
        _update_view_layer(bpy_module)


def _move_to_collection(bpy_module: Any, obj: Any, collection_path: Any) -> None:
    if not isinstance(collection_path, str) or not collection_path.strip():
        return
    collection = _ensure_collection_path(bpy_module, collection_path)
    if collection.objects.get(obj.name) is None:
        collection.objects.link(obj)
    for existing_collection in list(getattr(obj, "users_collection", [])):
        if existing_collection != collection:
            existing_collection.objects.unlink(obj)


def _ensure_collection_path(bpy_module: Any, collection_path: str) -> Any:
    parent = bpy_module.context.scene.collection
    current = parent
    for part in [value for value in collection_path.split("/") if value]:
        child = bpy_module.data.collections.get(part)
        if child is None:
            child = bpy_module.data.collections.new(part)
        if current.children.get(child.name) is None:
            current.children.link(child)
        current = child
    return current


def _update_view_layer(bpy_module: Any) -> None:
    update = getattr(getattr(bpy_module.context, "view_layer", None), "update", None)
    if callable(update):
        update()


def _ensure_material(
    bpy_module: Any,
    material_name: str,
    material_spec: dict[str, Any] | None = None,
) -> Any:
    material = bpy_module.data.materials.get(material_name)
    if material is None:
        material = bpy_module.data.materials.new(material_name)
    color = (material_spec or {}).get("color", [0.8, 0.8, 0.8, 1.0])
    if _is_number_list(color, 4):
        material.diffuse_color = tuple(float(value) for value in color)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF") if material.node_tree else None
    if principled is not None:
        _set_node_input(principled, "Base Color", material.diffuse_color)
        if "roughness" in (material_spec or {}):
            _set_node_input(principled, "Roughness", float(material_spec["roughness"]))
        if "metallic" in (material_spec or {}):
            _set_node_input(principled, "Metallic", float(material_spec["metallic"]))
    return material


def _set_node_input(node: Any, input_name: str, value: Any) -> None:
    if input_name in node.inputs:
        node.inputs[input_name].default_value = value


def _assign_material(obj: Any, material: Any) -> None:
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def _ensure_bevel_modifier(obj: Any, bevel_radius: float) -> None:
    modifier = obj.modifiers.get("precision_bevel") if hasattr(obj.modifiers, "get") else None
    if modifier is None:
        modifier = obj.modifiers.new("precision_bevel", "BEVEL")
    modifier.width = bevel_radius
    modifier.segments = max(1, int(getattr(modifier, "segments", 1)))


def _ensure_standard_camera(bpy_module: Any) -> Any:
    camera = bpy_module.data.objects.get("Precision_Camera")
    if camera is None:
        camera_data = bpy_module.data.cameras.new("Precision_Camera")
        camera = bpy_module.data.objects.new("Precision_Camera", camera_data)
        bpy_module.context.scene.collection.objects.link(camera)
    camera.location = (3.0, -5.0, 2.5)
    camera.rotation_euler = (1.1, 0.0, 0.55)
    bpy_module.context.scene.camera = camera
    return camera


def _ensure_standard_light(bpy_module: Any) -> Any:
    light = bpy_module.data.objects.get("Precision_Key_Light")
    if light is None:
        light_data = bpy_module.data.lights.new("Precision_Key_Light", type="AREA")
        light = bpy_module.data.objects.new("Precision_Key_Light", light_data)
        bpy_module.context.scene.collection.objects.link(light)
    light.location = (2.5, -3.0, 4.0)
    light.data.energy = 500
    light.data.size = 4
    return light


def _material_specs_by_name(materials: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        material["name"]: material
        for material in materials
        if isinstance(material, dict) and isinstance(material.get("name"), str)
    }


def _scene_result_payload(
    dry_run: bool,
    spec_path: str | Path,
    operations: list[dict[str, Any]],
    objects: list[dict[str, Any]],
    materials: list[str],
    camera: str | None,
    lights: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "dry_run": dry_run,
        "spec_path": str(spec_path),
        "operations": operations,
        "objects": objects,
        "materials": materials,
        "camera": camera,
        "lights": lights,
    }


def _object_result(obj: Any) -> dict[str, Any]:
    return {
        "name": obj.name,
        "type": getattr(obj, "type", None),
        "dimensions": _read_vector(getattr(obj, "dimensions", ())),
        "location": _read_vector(getattr(obj, "location", ())),
        "materials": [
            slot.material.name
            for slot in getattr(obj, "material_slots", [])
            if getattr(slot, "material", None) is not None
        ],
    }


def _write_optional_json(output_path: str | Path | None, payload: dict[str, Any]) -> None:
    if output_path is None:
        return
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _try_load_bpy() -> Any | None:
    try:
        import bpy  # type: ignore
    except ModuleNotFoundError:
        return None
    if not hasattr(bpy, "context") or not hasattr(bpy, "ops"):
        return None
    return bpy


def _vector(value: Any, fallback: tuple[float, float, float]) -> tuple[float, float, float]:
    if _is_number_list(value, 3):
        return tuple(float(item) for item in value)
    return fallback


def _read_vector(value: Any) -> list[float]:
    return [float(item) for item in value]


def _is_number_list(value: Any, expected_length: int) -> bool:
    return (
        isinstance(value, list)
        and len(value) == expected_length
        and all(isinstance(item, int | float) for item in value)
    )


def _failure(code: str, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
        "data": data or {},
    }
