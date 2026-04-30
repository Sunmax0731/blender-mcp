from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

if __package__ in (None, ""):
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))
    from blender_mcp_installer.runner import (  # type: ignore[no-redef]
        InstallerRunner,
        InstallerStep,
        default_log_dir,
        default_steps,
        repo_root,
    )
    from blender_mcp_installer.runtime import prepare_runtime_root  # type: ignore[no-redef]
else:
    from .runner import InstallerRunner, InstallerStep, default_log_dir, default_steps, repo_root
    from .runtime import prepare_runtime_root


@dataclass
class QueueEvent:
    kind: str
    payload: object


class InstallerApp:
    def __init__(self, root_window: tk.Tk) -> None:
        self.root_window = root_window
        self.repo_root = repo_root()
        self.runner = InstallerRunner(self.repo_root)
        self.steps = default_steps(self.repo_root)
        self.events: queue.Queue[QueueEvent] = queue.Queue()
        self.output_dir: Path | None = None

        self.confirm_var = tk.BooleanVar(value=False)
        self.precision_profile_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready.")
        self.log_path_var = tk.StringVar(value="Log not created")
        self.install_succeeded = False

        self.root_window.title("Blender MCP One-Click Installer")
        self.root_window.geometry("900x700")

        self._build_ui()
        self._update_start_button()
        self.root_window.after(150, self._drain_events)

    def _build_ui(self) -> None:
        container = tk.Frame(self.root_window, padx=16, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        intro = (
            "This app runs the following steps:\n"
            "1. Install the official Blender MCP add-on\n"
            "2. Install the official Blender MCP server\n"
            "3. Register blender-official in Codex config\n"
            "4. Enable the official mcp add-on in Blender\n"
            "5. Remove the supplemental Blender prompt UI\n"
            "Optional: Install precision profile templates, Skill, and subagents"
        )
        tk.Label(container, text=intro, justify=tk.LEFT, anchor="w").pack(fill=tk.X)

        preview = (
            "Targets to be changed:\n"
            "- Blender add-on directory\n"
            f"- {self.repo_root / '.official-mcp-venv'}\n"
            f"- {Path.home() / '.codex' / 'config.toml'} and its backup\n"
            "- Blender user preferences\n"
            "- Supplemental Blender prompt UI registration, if present"
        )
        tk.Label(container, text=preview, justify=tk.LEFT, anchor="w", pady=8).pack(fill=tk.X)

        check = tk.Checkbutton(
            container,
            text="I reviewed the changes above and understand that local settings will be updated.",
            variable=self.confirm_var,
            command=self._update_start_button,
        )
        check.pack(anchor="w", pady=(0, 12))

        precision_check = tk.Checkbutton(
            container,
            text="Also install v2 precision profile templates, Skill, and subagent files.",
            variable=self.precision_profile_var,
        )
        precision_check.pack(anchor="w", pady=(0, 12))

        controls = tk.Frame(container)
        controls.pack(fill=tk.X, pady=(0, 12))
        self.start_button = tk.Button(controls, text="Start Install", command=self._start_install)
        self.start_button.pack(side=tk.LEFT)

        self.finish_button = tk.Button(
            controls,
            text="Finish",
            command=self._finish_install,
            state=tk.DISABLED,
        )
        self.finish_button.pack(side=tk.LEFT, padx=(8, 0))

        tk.Label(controls, textvariable=self.status_var, anchor="w").pack(side=tk.LEFT, padx=(12, 0))

        tk.Label(container, text="Log").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(container, height=24, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, textvariable=self.log_path_var, anchor="w", pady=8).pack(fill=tk.X)

    def _update_start_button(self) -> None:
        can_start = self.confirm_var.get() and not self.install_succeeded
        self.start_button.configure(state=tk.NORMAL if can_start else tk.DISABLED)

    def _start_install(self) -> None:
        self.install_succeeded = False
        self.start_button.configure(state=tk.DISABLED)
        self.finish_button.configure(state=tk.DISABLED)
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.output_dir = default_log_dir(self.repo_root)
        self.steps = default_steps(
            self.repo_root,
            include_precision_profile=self.precision_profile_var.get(),
        )
        self.log_path_var.set(f"Log path: {self.output_dir}")
        self.status_var.set("Starting install...")

        worker = threading.Thread(target=self._run_install, daemon=True)
        worker.start()

    def _run_install(self) -> None:
        assert self.output_dir is not None

        def on_log(message: str) -> None:
            self.events.put(QueueEvent("log", message))

        def on_progress(index: int, total: int, step: InstallerStep) -> None:
            self.events.put(QueueEvent("progress", (index, total, step.description)))

        success, log_path = self.runner.run(
            self.steps,
            self.output_dir,
            log_callback=on_log,
            progress_callback=on_progress,
        )
        self.events.put(QueueEvent("done", (success, str(log_path))))

    def _drain_events(self) -> None:
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break

            if event.kind == "log":
                self._append_log(str(event.payload))
            elif event.kind == "progress":
                index, total, description = event.payload  # type: ignore[misc]
                self.status_var.set(f"Running {index}/{total}: {description}")
            elif event.kind == "done":
                success, log_path = event.payload  # type: ignore[misc]
                self.log_path_var.set(f"Log path: {log_path}")
                if success:
                    self.install_succeeded = True
                    self.status_var.set("Install completed. Restart Codex App before live validation.")
                    self.finish_button.configure(state=tk.NORMAL)
                    messagebox.showinfo(
                        "Completed",
                        "Install completed.\nClick Finish to close this installer.",
                    )
                else:
                    self.install_succeeded = False
                    self.status_var.set("Install failed. Check the log and try again.")
                    self.finish_button.configure(state=tk.DISABLED)
                    messagebox.showerror(
                        "Failed",
                        "Install failed.\nCheck the log output and retry.",
                    )
                self._update_start_button()

        self.root_window.after(150, self._drain_events)

    def _finish_install(self) -> None:
        self.root_window.destroy()

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Blender MCP one-click installer")
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Print the planned steps without starting the GUI.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the installer steps without starting the GUI.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional log directory for headless mode.",
    )
    parser.add_argument(
        "--no-launch-blender",
        action="store_true",
        help="Skip the final Blender launch step.",
    )
    parser.add_argument(
        "--include-precision-profile",
        action="store_true",
        help="Install optional precision profile templates, Skill, and subagent files.",
    )
    return parser.parse_args()


