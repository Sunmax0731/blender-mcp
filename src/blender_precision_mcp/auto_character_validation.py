from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
VALIDATION_REPORT_SCHEMA_PATH = ROOT / "schemas" / "precision" / "validation_report.schema.json"


@dataclass(frozen=True, slots=True)
class ValidatorFinding:
    status: str
    stage: str
    check_name: str
    evidence: dict[str, Any]
    suggested_fix: str
    retryable: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "stage": self.stage,
            "check_name": self.check_name,
            "evidence": self.evidence,
            "suggested_fix": self.suggested_fix,
            "retryable": self.retryable,
        }


def validate_auto_character(
    character_spec: dict[str, Any],
    pipeline_spec: dict[str, Any],
    *,
    artifact_paths: list[str] | None = None,
    spec_path: str = "generated://character_spec",
) -> dict[str, Any]:
    findings = (
        validate_shape_stage(character_spec, pipeline_spec)
        + validate_look_stage(character_spec, pipeline_spec)
        + validate_rig_stage(character_spec, pipeline_spec)
        + validate_expression_stage(character_spec, pipeline_spec)
        + validate_weight_stage(character_spec, pipeline_spec)
    )

    checks = [
        {
            "name": f"{finding.stage}.{finding.check_name}",
            "status": _report_status_from_finding(finding.status),
            "message": _message_for_finding(finding),
            "evidence": finding.evidence,
        }
        for finding in findings
    ]
    warnings = [
        _message_for_finding(finding)
        for finding in findings
        if finding.status == "warning"
    ]
    failures = [
        {
            "name": f"{finding.stage}.{finding.check_name}",
            "message": _message_for_finding(finding),
            "suggestion": finding.suggested_fix,
            "evidence": finding.evidence,
        }
        for finding in findings
        if finding.status == "failed"
    ]
    stage_summary = _summarize_by_stage(findings)
    report = {
        "schema_version": "0.1",
        "status": _report_status_from_findings(findings),
        "spec_path": spec_path,
        "checks": checks,
        "warnings": warnings,
        "failures": failures,
        "artifacts": artifact_paths or [],
        "validator_results": [finding.to_dict() for finding in findings],
        "stage_summary": stage_summary,
    }
    _validate_report_schema(report)
    return report


def validate_shape_stage(character_spec: dict[str, Any], pipeline_spec: dict[str, Any]) -> list[ValidatorFinding]:
    parts = character_spec.get("parts", [])
    body = character_spec.get("body_proportions", {})
    stage = pipeline_spec.get("shape_stage", {})
    return [
        ValidatorFinding(
            status="pass" if len(parts) >= 2 else "failed",
            stage="shape",
            check_name="silhouette",
            evidence={"part_count": len(parts)},
            suggested_fix="Add missing primary parts to character_spec.parts.",
            retryable=True,
        ),
        ValidatorFinding(
            status="pass" if float(body.get("head_count", 0)) > 0 else "failed",
            stage="shape",
            check_name="ratio",
            evidence={"head_count": body.get("head_count")},
            suggested_fix="Set valid body proportions before rebuilding the shape stage.",
            retryable=True,
        ),
        ValidatorFinding(
            status="pass" if "shape_symmetry" in stage.get("validators", []) else "warning",
            stage="shape",
            check_name="symmetry",
            evidence={"validators": stage.get("validators", [])},
            suggested_fix="Add shape_symmetry validator to shape_stage.",
            retryable=False,
        ),
    ]


def validate_look_stage(character_spec: dict[str, Any], pipeline_spec: dict[str, Any]) -> list[ValidatorFinding]:
    look_spec = character_spec.get("look_spec", {})
    materials = look_spec.get("materials", [])
    textures = look_spec.get("textures", [])
    stage = pipeline_spec.get("look_stage", {})
    return [
        ValidatorFinding(
            status="pass" if materials else "failed",
            stage="look",
            check_name="color",
            evidence={"material_count": len(materials)},
            suggested_fix="Add material presets to look_spec.materials.",
            retryable=True,
        ),
        ValidatorFinding(
            status="pass" if textures else "warning",
            stage="look",
            check_name="pattern_placement",
            evidence={"texture_count": len(textures)},
            suggested_fix="Add texture definitions for patterned surfaces.",
            retryable=True,
        ),
        ValidatorFinding(
            status="pass" if "look_texture_uv" in stage.get("validators", []) else "failed",
            stage="look",
            check_name="texture_uv_integrity",
            evidence={"validators": stage.get("validators", [])},
            suggested_fix="Add look_texture_uv validator to look_stage.",
            retryable=True,
        ),
    ]


