from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_auto_character_live_test.py"


spec = importlib.util.spec_from_file_location("run_auto_character_live_test", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
live_test = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live_test)


def test_live_test_main_writes_strict_validation_and_artifact_summary(tmp_path, monkeypatch):
    output_dir = tmp_path / "live-test"

    def fake_workflow(prompt, output_dir, **kwargs):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "character_spec.yaml").write_text(
            "\n".join(
                [
                    "schema_version: '0.1'",
                    "character_type: chibi",
                    "parts:",
                    "  - name: body",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (output_dir / "pipeline_spec.yaml").write_text(
            "\n".join(
                [
                    "shape_stage:",
                    "  validators:",
                    "    - shape_symmetry",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return {
            "mode": "live",
            "status": "warning",
            "execution_mode": "fallback_required",
        }

    monkeypatch.setattr(
        live_test,
        "run_auto_character_workflow",
        fake_workflow,
    )
    monkeypatch.setattr(
        live_test,
        "build_live_rig_plan",
        lambda character_spec: {
            "target_object": "RoundBuddy_Body",
            "shape_keys": ["smile", "blink"],
        },
    )
    monkeypatch.setattr(
        live_test,
        "build_model_spec_from_character_spec",
        lambda character_spec, output_dir: {
            "schema_version": "0.2",
            "objects": [{"name": "RoundBuddy_Body"}],
            "exports": [{"format": "blend", "path": f"{output_dir}/exports/final.blend"}],
        },
    )
    monkeypatch.setattr(live_test, "resolve_blender_exe", lambda explicit_path: tmp_path / "blender.exe")

    def fake_validate_model_spec(spec_path, *, output_path, live_scene, live_scene_snapshot):
        report = {
            "status": "ok",
            "checks": [{"name": "scene.objects", "status": "ok"}],
            "live_scene": live_scene,
            "snapshot_object_count": len(live_scene_snapshot["objects"]),
        }
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report

    monkeypatch.setattr(live_test, "validate_model_spec", fake_validate_model_spec)

    def fake_subprocess_run(args, cwd, capture_output, text, check):
        script_path = Path(args[-1])
        run_dir = script_path.parent
        (run_dir / "validation").mkdir(parents=True, exist_ok=True)
        (run_dir / "review").mkdir(parents=True, exist_ok=True)
        (run_dir / "exports").mkdir(parents=True, exist_ok=True)

        (run_dir / "scene_build_report.json").write_text(
            json.dumps({"objects": [{"name": "RoundBuddy_Body"}]}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (run_dir / "validation" / "live_scene_snapshot.json").write_text(
            json.dumps(
                {
                    "available": True,
                    "camera": "Precision_Camera",
                    "lights": ["Precision_Key_Light"],
                    "materials": ["mat_skin"],
                    "objects": [
                        {
                            "name": "RoundBuddy_Body",
                            "type": "MESH",
                            "dimensions": [1.0, 1.0, 1.0],
                            "location": [0.0, 0.0, 0.5],
                            "materials": ["mat_skin"],
                            "visible": True,
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (run_dir / "validation" / "object_list.json").write_text(
            json.dumps([{"name": "RoundBuddy_Body", "type": "MESH"}], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (run_dir / "validation" / "rig_report.json").write_text(
            json.dumps({"status": "ok", "bone_count": 12}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (run_dir / "validation" / "shape_key_report.json").write_text(
            json.dumps({"status": "ok", "shape_key_count": 3}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (run_dir / "validation" / "weight_report.json").write_text(
            json.dumps({"status": "ok", "pose_test_count": 3}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (run_dir / "review" / "review_manifest.json").write_text(
            json.dumps({"status": "captured", "images": ["front.png"]}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (run_dir / "export_manifest.json").write_text(
            json.dumps(
                {"exports": [{"format": "blend", "path": str(run_dir / "exports" / "final.blend")}]},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (run_dir / "exports" / "final.blend").write_text("placeholder blend", encoding="utf-8")

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(live_test.subprocess, "run", fake_subprocess_run)
    monkeypatch.setattr(
        live_test.sys,
        "argv",
        [
            "run_auto_character_live_test.py",
            "--prompt",
            "Create a chibi hero with pink cape and expressive talking face.",
            "--output-dir",
            str(output_dir),
        ],
    )

    exit_code = live_test.main()

    summary = json.loads((output_dir / "live_test_summary.json").read_text(encoding="utf-8"))
    validation_report = json.loads(
        (output_dir / "validation" / "final_validation_report.json").read_text(encoding="utf-8")
    )
    object_list = json.loads((output_dir / "validation" / "object_list.json").read_text(encoding="utf-8"))
    rig_report = json.loads((output_dir / "validation" / "rig_report.json").read_text(encoding="utf-8"))
    shape_key_report = json.loads(
        (output_dir / "validation" / "shape_key_report.json").read_text(encoding="utf-8")
    )
    weight_report = json.loads((output_dir / "validation" / "weight_report.json").read_text(encoding="utf-8"))
    review_manifest = json.loads((output_dir / "review" / "review_manifest.json").read_text(encoding="utf-8"))
    export_manifest = json.loads((output_dir / "export_manifest.json").read_text(encoding="utf-8"))

    assert exit_code == 0
    assert summary["success"] is True
    assert summary["results"]["validation_status"] == "ok"
    assert summary["results"]["rig_status"] == "ok"
    assert summary["results"]["shape_key_status"] == "ok"
    assert summary["results"]["weight_status"] == "ok"
    assert summary["results"]["review_status"] == "captured"
    assert summary["results"]["export_count"] == 1
    assert validation_report["status"] == "ok"
    assert object_list[0]["name"] == "RoundBuddy_Body"
    assert rig_report["bone_count"] == 12
    assert shape_key_report["shape_key_count"] == 3
    assert weight_report["pose_test_count"] == 3
    assert review_manifest["status"] == "captured"
    assert export_manifest["exports"][0]["format"] == "blend"
