from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Callable, Iterable

from .runtime import prepare_runtime_root


@dataclass(frozen=True)
class InstallerStep:
    name: str
    script_path: Path
    description: str
    extra_args: tuple[str, ...] = ()


def repo_root() -> Path:
    return prepare_runtime_root()


def powershell_command(script_path: Path, extra_args: Iterable[str] | None = None) -> list[str]:
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
    ]
    if extra_args:
        command.extend(list(extra_args))
    return command


def default_steps(
    root: Path | None = None,
    include_launch_blender: bool = True,
    include_precision_profile: bool = False,
) -> list[InstallerStep]:
    base = root or repo_root()
    scripts_dir = base / "scripts"
    steps = [
        InstallerStep(
            name="official-addon",
            script_path=scripts_dir / "install_official_blender_mcp.ps1",
            description="Install the official Blender MCP add-on.",
        ),
        InstallerStep(
            name="official-server",
            script_path=scripts_dir / "install_official_blender_mcp_server.ps1",
            description="Install the official Blender MCP server into the dedicated venv.",
        ),
        InstallerStep(
            name="codex-config",
            script_path=scripts_dir / "register_official_blender_mcp_in_codex.ps1",
            description="Register blender-official in the Codex config.",
        ),
        InstallerStep(
            name="enable-addon",
            script_path=scripts_dir / "enable_official_blender_mcp_addon.ps1",
            description="Enable the official mcp add-on in Blender.",
        ),
    ]
    if include_precision_profile:
        steps.append(
            InstallerStep(
                name="precision-profile",
                script_path=scripts_dir / "install_precision_profile.ps1",
                description="Install optional precision profile templates, Skill, and subagent files.",
            )
        )
    if include_launch_blender:
        steps.append(
            InstallerStep(
                name="launch-blender",
                script_path=scripts_dir / "launch_blender.ps1",
                description="Start Blender for manual validation.",
            )
        )
    return steps


def default_log_dir(root: Path | None = None, now: datetime | None = None) -> Path:
    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    base = root or repo_root()
    return base / "artifacts" / "one-click-installer" / timestamp


class InstallerRunner:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or repo_root()

    def run(
        self,
        steps: Iterable[InstallerStep],
        output_dir: Path,
        log_callback: Callable[[str], None] | None = None,
        progress_callback: Callable[[int, int, InstallerStep], None] | None = None,
    ) -> tuple[bool, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path = output_dir / "installer.log"
        steps_list = list(steps)
        with log_path.open("a", encoding="utf-8") as handle:
            for index, step in enumerate(steps_list, start=1):
                if progress_callback:
                    progress_callback(index, len(steps_list), step)

                command = powershell_command(step.script_path, step.extra_args)
                self._write_line(handle, log_callback, f"[STEP {index}/{len(steps_list)}] {step.name}")
                self._write_line(handle, log_callback, f"[DESC] {step.description}")
                self._write_line(handle, log_callback, f"[CMD] {' '.join(command)}")

                completed = subprocess.run(
                    command,
                    cwd=self.root,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                )
                if completed.stdout:
                    for line in completed.stdout.splitlines():
                        self._write_line(handle, log_callback, line)
                if completed.stderr:
                    for line in completed.stderr.splitlines():
                        self._write_line(handle, log_callback, f"[stderr] {line}")

                self._write_line(handle, log_callback, f"[EXIT] {completed.returncode}")
                if completed.returncode != 0:
                    self._write_line(handle, log_callback, f"[FAILED] {step.name}")
                    return False, log_path

        return True, log_path

    @staticmethod
    def _write_line(
        handle,
        log_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        handle.write(message + "\n")
        handle.flush()
        if log_callback:
            log_callback(message)
