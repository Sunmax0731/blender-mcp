from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def run_live_rig_bridge(rig_plan: dict[str, Any], output_dir: str | Path) -> dict[str, Any]:
    import bpy  # type: ignore

    resolved_output_dir = Path(output_dir)
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    armature_object = _build_armature(bpy, rig_plan)
    bound_meshes = _bind_meshes_to_armature(bpy, armature_object)
    shape_key_result = _build_shape_keys(bpy, rig_plan)
    weight_result = _run_pose_tests(bpy, rig_plan, armature_object, bound_meshes)

    rig_report = {
        "status": "ok",
        "armature_name": armature_object.name,
        "bone_count": len(armature_object.data.bones),
        "bones": [bone.name for bone in armature_object.data.bones],
        "bound_meshes": bound_meshes,
    }
    shape_key_report = {
        "status": "ok",
        "target_object": shape_key_result["target_object"],
        "created_shape_keys": shape_key_result["created"],
        "generated_without_library": shape_key_result["generated_without_library"],
        "missing_shape_keys": shape_key_result["missing"],
    }
    weight_report = {
        "status": "ok" if weight_result["failures"] == 0 else "warning",
        "binding_mode": rig_plan.get("weight_plan", {}).get("binding_mode"),
        "pose_tests": weight_result["pose_tests"],
        "bound_meshes": bound_meshes,
        "failures": weight_result["failures"],
    }

    rig_report_path = resolved_output_dir / "rig_report.json"
    shape_key_report_path = resolved_output_dir / "shape_key_report.json"
    weight_report_path = resolved_output_dir / "weight_report.json"
    _write_json(rig_report_path, rig_report)
    _write_json(shape_key_report_path, shape_key_report)
    _write_json(weight_report_path, weight_report)

    return {
        "status": "ok" if weight_result["failures"] == 0 else "warning",
        "armature_name": armature_object.name,
        "rig_report_path": str(rig_report_path),
        "shape_key_report_path": str(shape_key_report_path),
        "weight_report_path": str(weight_report_path),
        "bound_meshes": bound_meshes,
    }


def _build_armature(bpy: Any, rig_plan: dict[str, Any]) -> Any:
    armature_name = str(rig_plan.get("armature", {}).get("name", "RoundBuddy_Rig"))
    existing = bpy.data.objects.get(armature_name)
    if existing is not None:
        bpy.data.objects.remove(existing, do_unlink=True)

    armature_data = bpy.data.armatures.new(armature_name)
    armature_object = bpy.data.objects.new(armature_name, armature_data)
    bpy.context.scene.collection.objects.link(armature_object)
    bpy.context.view_layer.objects.active = armature_object
    armature_object.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")

    bone_positions = _bone_positions(str(rig_plan.get("character_type", "humanoid")))
    required_bones = [
        str(name)
        for name in rig_plan.get("armature", {}).get("required_bones", [])
        if isinstance(name, str)
    ]

    edit_bones: dict[str, Any] = {}
    for bone_name in required_bones:
        head, tail = bone_positions.get(bone_name, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.2)))
        bone = armature_data.edit_bones.new(bone_name)
        bone.head = head
        bone.tail = tail
        edit_bones[bone_name] = bone

    hierarchy = [
        ("hips", "root"),
        ("spine", "hips"),
        ("chest", "spine"),
        ("neck", "chest"),
        ("head", "neck"),
        ("arm_l", "chest"),
        ("arm_r", "chest"),
        ("leg_l", "hips"),
        ("leg_r", "hips"),
        ("foreleg_l", "spine"),
        ("foreleg_r", "spine"),
        ("hindleg_l", "hips"),
        ("hindleg_r", "hips"),
        ("tail", "hips"),
    ]
    for child_name, parent_name in hierarchy:
        child = edit_bones.get(child_name)
        parent = edit_bones.get(parent_name)
        if child is not None and parent is not None:
            child.parent = parent

    bpy.ops.object.mode_set(mode="OBJECT")
    armature_object.select_set(False)
    return armature_object


def _bind_meshes_to_armature(bpy: Any, armature_object: Any) -> list[str]:
    mesh_objects = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "MESH" and obj.name.startswith("RoundBuddy_")
    ]
    for obj in mesh_objects:
        obj.select_set(False)
    armature_object.select_set(True)
    bpy.context.view_layer.objects.active = armature_object
    for obj in mesh_objects:
        obj.select_set(True)

    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    armature_object.select_set(False)
    for obj in mesh_objects:
        obj.select_set(False)
    return [obj.name for obj in mesh_objects]


