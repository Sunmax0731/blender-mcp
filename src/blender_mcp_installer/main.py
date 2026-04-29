from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from .runner import InstallerRunner, InstallerStep, default_log_dir, default_steps, repo_root


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
        self.status_var = tk.StringVar(value="実行前です。")
        self.log_path_var = tk.StringVar(value="ログ未作成")

        self.root_window.title("Blender MCP 1クリック導入")
        self.root_window.geometry("900x700")

        self._build_ui()
        self._update_start_button()
        self.root_window.after(150, self._drain_events)

    def _build_ui(self) -> None:
        container = tk.Frame(self.root_window, padx=16, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        intro = (
            "このアプリは次を順に実行します。\n"
            "1. 公式 Blender MCP add-on を導入\n"
            "2. 公式 Blender MCP server を導入\n"
            "3. Codex 設定へ blender-official を登録\n"
            "4. 公式 mcp を有効化し legacy blender_mcp を無効化"
        )
        tk.Label(container, text=intro, justify=tk.LEFT, anchor="w").pack(fill=tk.X)

        preview = (
            "変更対象:\n"
            "- Blender add-on 配置先\n"
            "- D:\\Claude\\MCP\\.official-mcp-venv\n"
            "- C:\\Users\\gkkjh\\.codex\\config.toml とそのバックアップ\n"
            "- Blender ユーザー設定"
        )
        tk.Label(container, text=preview, justify=tk.LEFT, anchor="w", pady=8).pack(fill=tk.X)

        check = tk.Checkbutton(
            container,
            text="変更対象を確認しました。設定変更を伴うことを理解しています。",
            variable=self.confirm_var,
            command=self._update_start_button,
        )
        check.pack(anchor="w", pady=(0, 12))

        controls = tk.Frame(container)
        controls.pack(fill=tk.X, pady=(0, 12))
        self.start_button = tk.Button(controls, text="導入を開始", command=self._start_install)
        self.start_button.pack(side=tk.LEFT)

        tk.Label(controls, textvariable=self.status_var, anchor="w").pack(side=tk.LEFT, padx=(12, 0))

        tk.Label(container, text="ログ").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(container, height=24, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, textvariable=self.log_path_var, anchor="w", pady=8).pack(fill=tk.X)

    def _update_start_button(self) -> None:
        self.start_button.configure(state=tk.NORMAL if self.confirm_var.get() else tk.DISABLED)

    def _start_install(self) -> None:
        self.start_button.configure(state=tk.DISABLED)
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.output_dir = default_log_dir(self.repo_root)
        self.log_path_var.set(f"ログ保存先: {self.output_dir}")
        self.status_var.set("導入を開始します。")

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
                self.status_var.set(f"実行中 {index}/{total}: {description}")
            elif event.kind == "done":
                success, log_path = event.payload  # type: ignore[misc]
                self.log_path_var.set(f"ログ保存先: {log_path}")
                if success:
                    self.status_var.set("導入が完了しました。Codex App 再起動後に接続確認を行ってください。")
                    messagebox.showinfo(
                        "完了",
                        "導入が完了しました。\nCodex App を再起動し、Blender を起動した状態で接続確認してください。",
                    )
                else:
                    self.status_var.set("導入に失敗しました。ログを確認してください。")
                    messagebox.showerror(
                        "失敗",
                        "導入中に失敗しました。ログを確認して再実行してください。",
                    )
                self._update_start_button()

        self.root_window.after(150, self._drain_events)

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
        help="GUI を起動せず、実行予定ステップを表示します。",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.plan:
        for step in default_steps(repo_root()):
            print(f"{step.name}: {step.description}")
        return

    root_window = tk.Tk()
    InstallerApp(root_window)
    root_window.mainloop()


if __name__ == "__main__":
    main()
