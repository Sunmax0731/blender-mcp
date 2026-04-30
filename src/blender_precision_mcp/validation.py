from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[2]
MODEL_SPEC_SCHEMA_PATH = ROOT / "schemas" / "precision" / "model_spec.schema.json"
VALIDATION_REPORT_SCHEMA_PATH = ROOT / "schemas" / "precision" / "validation_report.schema.json"


@dataclass(frozen=True, slots=True)
class ValidationReport:
    schema_version: str
    status: str
    spec_path: str
    checks: list[dict[str, Any]]
    warnings: list[str]
    failures: list[dict[str, Any]]
    artifacts: list[str]
    live_scene: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "status": self.status,
            "spec_path": self.spec_path,
            "checks": self.checks,
            "warnings": self.warnings,
            "failures": self.failures,
            "artifacts": self.artifacts,
        }
        if self.live_scene is not None:
            payload["live_scene"] = self.live_scene
        return payload


def load_model_spec(path: str | Path) -> dict[str, Any]:
    spec_path = Path(path)
    if not spec_path.exists():
        raise FileNotFoundError(f"model_spec not found: {spec_path}")
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"model_spec must be a mapping: {spec_path}")
    return data


def validate_model_spec(
    spec_path: str | Path,
    output_path: str | Path | None = None,
    live_scene: bool = False,
    live_scene_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_spec_path = Path(spec_path)
    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    failures: list[dict[str, Any]] = []
    artifacts: list[str] = []
    collected_live_scene: dict[str, Any] | None = None

    try:
        spec = load_model_spec(resolved_spec_path)
        _validate_json_schema(spec, MODEL_SPEC_SCHEMA_PATH)
        checks.append(_check("schema", "ok", "model_spec schema validation passed"))
        _run_static_checks(spec, checks, warnings, failures)
        if live_scene:
            collected_live_scene = live_scene_snapshot or collect_live_scene_snapshot()
            _run_live_scene_checks(spec, collected_live_scene, checks, warnings, failures)
    except Exception as exc:
        failures.append(
            {
                "name": "model_spec",
                "message": str(exc),
                "suggestion": "Fix the model_spec structure and run validation again.",
            }
        )

    status = _status_from_findings(warnings, failures)
    report = ValidationReport(
        schema_version="0.1",
        status=status,
        spec_path=str(resolved_spec_path),
        checks=checks,
        warnings=warnings,
        failures=failures,
        artifacts=artifacts,
        live_scene=collected_live_scene,
    )
    payload = report.to_dict()
    _validate_json_schema(payload, VALIDATION_REPORT_SCHEMA_PATH)

    if output_path is not None:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        payload["artifacts"].append(str(destination))
        destination.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return payload


def collect_live_scene_snapshot() -> dict[str, Any]:
    try:
        import bpy  # type: ignore
    except Exception as exc:
        return {
            "available": False,
            "error": {
                "code": "BLENDER_NOT_AVAILABLE",
                "message": f"Blender Python is not available: {exc}",
            },
            "objects": [],
            "materials": [],
            "camera": None,
            "lights": [],
        }

    try:
        scene = bpy.context.scene
        objects: list[dict[str, Any]] = []
        lights: list[str] = []
        for obj in scene.objects:
            material_names = [
                slot.material.name
                for slot in getattr(obj, "material_slots", [])
                if getattr(slot, "material", None) is not None
            ]
            object_data = {
                "name": obj.name,
                "type": obj.type,
                "dimensions": [
                    float(obj.dimensions.x),
                    float(obj.dimensions.y),
                    float(obj.dimensions.z),
                ],
                "location": [
                    float(obj.location.x),
                    float(obj.location.y),
                    float(obj.location.z),
                ],
                "materials": material_names,
                "visible": bool(obj.visible_get()),
            }
            objects.append(object_data)
            if obj.type == "LIGHT":
                lights.append(obj.name)

        return {
            "available": True,
            "scene_name": scene.name,
            "objects": objects,
            "materials": sorted(material.name for material in bpy.data.materials),
            "camera": scene.camera.name if scene.camera else None,
            "lights": lights,
        }
    except Exception as exc:
        return {
            "available": False,
            "error": {
                "code": "BLENDER_NOT_AVAILABLE",
                "message": f"Blender live scene cannot be inspected: {exc}",
            },
            "objects": [],
            "materials": [],
            "camera": None,
            "lights": [],
        }


def _run_static_checks(
    spec: dict[str, Any],
    checks: list[dict[str, Any]],
    warnings: list[str],
    failures: list[dict[str, Any]],
) -> None:
    objects = spec.get("objects", [])
    materials = spec.get("materials", [])
    validation = spec.get("validation", {})

    material_names = {
        material.get("name")
        for material in materials
        if isinstance(material, dict) and isinstance(material.get("name"), str)
    }
    object_names: set[str] = set()

    for index, obj in enumerate(objects):
        if not isinstance(obj, dict):
            failures.append(_failure(f"objects[{index}]", "Object entry must be a mapping."))
            continue

        name = obj.get("name")
        if not isinstance(name, str) or not name.strip():
            failures.append(_failure(f"objects[{index}].name", "Object name is required."))
        elif name in object_names:
            failures.append(_failure(name, "Object names must be unique."))
        else:
            object_names.add(name)

        dimensions = obj.get("dimensions")
        if dimensions is not None and not _is_number_list(dimensions, expected_length=3):
            failures.append(
                _failure(
                    str(name or f"objects[{index}]"),
                    "dimensions must be a 3-number list.",
                    "Use dimensions such as [1.0, 0.5, 0.25].",
                )
            )

        material_name = obj.get("material")
        if isinstance(material_name, str) and material_names and material_name not in material_names:
            failures.append(
                _failure(
                    str(name or f"objects[{index}]"),
                    f"material '{material_name}' is not defined.",
                    "Add the material to the materials section or update the object reference.",
                )
            )

    if not objects:
        failures.append(_failure("objects", "At least one object is required."))
    else:
        checks.append(_check("objects", "ok", f"{len(objects)} object(s) declared"))

    if validation.get("require_named_objects", False) and len(object_names) != len(objects):
        failures.append(
            _failure(
                "validation.require_named_objects",
                "All objects must have unique names when require_named_objects is true.",
            )
        )

    if validation.get("require_named_materials", False) and materials and len(material_names) != len(materials):
        failures.append(
            _failure(
                "validation.require_named_materials",
                "All materials must have unique names when require_named_materials is true.",
            )
        )

    if validation.get("require_review_images", False):
        visual_qa = spec.get("visual_qa", {})
        if not isinstance(visual_qa, dict) or not visual_qa.get("views"):
            warnings.append("validation requires review images, but visual_qa.views is empty.")
        else:
            checks.append(_check("visual_qa", "ok", "review image views are declared"))

    if not materials:
        warnings.append("No materials are declared. Models should define named materials.")
    else:
        checks.append(_check("materials", "ok", f"{len(materials)} material(s) declared"))


def _run_live_scene_checks(
    spec: dict[str, Any],
    snapshot: dict[str, Any],
    checks: list[dict[str, Any]],
    warnings: list[str],
    failures: list[dict[str, Any]],
) -> None:
    if not snapshot.get("available", False):
        error = snapshot.get("error", {})
        failures.append(
            _failure(
                "live_scene",
                str(error.get("message") or "Blender live scene is not available."),
                "Start Blender with the official MCP add-on or run validation inside Blender Python.",
                evidence={"code": error.get("code", "BLENDER_NOT_AVAILABLE")},
            )
        )
        return

    checks.append(
        _check(
            "live_scene",
            "ok",
            "Blender live scene snapshot collected",
            evidence={
                "scene_name": snapshot.get("scene_name"),
                "object_count": len(snapshot.get("objects", [])),
            },
        )
    )

    validation = spec.get("validation", {})
    dimension_threshold = float(validation.get("max_dimension_error_m", 0.01))
    location_threshold = float(validation.get("max_location_error_m", 0.01))

    scene_objects = {
        obj.get("name"): obj
        for obj in snapshot.get("objects", [])
        if isinstance(obj, dict) and isinstance(obj.get("name"), str)
    }
    scene_materials = set(snapshot.get("materials", []))

    for expected in spec.get("objects", []):
        if not isinstance(expected, dict):
            continue
        name = expected.get("name")
        if not isinstance(name, str):
            continue
        actual = scene_objects.get(name)
        if actual is None:
            failures.append(
                _failure(
                    f"live_scene.objects.{name}",
                    f"Object '{name}' is declared in model_spec but not found in the live scene.",
                    "Create or rename the object so it matches the model_spec.",
                )
            )
            continue

        checks.append(
            _check(
                f"live_scene.objects.{name}.exists",
                "ok",
                f"Object '{name}' exists in the live scene.",
                evidence={"type": actual.get("type"), "visible": actual.get("visible")},
            )
        )
        _compare_vector_field(
            object_name=name,
            field_name="dimensions",
            expected=expected.get("dimensions"),
            actual=actual.get("dimensions"),
            threshold=dimension_threshold,
            checks=checks,
            failures=failures,
        )
        _compare_vector_field(
            object_name=name,
            field_name="location",
            expected=expected.get("location"),
            actual=actual.get("location"),
            threshold=location_threshold,
            checks=checks,
            failures=failures,
        )

        expected_material = expected.get("material")
        if isinstance(expected_material, str):
            actual_materials = actual.get("materials", [])
            if expected_material not in actual_materials:
                failures.append(
                    _failure(
                        f"live_scene.objects.{name}.material",
                        f"Object '{name}' does not use expected material '{expected_material}'.",
                        "Assign the expected material or update the model_spec.",
                        evidence={"expected": expected_material, "actual": actual_materials},
                    )
                )
            else:
                checks.append(
                    _check(
                        f"live_scene.objects.{name}.material",
                        "ok",
                        f"Object '{name}' uses expected material '{expected_material}'.",
                        evidence={"actual": actual_materials},
                    )
                )

    for material in spec.get("materials", []):
        if not isinstance(material, dict):
            continue
        name = material.get("name")
        if isinstance(name, str) and name not in scene_materials:
            failures.append(
                _failure(
                    f"live_scene.materials.{name}",
                    f"Material '{name}' is declared in model_spec but not found in the live scene.",
                    "Create or rename the material so it matches the model_spec.",
                )
            )

    if validation.get("require_camera", False):
        camera = snapshot.get("camera")
        if camera:
            checks.append(
                _check(
                    "live_scene.camera",
                    "ok",
                    "Live scene has an active camera.",
                    evidence={"camera": camera},
                )
            )
        else:
            failures.append(_failure("live_scene.camera", "Active camera is required but not found."))

    if validation.get("require_lights", False):
        lights = snapshot.get("lights", [])
        if lights:
            checks.append(
                _check(
                    "live_scene.lights",
                    "ok",
                    "Live scene has light objects.",
                    evidence={"lights": lights},
                )
            )
        else:
            failures.append(_failure("live_scene.lights", "At least one light is required but not found."))

    if validation.get("forbid_extra_objects", False):
        expected_objects = {
            obj.get("name")
            for obj in spec.get("objects", [])
            if isinstance(obj, dict) and isinstance(obj.get("name"), str)
        }
        allowed_scene_objects = set(expected_objects)
        if validation.get("require_camera", False) and snapshot.get("camera"):
            allowed_scene_objects.add(str(snapshot["camera"]))
        if validation.get("require_lights", False):
            allowed_scene_objects.update(str(light) for light in snapshot.get("lights", []))

        extra_objects = sorted(
            name
            for name in scene_objects
            if isinstance(name, str) and name not in allowed_scene_objects
        )
        if extra_objects:
            failures.append(
                _failure(
                    "live_scene.extra_objects",
                    "Live scene contains objects that are not declared in model_spec.",
                    "Remove undeclared scene objects or disable validation.forbid_extra_objects.",
                    evidence={"extra_objects": extra_objects},
                )
            )
        else:
            checks.append(
                _check(
                    "live_scene.extra_objects",
                    "ok",
                    "Live scene has no undeclared objects.",
                )
            )

    if not snapshot.get("objects"):
        warnings.append("Live scene snapshot contains no objects.")


def _compare_vector_field(
    object_name: str,
    field_name: str,
    expected: Any,
    actual: Any,
    threshold: float,
    checks: list[dict[str, Any]],
    failures: list[dict[str, Any]],
) -> None:
    if expected is None:
        return
    if not _is_number_list(expected, 3):
        return
    if not _is_number_list(actual, 3):
        failures.append(
            _failure(
                f"live_scene.objects.{object_name}.{field_name}",
                f"Cannot measure {field_name} for object '{object_name}'.",
            )
        )
        return

    deltas = [
        abs(float(actual_value) - float(expected_value))
        for actual_value, expected_value in zip(actual, expected, strict=True)
    ]
    max_delta = max(deltas)
    evidence = {
        "expected": [float(value) for value in expected],
        "actual": [float(value) for value in actual],
        "deltas": deltas,
        "threshold": threshold,
        "max_delta": max_delta,
    }
    if max_delta > threshold:
        failures.append(
            _failure(
                f"live_scene.objects.{object_name}.{field_name}",
                f"Object '{object_name}' {field_name} differs from model_spec beyond threshold.",
                "Adjust the scene object transform or update the model_spec threshold.",
                evidence=evidence,
            )
        )
    else:
        checks.append(
            _check(
                f"live_scene.objects.{object_name}.{field_name}",
                "ok",
                f"Object '{object_name}' {field_name} is within threshold.",
                evidence=evidence,
            )
        )


def _validate_json_schema(instance: dict[str, Any], schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=instance, schema=schema)


def _status_from_findings(warnings: list[str], failures: list[dict[str, Any]]) -> str:
    if failures:
        return "failed"
    if warnings:
        return "warning"
    return "ok"


def _check(
    name: str,
    status: str,
    message: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "name": name,
        "status": status,
        "message": message,
    }
    if evidence is not None:
        payload["evidence"] = evidence
    return payload


def _failure(
    name: str,
    message: str,
    suggestion: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "name": name,
        "message": message,
        "suggestion": suggestion or "Update model_spec and run validation again.",
    }
    if evidence is not None:
        payload["evidence"] = evidence
    return payload


def _is_number_list(value: Any, expected_length: int) -> bool:
    return (
        isinstance(value, list)
        and len(value) == expected_length
        and all(isinstance(item, int | float) for item in value)
    )
