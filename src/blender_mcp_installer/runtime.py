from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys


def source_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def bundled_root() -> Path | None:
    meipass = getattr(sys, "_MEIPASS", None)
    if not meipass:
        return None
    return Path(meipass)


def support_root() -> Path:
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        return Path(local_appdata) / "BlenderMcpInstaller"
    return Path.home() / "AppData" / "Local" / "BlenderMcpInstaller"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def prepare_runtime_root() -> Path:
    if not is_frozen():
        return source_repo_root()

    bundle_root = bundled_root()
    if bundle_root is None:
        return source_repo_root()

    runtime_root = support_root()
    runtime_root.mkdir(parents=True, exist_ok=True)

    for directory_name in ("scripts", "templates"):
        bundled_directory = bundle_root / directory_name
        runtime_directory = runtime_root / directory_name
        if bundled_directory.exists():
            shutil.copytree(bundled_directory, runtime_directory, dirs_exist_ok=True)

    return runtime_root