def _build_shape_keys(bpy: Any, rig_plan: dict[str, Any]) -> dict[str, Any]:
    target_name = str(rig_plan.get("shape_keys", {}).get("target_object", "RoundBuddy_Head"))
    target_object = bpy.data.objects.get(target_name)
    if target_object is None or target_object.type != "MESH":
        return {"target_object": target_name, "created": [], "missing": list(rig_plan.get("shape_keys", {}).get("supported", []))}

    if target_object.data.shape_keys is None:
        target_object.shape_key_add(name="Basis")

    created: list[str] = []
    generated_without_library: list[str] = []
    required_expressions = [
        expression_name
        for expression_name in rig_plan.get("shape_keys", {}).get("required", [])
        if isinstance(expression_name, str)
    ]
    missing_expression_names = {
        expression_name
        for expression_name in rig_plan.get("shape_keys", {}).get("missing_from_library", [])
        if isinstance(expression_name, str)
    }
    for expression_name in required_expressions:
        if not isinstance(expression_name, str):
            continue
        if target_object.data.shape_keys and expression_name in target_object.data.shape_keys.key_blocks:
            created.append(expression_name)
            continue
        key_block = target_object.shape_key_add(name=expression_name)
        _apply_shape_key_delta(target_object, key_block, expression_name)
        created.append(expression_name)
        if expression_name in missing_expression_names:
            generated_without_library.append(expression_name)

    return {
        "target_object": target_name,
        "created": created,
        "generated_without_library": generated_without_library,
        "missing": [],
    }


def _apply_shape_key_delta(target_object: Any, key_block: Any, expression_name: str) -> None:
    for index, vertex in enumerate(target_object.data.vertices):
        basis = target_object.data.shape_keys.key_blocks["Basis"].data[index].co.copy()
        adjusted = basis.copy()
        if expression_name == "smile" and basis.z < target_object.location.z:
            adjusted.x *= 1.03
            adjusted.z += 0.01
        elif expression_name == "angry" and basis.z > target_object.location.z:
            adjusted.z -= 0.01
        elif expression_name == "surprised":
            adjusted.y -= 0.01
            adjusted.z += 0.005
        elif expression_name == "blink" and abs(basis.x) < 0.18:
            adjusted.z -= 0.015
        elif expression_name.startswith("mouth_") and basis.z < target_object.location.z:
            adjusted.y -= 0.015
        key_block.data[index].co = adjusted


def _run_pose_tests(bpy: Any, rig_plan: dict[str, Any], armature_object: Any, bound_meshes: list[str]) -> dict[str, Any]:
    bpy.context.view_layer.objects.active = armature_object
    armature_object.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")

    pose_bones = armature_object.pose.bones
    original_rotations = {
        bone.name: tuple(bone.rotation_euler)
        for bone in pose_bones
    }

    results: list[dict[str, Any]] = []
    failures = 0
    for pose_test in rig_plan.get("weight_plan", {}).get("supported_pose_tests", []):
        status = "ok"
        message = "pose test executed"
        try:
            _apply_pose_test(pose_bones, str(pose_test))
            bpy.context.view_layer.update()
            _verify_bound_meshes(bpy, bound_meshes)
        except Exception as exc:
            status = "failed"
            message = str(exc)
            failures += 1
        finally:
            _restore_pose_rotations(pose_bones, original_rotations)
            bpy.context.view_layer.update()
        results.append({"name": pose_test, "status": status, "message": message})

    bpy.ops.object.mode_set(mode="OBJECT")
    armature_object.select_set(False)
    return {"pose_tests": results, "failures": failures}


