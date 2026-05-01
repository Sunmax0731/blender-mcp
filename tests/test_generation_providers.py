from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICES_DIR = REPO_ROOT / "blender_addon" / "blender_mcp" / "services"


def _load_service_module(module_basename: str):
    package_name = "blender_mcp"
    services_name = "blender_mcp.services"
    module_name = f"blender_mcp.services.{module_basename}"

    package = types.ModuleType(package_name)
    package.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp")]
    services = types.ModuleType(services_name)
    services.__path__ = [str(SERVICES_DIR)]
    sys.modules[package_name] = package
    sys.modules[services_name] = services

    for helper in ("http_utils",):
        helper_name = f"blender_mcp.services.{helper}"
        if helper_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(helper_name, SERVICES_DIR / f"{helper}.py")
            module = importlib.util.module_from_spec(spec)
            assert spec is not None and spec.loader is not None
            sys.modules[helper_name] = module
            spec.loader.exec_module(module)

    spec = importlib.util.spec_from_file_location(module_name, SERVICES_DIR / f"{module_basename}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_meshy_extract_model_url_prefers_glb():
    module = _load_service_module("meshy")
    url = module.extract_model_url({"model_urls": {"fbx": "a", "glb": "b"}})
    assert url == "b"


def test_tripo_extract_model_url_prefers_pbr():
    module = _load_service_module("tripo")
    url = module.extract_model_url({"output": {"model": "a", "pbr_model": "b"}})
    assert url == "b"


def test_rodin_extract_model_url_prefers_glb_name():
    module = _load_service_module("rodin")
    url = module.extract_model_url(
        {
            "files": [
                {"name": "preview.webp", "url": "preview"},
                {"name": "asset.glb", "url": "model"},
            ]
        }
    )
    assert url == "model"


def test_spar3d_extract_model_url_from_nested_output():
    module = _load_service_module("spar3d")
    url = module.extract_model_url({"output": {"glb_url": "nested"}})
    assert url == "nested"


def test_spar3d_build_multipart_fields_uses_image_path(tmp_path):
    module = _load_service_module("spar3d")
    image_path = tmp_path / "input.png"
    image_path.write_bytes(b"pngdata")

    fields = module._build_multipart_fields(  # noqa: SLF001
        {"prompt": "cat", "image_field_name": "input_image", "image_content_type": "image/png"},
        image_path,
    )

    assert fields["prompt"] == "cat"
    assert fields["input_image"][0] == "input.png"
    assert fields["input_image"][1] == b"pngdata"
    assert fields["input_image"][2] == "image/png"


def test_generation_parse_optional_json_requires_object():
    package_name = "blender_mcp"
    services_name = "blender_mcp.services"
    module_name = "blender_mcp.services.generation"

    package = types.ModuleType(package_name)
    package.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp")]
    services = types.ModuleType(services_name)
    services.__path__ = [str(SERVICES_DIR)]
    preferences = types.ModuleType("blender_mcp.preferences")
    preferences.get_service_settings = lambda _preferences, _key: {}
    sys.modules[package_name] = package
    sys.modules[services_name] = services
    sys.modules["blender_mcp.preferences"] = preferences

    for helper in ("http_utils", "meshy", "rodin", "spar3d", "tripo"):
        helper_name = f"blender_mcp.services.{helper}"
        if helper_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(helper_name, SERVICES_DIR / f"{helper}.py")
            module = importlib.util.module_from_spec(spec)
            assert spec is not None and spec.loader is not None
            sys.modules[helper_name] = module
            spec.loader.exec_module(module)

    spec = importlib.util.spec_from_file_location(module_name, SERVICES_DIR / "generation.py")
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    assert module.parse_optional_json('{"prompt":"cat"}') == {"prompt": "cat"}
    try:
        module.parse_optional_json('["not","object"]')
    except ValueError as exc:
        assert "オブジェクト形式" in str(exc)
    else:
        raise AssertionError("ValueError was not raised")


def test_generation_submit_for_rodin_returns_subscription_key(monkeypatch):
    package_name = "blender_mcp"
    services_name = "blender_mcp.services"
    module_name = "blender_mcp.services.generation"

    package = types.ModuleType(package_name)
    package.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp")]
    services = types.ModuleType(services_name)
    services.__path__ = [str(SERVICES_DIR)]
    preferences = types.ModuleType("blender_mcp.preferences")
    preferences.get_service_settings = lambda _preferences, _key: {
        "label": "Hyper3D Rodin",
        "enabled": True,
        "api_key": "secret",
        "endpoint": "https://api.hyper3d.com",
        "requires_api_key": True,
    }
    sys.modules[package_name] = package
    sys.modules[services_name] = services
    sys.modules["blender_mcp.preferences"] = preferences

    for helper in ("http_utils", "meshy", "rodin", "spar3d", "tripo"):
        helper_name = f"blender_mcp.services.{helper}"
        if helper_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(helper_name, SERVICES_DIR / f"{helper}.py")
            module = importlib.util.module_from_spec(spec)
            assert spec is not None and spec.loader is not None
            sys.modules[helper_name] = module
            spec.loader.exec_module(module)

    spec = importlib.util.spec_from_file_location(module_name, SERVICES_DIR / "generation.py")
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    monkeypatch.setattr(
        sys.modules["blender_mcp.services.rodin"],
        "submit_text_generation",
        lambda **_kwargs: {"task_uuid": "task-1", "subscription_key": "sub-1", "raw": {"ok": True}},
    )

    result = module.submit_generation_task(
        preferences=object(),
        service_key="rodin",
        prompt="robot character",
    )

    assert result["task_id"] == "task-1"
    assert result["metadata"]["subscription_key"] == "sub-1"


def test_generation_submit_for_meshy_refine_uses_preview_task_id(monkeypatch):
    package_name = "blender_mcp"
    services_name = "blender_mcp.services"
    module_name = "blender_mcp.services.generation"

    package = types.ModuleType(package_name)
    package.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp")]
    services = types.ModuleType(services_name)
    services.__path__ = [str(SERVICES_DIR)]
    preferences = types.ModuleType("blender_mcp.preferences")
    preferences.get_service_settings = lambda _preferences, _key: {
        "label": "Meshy",
        "enabled": True,
        "api_key": "secret",
        "endpoint": "https://api.meshy.ai",
        "requires_api_key": True,
    }
    sys.modules[package_name] = package
    sys.modules[services_name] = services
    sys.modules["blender_mcp.preferences"] = preferences

    for helper in ("http_utils", "meshy", "rodin", "spar3d", "tripo"):
        helper_name = f"blender_mcp.services.{helper}"
        if helper_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(helper_name, SERVICES_DIR / f"{helper}.py")
            module = importlib.util.module_from_spec(spec)
            assert spec is not None and spec.loader is not None
            sys.modules[helper_name] = module
            spec.loader.exec_module(module)

    spec = importlib.util.spec_from_file_location(module_name, SERVICES_DIR / "generation.py")
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    captured = {}

    def _fake_submit_refine_task(**kwargs):
        captured.update(kwargs)
        return {"task_id": "refine-1", "raw": {"ok": True}}

    monkeypatch.setattr(sys.modules["blender_mcp.services.meshy"], "submit_refine_task", _fake_submit_refine_task)

    result = module.submit_generation_task(
        preferences=object(),
        service_key="meshy",
        prompt="",
        payload_json='{"mode":"refine","preview_task_id":"preview-1","target_formats":["glb"]}',
    )

    assert captured["preview_task_id"] == "preview-1"
    assert captured["target_formats"] == ["glb"]
    assert result["task_id"] == "refine-1"
    assert result["metadata"]["mode"] == "refine"


def test_generation_submit_for_tripo_followup_task_uses_payload_type(monkeypatch):
    package_name = "blender_mcp"
    services_name = "blender_mcp.services"
    module_name = "blender_mcp.services.generation"

    package = types.ModuleType(package_name)
    package.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp")]
    services = types.ModuleType(services_name)
    services.__path__ = [str(SERVICES_DIR)]
    preferences = types.ModuleType("blender_mcp.preferences")
    preferences.get_service_settings = lambda _preferences, _key: {
        "label": "Tripo AI",
        "enabled": True,
        "api_key": "secret",
        "endpoint": "https://api.tripo3d.ai/v2/openapi",
        "requires_api_key": True,
    }
    sys.modules[package_name] = package
    sys.modules[services_name] = services
    sys.modules["blender_mcp.preferences"] = preferences

    for helper in ("http_utils", "meshy", "rodin", "spar3d", "tripo"):
        helper_name = f"blender_mcp.services.{helper}"
        if helper_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(helper_name, SERVICES_DIR / f"{helper}.py")
            module = importlib.util.module_from_spec(spec)
            assert spec is not None and spec.loader is not None
            sys.modules[helper_name] = module
            spec.loader.exec_module(module)

    spec = importlib.util.spec_from_file_location(module_name, SERVICES_DIR / "generation.py")
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    captured = {}

    def _fake_create_task(**kwargs):
        captured.update(kwargs)
        return {"task_id": "tripo-followup-1", "raw": {"ok": True}}

    monkeypatch.setattr(sys.modules["blender_mcp.services.tripo"], "create_task", _fake_create_task)

    result = module.submit_generation_task(
        preferences=object(),
        service_key="tripo",
        prompt="",
        payload_json='{"type":"refine_model","draft_model_task_id":"draft-1"}',
    )

    assert captured["payload"]["type"] == "refine_model"
    assert captured["payload"]["draft_model_task_id"] == "draft-1"
    assert result["task_id"] == "tripo-followup-1"
    assert result["metadata"]["task_type"] == "refine_model"
