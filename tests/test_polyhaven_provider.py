from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROVIDER_PATH = REPO_ROOT / "blender_addon" / "blender_mcp" / "services" / "polyhaven.py"


def _load_polyhaven_module():
    package_name = "blender_mcp"
    services_name = "blender_mcp.services"
    module_name = "blender_mcp.services.polyhaven"

    package = types.ModuleType(package_name)
    package.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp")]
    services = types.ModuleType(services_name)
    services.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp" / "services")]

    sys.modules[package_name] = package
    sys.modules[services_name] = services

    spec = importlib.util.spec_from_file_location(module_name, PROVIDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_search_assets_filters_query_and_sorts_by_downloads(monkeypatch):
    module = _load_polyhaven_module()

    payload = {
        "forest_rock": {
            "name": "Forest Rock",
            "type": 2,
            "categories": ["rocks", "forest"],
            "tags": ["stone"],
            "download_count": 50,
        },
        "desert_rock": {
            "name": "Desert Rock",
            "type": 2,
            "categories": ["rocks", "desert"],
            "tags": ["stone"],
            "download_count": 80,
        },
        "studio_hdri": {
            "name": "Studio HDRI",
            "type": 0,
            "categories": ["studio"],
            "tags": ["light"],
            "download_count": 100,
        },
    }

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    monkeypatch.setattr(module.request, "urlopen", lambda req, timeout=15.0: _FakeResponse())

    result = module.search_assets(
        base_url="https://api.polyhaven.com",
        asset_type="models",
        query_text="rock",
        category_text="",
        limit=5,
    )

    assert result["total_count"] == 2
    assert [asset["id"] for asset in result["assets"]] == ["desert_rock", "forest_rock"]


def test_format_search_results_handles_empty_payload():
    module = _load_polyhaven_module()

    text = module.format_search_results(
        {
            "asset_type": "all",
            "query": "",
            "category": "",
            "total_count": 0,
            "returned_count": 0,
            "assets": [],
        }
    )

    assert "No assets matched" in text
