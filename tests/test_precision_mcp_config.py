from __future__ import annotations

from pathlib import Path

from blender_precision_mcp.config import load_precision_config
from blender_precision_mcp.config import parse_tool_packs
from blender_precision_mcp.main import main
from blender_precision_mcp.server import create_mcp_server


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "templates" / "precision" / "blender_precision_config.yaml"


def test_load_precision_config_template_resolves_precise_profile():
    config = load_precision_config(CONFIG_PATH)
    resolved = config.resolve_profile("precise")

    assert config.server.name == "blender-precision-mcp"
    assert config.blender.host == "127.0.0.1"
    assert resolved.profile.name == "precise"
    assert "modeling" in resolved.selected_tool_packs
    assert "create_or_update_scene_from_spec" in resolved.enabled_tools
    assert "execute_blender_code" not in resolved.enabled_tools


def test_resolve_profile_can_override_tool_packs():
    config = load_precision_config(CONFIG_PATH)
    resolved = config.resolve_profile(
        "precise",
        requested_tool_packs=parse_tool_packs("validation,visual_qa"),
    )

    assert resolved.selected_tool_packs == ("validation", "visual_qa")
    assert "validate_scene_against_spec" in resolved.enabled_tools
    assert "capture_review_views" in resolved.enabled_tools
    assert "create_or_update_scene_from_spec" not in resolved.enabled_tools


def test_create_precision_mcp_server_registers_status_tools():
    config = load_precision_config(CONFIG_PATH)
    server = create_mcp_server(config.resolve_profile("safe"))

    assert server.name == "blender-precision-mcp"


def test_precision_cli_dry_run(capsys):
    exit_code = main(
        [
            "--config",
            str(CONFIG_PATH),
            "--profile",
            "audit",
            "--tool-pack",
            "validation",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert '"profile": "audit"' in captured.out
    assert "validate_scene_against_spec" in captured.out
