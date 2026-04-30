from __future__ import annotations

from blender_precision_mcp.mesh_quality import _evaluate_mesh_quality
from blender_precision_mcp.mesh_quality import analyze_mesh_quality
from blender_precision_mcp.mesh_quality import apply_mesh_cleanup
from blender_precision_mcp.mesh_quality import validate_retopology_result


def test_analyze_mesh_quality_reports_blender_unavailable():
    result = analyze_mesh_quality(target_objects=["example_body"])

    assert result["success"] is False
    assert result["error"]["code"] == "blender_unavailable"


def test_apply_mesh_cleanup_dry_run_returns_safety_plan():
    result = apply_mesh_cleanup(
        target_object="example_body",
        operations=["delete_loose"],
        dry_run=True,
    )

    assert result["success"] is True
    assert result["data"]["dry_run"] is True
    actions = [operation["action"] for operation in result["data"]["operations"]]
    assert actions == ["backup_object", "confirm", "delete_loose"]


def test_apply_mesh_cleanup_requires_confirm_for_execute():
    result = apply_mesh_cleanup(
        target_object="example_body",
        dry_run=False,
        confirm=False,
    )

    assert result["success"] is False
    assert result["error"]["code"] == "confirmation_required"


def test_apply_mesh_cleanup_execute_reports_blender_unavailable():
    result = apply_mesh_cleanup(
        target_object="example_body",
        dry_run=False,
        confirm=True,
    )

    assert result["success"] is False
    assert result["error"]["code"] == "blender_unavailable"


def test_validate_retopology_result_reports_blender_unavailable():
    result = validate_retopology_result(target_object="example_body")

    assert result["success"] is False
    assert result["error"]["code"] == "blender_unavailable"


def test_evaluate_mesh_quality_thresholds():
    failures = _evaluate_mesh_quality(
        {
            "name": "example_body",
            "non_manifold_edges": 2,
            "loose_vertices": 1,
            "loose_edges": 0,
            "face_count": 120,
            "quad_ratio": 0.25,
        },
        {
            "max_non_manifold_edges": 0,
            "max_loose_vertices": 0,
            "max_loose_edges": 0,
            "max_face_count": 100,
            "min_quad_ratio": 0.5,
        },
    )

    assert [failure["code"] for failure in failures] == [
        "max_non_manifold_edges",
        "max_loose_vertices",
        "max_face_count",
        "min_quad_ratio",
    ]
