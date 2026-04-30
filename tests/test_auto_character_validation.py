from __future__ import annotations

from blender_precision_mcp.auto_character import build_pipeline_spec
from blender_precision_mcp.auto_character import normalize_prompt_to_character_spec
import blender_precision_mcp.auto_character_validation as auto_character_validation
from blender_precision_mcp.auto_character_validation import ValidatorFinding
from blender_precision_mcp.auto_character_validation import run_auto_fix_retry_loop
from blender_precision_mcp.auto_character_validation import validate_auto_character


def test_validate_auto_character_returns_stage_summary_and_validator_results():
    prompt = "Create a stylized humanoid character with blue jacket and short hair."
    character_spec = normalize_prompt_to_character_spec(prompt)
    pipeline_spec = build_pipeline_spec(
        prompt,
        character_spec,
        run_directory="outputs/auto-character/humanoid-run",
    )

    report = validate_auto_character(
        character_spec,
        pipeline_spec,
        artifact_paths=["validation/final_validation_report.json"],
    )

    assert report["status"] == "ok"
    assert len(report["validator_results"]) == 15
    assert len(report["stage_summary"]) == 5
    assert report["stage_summary"][0]["stage"] == "shape"
    assert all(item["status"] == "ok" for item in report["stage_summary"])
    assert report["artifacts"] == ["validation/final_validation_report.json"]


def test_validate_auto_character_reports_failures_and_warnings():
    prompt = "Create a creature beast with green patterned skin."
    character_spec = normalize_prompt_to_character_spec(prompt)
    pipeline_spec = build_pipeline_spec(
        prompt,
        character_spec,
        run_directory="outputs/auto-character/creature-run",
    )

    character_spec["look_spec"]["materials"] = []
    pipeline_spec["look_stage"]["validators"] = ["look_color"]
    pipeline_spec["expression_stage"]["validators"] = ["expression_coverage"]
    pipeline_spec["weight_stage"]["validators"] = ["weight_joint_deform"]

    report = validate_auto_character(character_spec, pipeline_spec)

    assert report["status"] == "failed"
    failure_names = {failure["name"] for failure in report["failures"]}
    assert "look.color" in failure_names
    assert "look.texture_uv_integrity" in failure_names
    assert "expression.neutral_restore" in failure_names
    assert any(result["status"] == "warning" for result in report["validator_results"])
    assert any(stage["stage"] == "look" and stage["status"] == "failed" for stage in report["stage_summary"])


def test_run_auto_fix_retry_loop_resolves_retryable_stage_failures():
    prompt = "Create a creature beast with green patterned skin."
    character_spec = normalize_prompt_to_character_spec(prompt)
    pipeline_spec = build_pipeline_spec(
        prompt,
        character_spec,
        run_directory="outputs/auto-character/creature-run",
    )

    character_spec["look_spec"]["materials"] = []
    pipeline_spec["look_stage"]["validators"] = ["look_color"]
    pipeline_spec["expression_stage"]["validators"] = ["expression_coverage"]

    fixed_spec, fixed_pipeline, retry_trace = run_auto_fix_retry_loop(character_spec, pipeline_spec)
    final_report = validate_auto_character(fixed_spec, fixed_pipeline)

    look_trace = next(item for item in retry_trace["stage_retry_trace"] if item["stage"] == "look")
    expression_trace = next(item for item in retry_trace["stage_retry_trace"] if item["stage"] == "expression")

    assert look_trace["stopping_reason"] == "resolved"
    assert expression_trace["stopping_reason"] == "resolved"
    assert look_trace["improvement"]["resolved_failed_checks"] >= 1
    assert final_report["status"] == "ok"


def test_run_auto_fix_retry_loop_stops_on_non_retryable_failure(monkeypatch):
    prompt = "Create a stylized humanoid character with blue jacket and short hair."
    character_spec = normalize_prompt_to_character_spec(prompt)
    pipeline_spec = build_pipeline_spec(
        prompt,
        character_spec,
        run_directory="outputs/auto-character/humanoid-run",
    )

    original_stage_findings = auto_character_validation._stage_findings

    def fake_stage_findings(stage_name, _character_spec, _pipeline_spec):
        if stage_name == "look":
            return [
                ValidatorFinding(
                    status="failed",
                    stage="look",
                    check_name="manual_override_required",
                    evidence={},
                    suggested_fix="Manual repair required.",
                    retryable=False,
                )
            ]
        return original_stage_findings(stage_name, _character_spec, _pipeline_spec)

    monkeypatch.setattr(
        "blender_precision_mcp.auto_character_validation._stage_findings",
        fake_stage_findings,
    )

    _fixed_spec, _fixed_pipeline, retry_trace = run_auto_fix_retry_loop(character_spec, pipeline_spec)
    look_trace = next(item for item in retry_trace["stage_retry_trace"] if item["stage"] == "look")

    assert look_trace["stopping_reason"] == "non_retryable_failed"
    assert retry_trace["final_failure_contract"]["status"] == "failed"


def test_run_auto_fix_retry_loop_keeps_retryable_failure_trace_when_no_fix_is_available(monkeypatch):
    prompt = "Create a stylized humanoid character with blue jacket and short hair."
    character_spec = normalize_prompt_to_character_spec(prompt)
    pipeline_spec = build_pipeline_spec(
        prompt,
        character_spec,
        run_directory="outputs/auto-character/humanoid-run",
    )

    original_stage_findings = auto_character_validation._stage_findings
    original_apply_stage_auto_fixes = auto_character_validation._apply_stage_auto_fixes

    def fake_stage_findings(stage_name, _character_spec, _pipeline_spec):
        if stage_name == "look":
            return [
                ValidatorFinding(
                    status="failed",
                    stage="look",
                    check_name="custom_retryable_failure",
                    evidence={"source": "test"},
                    suggested_fix="Automatic retry was attempted but no fix is available.",
                    retryable=True,
                )
            ]
        return original_stage_findings(stage_name, _character_spec, _pipeline_spec)

    monkeypatch.setattr(
        "blender_precision_mcp.auto_character_validation._stage_findings",
        fake_stage_findings,
    )
    monkeypatch.setattr(
        "blender_precision_mcp.auto_character_validation._apply_stage_auto_fixes",
        lambda stage_name, character_spec, pipeline_spec, failed_findings: []
        if stage_name == "look"
        else original_apply_stage_auto_fixes(
            stage_name,
            character_spec,
            pipeline_spec,
            failed_findings,
        ),
    )

    _fixed_spec, _fixed_pipeline, retry_trace = run_auto_fix_retry_loop(character_spec, pipeline_spec)
    look_trace = next(item for item in retry_trace["stage_retry_trace"] if item["stage"] == "look")

    assert look_trace["stopping_reason"] == "no_fix_available"
    assert look_trace["attempts"][-1]["failed_checks"] == ["look.custom_retryable_failure"]
    assert retry_trace["final_failure_contract"]["status"] == "failed"
    assert retry_trace["final_failure_contract"]["blocking_stages"] == ["look"]
    assert retry_trace["final_failure_contract"]["remaining_failures"][0]["retryable"] is True
    assert retry_trace["final_failure_contract"]["non_retryable_failures"] == []
