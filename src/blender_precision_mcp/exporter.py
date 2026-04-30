from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .scene_builder import load_scene_spec


DEFAULT_SPEC_PATH = Path("templates/precision/model_spec.yaml")
SUPPORTED_EXPORT_FORMATS = ("blend", "glb")


def export_scene(
    spec_path: str | Path = DEFAULT_SPEC_PATH,
    output_manifest_path: str | Path | None = None,
    validation_artifacts: list[str] | None = None,
    review_artifacts: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    try:
        spec = load_scene_spec(spec_path)
    except Exception as exc:
        return _failure("model_spec_load_failed", str(exc))

    exports = _read_exports(spec)
    unsupported = [entry for entry in exports if entry["format"] not in SUPPORTED_EXPORT_FORMATS]
    operations = [_export_operation(entry) for entry in exports]
    if unsupported:
        return _failure(
            "unsupported_export_format",
            "Some export formats are not supported.",
            data={
                "supported_formats": list(SUPPORTED_EXPORT_FORMATS),
                "unsupported": unsupported,
                "operations": operations,
            },
        )

    manifest = _manifest(
        spec_path=spec_path,
        dry_run=dry_run,
        operations=operations,
        exports=[],
        validation_artifacts=validation_artifacts or [],
        review_artifacts=review_artifacts or [],
    )

    if dry_run:
        _write_optional_json(output_manifest_path, manifest)
        return {"success": True, "data": manifest}

    bpy_module = _try_load_bpy()
    if bpy_module is None:
        return _failure(
            "blender_unavailable",
            "Blender Python module bpy is not available.",
            data={"operations": operations},
        )

    exported: list[dict[str, Any]] = []
    try:
        for entry in exports:
            exported.append(_execute_export(bpy_module, entry))
    except Exception as exc:
        return _failure("export_failed", str(exc), data={"exports": exported, "operations": operations})

    manifest = _manifest(
        spec_path=spec_path,
        dry_run=False,
        operations=operations,
        exports=exported,
        validation_artifacts=validation_artifacts or [],
        review_artifacts=review_artifacts or [],
    )
    _write_optional_json(output_manifest_path, manifest)
    return {"success": True, "data": manifest}


def _read_exports(spec: dict[str, Any]) -> list[dict[str, str]]:
    entries = spec.get("exports", [])
    if not isinstance(entries, list):
        return []
    exports: list[dict[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        export_format = str(entry.get("format", "")).lower().strip()
        path = str(entry.get("path", "")).strip()
        if export_format and path:
            exports.append({"format": export_format, "path": path})
    return exports


def _export_operation(entry: dict[str, str]) -> dict[str, str]:
    return {
        "action": "export_scene",
        "format": entry["format"],
        "path": entry["path"],
    }


def _execute_export(bpy_module: Any, entry: dict[str, str]) -> dict[str, Any]:
    destination = Path(entry["path"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    export_format = entry["format"]
    if export_format == "blend":
        bpy_module.ops.wm.save_as_mainfile(filepath=str(destination))
    elif export_format == "glb":
        bpy_module.ops.export_scene.gltf(filepath=str(destination), export_format="GLB")
    else:
        raise ValueError(f"Unsupported export format: {export_format}")
    return {
        "format": export_format,
        "path": str(destination),
        "exists": destination.exists(),
        "size_bytes": destination.stat().st_size if destination.exists() else None,
    }


def _manifest(
    spec_path: str | Path,
    dry_run: bool,
    operations: list[dict[str, str]],
    exports: list[dict[str, Any]],
    validation_artifacts: list[str],
    review_artifacts: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source_spec": str(spec_path),
        "dry_run": dry_run,
        "operations": operations,
        "exports": exports,
        "artifacts": {
            "validation": validation_artifacts,
            "review": review_artifacts,
        },
    }


def _write_optional_json(output_path: str | Path | None, payload: dict[str, Any]) -> None:
    if output_path is None:
        return
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload["manifest_path"] = str(destination)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
