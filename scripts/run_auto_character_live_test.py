from __future__ import annotations

import argparse
import json
import subprocess
import sys
import textwrap
from pathlib import Path

from blender_precision_mcp.auto_character import normalize_prompt_to_character_spec
from blender_precision_mcp.auto_character_model_spec import build_model_spec_from_character_spec
from blender_precision_mcp.auto_character_rig_plan import build_live_rig_plan
from blender_precision_mcp.auto_character_workflow import run_auto_character_workflow
from blender_precision_mcp.validation import validate_model_spec


ROOT = Path(__file__).resolve().parents[1]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a live Blender auto character generation test.")
    parser.add_argument(
        "--prompt",
        default="Create a chibi hero with pink cape and expressive talking face.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "artifacts" / "auto-character-live-test",
    )
    parser.add_argument("--base-asset-manifest", type=Path, default=None)
    parser.add_argument("--adaptation-plan", type=Path, default=None)
    parser.add_argument("--image-reference-package", type=Path, default=None)
    parser.add_argument("--blender-exe", type=Path, default=None)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    workflow_summary = run_auto_character_workflow(
        args.prompt,
        output_dir=output_dir,
        live=True,
        base_asset_manifest_path=args.base_asset_manifest,
        adaptation_plan_path=args.adaptation_plan,
        image_reference_package_path=args.image_reference_package,
    )
    character_spec = normalize_prompt_to_character_spec(args.prompt)
    rig_plan = build_live_rig_plan(character_spec)
    model_spec = build_model_spec_from_character_spec(
        character_spec,
        output_dir=str(output_dir).replace("\\", "/"),
    )

    model_spec_path = output_dir / "model_spec.json"
    rig_plan_path = output_dir / "rig_plan.json"
    model_spec_path.write_text(
        json.dumps(model_spec, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    rig_plan_path.write_text(
        json.dumps(rig_plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    blender_exe = resolve_blender_exe(args.blender_exe)
    blender_script_path = output_dir / "run_live_character_test_blender.py"
    scene_report_path = output_dir / "scene_build_report.json"
    review_dir = output_dir / "review"
    export_manifest_path = output_dir / "export_manifest.json"
    live_scene_snapshot_path = output_dir / "validation" / "live_scene_snapshot.json"
    object_list_path = output_dir / "validation" / "object_list.json"
    validation_report_path = output_dir / "validation" / "final_validation_report.json"
    summary_path = output_dir / "live_test_summary.json"

    for directory in (review_dir, validation_report_path.parent):
        directory.mkdir(parents=True, exist_ok=True)

    blender_script_path.write_text(
        _build_blender_runner_script(
            src_dir=ROOT / "src",
            spec_path=model_spec_path,
            scene_report_path=scene_report_path,
            review_dir=review_dir,
            export_manifest_path=export_manifest_path,
            live_scene_snapshot_path=live_scene_snapshot_path,
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

    if result.returncode != 0:
        summary = {
            "success": False,
            "mode": "live",
            "blender_exe": str(blender_exe),
            "error": {
                "code": "blender_background_failed",
                "message": result.stderr.strip() or result.stdout.strip() or "Blender background execution failed.",
            },
            "workflow_summary": workflow_summary,
            "artifacts": {
                "model_spec": str(model_spec_path),
                "rig_plan": str(rig_plan_path),
                "blender_script": str(blender_script_path),
            },
        }
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1

    live_scene_snapshot = json.loads(live_scene_snapshot_path.read_text(encoding="utf-8"))
    validation_report = validate_model_spec(
        model_spec_path,
        output_path=validation_report_path,
        live_scene=True,
        live_scene_snapshot=live_scene_snapshot,
    )

    review_manifest_path = review_dir / "review_manifest.json"
    rig_report_path = output_dir / "validation" / "rig_report.json"
    shape_key_report_path = output_dir / "validation" / "shape_key_report.json"
    weight_report_path = output_dir / "validation" / "weight_report.json"
    review_manifest = json.loads(review_manifest_path.read_text(encoding="utf-8"))
    export_manifest = json.loads(export_manifest_path.read_text(encoding="utf-8"))
    scene_report = json.loads(scene_report_path.read_text(encoding="utf-8"))
    rig_report = json.loads(rig_report_path.read_text(encoding="utf-8"))
    shape_key_report = json.loads(shape_key_report_path.read_text(encoding="utf-8"))
    weight_report = json.loads(weight_report_path.read_text(encoding="utf-8"))

    summary = {
        "success": bool(
            scene_report.get("objects")
            and validation_report.get("status") == "ok"
            and rig_report.get("bone_count", 0) > 0
            and review_manifest.get("status") == "captured"
            and export_manifest.get("exports")
        ),
        "mode": "live",
        "blender_exe": str(blender_exe),
        "workflow_summary": workflow_summary,
        "artifacts": {
            "character_spec": str(output_dir / "character_spec.yaml"),
            "pipeline_spec": str(output_dir / "pipeline_spec.yaml"),
            "model_spec": str(model_spec_path),
            "rig_plan": str(rig_plan_path),
            "scene_build_report": str(scene_report_path),
            "validation_report": str(validation_report_path),
            "live_scene_snapshot": str(live_scene_snapshot_path),
            "object_list": str(object_list_path),
            "rig_report": str(rig_report_path),
            "shape_key_report": str(shape_key_report_path),
            "weight_report": str(weight_report_path),
            "review_manifest": str(review_manifest_path),
            "export_manifest": str(export_manifest_path),
        },
        "results": {
            "scene_success": True,
            "validation_status": validation_report.get("status"),
            "rig_status": rig_report.get("status"),
            "shape_key_status": shape_key_report.get("status"),
            "weight_status": weight_report.get("status"),
            "review_status": review_manifest.get("status"),
            "export_count": len(export_manifest.get("exports", [])),
        },
    }
    if args.base_asset_manifest and args.adaptation_plan:
        summary["artifacts"]["base_asset_manifest"] = str(output_dir / "validation" / "base_asset_manifest.json")
        summary["artifacts"]["adaptation_plan"] = str(output_dir / "validation" / "adaptation_plan.json")
    if args.image_reference_package:
        summary["artifacts"]["image_reference_manifest"] = str(
            output_dir / "validation" / "image_reference_manifest.json"
        )
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

    try:
        import winreg
    except ImportError:
        winreg = None

    if winreg is not None:
        registry_roots = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for root, path in registry_roots:
            try:
                with winreg.OpenKey(root, path) as uninstall_root:
                    for index in range(winreg.QueryInfoKey(uninstall_root)[0]):
                        subkey_name = winreg.EnumKey(uninstall_root, index)
                        with winreg.OpenKey(uninstall_root, subkey_name) as subkey:
                            display_name = _winreg_query(subkey, "DisplayName")
                            install_location = _winreg_query(subkey, "InstallLocation")
                            if display_name and "Blender" in display_name and install_location:
                                candidate = Path(install_location) / "blender.exe"
                                if candidate.exists():
                                    return candidate
            except OSError:
                continue

    raise FileNotFoundError("Blender executable could not be resolved. Set --blender-exe or BLENDER_PATH.")


def _env_path(key: str) -> Path | None:
    value = Path(Path.cwd()).anchor  # placeholder to keep type narrow
    raw = None
    try:
        import os

        raw = os.environ.get(key)
    except Exception:
        raw = None
    if not raw:
        return None
    value = Path(raw)
    return value


def _winreg_query(key: object, name: str) -> str | None:
    try:
        import winreg

        value, _ = winreg.QueryValueEx(key, name)
        return str(value) if value else None
    except OSError:
        return None


def _build_blender_runner_script(
    *,
    src_dir: Path,
    spec_path: Path,
    scene_report_path: Path,
    review_dir: Path,
    export_manifest_path: Path,
    live_scene_snapshot_path: Path,
    object_list_path: Path,
) -> str:
    return textwrap.dedent(
        f"""
        import json
        import sys
        from pathlib import Path

        sys.path.insert(0, {json.dumps(str(src_dir))})

        import bpy
        from blender_precision_mcp.exporter import export_scene
        from blender_precision_mcp.auto_character_live_rig import run_live_rig_bridge
        from blender_precision_mcp.scene_builder import create_or_update_scene_from_spec
        from blender_precision_mcp.visual_qa import capture_review_views

        spec_path = Path({json.dumps(str(spec_path))})
        rig_plan_path = Path({json.dumps(str(spec_path.parent / "rig_plan.json"))})
        scene_report_path = Path({json.dumps(str(scene_report_path))})
        review_dir = Path({json.dumps(str(review_dir))})
        export_manifest_path = Path({json.dumps(str(export_manifest_path))})
        live_scene_snapshot_path = Path({json.dumps(str(live_scene_snapshot_path))})
        object_list_path = Path({json.dumps(str(object_list_path))})

        review_dir.mkdir(parents=True, exist_ok=True)
        live_scene_snapshot_path.parent.mkdir(parents=True, exist_ok=True)

        scene_result = create_or_update_scene_from_spec(
            spec_path=spec_path,
            output_path=scene_report_path,
            dry_run=False,
        )
        rig_plan = json.loads(rig_plan_path.read_text(encoding="utf-8"))
        rig_result = run_live_rig_bridge(rig_plan, live_scene_snapshot_path.parent)
        review_result = capture_review_views(
            spec_path=spec_path,
            output_dir=review_dir,
            dry_run=False,
        )
        export_result = export_scene(
            spec_path=spec_path,
            output_manifest_path=export_manifest_path,
            validation_artifacts=[],
            review_artifacts=[str(review_result.get("manifest_path", review_dir / "review_manifest.json"))],
            dry_run=False,
        )

        scene = bpy.context.scene
        objects = []
        lights = []
        for obj in scene.objects:
            materials = [
                slot.material.name
                for slot in getattr(obj, "material_slots", [])
                if getattr(slot, "material", None) is not None
            ]
            object_data = {{
                "name": obj.name,
                "type": obj.type,
                "dimensions": [float(obj.dimensions.x), float(obj.dimensions.y), float(obj.dimensions.z)],
                "location": [float(obj.location.x), float(obj.location.y), float(obj.location.z)],
                "materials": materials,
                "visible": bool(obj.visible_get()),
            }}
            objects.append(object_data)
            if obj.type == "LIGHT":
                lights.append(obj.name)

        snapshot = {{
            "available": True,
            "scene_name": scene.name,
            "objects": objects,
            "materials": sorted(material.name for material in bpy.data.materials),
            "camera": scene.camera.name if scene.camera else None,
            "lights": lights,
        }}
        live_scene_snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
        object_list_path.write_text(json.dumps(objects, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")

        summary = {{
            "scene_result": scene_result,
            "rig_result": rig_result,
            "review_result": review_result,
            "export_result": export_result,
            "snapshot_path": str(live_scene_snapshot_path),
            "object_list_path": str(object_list_path),
        }}
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        """
    ).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
