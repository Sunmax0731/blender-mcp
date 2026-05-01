from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ADDON_REGISTRY_PATH = ROOT / "templates" / "precision" / "addon_registry.yaml"
ADDON_REGISTRY_SCHEMA_PATH = ROOT / "schemas" / "precision" / "addon_registry.schema.json"


def load_addon_registry(path: str | Path = DEFAULT_ADDON_REGISTRY_PATH) -> dict[str, Any]:
    registry_path = Path(path)
    if not registry_path.exists():
        raise FileNotFoundError(f"add-on registry not found: {registry_path}")
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(registry, dict):
        raise ValueError(f"add-on registry must be a mapping: {registry_path}")
    schema = json.loads(ADDON_REGISTRY_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=registry, schema=schema)
    return registry


def list_blender_addons(
    registry_path: str | Path = DEFAULT_ADDON_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = load_addon_registry(registry_path)
    approved_modules = _approved_module_names(registry)
    bpy_info = _try_load_blender_addon_utils()
    if bpy_info is None:
        return {
            "success": True,
            "data": {
                "blender_available": False,
                "approved_modules": approved_modules,
                "installed_addons": [],
                "warnings": ["Blender Python modules are not available; registry inspection only."],
            },
        }

    addon_utils = bpy_info["addon_utils"]
    installed = []
    for module in addon_utils.modules():
        name = getattr(module, "__name__", "")
        enabled = False
        if hasattr(addon_utils, "check"):
            try:
                enabled = bool(addon_utils.check(name)[1])
            except Exception:
                enabled = False
        installed.append(
            {
                "module": name,
                "enabled": enabled,
                "approved": name in approved_modules,
            }
        )

    return {
        "success": True,
        "data": {
            "blender_available": True,
            "approved_modules": approved_modules,
            "installed_addons": installed,
            "warnings": [],
        },
    }


def get_addon_status(
    module: str,
    registry_path: str | Path = DEFAULT_ADDON_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = load_addon_registry(registry_path)
    approved = _find_approved_addon(registry, module)
    bpy_info = _try_load_blender_addon_utils()

    status: dict[str, Any] = {
        "module": module,
        "approved": approved is not None,
        "registry_entry": approved,
        "installed": False,
        "enabled": False,
        "blender_available": bpy_info is not None,
    }
    if bpy_info is not None:
        addon_utils = bpy_info["addon_utils"]
        try:
            installed, enabled = addon_utils.check(module)
            status["installed"] = bool(installed)
            status["enabled"] = bool(enabled)
        except Exception as exc:
            status["warning"] = str(exc)

    return {"success": True, "data": status}


def inspect_addon_capabilities(
    module: str | None = None,
    registry_path: str | Path = DEFAULT_ADDON_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = load_addon_registry(registry_path)
    entries = registry.get("approved_addons", [])
    if module:
        entries = [entry for entry in entries if entry.get("module") == module]

    capabilities = []
    for entry in entries:
        capabilities.append(
            {
                "module": entry.get("module"),
                "display_name": entry.get("display_name"),
                "allowed_operations": entry.get("allowed_operations", []),
                "operators": [
                    {
                        "idname": operator.get("idname"),
                        "destructive": bool(operator.get("destructive", False)),
                        "backup_required": bool(operator.get("backup_required", False)),
                        "context": operator.get("context", {}),
                        "property_map": operator.get("property_map", {}),
                    }
                    for operator in entry.get("operators", [])
                ],
            }
        )

    return {
        "success": True,
        "data": {
            "capabilities": capabilities,
            "blender_available": _try_load_blender_addon_utils() is not None,
        },
    }


def list_registered_operators(
    registry_path: str | Path = DEFAULT_ADDON_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = load_addon_registry(registry_path)
    operators = []
    for entry in registry.get("approved_addons", []):
        for operator in entry.get("operators", []):
            operators.append(
                {
                    "module": entry.get("module"),
                    "idname": operator.get("idname"),
                    "label": operator.get("label"),
                    "destructive": bool(operator.get("destructive", False)),
                    "backup_required": bool(operator.get("backup_required", False)),
                    "context": operator.get("context", {}),
                }
            )
    return {"success": True, "data": {"operators": operators}}


def _approved_module_names(registry: dict[str, Any]) -> list[str]:
    return [
        entry["module"]
        for entry in registry.get("approved_addons", [])
        if isinstance(entry, dict) and isinstance(entry.get("module"), str)
    ]


def _find_approved_addon(registry: dict[str, Any], module: str) -> dict[str, Any] | None:
    for entry in registry.get("approved_addons", []):
        if isinstance(entry, dict) and entry.get("module") == module:
            return entry
    return None


def _try_load_blender_addon_utils() -> dict[str, Any] | None:
    try:
        import addon_utils  # type: ignore
        import bpy  # type: ignore
    except ModuleNotFoundError:
        return None
    return {"addon_utils": addon_utils, "bpy": bpy}
