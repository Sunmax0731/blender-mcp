from __future__ import annotations

from pathlib import Path
from typing import Any

from .addons import load_addon_registry


DEFAULT_REGISTRY_PATH = Path("templates/precision/addon_registry.yaml")


def prepare_operator_context(
    operator_idname: str,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    operator_entry = _find_operator(operator_idname, registry_path)
    if operator_entry is None:
        return _failure("not_approved", f"Operator is not approved: {operator_idname}")

    context = operator_entry.get("context", {})
    bpy_module = _try_load_bpy()
    if bpy_module is None:
        return _failure(
            "blender_unavailable",
            "Blender Python module bpy is not available.",
            data={"operator": operator_idname, "required_context": context},
        )

    issues: list[str] = []
    required_mode = context.get("mode")
    active_object = getattr(bpy_module.context, "active_object", None)

    if context.get("requires_active_object") and active_object is None:
        issues.append("active object is required")
    if context.get("requires_selected_objects") and not getattr(
        bpy_module.context, "selected_objects", []
    ):
        issues.append("selected objects are required")
    if required_mode and active_object is not None and getattr(active_object, "mode", None) != required_mode:
        try:
            bpy_module.ops.object.mode_set(mode=required_mode)
        except Exception as exc:
            issues.append(f"failed to switch mode to {required_mode}: {exc}")

    if issues:
        return _failure(
            "context_not_ready",
            "Operator context requirements are not satisfied.",
            data={"operator": operator_idname, "issues": issues, "required_context": context},
        )

    return {
        "success": True,
        "data": {
            "operator": operator_idname,
            "required_context": context,
            "context_ready": True,
        },
    }


def check_operator_poll(operator_idname: str) -> dict[str, Any]:
    bpy_module = _try_load_bpy()
    if bpy_module is None:
        return _failure("blender_unavailable", "Blender Python module bpy is not available.")

    operator_callable = _resolve_bpy_operator(bpy_module, operator_idname)
    if operator_callable is None:
        return _failure("operator_missing", f"Operator is not registered: {operator_idname}")

    try:
        poll_result = bool(operator_callable.poll())
    except Exception as exc:
        return _failure("poll_failed", str(exc))

    return {
        "success": poll_result,
        "data": {
            "operator": operator_idname,
            "poll": poll_result,
        },
    }


def run_approved_addon_operator(
    operator_idname: str,
    parameters: dict[str, Any] | None = None,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    dry_run: bool = True,
) -> dict[str, Any]:
    operator_entry = _find_operator(operator_idname, registry_path)
    if operator_entry is None:
        return _failure("not_approved", f"Operator is not approved: {operator_idname}")

    if operator_entry.get("destructive") and not operator_entry.get("backup_required"):
        return _failure(
            "backup_policy_violation",
            "Destructive approved operators must require backup.",
        )

    context_result = prepare_operator_context(operator_idname, registry_path)
    if not context_result["success"] and not dry_run:
        return context_result

    mapped_parameters = _map_parameters(parameters or {}, operator_entry.get("property_map", {}))
    if dry_run:
        return {
            "success": True,
            "data": {
                "operator": operator_idname,
                "dry_run": True,
                "destructive": bool(operator_entry.get("destructive", False)),
                "backup_required": bool(operator_entry.get("backup_required", False)),
                "parameters": mapped_parameters,
                "context": context_result,
            },
        }

    bpy_module = _try_load_bpy()
    if bpy_module is None:
        return _failure("blender_unavailable", "Blender Python module bpy is not available.")

    poll_result = check_operator_poll(operator_idname)
    if not poll_result["success"]:
        return poll_result

    operator_callable = _resolve_bpy_operator(bpy_module, operator_idname)
    if operator_callable is None:
        return _failure("operator_missing", f"Operator is not registered: {operator_idname}")

    try:
        result = operator_callable(**mapped_parameters)
    except Exception as exc:
        return _failure("operator_execution_failed", str(exc))

    return {
        "success": True,
        "data": {
            "operator": operator_idname,
            "result": list(result) if isinstance(result, set) else result,
        },
    }


def apply_retopology(
    target_object: str,
    target_face_count: int,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    dry_run: bool = True,
) -> dict[str, Any]:
    operator_entry = _find_operator_for_operation("retopology", registry_path)
    if operator_entry is None:
        return _failure("operation_not_approved", "No approved retopology operator is registered.")
    return run_approved_addon_operator(
        operator_entry["idname"],
        parameters={"target_object": target_object, "target_face_count": target_face_count},
        registry_path=registry_path,
        dry_run=dry_run,
    )


def _find_operator(operator_idname: str, registry_path: str | Path) -> dict[str, Any] | None:
    registry = load_addon_registry(registry_path)
    for addon in registry.get("approved_addons", []):
        for operator in addon.get("operators", []):
            if operator.get("idname") == operator_idname:
                return operator
    return None


def _find_operator_for_operation(operation: str, registry_path: str | Path) -> dict[str, Any] | None:
    registry = load_addon_registry(registry_path)
    for addon in registry.get("approved_addons", []):
        if operation not in addon.get("allowed_operations", []):
            continue
        operators = addon.get("operators", [])
        if operators:
            return operators[0]
    return None


def _map_parameters(parameters: dict[str, Any], property_map: dict[str, str]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for key, value in parameters.items():
        mapped[property_map.get(key, key)] = value
    return mapped


def _resolve_bpy_operator(bpy_module: Any, operator_idname: str) -> Any | None:
    parts = operator_idname.split(".")
    if len(parts) != 2:
        return None
    namespace, operator_name = parts
    namespace_obj = getattr(bpy_module.ops, namespace, None)
    if namespace_obj is None:
        return None
    return getattr(namespace_obj, operator_name, None)


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
