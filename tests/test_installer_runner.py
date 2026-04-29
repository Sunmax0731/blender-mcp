from datetime import datetime
from pathlib import Path

from blender_mcp_installer.main import parse_args
from blender_mcp_installer.runner import default_log_dir, default_steps, powershell_command


def test_default_steps_reference_existing_scripts() -> None:
    steps = default_steps(Path("D:/Claude/MCP"))

    assert [step.name for step in steps] == [
        "official-addon",
        "official-server",
        "codex-config",
        "enable-addon",
    ]
    assert all(step.script_path.suffix == ".ps1" for step in steps)


def test_powershell_command_contains_script_path() -> None:
    script_path = Path("D:/Claude/MCP/scripts/install_official_blender_mcp.ps1")

    command = powershell_command(script_path)

    assert command[:4] == ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass"]
    assert command[-2:] == ["-File", str(script_path)]


def test_default_log_dir_uses_timestamped_artifact_path() -> None:
    root = Path("D:/Claude/MCP")
    now = datetime(2026, 4, 30, 12, 34, 56)

    log_dir = default_log_dir(root, now)

    assert log_dir == root / "artifacts" / "one-click-installer" / "20260430_123456"


def test_parse_args_supports_headless_mode(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["blender-mcp-installer", "--headless", "--output-dir", "D:/Claude/MCP/artifacts/run1"],
    )

    args = parse_args()

    assert args.headless is True
    assert str(args.output_dir).endswith("artifacts\\run1") or str(args.output_dir).endswith(
        "artifacts/run1"
    )
