from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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
    confirm: bool = False,
) -> dict[str, Any]:
    operator_entry = _find_operator(operator_idname, registry_path)
    if operator_entry is None:
        return _failure("not_approved", f"Operator is not approved: {operator_idname}")

    if operator_entry.get("destructive") and not operator_entry.get("backup_required"):
        return _failure(
            "backup_policy_violation",
            "Destructive approved operators must require backup.",
        )

    destructive = bool(operator_entry.get("destructive", False))
    backup_required = bool(operator_entry.get("backup_required", False))
    mapped_parameters = _map_parameters(parameters or {}, operator_entry.get("property_map", {}))
    safety_actions = _operator_safety_actions(operator_entry, confirm=confirm)

    if destructive and not dry_run and not confirm:
        return _failure(
            "confirmation_required",
            "Destructive approved operators require explicit confirm=true before execution.",
            data={
                "operator": operator_idname,
                "destructive": destructive,
                "backup_required": backup_required,
                "parameters": mapped_parameters,
                "safety_actions": safety_actions,
            },
        )

    context_result = prepare_operator_context(operator_idname, registry_path)
    if not context_result["success"] and not dry_run:
        return context_result

    if dry_run:
        return {
            "success": True,
            "data": {
                "operator": operator_idname,
                "dry_run": True,
                "confirm_required": destructive,
                "destructive": destructive,
                "backup_required": backup_required,
                "parameters": mapped_parameters,
                "context": context_result,
                "safety_actions": safety_actions,
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

    backup_result = _create_operator_backup(
        bpy_module=bpy_module,
        operator_idname=operator_idname,
        operator_entry=operator_entry,
        parameters=parameters or {},
    )
    if not backup_result["success"]:
        return backup_result

    try:
        result = operator_callable(**mapped_parameters)
    except Exception as exc:
        return _failure("operator_execution_failed", str(exc))

    return {
        "success": True,
        "data": {
            "operator": operator_idname,
            "result": list(result) if isinstance(result, set) else result,
            "destructive": destructive,
            "backup_required": backup_required,
            "backup": backup_result["data"],
            "safety_actions": safety_actions,
        },
    }


def apply_retopology(
    target_object: str,
    target_face_count: int,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    dry_run: bool = True,
    confirm: bool = False,
) -> dict[str, Any]:
    operator_entry = _find_operator_for_operation("retopology", registry_path)
    if operator_entry is None:
        return _failure("operation_not_approved", "No approved retopology operator is registered.")
    return run_approved_addon_operator(
        operator_entry["idname"],
        parameters={"target_object": target_object, "target_face_count": target_face_count},
        registry_path=registry_path,
        dry_run=dry_run,
        confirm=confirm,
    )


def _find_operator(operator_idname: str, registry_path: str | Path) -> dict[str, Any] | None:
    registry = _load_operator_registry(registry_path)
    for addon in registry.get("approved_addons", []):
        for operator in addon.get("operators", []):
            if operator.get("idname") == operator_idname:
                return operator
    return None


def _find_operator_for_operation(operation: str, registry_path: str | Path) -> dict[str, Any] | None:
    registry = _load_operator_registry(registry_path)
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


def _operator_safety_actions(operator_entry: dict[str, Any], confirm: bool) -> list[dict[str, Any]]:
    actions = [
        {
            "name": "preview",
            "status": "required",
            "message": "Inspect dry_run parameters and context before execution.",
        },
        {
            "name": "confirm",
            "status": "satisfied" if confirm else "required",
            "message": "Set confirm=true before executing a destructive operator.",
        },
    ]
    if operator_entry.get("backup_required"):
        actions.append(
            {
                "name": "backup",
                "status": "required",
                "message": "Duplicate the target or active object before execution.",
            }
        )
    return actions


def _create_operator_backup(
    bpy_module: Any,
    operator_idname: str,
    operator_entry: dict[str, Any],
    parameters: dict[str, Any],
) -> dict[str, Any]:
    if not operator_entry.get("backup_required"):
        return {"success": True, "data": {"created": False, "objects": []}}

    target_name = parameters.get("target_object")
    source = bpy_module.data.objects.get(target_name) if isinstance(target_name, str) else None
    if source is None:
        source = getattr(bpy_module.context, "active_object", None)
    if source is None:
        return _failure(
            "backup_failed",
            "Backup is required but no target or active object is available.",
            data={"operator": operator_idname},
        )

    try:
        backup = source.copy()
        if getattr(source, "data", None) is not None:
            backup.data = source.data.copy()
        backup.name = f"{source.name}_backup_before_{operator_idname.replace('.', '_')}"
        bpy_module.context.collection.objects.link(backup)
        backup.hide_viewport = True
        backup.hide_render = True
    except Exception as exc:
        return _failure("backup_failed", str(exc), data={"operator": operator_idname})

    return {
        "success": True,
        "data": {
            "created": True,
            "objects": [backup.name],
            "source": source.name,
        },
    }


def _load_operator_registry(path: str | Path) -> dict[str, Any]:
    registry_path = Path(path)
    if registry_path.suffix.lower() == ".json":
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"add-on registry must be a mapping: {registry_path}")
        return data

    try:
        from .addons import load_addon_registry

        return load_addon_registry(registry_path)
    except ModuleNotFoundError:
        return _parse_minimal_addon_registry_yaml(registry_path.read_text(encoding="utf-8"))


def _parse_minimal_addon_registry_yaml(text: str) -> dict[str, Any]:
    registry: dict[str, Any] = {"approved_addons": []}
    current_addon: dict[str, Any] | None = None
    current_operator: dict[str, Any] | None = None
    section: str | None = None
    operator_subsection: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if not stripped:
            continue
        if stripped == "approved_addons:":
            section = "approved_addons"
            continue
        if section == "approved_addons" and stripped.startswith("- "):
            current_addon = {}
            registry["approved_addons"].append(current_addon)
            current_operator = None
            item = stripped[2:]
            if ":" in item:
                key, value = item.split(":", 1)
                current_addon[key.strip()] = _parse_minimal_yaml_value(value.strip())
            continue
        if current_addon is not None and indent == 4 and stripped == "operators:":
            current_addon["operators"] = []
            operator_subsection = None
            continue
        if current_addon is not None and indent == 6 and stripped.startswith("- "):
            current_operator = {}
            current_addon.setdefault("operators", []).append(current_operator)
            item = stripped[2:]
            if ":" in item:
                key, value = item.split(":", 1)
                current_operator[key.strip()] = _parse_minimal_yaml_value(value.strip())
            continue
        if current_operator is not None and indent == 8 and stripped.endswith(":"):
            operator_subsection = stripped[:-1]
            current_operator.setdefault(operator_subsection, {})
            continue
        if current_operator is not None and indent >= 10 and operator_subsection and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_operator[operator_subsection][key.strip()] = _parse_minimal_yaml_value(value.strip())
            continue
        if current_operator is not None and indent == 8 and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_operator[key.strip()] = _parse_minimal_yaml_value(value.strip())
            continue
        if current_addon is not None and indent == 4 and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_addon[key.strip()] = _parse_minimal_yaml_value(value.strip())

    return registry


def _parse_minimal_yaml_value(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value.strip("\"'")


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
