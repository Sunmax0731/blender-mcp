from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_precision_mcp.vrm_base_conversion import VRM_ADDON_REPO
from blender_precision_mcp.vrm_base_conversion import build_vrm_import_blender_script
from blender_precision_mcp.vrm_base_conversion import select_vrm_addon_asset


DEFAULT_VRM_PATH = ROOT / "templates" / "precision" / "base_character_package" / "BaseAvatar.vrm"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert a base-character-package VRM into a .blend.")
    parser.add_argument("--vrm-path", type=Path, default=DEFAULT_VRM_PATH)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "artifacts" / "vrm-base-character-convert",
    )
    parser.add_argument("--package-blend-path", type=Path, default=None)
    parser.add_argument("--blender-exe", type=Path, default=None)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    vrm_path = args.vrm_path.resolve()
    if not vrm_path.exists():
        raise FileNotFoundError(f"VRM file not found: {vrm_path}")

    output_dir = args.output_dir.resolve()
    download_dir = output_dir / "downloads"
    validation_dir = output_dir / "validation"
    export_dir = output_dir / "exports"
    for directory in (download_dir, validation_dir, export_dir):
        directory.mkdir(parents=True, exist_ok=True)

    release = fetch_latest_release(VRM_ADDON_REPO)
    release_path = download_dir / "vrm_addon_release.json"
    release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    asset = select_vrm_addon_asset(release)
    addon_zip_path = download_dir / str(asset["name"])
    download_file(str(asset["browser_download_url"]), addon_zip_path)

    blender_exe = resolve_blender_exe(args.blender_exe)
    blender_script_path = output_dir / "run_vrm_import.py"
    report_path = validation_dir / "vrm_conversion_report.json"
    object_list_path = validation_dir / "object_list.json"
    blend_path = export_dir / f"{vrm_path.stem}.blend"
    package_blend_path = (
        args.package_blend_path.resolve()
        if args.package_blend_path is not None
        else vrm_path.with_suffix(".blend")
    )
    summary_path = output_dir / "conversion_summary.json"

    blender_script_path.write_text(
        build_vrm_import_blender_script(
            addon_zip_path=addon_zip_path,
            vrm_path=vrm_path,
            blend_path=blend_path,
            report_path=report_path,
            object_list_path=object_list_path,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [str(blender_exe), "--background", "--factory-startup", "--python", str(blender_script_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    summary: dict[str, Any] = {
        "success": False,
        "source_vrm": str(vrm_path),
        "blender_exe": str(blender_exe),
        "artifacts": {
            "release": str(release_path),
            "addon_zip": str(addon_zip_path),
            "blender_script": str(blender_script_path),
            "report": str(report_path),
            "object_list": str(object_list_path),
            "blend": str(blend_path),
        },
        "release": {
            "tag_name": release.get("tag_name"),
            "html_url": release.get("html_url"),
        },
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

    if result.returncode == 0 and report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        summary["success"] = report.get("status") == "ok" and blend_path.exists()
        if summary["success"]:
            package_blend_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(blend_path, package_blend_path)
        summary["results"] = {
            "object_count": report.get("object_count"),
            "armatures": report.get("armatures", []),
            "materials": len(report.get("materials", [])),
        }
        summary["artifacts"]["package_blend"] = str(package_blend_path)
    else:
        summary["error"] = {
            "code": "blender_vrm_import_failed",
            "message": result.stderr.strip() or result.stdout.strip() or "VRM import failed.",
        }

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["success"] else 1


def fetch_latest_release(repo: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def download_file(url: str, destination: Path) -> None:
    with urllib.request.urlopen(url) as response:
        destination.write_bytes(response.read())


def resolve_blender_exe(explicit_path: Path | None) -> Path:
    candidates = [
        explicit_path,
        _env_path("BLENDER_PATH"),
        _env_path("BLENDER_EXE"),
        Path(r"F:\Steam\steamapps\common\Blender\blender.exe"),
        Path(r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"),
        Path(r"C:\Program Files\Blender Foundation\Blender\blender.exe"),
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    raise FileNotFoundError("Blender executable could not be resolved. Set --blender-exe or BLENDER_PATH.")


def _env_path(key: str) -> Path | None:
    import os

    raw = os.environ.get(key)
    return Path(raw) if raw else None


if __name__ == "__main__":
    raise SystemExit(main())
