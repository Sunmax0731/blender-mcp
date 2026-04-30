from __future__ import annotations

import json

from PIL import Image

from blender_precision_mcp.auto_character_workflow import run_auto_character_dry_run


def test_dry_run_regression_matrix_for_prompt_base_asset_and_image_reference(tmp_path):
    base_asset_manifest_path, adaptation_plan_path = _write_base_asset_inputs(tmp_path)
    image_reference_package_path = _write_image_reference_package(tmp_path)

    cases = [
        {
            "name": "prompt_only",
            "prompt": "Create a stylized human character with blue jacket and short hair.",
            "kwargs": {},
            "expected": {
                "character_type": "humanoid",
                "base_asset_enabled": False,
                "image_reference_enabled": False,
            },
        },
        {
            "name": "base_asset",
            "prompt": "Create a humanoid hero that reuses the existing base avatar.",
            "kwargs": {
                "base_asset_manifest_path": base_asset_manifest_path,
                "adaptation_plan_path": adaptation_plan_path,
            },
            "expected": {
                "character_type": "humanoid",
                "base_asset_enabled": True,
                "image_reference_enabled": False,
            },
        },
        {
            "name": "image_reference",
            "prompt": "Create a humanoid hero with blue jacket and short hair.",
            "kwargs": {
                "image_reference_package_path": image_reference_package_path,
            },
            "expected": {
                "character_type": "humanoid",
                "base_asset_enabled": False,
                "image_reference_enabled": True,
            },
        },
    ]

    for case in cases:
        output_dir = tmp_path / case["name"]
        summary = run_auto_character_dry_run(
            case["prompt"],
            output_dir=output_dir,
            **case["kwargs"],
        )
        manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
        report = json.loads(
            (output_dir / "validation" / "final_validation_report.json").read_text(encoding="utf-8")
        )
        retry_trace = json.loads((output_dir / "validation" / "retry_trace.json").read_text(encoding="utf-8"))
        character_spec = (output_dir / "character_spec.yaml").read_text(encoding="utf-8")
        pipeline_spec = (output_dir / "pipeline_spec.yaml").read_text(encoding="utf-8")

        assert summary["mode"] == "dry_run"
        assert summary["status"] == "ok"
        assert summary["character_type"] == case["expected"]["character_type"]
        assert summary["base_asset_enabled"] is case["expected"]["base_asset_enabled"]
        assert summary["image_reference_enabled"] is case["expected"]["image_reference_enabled"]
        assert report["status"] == "ok"
        assert manifest["artifact_paths"]["retry_trace"].endswith("validation\\retry_trace.json")
        assert manifest["validation_trace"]["retry_trace_ref"] == manifest["artifact_paths"]["retry_trace"]
        assert retry_trace["final_failure_contract"]["status"] == "ok"
        assert len(retry_trace["stage_retry_trace"]) == 5
        assert "hair_preset:" in pipeline_spec
        assert "schema_version:" in character_spec

        if case["expected"]["base_asset_enabled"]:
            assert "base_asset:" in character_spec
            assert "base_asset_mode: reuse_base_mesh" in pipeline_spec
            assert manifest["base_asset_trace"]["enabled"] is True
            assert (output_dir / "validation" / "base_asset_manifest.json").exists()
            assert (output_dir / "validation" / "adaptation_plan.json").exists()
        else:
            assert "base_asset:" not in character_spec
            assert "base_asset_trace" not in manifest

        if case["expected"]["image_reference_enabled"]:
            assert "image_reference:" in character_spec
            assert "image_reference_mode: guided_shape" in pipeline_spec
            assert manifest["image_reference_trace"]["enabled"] is True
            assert (output_dir / "validation" / "image_reference_manifest.json").exists()
        else:
            assert "image_reference_trace" not in manifest


def _write_base_asset_inputs(tmp_path):
    base_asset_dir = tmp_path / "base-asset-inputs"
    base_asset_dir.mkdir(parents=True, exist_ok=True)

    base_asset_manifest = {
        "status": "ok",
        "source_file_path": "D:/base/BaseAvatar.blend",
        "main_mesh_object": "Body",
        "face_mesh_object": "Face",
    }
    adaptation_plan = {
        "status": "ok",
        "reuse_targets": ["mesh", "rig", "shape_keys", "materials_and_textures"],
        "regenerate_targets": [],
        "target_objects": {
            "main_mesh_object": "Body",
            "face_mesh_object": "Face",
            "armature_objects": ["Armature"],
            "material_names": ["Skin"],
        },
    }
    manifest_path = base_asset_dir / "base_asset_manifest.json"
    adaptation_plan_path = base_asset_dir / "adaptation_plan.json"
    manifest_path.write_text(json.dumps(base_asset_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    adaptation_plan_path.write_text(json.dumps(adaptation_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path, adaptation_plan_path


def _write_image_reference_package(tmp_path):
    package_dir = tmp_path / "image-reference-package"
    package_dir.mkdir(parents=True, exist_ok=True)
    _write_reference_image(package_dir / "front.png", body_color=(32, 64, 196, 255), hair_color=(220, 90, 120, 255))
    _write_reference_image(package_dir / "side.png", body_color=(32, 64, 196, 255), hair_color=(220, 90, 120, 255))
    _write_reference_image(
        package_dir / "face_closeup.png",
        body_color=(240, 220, 200, 255),
        hair_color=(220, 90, 120, 255),
    )
    (package_dir / "notes.md").write_text(
        "\n".join(
            [
                "Hair silhouette to preserve: long layered hair",
                "Face features to preserve: large eyes and rounded mouth",
                "Pattern or color placement to preserve: blue jacket with pink trim",
            ]
        ),
        encoding="utf-8",
    )
    return package_dir


def _write_reference_image(path, *, body_color, hair_color):
    image = Image.new("RGBA", (128, 192), (255, 255, 255, 0))
    pixels = image.load()
    for y in range(36, 170):
        for x in range(34, 96):
            pixels[x, y] = body_color
    for y in range(10, 52):
        for x in range(28, 102):
            pixels[x, y] = hair_color
    image.save(path)
