from __future__ import annotations

import json

from blender_precision_mcp.auto_character_workflow import run_auto_character_workflow
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


def test_run_auto_character_workflow_reports_fallback_when_live_is_requested_without_bpy(tmp_path):
    output_dir = tmp_path / "live-requested"

    summary = run_auto_character_workflow(
        "Create a stylized human character with blue jacket and short hair.",
        output_dir=output_dir,
        live=True,
    )

    assert summary["mode"] == "live"
    assert summary["execution_mode"] == "fallback_required"
    assert summary["status"] == "warning"
    assert summary["fallback"]["required"] is True
    assert summary["fallback"]["route"] == "blender_background"
    assert summary["error"]["code"] == "blender_unavailable"

    report = json.loads(
        (output_dir / "validation" / "final_validation_report.json").read_text(encoding="utf-8")
    )
    assert report["execution"]["mode"] == "fallback_required"
    assert report["execution"]["error"]["code"] == "blender_unavailable"


def test_run_auto_character_workflow_writes_run_manifest_for_traceability(tmp_path):
    output_dir = tmp_path / "traceability"

    summary = run_auto_character_dry_run(
        "Create a chibi hero with pink cape and expressive talking face.",
        output_dir=output_dir,
    )

    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))

    assert summary["run_manifest_path"] == str(output_dir / "run_manifest.json")
    assert manifest["character_type"] == "chibi"
    assert manifest["final_status"] == "ok"
    assert manifest["artifact_paths"]["prompt"] == str(output_dir / "prompt.txt")
    assert manifest["artifact_paths"]["character_spec"] == str(output_dir / "character_spec.yaml")
    assert manifest["artifact_paths"]["pipeline_spec"] == str(output_dir / "pipeline_spec.yaml")
    assert manifest["artifact_paths"]["validation_report"] == str(
        output_dir / "validation" / "final_validation_report.json"
    )
    assert manifest["validation_trace"]["stage_summary_ref"] == manifest["artifact_paths"]["validation_report"]
    assert manifest["validation_trace"]["validator_results_ref"] == manifest["artifact_paths"]["validation_report"]
    assert manifest["fallbacks_used"] == []


def test_run_auto_character_workflow_copies_base_asset_artifacts_and_traceability(tmp_path):
    output_dir = tmp_path / "base-asset"
    validation_dir = output_dir / "input-validation"
    validation_dir.mkdir(parents=True, exist_ok=True)

    base_asset_manifest = {
        "status": "ok",
        "source_file_path": "D:/base/BaseAvatar.blend",
        "main_mesh_object": "Body",
        "face_mesh_object": "Face",
    }
    adaptation_plan = {
        "status": "ok",
        "reuse_targets": ["mesh", "rig", "shape_keys"],
        "regenerate_targets": ["materials_and_textures"],
        "target_objects": {
            "main_mesh_object": "Body",
            "face_mesh_object": "Face",
            "armature_objects": ["Armature"],
            "material_names": ["Skin"],
        },
    }
    manifest_path = validation_dir / "base_asset_manifest.json"
    adaptation_plan_path = validation_dir / "adaptation_plan.json"
    manifest_path.write_text(json.dumps(base_asset_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    adaptation_plan_path.write_text(json.dumps(adaptation_plan, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = run_auto_character_dry_run(
        "Create a stylized human character with blue jacket and short hair.",
        output_dir=output_dir,
        base_asset_manifest_path=manifest_path,
        adaptation_plan_path=adaptation_plan_path,
    )

    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
    character_spec = (output_dir / "character_spec.yaml").read_text(encoding="utf-8")
    pipeline_spec = (output_dir / "pipeline_spec.yaml").read_text(encoding="utf-8")

    assert summary["base_asset_enabled"] is True
    assert (output_dir / "validation" / "base_asset_manifest.json").exists()
    assert (output_dir / "validation" / "adaptation_plan.json").exists()
    assert manifest["base_asset_trace"]["enabled"] is True
    assert manifest["base_asset_trace"]["source_file_path"] == "D:/base/BaseAvatar.blend"
    assert manifest["artifact_paths"]["base_asset_manifest"].endswith("validation\\base_asset_manifest.json")
    assert "base_asset:" in character_spec
    assert "base_asset_mode: reuse_base_mesh" in pipeline_spec
