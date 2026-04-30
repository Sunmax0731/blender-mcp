from datetime import datetime
from pathlib import Path
import subprocess
import sys

from blender_mcp_installer.main import parse_args
from blender_mcp_installer.runtime import source_repo_root, support_root
from blender_mcp_installer.runner import default_log_dir, default_steps, powershell_command


def test_default_steps_reference_existing_scripts() -> None:
    steps = default_steps(Path("D:/Claude/MCP"))

    assert [step.name for step in steps] == [
        "official-addon",
        "official-server",
        "codex-config",
        "enable-addon",
        "launch-blender",
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


def test_default_steps_can_skip_launch_blender() -> None:
    steps = default_steps(Path("D:/Claude/MCP"), include_launch_blender=False)

    assert [step.name for step in steps] == [
        "official-addon",
        "official-server",
        "codex-config",
        "enable-addon",
    ]


def test_default_steps_can_include_precision_profile() -> None:
    steps = default_steps(
        Path("D:/Claude/MCP"),
        include_launch_blender=False,
        include_precision_profile=True,
    )

    assert [step.name for step in steps] == [
        "official-addon",
        "official-server",
        "codex-config",
        "enable-addon",
        "precision-profile",
    ]


def test_default_steps_do_not_surface_legacy_context() -> None:
    steps = default_steps(Path("D:/Claude/MCP"))

    descriptions = "\n".join(step.description for step in steps).lower()

    assert "legacy" not in descriptions
    assert "disable" not in descriptions


def test_main_py_can_run_as_script_for_plan_mode() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    main_py = repo_root / "src" / "blender_mcp_installer" / "main.py"

    result = subprocess.run(
        [sys.executable, str(main_py), "--plan"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "official-addon" in result.stdout


def test_plan_mode_can_include_precision_profile() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    main_py = repo_root / "src" / "blender_mcp_installer" / "main.py"

    result = subprocess.run(
        [sys.executable, str(main_py), "--plan", "--include-precision-profile", "--no-launch-blender"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "precision-profile" in result.stdout


def test_source_repo_root_points_to_workspace_repo() -> None:
    assert source_repo_root() == Path("D:/Claude/MCP")


def test_support_root_uses_local_appdata(monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\tester\AppData\Local")

    assert support_root() == Path(r"C:\Users\tester\AppData\Local\BlenderMcpInstaller")
