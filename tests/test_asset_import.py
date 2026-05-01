from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "blender_addon" / "blender_mcp" / "services" / "asset_import.py"


def _load_asset_import_module():
    package_name = "blender_mcp"
    services_name = "blender_mcp.services"
    module_name = "blender_mcp.services.asset_import"

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


def test_infer_filename_from_url_keeps_glb_name():
    module = _load_asset_import_module()
    assert module.infer_filename_from_url("https://example.com/assets/model.glb?token=1") == "model.glb"


def test_infer_filename_from_url_rejects_unsupported_extension():
    module = _load_asset_import_module()
    try:
        module.infer_filename_from_url("https://example.com/assets/model.zip")
    except ValueError as exc:
        assert "Unsupported import extension" in str(exc)
    else:
        raise AssertionError("ValueError was not raised")


def test_sanitize_collection_component_replaces_separators():
    module = _load_asset_import_module()
    assert module.sanitize_collection_component("Rodin / demo job") == "Rodin___demo_job"
