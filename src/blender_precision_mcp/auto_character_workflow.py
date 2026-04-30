from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .auto_character import build_pipeline_spec
from .auto_character import normalize_prompt_to_character_spec
from .auto_character_validation import validate_auto_character


def run_auto_character_dry_run(prompt: str, output_dir: str | Path) -> dict[str, Any]:
    resolved_output_dir = Path(output_dir)
    validation_dir = resolved_output_dir / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)

    character_spec = normalize_prompt_to_character_spec(prompt)
    pipeline_spec = build_pipeline_spec(
        prompt,
        character_spec,
        run_directory=str(resolved_output_dir).replace("\\", "/"),
        character_spec_ref="character_spec.yaml",
    )

    prompt_path = resolved_output_dir / "prompt.txt"
    character_spec_path = resolved_output_dir / "character_spec.yaml"
    pipeline_spec_path = resolved_output_dir / "pipeline_spec.yaml"
    validation_report_path = validation_dir / "final_validation_report.json"

    prompt_path.write_text(prompt.strip() + "\n", encoding="utf-8")
    character_spec_path.write_text(
        yaml.safe_dump(character_spec, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    pipeline_spec_path.write_text(
        yaml.safe_dump(pipeline_spec, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    artifact_paths = [
        str(prompt_path),
        str(character_spec_path),
        str(pipeline_spec_path),
        str(validation_report_path),
    ]
    validation_report = validate_auto_character(
        character_spec,
        pipeline_spec,
        artifact_paths=artifact_paths,
        spec_path=str(character_spec_path),
    )
    validation_report_path.write_text(
        json.dumps(validation_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    summary = {
        "mode": "dry_run",
        "prompt": prompt,
        "character_type": character_spec["character_type"],
        "status": validation_report["status"],
        "artifacts": artifact_paths,
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
