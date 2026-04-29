from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTTP_CLIENT_PATH = REPO_ROOT / "blender_addon" / "blender_mcp" / "services" / "http_client.py"


def _load_http_client_module():
    package_name = "blender_mcp"
    services_name = "blender_mcp.services"
    config_name = "blender_mcp.config"
    module_name = "blender_mcp.services.http_client"

    package = types.ModuleType(package_name)
    package.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp")]
    services = types.ModuleType(services_name)
    services.__path__ = [str(REPO_ROOT / "blender_addon" / "blender_mcp" / "services")]
    config = types.ModuleType(config_name)
    config.SERVER_URL = "http://127.0.0.1:8765"
    config.DEFAULT_HTTP_TIMEOUT_SECONDS = 2.0
    config.AI_SUGGESTION_TIMEOUT_SECONDS = 60.0

    sys.modules[package_name] = package
    sys.modules[services_name] = services
    sys.modules[config_name] = config

    spec = importlib.util.spec_from_file_location(module_name, HTTP_CLIENT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_request_ai_suggestion_uses_longer_timeout(monkeypatch):
    module = _load_http_client_module()
    captured: dict[str, object] = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"success": true}'

    def fake_urlopen(req, timeout):
        captured["timeout"] = timeout
        return _FakeResponse()

    monkeypatch.setattr(module.request, "urlopen", fake_urlopen)

    result = module.request_ai_suggestion(prompt="test")

    assert result["success"] is True
    assert captured["timeout"] == 60.0


def test_post_addon_status_keeps_default_timeout(monkeypatch):
    module = _load_http_client_module()
    captured: dict[str, object] = {}

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"success": true}'

    def fake_urlopen(req, timeout):
        captured["timeout"] = timeout
        return _FakeResponse()

    monkeypatch.setattr(module.request, "urlopen", fake_urlopen)

    result = module.post_addon_status(addon_version="0.1.1", blender_version="5.1.1")

    assert result["success"] is True
    assert captured["timeout"] == 2.0