def _apply_pose_test(pose_bones: Any, pose_test: str) -> None:
    if pose_test == "arms_raise":
        _rotate_if_present(pose_bones, "arm_l", -0.8)
        _rotate_if_present(pose_bones, "arm_r", 0.8)
    elif pose_test == "elbows_bend":
        _rotate_if_present(pose_bones, "arm_l", -0.5, axis="Y")
        _rotate_if_present(pose_bones, "arm_r", 0.5, axis="Y")
    elif pose_test == "knees_bend":
        _rotate_if_present(pose_bones, "leg_l", 0.45, axis="Y")
        _rotate_if_present(pose_bones, "leg_r", 0.45, axis="Y")
    elif pose_test == "neck_turn":
        _rotate_if_present(pose_bones, "neck", 0.35, axis="Z")
    elif pose_test == "foreleg_bend":
        _rotate_if_present(pose_bones, "foreleg_l", 0.35, axis="Y")
        _rotate_if_present(pose_bones, "foreleg_r", 0.35, axis="Y")
    elif pose_test == "hindleg_bend":
        _rotate_if_present(pose_bones, "hindleg_l", 0.35, axis="Y")
        _rotate_if_present(pose_bones, "hindleg_r", 0.35, axis="Y")
    elif pose_test == "tail_swing":
        _rotate_if_present(pose_bones, "tail", 0.5, axis="Z")
    elif pose_test == "balance_hop":
        _rotate_if_present(pose_bones, "leg_l", 0.3, axis="Y")
        _rotate_if_present(pose_bones, "leg_r", -0.15, axis="Y")


def _rotate_if_present(pose_bones: Any, bone_name: str, amount: float, axis: str = "X") -> None:
    bone = pose_bones.get(bone_name)
    if bone is None:
        return
    bone.rotation_mode = "XYZ"
    if axis == "X":
        bone.rotation_euler.x = amount
    elif axis == "Y":
        bone.rotation_euler.y = amount
    elif axis == "Z":
        bone.rotation_euler.z = amount


def _restore_pose_rotations(pose_bones: Any, original_rotations: dict[str, tuple[float, float, float]]) -> None:
    for bone_name, rotation in original_rotations.items():
        bone = pose_bones.get(bone_name)
        if bone is None:
            continue
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = rotation


def _verify_bound_meshes(bpy: Any, bound_meshes: list[str]) -> None:
    for name in bound_meshes:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise RuntimeError(f"Bound mesh not found during pose test: {name}")
        if len(obj.vertex_groups) == 0:
            raise RuntimeError(f"Auto weight binding did not create vertex groups: {name}")
        if not any(modifier.type == "ARMATURE" for modifier in obj.modifiers):
            raise RuntimeError(f"Armature modifier not found on bound mesh: {name}")


def _bone_positions(character_type: str) -> dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]]:
    if character_type == "creature":
        return {
            "root": ((0.0, 0.0, 0.0), (0.0, 0.0, 0.2)),
            "hips": ((0.0, 0.0, 0.2), (0.0, 0.0, 0.5)),
            "spine": ((0.0, 0.0, 0.5), (0.0, 0.0, 0.9)),
            "neck": ((0.0, 0.0, 0.9), (0.0, -0.15, 1.15)),
            "head": ((0.0, -0.15, 1.15), (0.0, -0.25, 1.45)),
            "foreleg_l": ((-0.22, 0.0, 0.65), (-0.22, 0.0, 0.2)),
            "foreleg_r": ((0.22, 0.0, 0.65), (0.22, 0.0, 0.2)),
            "hindleg_l": ((-0.16, 0.0, 0.45), (-0.16, 0.0, 0.1)),
            "hindleg_r": ((0.16, 0.0, 0.45), (0.16, 0.0, 0.1)),
            "tail": ((0.0, 0.08, 0.55), (0.0, 0.45, 0.7)),
        }
    return {
        "root": ((0.0, 0.0, 0.0), (0.0, 0.0, 0.2)),
        "hips": ((0.0, 0.0, 0.2), (0.0, 0.0, 0.55)),
        "spine": ((0.0, 0.0, 0.55), (0.0, 0.0, 0.9)),
        "chest": ((0.0, 0.0, 0.9), (0.0, 0.0, 1.15)),
        "neck": ((0.0, 0.0, 1.15), (0.0, 0.0, 1.3)),
        "head": ((0.0, 0.0, 1.3), (0.0, 0.0, 1.62)),
        "arm_l": ((-0.08, 0.0, 1.05), (-0.48, 0.0, 0.98)),
        "arm_r": ((0.08, 0.0, 1.05), (0.48, 0.0, 0.98)),
        "leg_l": ((-0.08, 0.0, 0.45), (-0.08, 0.0, 0.02)),
        "leg_r": ((0.08, 0.0, 0.45), (0.08, 0.0, 0.02)),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
