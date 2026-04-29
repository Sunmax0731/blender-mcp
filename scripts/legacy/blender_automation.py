from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ADDON_SOURCE_DIR = REPO_ROOT / "blender_addon" / "blender_mcp"
DIST_DIR = REPO_ROOT / "dist"
DEFAULT_ZIP_PATH = DIST_DIR / "blender_mcp_addon.zip"
TEXT_EXTENSIONS = {".py", ".md", ".json", ".toml", ".txt", ".yml", ".yaml"}
SKIP_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".pyd"}


def resolve_addons_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA is not set.")
    return Path(appdata) / "Blender Foundation" / "Blender" / "5.1" / "scripts" / "addons"


def iter_addon_files(source_dir: Path = ADDON_SOURCE_DIR):
    for path in sorted(source_dir.rglob("*")):
        if path.is_dir():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        yield path


def read_normalized_bytes(path: Path) -> bytes:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        text = path.read_text(encoding="utf-8-sig")
        return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return path.read_bytes()


def build_addon_zip(source_dir: Path = ADDON_SOURCE_DIR, zip_path: Path = DEFAULT_ZIP_PATH) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source_path in iter_addon_files(source_dir):
            relative_path = source_path.relative_to(source_dir.parent).as_posix()
            archive.writestr(relative_path, read_normalized_bytes(source_path))
    return zip_path


def sync_addon_directory(source_dir: Path = ADDON_SOURCE_DIR, target_root: Path | None = None) -> Path:
    target_root = target_root or resolve_addons_dir()
    if "Blender Foundation" not in str(target_root):
        raise RuntimeError(f"Unexpected target_root: {target_root}")

    target_dir = target_root / source_dir.name
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_path in iter_addon_files(source_dir):
        relative_path = source_path.relative_to(source_dir)
        destination = target_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(read_normalized_bytes(source_path))
    return target_dir
