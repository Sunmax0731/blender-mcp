from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .scene_builder import load_scene_spec


DEFAULT_SPEC_PATH = Path("templates/precision/model_spec.yaml")
DEFAULT_CLEANUP_OPERATIONS = ("delete_loose", "normals_make_consistent")


def analyze_mesh_quality(
    target_objects: list[str] | None = None,
    spec_path: str | Path = DEFAULT_SPEC_PATH,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    thresholds = _load_mesh_quality_thresholds(spec_path)
    bpy_module = _try_load_bpy()
    if bpy_module is None:
        return _failure("blender_unavailable", "Blender Python module bpy is not available.")

    object_names = _resolve_target_objects(bpy_module, target_objects)
    metrics: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    try:
        for name in object_names:
            obj = bpy_module.data.objects.get(name)
            if obj is None or getattr(obj, "type", None) != "MESH":
                failures.append(_quality_failure(name, "object_not_found", "Target mesh object was not found."))
                continue
            metric = _collect_mesh_metrics(obj)
            metric["thresholds"] = _thresholds_for_object(name, thresholds)
            metric["failures"] = _evaluate_mesh_quality(metric, metric["thresholds"])
            metrics.append(metric)
            failures.extend(metric["failures"])
    except Exception as exc:
        return _failure("mesh_quality_failed", str(exc))

    payload = _quality_payload(
        status="failed" if failures else "ok",
        metrics=metrics,
        failures=failures,
        operations=[],
    )
    _write_optional_json(output_path, payload)
    return {"success": not failures, "data": payload}


def apply_mesh_cleanup(
    target_object: str,
    operations: list[str] | None = None,
    output_path: str | Path | None = None,
    dry_run: bool = True,
    confirm: bool = False,
    create_backup: bool = True,
) -> dict[str, Any]:
    cleanup_operations = tuple(operations or DEFAULT_CLEANUP_OPERATIONS)
    plan = _cleanup_plan(target_object, cleanup_operations, create_backup=create_backup, confirm=confirm)
    if dry_run:
        return {"success": True, "data": {"dry_run": True, "operations": plan}}
    if not confirm:
        return _failure(
            "confirmation_required",
            "Mesh cleanup requires explicit confirm=true before execution.",
            data={"dry_run": False, "operations": plan},
        )
    if not create_backup:
        return _failure(
            "backup_required",
            "Mesh cleanup requires create_backup=true before execution.",
            data={"dry_run": False, "operations": plan},
        )

    bpy_module = _try_load_bpy()
    if bpy_module is None:
        return _failure(
            "blender_unavailable",
            "Blender Python module bpy is not available.",
            data={"operations": plan},
        )

    obj = bpy_module.data.objects.get(target_object)
    if obj is None or getattr(obj, "type", None) != "MESH":
        return _failure("object_not_found", f"Target mesh object was not found: {target_object}")

    before = _collect_mesh_metrics(obj)
    try:
        backup_name = _backup_object(bpy_module, obj)
        _activate_object(bpy_module, obj)
        executed = _execute_cleanup_operations(bpy_module, cleanup_operations)
        bpy_module.context.view_layer.update()
        after = _collect_mesh_metrics(obj)
    except Exception as exc:
        return _failure("mesh_cleanup_failed", str(exc), data={"operations": plan})

    payload = _quality_payload(
        status="executed",
        metrics=[after],
        failures=[],
        operations=plan,
        before=before,
        backup={"created": True, "objects": [backup_name], "source": obj.name},
        executed=executed,
    )
    _write_optional_json(output_path, payload)
    return {"success": True, "data": payload}


def validate_retopology_result(
    target_object: str,
    spec_path: str | Path = DEFAULT_SPEC_PATH,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    result = analyze_mesh_quality(
        target_objects=[target_object],
        spec_path=spec_path,
        output_path=output_path,
    )
    if not result["success"]:
        result.setdefault("error", {"code": "retopology_validation_failed", "message": "Mesh quality thresholds failed."})
    return result


def _load_mesh_quality_thresholds(spec_path: str | Path) -> dict[str, Any]:
    try:
        spec = load_scene_spec(spec_path)
    except Exception:
        return {"defaults": {}, "objects": {}}
    mesh_quality = spec.get("mesh_quality", {}) if isinstance(spec.get("mesh_quality"), dict) else {}
    object_thresholds = {
        entry["name"]: entry
        for entry in mesh_quality.get("objects", [])
        if isinstance(entry, dict) and isinstance(entry.get("name"), str)
    }
    return {
        "defaults": mesh_quality.get("defaults", {}) if isinstance(mesh_quality.get("defaults"), dict) else {},
        "objects": object_thresholds,
    }


def _resolve_target_objects(bpy_module: Any, target_objects: list[str] | None) -> list[str]:
    if target_objects:
        return [name for name in target_objects if isinstance(name, str) and name.strip()]
    return sorted(obj.name for obj in bpy_module.context.scene.objects if getattr(obj, "type", None) == "MESH")


def _collect_mesh_metrics(obj: Any) -> dict[str, Any]:
    mesh = obj.data
    face_count = len(mesh.polygons)
    triangle_count = sum(1 for polygon in mesh.polygons if len(polygon.vertices) == 3)
    quad_count = sum(1 for polygon in mesh.polygons if len(polygon.vertices) == 4)
    ngon_count = sum(1 for polygon in mesh.polygons if len(polygon.vertices) > 4)
    loose_vertices, loose_edges, non_manifold_edges = _collect_topology_metrics(mesh)
    return {
        "name": obj.name,
        "type": getattr(obj, "type", None),
        "vertex_count": len(mesh.vertices),
        "edge_count": len(mesh.edges),
        "face_count": face_count,
        "triangle_count": triangle_count,
        "quad_count": quad_count,
        "ngon_count": ngon_count,
        "triangle_ratio": _ratio(triangle_count, face_count),
        "quad_ratio": _ratio(quad_count, face_count),
        "loose_vertices": loose_vertices,
        "loose_edges": loose_edges,
        "non_manifold_edges": non_manifold_edges,
    }


def _collect_topology_metrics(mesh: Any) -> tuple[int, int, int]:
    try:
        import bmesh  # type: ignore

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        loose_vertices = sum(1 for vert in bm.verts if not vert.link_edges and not vert.link_faces)
        loose_edges = sum(1 for edge in bm.edges if not edge.link_faces)
        non_manifold_edges = sum(1 for edge in bm.edges if not edge.is_manifold)
        bm.free()
        return loose_vertices, loose_edges, non_manifold_edges
    except Exception:
        used_vertices = {vertex_index for edge in mesh.edges for vertex_index in edge.vertices}
        face_edges = {edge_key for polygon in mesh.polygons for edge_key in polygon.edge_keys}
        loose_vertices = sum(1 for vertex in mesh.vertices if vertex.index not in used_vertices)
        loose_edges = sum(1 for edge in mesh.edges if tuple(sorted(edge.vertices)) not in face_edges)
        return loose_vertices, loose_edges, 0


def _thresholds_for_object(name: str, thresholds: dict[str, Any]) -> dict[str, Any]:
    merged = dict(thresholds.get("defaults", {}))
    merged.update(thresholds.get("objects", {}).get(name, {}))
    merged.pop("name", None)
    return merged


def _evaluate_mesh_quality(metric: dict[str, Any], thresholds: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    checks = (
        ("max_non_manifold_edges", "non_manifold_edges", "<="),
        ("max_loose_vertices", "loose_vertices", "<="),
        ("max_loose_edges", "loose_edges", "<="),
        ("max_face_count", "face_count", "<="),
        ("min_quad_ratio", "quad_ratio", ">="),
    )
    for threshold_name, metric_name, operator in checks:
        if threshold_name not in thresholds:
            continue
        threshold = thresholds[threshold_name]
        actual = metric.get(metric_name)
        if not isinstance(threshold, int | float) or not isinstance(actual, int | float):
            continue
        failed = actual > threshold if operator == "<=" else actual < threshold
        if failed:
            failures.append(
                _quality_failure(
                    metric["name"],
                    threshold_name,
                    f"{metric_name}={actual} does not satisfy {operator} {threshold}.",
                    evidence={"metric": metric_name, "actual": actual, "threshold": threshold},
                )
            )
    return failures


def _execute_cleanup_operations(bpy_module: Any, operations: tuple[str, ...]) -> list[str]:
    executed: list[str] = []
    bpy_module.ops.object.mode_set(mode="EDIT")
    bpy_module.ops.mesh.select_all(action="SELECT")
    if "delete_loose" in operations:
        bpy_module.ops.mesh.delete_loose()
        executed.append("delete_loose")
    if "merge_by_distance" in operations:
        bpy_module.ops.mesh.remove_doubles(threshold=0.0001)
        executed.append("merge_by_distance")
    if "normals_make_consistent" in operations:
        bpy_module.ops.mesh.normals_make_consistent(inside=False)
        executed.append("normals_make_consistent")
    bpy_module.ops.object.mode_set(mode="OBJECT")
    return executed


def _backup_object(bpy_module: Any, obj: Any) -> str:
    backup = obj.copy()
    backup.data = obj.data.copy()
    backup.name = f"{obj.name}_backup_before_mesh_cleanup"
    bpy_module.context.collection.objects.link(backup)
    backup.hide_viewport = True
    backup.hide_render = True
    return backup.name


def _activate_object(bpy_module: Any, obj: Any) -> None:
    bpy_module.ops.object.mode_set(mode="OBJECT")
    bpy_module.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy_module.context.view_layer.objects.active = obj


def _cleanup_plan(target_object: str, operations: tuple[str, ...], create_backup: bool, confirm: bool) -> list[dict[str, Any]]:
    return [
        {"action": "backup_object", "target_object": target_object, "required": True, "enabled": create_backup},
        {"action": "confirm", "required": True, "satisfied": confirm},
        *({"action": operation, "target_object": target_object} for operation in operations),
    ]


def _quality_payload(
    status: str,
    metrics: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    **extra: Any,
) -> dict[str, Any]:
    payload = {
        "schema_version": "0.1",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "metrics": metrics,
        "failures": failures,
        "operations": operations,
    }
    payload.update(extra)
    return payload


def _write_optional_json(output_path: str | Path | None, payload: dict[str, Any]) -> None:
    if output_path is None:
        return
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _quality_failure(
    object_name: str,
    code: str,
    message: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {"object": object_name, "code": code, "message": message}
    if evidence:
        payload["evidence"] = evidence
    return payload


def _ratio(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(count / total, 6)


def _try_load_bpy() -> Any | None:
    try:
        import bpy  # type: ignore
    except ModuleNotFoundError:
        return None
    if not hasattr(bpy, "context") or not hasattr(bpy, "ops"):
        return None
    return bpy


def _failure(code: str, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
        "data": data or {},
    }
