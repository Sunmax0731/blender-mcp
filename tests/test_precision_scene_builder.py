from __future__ import annotations

import json
from pathlib import Path

from blender_precision_mcp.scene_builder import assign_materials_from_spec
from blender_precision_mcp.scene_builder import create_or_update_scene_from_spec
from blender_precision_mcp.scene_builder import create_parametric_object


ROOT = Path(__file__).resolve().parents[1]
MODEL_SPEC = ROOT / "templates" / "precision" / "model_spec.yaml"


def test_create_parametric_object_dry_run_returns_operation_plan():
    result = create_parametric_object(
        {
            "name": "example_sphere",
            "type": "sphere",
            "dimensions": [1.0, 1.0, 1.0],
            "location": [0.0, 0.0, 0.5],
            "rotation": [0.0, 0.0, 0.0],
            "material": "mat_default",
            "requirements": {"bevel_radius": 0.02},
        },
        dry_run=True,
    )

    assert result["success"] is True
    assert result["data"]["dry_run"] is True
    assert result["data"]["operations"][0]["name"] == "example_sphere"
    assert result["data"]["operations"][0]["type"] == "sphere"
    assert result["data"]["operations"][0]["bevel_radius"] == 0.02


def test_create_parametric_object_rejects_unsupported_type():
    result = create_parametric_object(
        {
            "name": "unsafe_object",
            "type": "python_script",
        },
        dry_run=True,
    )

    assert result["success"] is False
    assert result["error"]["code"] == "unsupported_object_type"
    assert "python_script" in result["error"]["message"]


def test_create_parametric_object_execute_reports_blender_unavailable():
    result = create_parametric_object(
        {
            "name": "example_box",
            "type": "box",
        },
        dry_run=False,
    )

    assert result["success"] is False
    assert result["error"]["code"] == "blender_unavailable"
    assert result["data"]["operations"][0]["name"] == "example_box"


def test_create_or_update_scene_from_spec_dry_run_writes_report(tmp_path):
    output_path = tmp_path / "scene_build_report.json"

    result = create_or_update_scene_from_spec(
        spec_path=MODEL_SPEC,
        output_path=output_path,
        dry_run=True,
    )

    assert result["success"] is True
    assert result["data"]["dry_run"] is True
    assert output_path.exists()
    saved = json.loads(output_path.read_text(encoding="utf-8"))
    operation_names = {operation["action"] for operation in saved["operations"]}
    assert "create_or_update_object" in operation_names
    assert "ensure_camera" in operation_names
    assert "ensure_light" in operation_names


def test_assign_materials_from_spec_dry_run_returns_assignment_plan():
    result = assign_materials_from_spec(MODEL_SPEC, dry_run=True)

    assert result["success"] is True
    assert result["data"]["dry_run"] is True
    assert result["data"]["operations"] == [
        {
            "action": "assign_material",
            "object": "example_body",
            "material": "mat_default",
        }
    ]
