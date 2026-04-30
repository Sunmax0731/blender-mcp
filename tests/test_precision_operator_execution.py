from __future__ import annotations

import json
import sys
from types import SimpleNamespace
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
    assert result["data"]["confirm_required"] is True
    assert result["data"]["parameters"]["target_count"] == 8000
    assert result["data"]["parameters"]["preserve_boundary"] is True
    assert result["data"]["safety_actions"]


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


def test_destructive_operator_requires_confirm_before_execute():
    result = run_approved_addon_operator(
        "object.example_retopology",
        registry_path=REGISTRY,
        dry_run=False,
        confirm=False,
    )

    assert result["success"] is False
    assert result["error"]["code"] == "confirmation_required"
    assert result["data"]["backup_required"] is True


def test_execute_operator_creates_backup_when_confirmed(tmp_path, monkeypatch):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "approved_addons": [
                    {
                        "module": "smoke_addon",
                        "allowed_operations": ["retopology"],
                        "operators": [
                            {
                                "idname": "object.example_retopology",
                                "context": {
                                    "mode": "OBJECT",
                                    "requires_active_object": True,
                                    "requires_selected_objects": True,
                                },
                                "destructive": True,
                                "backup_required": True,
                                "property_map": {"target_face_count": "target_count"},
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    fake_bpy = _make_fake_bpy()
    monkeypatch.setitem(sys.modules, "bpy", fake_bpy)

    result = run_approved_addon_operator(
        "object.example_retopology",
        parameters={"target_object": "Cube", "target_face_count": 1200},
        registry_path=registry_path,
        dry_run=False,
        confirm=True,
    )

    assert result["success"] is True
    assert result["data"]["backup"]["created"] is True
    assert result["data"]["backup"]["source"] == "Cube"
    assert result["data"]["result"] == ["FINISHED"]
    assert fake_bpy.ops.object.example_retopology.calls == [
        {"target_object": "Cube", "target_count": 1200}
    ]


class _FakeObject:
    def __init__(self, name: str) -> None:
        self.name = name
        self.mode = "OBJECT"
        self.data = SimpleNamespace(copy=lambda: SimpleNamespace())
        self.hide_viewport = False
        self.hide_render = False

    def copy(self):
        return _FakeObject(f"{self.name}_copy")


class _FakeOperator:
    def __init__(self) -> None:
        self.calls = []

    def poll(self) -> bool:
        return True

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return {"FINISHED"}


class _FakeObjectMap(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class _FakeCollectionObjects:
    def __init__(self, objects: _FakeObjectMap) -> None:
        self.objects = objects

    def link(self, obj: _FakeObject) -> None:
        self.objects[obj.name] = obj


def _make_fake_bpy():
    cube = _FakeObject("Cube")
    objects = _FakeObjectMap({"Cube": cube})
    return SimpleNamespace(
        context=SimpleNamespace(
            active_object=cube,
            selected_objects=[cube],
            collection=SimpleNamespace(objects=_FakeCollectionObjects(objects)),
        ),
        data=SimpleNamespace(objects=objects),
        ops=SimpleNamespace(object=SimpleNamespace(example_retopology=_FakeOperator())),
    )
