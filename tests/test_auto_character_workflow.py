from __future__ import annotations

import json

from blender_precision_mcp.auto_character_workflow import run_auto_character_dry_run


def test_run_auto_character_dry_run_smoke_for_supported_types(tmp_path):
    cases = [
        ("humanoid", "Create a stylized human character with blue jacket and short hair."),
        ("chibi", "Create a chibi hero with pink cape and expressive talking face."),
        ("creature", "Create a green creature beast with striped tail for animation."),
    ]

    for expected_type, prompt in cases:
        output_dir = tmp_path / expected_type
        summary = run_auto_character_dry_run(prompt, output_dir)

        assert summary["mode"] == "dry_run"
        assert summary["character_type"] == expected_type
        assert summary["status"] == "ok"
        assert (output_dir / "prompt.txt").exists()
        assert (output_dir / "character_spec.yaml").exists()
        assert (output_dir / "pipeline_spec.yaml").exists()
        assert (output_dir / "validation" / "final_validation_report.json").exists()
        assert (output_dir / "dry_run_summary.json").exists()

        report = json.loads(
            (output_dir / "validation" / "final_validation_report.json").read_text(encoding="utf-8")
        )
        assert report["status"] == "ok"
        assert len(report["stage_summary"]) == 5
