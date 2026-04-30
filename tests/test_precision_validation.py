from __future__ import annotations

import json
from pathlib import Path

from blender_precision_mcp.validation import load_model_spec
from blender_precision_mcp.validation import validate_model_spec


ROOT = Path(__file__).resolve().parents[1]
MODEL_SPEC = ROOT / "templates" / "precision" / "model_spec.yaml"


def test_load_model_spec_reads_template():
    spec = load_model_spec(MODEL_SPEC)

    assert spec["schema_version"] == "0.2"
    assert spec["objects"][0]["name"] == "example_body"


def test_validate_model_spec_returns_report_and_artifact(tmp_path):
    output_path = tmp_path / "validation_report.json"

    report = validate_model_spec(MODEL_SPEC, output_path=output_path)

    assert report["status"] == "ok"
    assert report["checks"]
    assert str(output_path) in report["artifacts"]

    saved_report = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved_report["status"] == "ok"
    assert saved_report["spec_path"] == str(MODEL_SPEC)


def test_validate_model_spec_reports_failures(tmp_path):
    bad_spec = tmp_path / "bad_model_spec.yaml"
    bad_spec.write_text(
        "\n".join(
            [
                'schema_version: "0.2"',
                "scene: {}",
                "objects:",
                "  - name: cube",
                "    type: box",
                "    dimensions: [1, 2]",
                "validation:",
                "  require_named_objects: true",
            ]
        ),
        encoding="utf-8",
    )

    report = validate_model_spec(bad_spec)

    assert report["status"] == "failed"
    assert report["failures"]
    assert "suggestion" in report["failures"][0]
