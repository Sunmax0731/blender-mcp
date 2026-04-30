from __future__ import annotations

import json

from blender_precision_mcp.exporter import export_scene


def test_export_scene_dry_run_writes_manifest(tmp_path):
    spec_path = tmp_path / "model_spec.json"
    manifest_path = tmp_path / "export_manifest.json"
    spec_path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "scene": {},
                "objects": [],
                "validation": {},
                "exports": [
                    {"format": "blend", "path": str(tmp_path / "final.blend")},
                    {"format": "glb", "path": str(tmp_path / "final.glb")},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = export_scene(
        spec_path=spec_path,
        output_manifest_path=manifest_path,
        validation_artifacts=["validation.json"],
        review_artifacts=["review_manifest.json"],
        dry_run=True,
    )

    assert result["success"] is True
    assert result["data"]["dry_run"] is True
    assert [operation["format"] for operation in result["data"]["operations"]] == ["blend", "glb"]
    assert result["data"]["artifacts"]["validation"] == ["validation.json"]
    assert manifest_path.exists()


def test_export_scene_rejects_unsupported_format(tmp_path):
    spec_path = tmp_path / "model_spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "scene": {},
                "objects": [],
                "validation": {},
                "exports": [{"format": "fbx", "path": str(tmp_path / "final.fbx")}],
            }
        ),
        encoding="utf-8",
    )

    result = export_scene(spec_path=spec_path, dry_run=True)

    assert result["success"] is False
    assert result["error"]["code"] == "unsupported_export_format"
    assert result["data"]["supported_formats"] == ["blend", "glb"]


def test_export_scene_execute_reports_blender_unavailable(tmp_path):
    spec_path = tmp_path / "model_spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "scene": {},
                "objects": [],
                "validation": {},
                "exports": [{"format": "blend", "path": str(tmp_path / "final.blend")}],
            }
        ),
        encoding="utf-8",
    )

    result = export_scene(spec_path=spec_path, dry_run=False)

    assert result["success"] is False
    assert result["error"]["code"] == "blender_unavailable"
