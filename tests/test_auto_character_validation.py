from __future__ import annotations

from blender_precision_mcp.auto_character import build_pipeline_spec
from blender_precision_mcp.auto_character import normalize_prompt_to_character_spec
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
