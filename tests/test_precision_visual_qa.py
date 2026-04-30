from __future__ import annotations

import json
from pathlib import Path

from blender_precision_mcp.visual_qa import build_review_capture_plan
from blender_precision_mcp.visual_qa import capture_review_views


ROOT = Path(__file__).resolve().parents[1]
MODEL_SPEC = ROOT / "templates" / "precision" / "model_spec.yaml"


def test_build_review_capture_plan_uses_spec_views(tmp_path):
    plan = build_review_capture_plan(MODEL_SPEC, output_dir=tmp_path)

    assert plan.output_dir == tmp_path
    assert plan.views == ("front", "side", "top", "perspective")
    assert plan.resolution == (1280, 1280)
    assert plan.manifest_path == tmp_path / "review_manifest.json"


def test_capture_review_views_dry_run_writes_manifest(tmp_path):
    result = capture_review_views(
        spec_path=MODEL_SPEC,
        output_dir=tmp_path,
        views=("front", "top"),
        dry_run=True,
    )

    manifest_path = Path(result["manifest_path"])
    saved = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result["status"] == "planned"
    assert saved["views"] == ["front", "top"]
    assert saved["artifacts"] == [str(tmp_path / "front.png"), str(tmp_path / "top.png")]
