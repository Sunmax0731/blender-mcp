from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXECUTOR_PATH = ROOT / "blender_addon" / "blender_mcp" / "services" / "command_executor.py"


def _load_execute_command():
    spec = importlib.util.spec_from_file_location("command_executor", EXECUTOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.execute_command


execute_command = _load_execute_command()


class FakeObject:
    def __init__(
        self,
        name: str,
        obj_type: str = "MESH",
        selected: bool = False,
        visible: bool = True,
        location=(0.0, 0.0, 0.0),
        rotation_euler=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0),
    ):
        self.name = name
        self.type = obj_type
        self._selected = selected
        self._visible = visible
        self.location = tuple(location)
        self.rotation_euler = tuple(rotation_euler)
        self.scale = tuple(scale)

    def select_get(self):
        return self._selected

    def select_set(self, value):
        self._selected = bool(value)

    def visible_get(self):
        return self._visible


class FakeObjects(list):
    def get(self, target_name):
        for obj in self:
            if obj.name == target_name:
                return obj
        return None


class FakeMeshOps:
    def __init__(self, bpy_module):
        self._bpy = bpy_module

    def primitive_cube_add(self, location, rotation, scale):
        obj = FakeObject("Cube", location=location, rotation_euler=rotation, scale=scale)
        self._bpy.data.objects.append(obj)
        self._bpy.context.active_object = obj


class FakeObjectOps:
    def __init__(self, bpy_module):
        self._bpy = bpy_module

    def select_all(self, action):
        for obj in self._bpy.data.objects:
            obj.select_set(False)

    def delete(self):
        active = self._bpy.context.view_layer.objects.active
        self._bpy.data.objects[:] = [obj for obj in self._bpy.data.objects if obj is not active]


class FakeContextObjects:
    def __init__(self):
        self.active = None


class FakeContext:
    def __init__(self):
        self.active_object = None
        self.view_layer = type("ViewLayer", (), {"objects": FakeContextObjects()})()


class FakeBpy:
    def __init__(self):
        self.data = type(
            "Data",
            (),
            {"objects": FakeObjects([FakeObject("Cube"), FakeObject("Lamp", "LIGHT")])},
        )()
        self.context = FakeContext()
        self.ops = type("Ops", (), {})()
        self.ops.mesh = FakeMeshOps(self)
        self.ops.object = FakeObjectOps(self)


def test_create_and_list_objects():
    bpy = FakeBpy()
    create_result = execute_command(
        {
            "requestId": "req-local-1",
            "action": "create_primitive",
            "params": {"type": "CUBE", "name": "Block_A"},
            "requiresConfirmation": False,
        },
        bpy,
    )
    assert create_result["success"] is True
    assert create_result["data"]["objectName"] == "Block_A"

    list_result = execute_command(
        {
            "requestId": "req-local-2",
            "action": "list_objects",
            "params": {"namePrefix": "B", "selectedOnly": False, "typeFilter": ["MESH"]},
            "requiresConfirmation": False,
        },
        bpy,
    )
    assert list_result["success"] is True
    assert list_result["data"]["objects"][0]["name"] == "Block_A"


def test_transform_object_absolute_and_delta():
    bpy = FakeBpy()
    absolute_result = execute_command(
        {
            "requestId": "req-local-3",
            "action": "transform_object",
            "params": {
                "targetObjectName": "Cube",
                "location": [1, 2, 3],
                "rotationEuler": [0.1, 0.2, 0.3],
                "scale": [2, 3, 4],
                "mode": "absolute",
            },
            "requiresConfirmation": False,
        },
        bpy,
    )
    assert absolute_result["success"] is True
    cube = bpy.data.objects.get("Cube")
    assert cube.location == (1.0, 2.0, 3.0)
    assert cube.scale == (2.0, 3.0, 4.0)

    delta_result = execute_command(
        {
            "requestId": "req-local-4",
            "action": "transform_object",
            "params": {
                "targetObjectName": "Cube",
                "location": [1, 0, -1],
                "rotationEuler": [0.1, 0.0, 0.0],
                "scale": [0.5, 1.0, 2.0],
                "mode": "delta",
            },
            "requiresConfirmation": False,
        },
        bpy,
    )
    assert delta_result["success"] is True
    assert cube.location == (2.0, 2.0, 2.0)
    assert cube.scale == (1.0, 3.0, 8.0)


def test_delete_object_requires_confirmation():
    bpy = FakeBpy()
    confirm_result = execute_command(
        {
            "requestId": "req-local-5",
            "action": "delete_object",
            "params": {"targetObjectName": "Cube"},
            "requiresConfirmation": True,
        },
        bpy,
    )
    assert confirm_result["error"]["code"] == "CONFIRMATION_REQUIRED"

    delete_result = execute_command(
        {
            "requestId": "req-local-6",
            "action": "delete_object",
            "params": {"targetObjectName": "Cube", "_approved": True},
            "requiresConfirmation": True,
        },
        bpy,
    )
    assert delete_result["success"] is True
    assert bpy.data.objects.get("Cube") is None