def validate_rig_stage(character_spec: dict[str, Any], pipeline_spec: dict[str, Any]) -> list[ValidatorFinding]:
    rig_spec = character_spec.get("rig_spec", {})
    required_bones = rig_spec.get("required_bones", [])
    stage = pipeline_spec.get("rig_stage", {})
    return [
        ValidatorFinding(
            status="pass" if rig_spec.get("template") else "failed",
            stage="rig",
            check_name="hierarchy",
            evidence={"template": rig_spec.get("template")},
            suggested_fix="Select a rig template before running rig_stage.",
            retryable=True,
        ),
        ValidatorFinding(
            status="pass" if len(required_bones) >= 6 else "failed",
            stage="rig",
            check_name="naming",
            evidence={"required_bones": required_bones},
            suggested_fix="Define the minimum required bones in rig_spec.required_bones.",
            retryable=True,
        ),
        ValidatorFinding(
            status="pass" if "rig_fit" in stage.get("validators", []) else "warning",
            stage="rig",
            check_name="fit",
            evidence={"validators": stage.get("validators", [])},
            suggested_fix="Add rig_fit validator to rig_stage.",
            retryable=False,
        ),
    ]


def validate_expression_stage(
    character_spec: dict[str, Any],
    pipeline_spec: dict[str, Any],
) -> list[ValidatorFinding]:
    expression_spec = character_spec.get("expression_spec", {})
    expressions = expression_spec.get("required_expressions", [])
    stage = pipeline_spec.get("expression_stage", {})
    return [
        ValidatorFinding(
            status="pass" if expressions else "failed",
            stage="expression",
            check_name="key_coverage",
            evidence={"required_expressions": expressions},
            suggested_fix="Declare the required expressions before generating shape keys.",
            retryable=True,
        ),
        ValidatorFinding(
            status="pass" if "blink" in expressions else "warning",
            stage="expression",
            check_name="deformation_correctness",
            evidence={"required_expressions": expressions},
            suggested_fix="Include blink as a baseline facial deformation check.",
            retryable=True,
        ),
        ValidatorFinding(
            status="pass" if "expression_restore" in stage.get("validators", []) else "failed",
            stage="expression",
            check_name="neutral_restore",
            evidence={"validators": stage.get("validators", [])},
            suggested_fix="Add expression_restore validator to expression_stage.",
            retryable=True,
        ),
    ]


def validate_weight_stage(character_spec: dict[str, Any], pipeline_spec: dict[str, Any]) -> list[ValidatorFinding]:
    pose_test_spec = character_spec.get("pose_test_spec", {})
    pose_tests = pose_test_spec.get("required_pose_tests", [])
    stage = pipeline_spec.get("weight_stage", {})
    return [
        ValidatorFinding(
            status="pass" if pose_tests else "failed",
            stage="weight",
            check_name="joint_deformation",
            evidence={"required_pose_tests": pose_tests},
            suggested_fix="Declare required pose tests before weight validation.",
            retryable=True,
        ),
        ValidatorFinding(
            status="pass" if pose_test_spec.get("base_pose") in {"t_pose", "a_pose"} else "failed",
            stage="weight",
            check_name="clipping",
            evidence={"base_pose": pose_test_spec.get("base_pose")},
            suggested_fix="Use a supported base pose for weight validation.",
            retryable=True,
        ),
        ValidatorFinding(
            status="pass" if "weight_symmetry" in stage.get("validators", []) else "warning",
            stage="weight",
            check_name="left_right_consistency",
            evidence={"validators": stage.get("validators", [])},
            suggested_fix="Add weight_symmetry validator to weight_stage.",
            retryable=False,
        ),
    ]


def _report_status_from_findings(findings: list[ValidatorFinding]) -> str:
    statuses = {finding.status for finding in findings}
    if "failed" in statuses:
        return "failed"
    if "warning" in statuses:
        return "warning"
    return "ok"


def _report_status_from_finding(status: str) -> str:
    if status == "pass":
        return "ok"
    if status == "warning":
        return "warning"
    return "failed"


def _message_for_finding(finding: ValidatorFinding) -> str:
    return f"{finding.stage} validator '{finding.check_name}' returned {finding.status}."


def _summarize_by_stage(findings: list[ValidatorFinding]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    stage_order = ["shape", "look", "rig", "expression", "weight"]
    for stage_name in stage_order:
        stage_findings = [finding for finding in findings if finding.stage == stage_name]
        summary.append(
            {
                "stage": stage_name,
                "status": _report_status_from_findings(stage_findings),
                "total_checks": len(stage_findings),
                "failed_checks": len([finding for finding in stage_findings if finding.status == "failed"]),
                "warning_checks": len([finding for finding in stage_findings if finding.status == "warning"]),
            }
        )
    return summary


def _validate_report_schema(report: dict[str, Any]) -> None:
    schema = json.loads(VALIDATION_REPORT_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=report, schema=schema)
