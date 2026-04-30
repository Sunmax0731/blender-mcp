from __future__ import annotations

from pathlib import Path

from blender_precision_mcp.operator_execution import apply_retopology
from blender_precision_mcp.operator_execution import prepare_operator_context
from blender_precision_mcp.operator_execution import run_approved_addon_operator


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "templates" / "precision" / "addon_registry.yaml"


def test_run_approved_addon_operator_dry_run_maps_properties():
    result = run_approved_addon_operator(
        "object.example_retopology",
        parameters={"target_face_count": 8000, "preserve_boundaries": True},
        registry_path=REGISTRY,
        dry_run=True,
    )

    assert result["success"] is True
    assert result["data"]["dry_run"] is True
    assert result["data"]["destructive"] is True
    assert result["data"]["backup_required"] is True
    assert result["data"]["parameters"]["target_count"] == 8000
    assert result["data"]["parameters"]["preserve_boundary"] is True


def test_run_unapproved_operator_is_rejected():
    result = run_approved_addon_operator(
        "object.unapproved_operator",
        registry_path=REGISTRY,
        dry_run=True,
    )

    assert result["success"] is False
    assert result["error"]["code"] == "not_approved"


def test_prepare_operator_context_reports_blender_unavailable_without_bpy():
    result = prepare_operator_context("object.example_retopology", REGISTRY)

    assert result["success"] is False
    assert result["error"]["code"] == "blender_unavailable"


def test_apply_retopology_uses_approved_operation():
    result = apply_retopology(
        target_object="example_body",
        target_face_count=8000,
        registry_path=REGISTRY,
        dry_run=True,
    )

    assert result["success"] is True
    assert result["data"]["operator"] == "object.example_retopology"
