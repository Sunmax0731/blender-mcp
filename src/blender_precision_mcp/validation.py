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

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "spec_path": self.spec_path,
            "checks": self.checks,
            "warnings": self.warnings,
            "failures": self.failures,
            "artifacts": self.artifacts,
        }


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
) -> dict[str, Any]:
    resolved_spec_path = Path(spec_path)
    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    failures: list[dict[str, Any]] = []
    artifacts: list[str] = []

    try:
        spec = load_model_spec(resolved_spec_path)
        _validate_json_schema(spec, MODEL_SPEC_SCHEMA_PATH)
        checks.append(_check("schema", "ok", "model_spec schema validation passed"))
        _run_static_checks(spec, checks, warnings, failures)
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


def _check(name: str, status: str, message: str) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "message": message,
    }


def _failure(name: str, message: str, suggestion: str | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "message": message,
        "suggestion": suggestion or "Update model_spec and run validation again.",
    }


def _is_number_list(value: Any, expected_length: int) -> bool:
    return (
        isinstance(value, list)
        and len(value) == expected_length
        and all(isinstance(item, int | float) for item in value)
    )
