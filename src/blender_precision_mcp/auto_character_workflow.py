from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .auto_character import build_pipeline_spec
from .auto_character import normalize_prompt_to_character_spec
from .auto_character_validation import validate_auto_character


def run_auto_character_dry_run(prompt: str, output_dir: str | Path) -> dict[str, Any]:
    return run_auto_character_workflow(prompt, output_dir=output_dir, live=False)


def run_auto_character_workflow(
    prompt: str,
    output_dir: str | Path,
    *,
    live: bool = False,
) -> dict[str, Any]:
    resolved_output_dir = Path(output_dir)
    validation_dir = resolved_output_dir / "validation"
    stage_reports_dir = resolved_output_dir / "stage_reports"
    review_dir = resolved_output_dir / "review"
    exports_dir = resolved_output_dir / "exports"
    for directory in (resolved_output_dir, validation_dir, stage_reports_dir, review_dir, exports_dir):
        directory.mkdir(parents=True, exist_ok=True)

    normalized_prompt = prompt.strip()
    run_id = _build_run_id(normalized_prompt)
    character_spec = normalize_prompt_to_character_spec(normalized_prompt)
    pipeline_spec = build_pipeline_spec(
        normalized_prompt,
        character_spec,
        run_directory=str(resolved_output_dir).replace("\\", "/"),
        character_spec_ref="character_spec.yaml",
    )

    prompt_path = resolved_output_dir / "prompt.txt"
    character_spec_path = resolved_output_dir / "character_spec.yaml"
    pipeline_spec_path = resolved_output_dir / "pipeline_spec.yaml"
    validation_report_path = validation_dir / "final_validation_report.json"
    run_manifest_path = resolved_output_dir / "run_manifest.json"

    prompt_path.write_text(normalized_prompt + "\n", encoding="utf-8")
    character_spec_path.write_text(
        yaml.safe_dump(character_spec, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    pipeline_spec_path.write_text(
        yaml.safe_dump(pipeline_spec, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    execution = _resolve_execution_context(live=live, pipeline_spec=pipeline_spec)
    artifact_index = _artifact_index(
        prompt_path=prompt_path,
        character_spec_path=character_spec_path,
        pipeline_spec_path=pipeline_spec_path,
        validation_report_path=validation_report_path,
        stage_reports_dir=stage_reports_dir,
        review_dir=review_dir,
        exports_dir=exports_dir,
        run_manifest_path=run_manifest_path,
    )
    artifact_paths = list(artifact_index.values())

    validation_report = validate_auto_character(
        character_spec,
        pipeline_spec,
        artifact_paths=artifact_paths,
        spec_path=str(character_spec_path),
    )
    if execution["error"] is not None:
        validation_report["warnings"].append(execution["error"]["message"])
        validation_report["execution"] = execution
        if validation_report["status"] == "ok":
            validation_report["status"] = "warning"
    else:
        validation_report["execution"] = execution

    validation_report_path.write_text(
        json.dumps(validation_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    run_manifest = _build_run_manifest(
        run_id=run_id,
        prompt=normalized_prompt,
        character_spec=character_spec,
        validation_report=validation_report,
        artifact_index=artifact_index,
        execution=execution,
    )
    run_manifest_path.write_text(
        json.dumps(run_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    summary = {
        "mode": "live" if live else "dry_run",
        "requested_live": live,
        "execution_mode": execution["mode"],
        "character_type": character_spec["character_type"],
        "status": validation_report["status"],
        "run_id": run_id,
        "artifacts": artifact_paths,
        "fallback": execution["fallback"],
        "error": execution["error"],
        "run_manifest_path": str(run_manifest_path),
    }
    summary_path = resolved_output_dir / "dry_run_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary["artifacts"].append(str(summary_path))
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def _resolve_execution_context(live: bool, pipeline_spec: dict[str, Any]) -> dict[str, Any]:
    fallback_plan = pipeline_spec.get("fallback_plan", {})
    preferred_route = str(fallback_plan.get("live_execution_route", "blender_background"))
    alternate_routes = [
        str(route)
        for route in fallback_plan.get("alternate_routes", [])
        if isinstance(route, str)
    ]

    if not live:
        return {
            "mode": "dry_run",
            "fallback": {
                "required": False,
                "route": None,
                "alternate_routes": alternate_routes,
            },
            "error": None,
        }

    bpy_module = _try_load_bpy()
    if bpy_module is not None:
        return {
            "mode": "live_in_process",
            "fallback": {
                "required": False,
                "route": None,
                "alternate_routes": alternate_routes,
            },
            "error": None,
        }

    return {
        "mode": "fallback_required",
        "fallback": {
            "required": True,
            "route": preferred_route,
            "alternate_routes": alternate_routes,
        },
        "error": {
            "code": "blender_unavailable",
            "message": "Blender Python module bpy is not available in the sidecar process.",
            "retryable": False,
        },
    }


def _artifact_index(
    *,
    prompt_path: Path,
    character_spec_path: Path,
    pipeline_spec_path: Path,
    validation_report_path: Path,
    stage_reports_dir: Path,
    review_dir: Path,
    exports_dir: Path,
    run_manifest_path: Path,
) -> dict[str, str]:
    return {
        "prompt": str(prompt_path),
        "character_spec": str(character_spec_path),
        "pipeline_spec": str(pipeline_spec_path),
        "validation_report": str(validation_report_path),
        "stage_reports_dir": str(stage_reports_dir),
        "review_dir": str(review_dir),
        "exports_dir": str(exports_dir),
        "run_manifest": str(run_manifest_path),
    }


def _build_run_manifest(
    *,
    run_id: str,
    prompt: str,
    character_spec: dict[str, Any],
    validation_report: dict[str, Any],
    artifact_index: dict[str, str],
    execution: dict[str, Any],
) -> dict[str, Any]:
    exported_files: list[str] = []
    final_status = validation_report["status"]
    return {
        "schema_version": "0.1",
        "run_id": run_id,
        "source_prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "character_type": character_spec["character_type"],
        "stages_executed": ["shape", "look", "rig", "expression", "weight"],
        "fallbacks_used": [execution["fallback"]["route"]] if execution["fallback"]["required"] else [],
        "final_status": final_status,
        "exported_files": exported_files,
        "artifact_paths": artifact_index,
        "validation_trace": {
            "validation_report": artifact_index["validation_report"],
            "stage_summary_ref": artifact_index["validation_report"],
            "validator_results_ref": artifact_index["validation_report"],
            "final_check_count": len(validation_report.get("checks", [])),
        },
        "execution": execution,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def _build_run_id(prompt: str) -> str:
    prompt_hash = hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:8]
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{prompt_hash}"


def _try_load_bpy() -> Any | None:
    try:
        import bpy  # type: ignore
    except ModuleNotFoundError:
        return None
    if not hasattr(bpy, "context") or not hasattr(bpy, "ops"):
        return None
    return bpy
