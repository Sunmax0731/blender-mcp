from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_precision_mcp.base_asset_analysis import build_base_asset_blender_script


DEFAULT_BLEND_PATH = ROOT / "artifacts" / "vrm-base-character-convert" / "exports" / "BaseAvatar.blend"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze a converted base character .blend and emit base asset artifacts."
    )
    parser.add_argument("--blend-path", type=Path, default=DEFAULT_BLEND_PATH)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "artifacts" / "base-character-analysis",
    )
    parser.add_argument("--blender-exe", type=Path, default=None)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    blend_path = args.blend_path.resolve()
    if not blend_path.exists():
        raise FileNotFoundError(f"Blend file not found: {blend_path}")

    output_dir = args.output_dir.resolve()
    validation_dir = output_dir / "validation"
    export_dir = output_dir / "exports"
    validation_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)

    blender_exe = resolve_blender_exe(args.blender_exe)
    blender_script_path = output_dir / "run_base_asset_analysis.py"
    snapshot_path = validation_dir / "base_asset_snapshot.json"
    object_list_path = validation_dir / "object_list.json"
    manifest_path = validation_dir / "base_asset_manifest.json"
    adaptation_plan_path = validation_dir / "adaptation_plan.json"
    summary_path = output_dir / "analysis_summary.json"

    blender_script_path.write_text(
        build_base_asset_blender_script(
            blend_path=blend_path,
            manifest_path=manifest_path,
            adaptation_plan_path=adaptation_plan_path,
            object_list_path=object_list_path,
            snapshot_path=snapshot_path,
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
        "source_blend": str(blend_path),
        "blender_exe": str(blender_exe),
        "artifacts": {
            "blender_script": str(blender_script_path),
            "snapshot": str(snapshot_path),
            "object_list": str(object_list_path),
            "base_asset_manifest": str(manifest_path),
            "adaptation_plan": str(adaptation_plan_path),
        },
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

    if result.returncode == 0 and manifest_path.exists() and adaptation_plan_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        adaptation_plan = json.loads(adaptation_plan_path.read_text(encoding="utf-8"))
        summary["success"] = manifest.get("status") == "ok" and adaptation_plan.get("status") == "ok"
        summary["results"] = {
            "main_mesh_object": manifest.get("main_mesh_object"),
            "face_mesh_object": manifest.get("face_mesh_object"),
            "armature_count": len(manifest.get("imported_armature_list", [])),
            "reusable_hair_objects": manifest.get("reusable_hair_objects", []),
            "reuse_targets": adaptation_plan.get("reuse_targets", []),
            "regenerate_targets": adaptation_plan.get("regenerate_targets", []),
        }
    else:
        summary["error"] = {
            "code": "base_asset_analysis_failed",
            "message": result.stderr.strip() or result.stdout.strip() or "Base asset analysis failed.",
        }

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["success"] else 1


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
