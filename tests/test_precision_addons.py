from __future__ import annotations

from pathlib import Path

from blender_precision_mcp.addons import get_addon_status
from blender_precision_mcp.addons import inspect_addon_capabilities
from blender_precision_mcp.addons import list_blender_addons
from blender_precision_mcp.addons import list_registered_operators
from blender_precision_mcp.addons import load_addon_registry


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "templates" / "precision" / "addon_registry.yaml"


def test_load_addon_registry_validates_template():
    registry = load_addon_registry(REGISTRY)

    assert registry["approved_addons"][0]["module"] == "example_retopology_addon"


def test_list_blender_addons_falls_back_to_registry_without_blender():
    result = list_blender_addons(REGISTRY)

    assert result["success"] is True
    assert "example_retopology_addon" in result["data"]["approved_modules"]


def test_get_addon_status_reports_registry_approval():
    result = get_addon_status("example_retopology_addon", REGISTRY)

    assert result["success"] is True
    assert result["data"]["approved"] is True


def test_inspect_addon_capabilities_returns_operator_metadata():
    result = inspect_addon_capabilities("example_retopology_addon", REGISTRY)

    operators = result["data"]["capabilities"][0]["operators"]
    assert operators[0]["idname"] == "object.example_retopology"
    assert operators[0]["backup_required"] is True


def test_list_registered_operators_returns_approved_operator_list():
    result = list_registered_operators(REGISTRY)

    assert result["data"]["operators"][0]["idname"] == "object.example_retopology"
