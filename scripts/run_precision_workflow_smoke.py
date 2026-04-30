from __future__ import annotations

import argparse
import json
from pathlib import Path

from blender_precision_mcp.exporter import export_scene
from blender_precision_mcp.scene_builder import create_or_update_scene_from_spec
from blender_precision_mcp.validation import validate_model_spec
from blender_precision_mcp.visual_qa import capture_review_views


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate precision workflow smoke artifacts."
    )
    parser.add_argument("--spec", type=Path, default=Path("templates/precision/model_spec.yaml"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/precision-workflow-smoke"))
    parser.add_argument("--live", action="store_true", help="Run scene generation/export through Blender Python.")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    scene_report_path = output_dir / "scene_build_report.json"
    validation_report_path = output_dir / "validation_report.json"
    review_dir = output_dir / "review"
    export_manifest_path = output_dir / "export_manifest.json"
    prompt_samples_path = output_dir / "prompt_samples.json"
    summary_path = output_dir / "smoke_summary.json"

    scene_result = create_or_update_scene_from_spec(
        spec_path=args.spec,
        output_path=scene_report_path,
        dry_run=not args.live,
    )
    validation_report = validate_model_spec(
        spec_path=args.spec,
        output_path=validation_report_path,
        live_scene=False,
    )
    review_manifest = capture_review_views(
        spec_path=args.spec,
        output_dir=review_dir,
        dry_run=not args.live,
    )
    export_result = export_scene(
        spec_path=args.spec,
        output_manifest_path=export_manifest_path,
        validation_artifacts=[str(validation_report_path)],
        review_artifacts=[str(review_manifest.get("manifest_path", review_dir / "review_manifest.json"))],
        dry_run=not args.live,
    )

    prompt_samples = {
        "scene_analysis": (
            "現在開いている Blender scene を解析し、object 構成、material、light、camera、"
            "品質上の懸念、改善案を日本語でまとめてください。"
        ),
        "various_prompts_modeling": (
            "Blenderで丸いキャラクターモデルを作成してください。body、arms、feet、eyes、mouth、"
            "cheeks、materials、lights、camera を設定し、最後に object 一覧と工夫点を説明してください。"
        ),
        "precision_workflow": (
            "model_spec に基づいて scene を生成し、validation report、visual QA manifest、"
            "export manifest を同じ artifact directory に保存してください。"
        ),
    }
    prompt_samples_path.write_text(
        json.dumps(prompt_samples, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    summary = {
        "success": bool(
            scene_result.get("success")
            and validation_report.get("status") != "failed"
            and review_manifest.get("status") in {"planned", "captured"}
            and export_result.get("success")
        ),
        "mode": "live" if args.live else "dry_run",
        "artifacts": {
            "scene_build_report": str(scene_report_path),
            "validation_report": str(validation_report_path),
            "review_manifest": str(review_manifest.get("manifest_path", review_dir / "review_manifest.json")),
            "export_manifest": str(export_manifest_path),
            "prompt_samples": str(prompt_samples_path),
        },
        "results": {
            "scene": scene_result,
            "validation_status": validation_report.get("status"),
            "review_status": review_manifest.get("status"),
            "export": export_result,
        },
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
