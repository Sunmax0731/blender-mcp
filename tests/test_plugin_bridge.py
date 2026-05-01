from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "blender_addon" / "blender_mcp" / "services" / "plugin_bridge.py"


def _load_plugin_bridge_module():
    package_name = "blender_mcp"
    services_name = "blender_mcp.services"
    module_name = "blender_mcp.services.plugin_bridge"

    package = types.ModuleType(package_name)
    package.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp")]
    services = types.ModuleType(services_name)
    services.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp" / "services")]

    sys.modules[package_name] = package
    sys.modules[services_name] = services

    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_inspect_plugin_bridge_reports_ready(monkeypatch):
    module = _load_plugin_bridge_module()

    fake_addon = types.SimpleNamespace(__name__="rodin_bridge", bl_info={"name": "RodinBridge"})
    fake_addon_utils = types.SimpleNamespace(modules=lambda: [fake_addon])
    sys.modules["addon_utils"] = fake_addon_utils

    fake_bpy = types.SimpleNamespace(
        context=types.SimpleNamespace(preferences=types.SimpleNamespace(addons={"rodin_bridge": object()})),
        ops=types.SimpleNamespace(rodin=types.SimpleNamespace(submit=object())),
    )

    result = module.inspect_plugin_bridge(fake_bpy, "rodin")

    assert result["ready"] is True
    assert "ready" in result["summary"]


def test_inspect_plugin_bridge_accepts_rodin_module_hint_from_enabled_addons():
    module = _load_plugin_bridge_module()

    fake_addon_utils = types.SimpleNamespace(modules=lambda: [])
    sys.modules["addon_utils"] = fake_addon_utils

    fake_bpy = types.SimpleNamespace(
        context=types.SimpleNamespace(preferences=types.SimpleNamespace(addons={"a_Rodin": object()})),
        ops=types.SimpleNamespace(rodin=types.SimpleNamespace(submit=object())),
    )

    result = module.inspect_plugin_bridge(fake_bpy, "rodin")

    assert result["ready"] is True
    assert "RodinBridge" in result["summary"]


def test_inspect_plugin_bridge_accepts_meshy_extension_display_name():
    module = _load_plugin_bridge_module()

    fake_addon = types.SimpleNamespace(
        __name__="bl_ext.user_default.meshy",
        bl_info={"name": "Meshy official plugin"},
    )
    fake_addon_utils = types.SimpleNamespace(modules=lambda: [fake_addon])
    sys.modules["addon_utils"] = fake_addon_utils

    fake_bpy = types.SimpleNamespace(
        context=types.SimpleNamespace(
            preferences=types.SimpleNamespace(addons={"bl_ext.user_default.meshy": object()})
        ),
        ops=types.SimpleNamespace(meshy=types.SimpleNamespace(bridge_start=object())),
    )

    result = module.inspect_plugin_bridge(fake_bpy, "meshy")

    assert result["ready"] is True
    assert "Meshy official plugin" in result["summary"]


def test_inspect_plugin_bridge_reports_missing_operator(monkeypatch):
    module = _load_plugin_bridge_module()

    fake_addon = types.SimpleNamespace(__name__="tripo_addon", bl_info={"name": "Tripo 3D"})
    fake_addon_utils = types.SimpleNamespace(modules=lambda: [fake_addon])
    sys.modules["addon_utils"] = fake_addon_utils

    fake_bpy = types.SimpleNamespace(
        context=types.SimpleNamespace(preferences=types.SimpleNamespace(addons={"tripo_addon": object()})),
        ops=types.SimpleNamespace(tripo3d=types.SimpleNamespace(generate_text_model=object())),
    )

    result = module.inspect_plugin_bridge(fake_bpy, "tripo")

    assert result["ready"] is False
    assert "download_task" in ",".join(result["missing_operators"])


def test_submit_via_plugin_bridge_for_tripo_sets_scene_and_invokes_operator():
    module = _load_plugin_bridge_module()

    fake_addon = types.SimpleNamespace(__name__="tripo_addon", bl_info={"name": "Tripo 3D"})
    fake_addon_utils = types.SimpleNamespace(modules=lambda: [fake_addon])
    sys.modules["addon_utils"] = fake_addon_utils

    calls = []
    fake_scene = types.SimpleNamespace(
        api_key="",
        api_key_confirmed=False,
        text_prompts="",
        enable_negative_prompts=False,
        negative_prompts="",
        model_version="v2.5-20250123",
        texture=True,
        pbr=True,
        texture_quality="standard",
        auto_size=False,
        quad=False,
        style="original",
        orientation="default",
        multiview_generate_mode=False,
    )
    fake_bpy = types.SimpleNamespace(
        context=types.SimpleNamespace(
            scene=fake_scene,
            preferences=types.SimpleNamespace(addons={"tripo_addon": object()}),
        ),
        ops=types.SimpleNamespace(
            tripo3d=types.SimpleNamespace(generate_text_model=lambda: calls.append("generate_text_model"), download_task=object())
        ),
    )

    result = module.submit_via_plugin_bridge(
        bpy_module=fake_bpy,
        service_key="tripo",
        api_key="tsk_example",
        prompt="robot cat",
        payload_json='{"texture_quality":"detailed","quad":true}',
    )

    assert calls == ["generate_text_model"]
    assert fake_scene.api_key == "tsk_example"
    assert fake_scene.text_prompts == "robot cat"
    assert fake_scene.texture_quality == "detailed"
    assert fake_scene.quad is True
    assert result["status"] == "submitted_via_plugin_bridge"


def test_submit_via_plugin_bridge_for_rodin_sets_properties_and_invokes_operator():
    module = _load_plugin_bridge_module()

    fake_addon = types.SimpleNamespace(__name__="rodin_bridge", bl_info={"name": "RodinBridge"})
    fake_addon_utils = types.SimpleNamespace(modules=lambda: [fake_addon])
    sys.modules["addon_utils"] = fake_addon_utils

    calls = []
    fake_rodin_prop = types.SimpleNamespace(
        textTo="Image",
        condition_type="bbox",
        prompt="",
        text_input="",
        gen_type="Manual",
        version="two",
        mode="Fast",
        quality=18000,
        bypass=True,
        polygons="Raw",
    )
    fake_bpy = types.SimpleNamespace(
        context=types.SimpleNamespace(
            scene=types.SimpleNamespace(rodin_prop=fake_rodin_prop),
            preferences=types.SimpleNamespace(addons={"rodin_bridge": object()}),
        ),
        ops=types.SimpleNamespace(rodin=types.SimpleNamespace(submit=lambda: calls.append("submit"))),
    )

    result = module.submit_via_plugin_bridge(
        bpy_module=fake_bpy,
        service_key="rodin",
        api_key="",
        prompt="armor knight",
        payload_json='{"version":"one","mode":"Default","quality":12000}',
    )

    assert calls == ["submit"]
    assert fake_rodin_prop.textTo == "Text"
    assert fake_rodin_prop.condition_type == "image"
    assert fake_rodin_prop.prompt == "armor knight"
    assert fake_rodin_prop.text_input == "armor knight"
    assert fake_rodin_prop.version == "one"
    assert fake_rodin_prop.quality == 12000
    assert result["status"] == "submitted_via_plugin_bridge"