def run_headless(
    output_dir: Path | None = None,
    include_launch_blender: bool = True,
    include_precision_profile: bool = False,
) -> int:
    root = repo_root()
    steps = default_steps(
        root,
        include_launch_blender=include_launch_blender,
        include_precision_profile=include_precision_profile,
    )
    runner = InstallerRunner(root)
    resolved_output_dir = output_dir or default_log_dir(root)

    print(f"OUTPUT_DIR: {resolved_output_dir}")

    def on_log(message: str) -> None:
        print(message)

    def on_progress(index: int, total: int, step: InstallerStep) -> None:
        print(f"PROGRESS {index}/{total}: {step.description}")

    success, log_path = runner.run(
        steps,
        resolved_output_dir,
        log_callback=on_log,
        progress_callback=on_progress,
    )
    print(f"LOG_PATH: {log_path}")
    return 0 if success else 1


def main() -> None:
    prepare_runtime_root()
    args = parse_args()
    if args.plan:
        for step in default_steps(
            repo_root(),
            include_launch_blender=not args.no_launch_blender,
            include_precision_profile=args.include_precision_profile,
        ):
            print(f"{step.name}: {step.description}")
        return

    if args.headless:
        raise SystemExit(
            run_headless(
                args.output_dir,
                include_launch_blender=not args.no_launch_blender,
                include_precision_profile=args.include_precision_profile,
            )
        )

    root_window = tk.Tk()
    InstallerApp(root_window)
    root_window.mainloop()


if __name__ == "__main__":
    main()
