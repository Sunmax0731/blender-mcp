from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_precision_workflow_smoke_generates_artifacts(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "run_precision_workflow_smoke.py"
    output_dir = tmp_path / "smoke"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--spec",
            str(repo_root / "templates" / "precision" / "model_spec.yaml"),
            "--output-dir",
            str(output_dir),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    summary = json.loads((output_dir / "smoke_summary.json").read_text(encoding="utf-8"))
    assert summary["success"] is True
    assert summary["mode"] == "dry_run"
    assert (output_dir / "scene_build_report.json").exists()
    assert (output_dir / "validation_report.json").exists()
    assert (output_dir / "review" / "review_manifest.json").exists()
    assert (output_dir / "export_manifest.json").exists()
    assert (output_dir / "prompt_samples.json").exists()
