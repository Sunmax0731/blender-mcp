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


def test_validate_model_spec_checks_live_scene_snapshot():
    snapshot = {
        "available": True,
        "scene_name": "Scene",
        "objects": [
            {
                "name": "example_body",
                "type": "MESH",
                "dimensions": [1.2, 0.4, 0.8],
                "location": [0.0, 0.0, 0.4],
                "materials": ["mat_default"],
                "visible": True,
            }
        ],
        "materials": ["mat_default"],
        "camera": "Camera",
        "lights": ["Key_Light"],
    }

    report = validate_model_spec(MODEL_SPEC, live_scene=True, live_scene_snapshot=snapshot)

    assert report["status"] == "ok"
    assert report["live_scene"]["available"] is True
    assert any(check["name"] == "live_scene.objects.example_body.dimensions" for check in report["checks"])
    assert any(check["name"] == "live_scene.camera" for check in report["checks"])
    assert any(check["name"] == "live_scene.lights" for check in report["checks"])


def test_validate_model_spec_reports_live_scene_measurement_failures():
    snapshot = {
        "available": True,
        "scene_name": "Scene",
        "objects": [
            {
                "name": "example_body",
                "type": "MESH",
                "dimensions": [1.5, 0.4, 0.8],
                "location": [0.2, 0.0, 0.4],
                "materials": ["wrong_material"],
                "visible": True,
            }
        ],
        "materials": ["wrong_material"],
        "camera": None,
        "lights": [],
    }

    report = validate_model_spec(MODEL_SPEC, live_scene=True, live_scene_snapshot=snapshot)

    assert report["status"] == "failed"
    failure_names = {failure["name"] for failure in report["failures"]}
    assert "live_scene.objects.example_body.dimensions" in failure_names
    assert "live_scene.objects.example_body.location" in failure_names
    assert "live_scene.objects.example_body.material" in failure_names
    assert "live_scene.materials.mat_default" in failure_names
    assert "live_scene.camera" in failure_names
    assert "live_scene.lights" in failure_names


def test_validate_model_spec_reports_extra_objects_when_forbidden(tmp_path):
    strict_spec = tmp_path / "strict_model_spec.json"
    strict_spec.write_text(
        json.dumps(
            {
                "schema_version": "0.2",
                "scene": {},
                "objects": [
                    {
                        "name": "example_body",
                        "type": "box",
                        "dimensions": [1.2, 0.4, 0.8],
                        "location": [0.0, 0.0, 0.4],
                        "material": "mat_default",
                    }
                ],
                "materials": [
                    {
                        "name": "mat_default",
                        "type": "principled",
                        "color": [0.8, 0.8, 0.8, 1.0],
                    }
                ],
                "validation": {
                    "require_camera": True,
                    "require_lights": True,
                    "forbid_extra_objects": True,
                    "allowed_extra_objects": ["RoundBuddy_Rig"],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    snapshot = {
        "available": True,
        "scene_name": "Scene",
        "objects": [
            {
                "name": "example_body",
                "type": "MESH",
                "dimensions": [1.2, 0.4, 0.8],
                "location": [0.0, 0.0, 0.4],
                "materials": ["mat_default"],
                "visible": True,
            },
            {
                "name": "Cube",
                "type": "MESH",
                "dimensions": [2.0, 2.0, 2.0],
                "location": [0.0, 0.0, 0.0],
                "materials": ["Material"],
                "visible": True,
            },
            {
                "name": "RoundBuddy_Rig",
                "type": "ARMATURE",
                "dimensions": [0.1, 0.1, 1.0],
                "location": [0.0, 0.0, 0.0],
                "materials": [],
                "visible": True,
            },
        ],
        "materials": ["mat_default", "Material"],
        "camera": "Camera",
        "lights": ["Light"],
    }

    report = validate_model_spec(strict_spec, live_scene=True, live_scene_snapshot=snapshot)

    assert report["status"] == "failed"
    assert any(failure["name"] == "live_scene.extra_objects" for failure in report["failures"])


def test_validate_model_spec_returns_structured_error_when_blender_is_unavailable():
    report = validate_model_spec(MODEL_SPEC, live_scene=True)

    assert report["status"] == "failed"
    assert report["live_scene"]["available"] is False
    assert report["live_scene"]["error"]["code"] == "BLENDER_NOT_AVAILABLE"
    assert any(failure["name"] == "live_scene" for failure in report["failures"])
