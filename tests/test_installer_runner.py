from datetime import datetime
from pathlib import Path
import subprocess
import sys

from blender_mcp_installer.main import parse_args
from blender_mcp_installer.plugins import load_third_party_plugins
from blender_mcp_installer.runtime import source_repo_root, support_root
from blender_mcp_installer.runner import default_log_dir, default_steps, powershell_command


def test_default_steps_reference_existing_scripts() -> None:
    steps = default_steps(Path("D:/Claude/MCP"))

    assert [step.name for step in steps] == [
        "official-addon",
        "official-server",
        "codex-config",
        "enable-addon",
        "remove-prompt-ui",
        "third-party-plugins",
        "supplemental-addon",
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


def test_parse_args_supports_skipping_third_party_plugins(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "blender-mcp-installer",
            "--headless",
            "--skip-third-party-plugins",
            "--skip-plugin",
            "meshy",
            "--skip-plugin",
            "rodin",
        ],
    )

    args = parse_args()

    assert args.skip_third_party_plugins is True
    assert args.skip_plugin == ["meshy", "rodin"]


def test_default_steps_can_skip_launch_blender() -> None:
    steps = default_steps(Path("D:/Claude/MCP"), include_launch_blender=False)

    assert [step.name for step in steps] == [
        "official-addon",
        "official-server",
        "codex-config",
        "enable-addon",
        "remove-prompt-ui",
        "third-party-plugins",
        "supplemental-addon",
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
        "remove-prompt-ui",
        "third-party-plugins",
        "supplemental-addon",
        "precision-profile",
    ]
    assert steps[-1].extra_args == ("-MergeCodexConfig",)


def test_default_steps_can_skip_third_party_plugins() -> None:
    steps = default_steps(
        Path("D:/Claude/MCP"),
        include_launch_blender=False,
        include_third_party_plugins=False,
    )

    assert [step.name for step in steps] == [
        "official-addon",
        "official-server",
        "codex-config",
        "enable-addon",
        "remove-prompt-ui",
        "supplemental-addon",
    ]


def test_third_party_plugin_manifest_loads_expected_plugins() -> None:
    plugins = load_third_party_plugins(Path("D:/Claude/MCP"))

    assert [plugin.key for plugin in plugins] == ["meshy", "tripo", "rodin"]
    assert plugins[0].install_method == "extension"
    assert plugins[1].install_method == "addon_zip"


def test_precision_profile_script_can_plan_config_merge(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "install_precision_profile.ps1"
    codex_home = tmp_path / "codex-home"

    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-CodexHome",
            str(codex_home),
            "-PlanConfigMerge",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Plan only: would create/update precision MCP venv" in result.stdout
    assert "Codex config merge preview: append [mcp_servers.blender_precision]" in result.stdout
    assert "Codex config not found" in result.stdout
    assert not (codex_home / "config.toml").exists()


def test_precision_profile_script_removes_generated_config_with_backup(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "install_precision_profile.ps1"
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config_path = codex_home / "config.toml"
    config_path.write_text(
        '\n'.join(
            [
                '[mcp_servers.existing]',
                'command = "tool"',
                '',
                '[mcp_servers.blender_precision]',
                'command = "uvx"',
                'args = [',
                '  "blender-precision-mcp",',
                '  "--config", "templates/precision/blender_precision_config.yaml",',
                ']',
                'cwd = "."',
                '',
                '[plugins.example]',
                'enabled = true',
                '',
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-CodexHome",
            str(codex_home),
            "-MergeCodexConfig",
            "-SkipVenvInstall",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    merged = config_path.read_text(encoding="utf-8")
    assert "[mcp_servers.existing]" in merged
    assert "[mcp_servers.blender_precision]" in merged
    assert 'command = "powershell"' in merged
    assert "start_precision_blender_mcp.ps1" in merged
    assert 'command = "uvx"' not in merged
    assert "[plugins.example]" in merged
    assert list(codex_home.glob("config.toml.backup-*"))


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


def test_plan_mode_can_skip_third_party_plugins() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    main_py = repo_root / "src" / "blender_mcp_installer" / "main.py"

    result = subprocess.run(
        [sys.executable, str(main_py), "--plan", "--skip-third-party-plugins", "--no-launch-blender"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "third-party-plugins" not in result.stdout


def test_source_repo_root_points_to_workspace_repo() -> None:
    assert source_repo_root() == Path("D:/Claude/MCP")


def test_support_root_uses_local_appdata(monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\tester\AppData\Local")

    assert support_root() == Path(r"C:\Users\tester\AppData\Local\BlenderMcpInstaller")


def test_prepare_runtime_root_copies_templates_for_frozen_runtime(
    monkeypatch,
    tmp_path: Path,
) -> None:
    from blender_mcp_installer import runtime

    bundle_root = tmp_path / "bundle"
    support_parent = tmp_path / "local-appdata"
    (bundle_root / "scripts").mkdir(parents=True)
    (bundle_root / "templates" / "precision").mkdir(parents=True)
    (bundle_root / "templates" / "installer").mkdir(parents=True)
    (bundle_root / "blender_addon" / "blender_mcp").mkdir(parents=True)
    (bundle_root / "scripts" / "install_precision_profile.ps1").write_text(
        "script",
        encoding="utf-8",
    )
    (bundle_root / "templates" / "precision" / "codex_config.toml").write_text(
        "[mcp_servers.blender_precision]\n",
        encoding="utf-8",
    )
    (bundle_root / "templates" / "installer" / "third_party_plugins.json").write_text(
        '{"plugins":[]}\n',
        encoding="utf-8",
    )
    (bundle_root / "blender_addon" / "blender_mcp" / "__init__.py").write_text(
        "bl_info = {}\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("LOCALAPPDATA", str(support_parent))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle_root), raising=False)

    runtime_root = runtime.prepare_runtime_root()

    assert runtime_root == support_parent / "BlenderMcpInstaller"
    assert (runtime_root / "scripts" / "install_precision_profile.ps1").exists()
    assert (runtime_root / "templates" / "precision" / "codex_config.toml").exists()
    assert (runtime_root / "templates" / "installer" / "third_party_plugins.json").exists()
    assert (runtime_root / "blender_addon" / "blender_mcp" / "__init__.py").exists()


def test_prepare_runtime_root_copies_precision_package_for_frozen_runtime(
    monkeypatch,
    tmp_path: Path,
) -> None:
    from blender_mcp_installer import runtime

    bundle_root = tmp_path / "bundle"
    support_parent = tmp_path / "local-appdata"
    (bundle_root / "src" / "blender_precision_mcp").mkdir(parents=True)
    (bundle_root / "src" / "blender_precision_mcp" / "main.py").write_text(
        "def main(): return 0",
        encoding="utf-8",
    )
    (bundle_root / "pyproject.toml").write_text(
        "[project]\nname='example'\nversion='0.0.0'\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("LOCALAPPDATA", str(support_parent))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle_root), raising=False)

    runtime_root = runtime.prepare_runtime_root()

    assert (runtime_root / "src" / "blender_precision_mcp" / "main.py").exists()
    assert (runtime_root / "pyproject.toml").exists()
