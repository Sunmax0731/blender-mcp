from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .validation import load_model_spec


DEFAULT_VIEWS = ("front", "side", "top", "perspective")


@dataclass(frozen=True, slots=True)
class ReviewCapturePlan:
    output_dir: Path
    views: tuple[str, ...]
    resolution: tuple[int, int]
    manifest_path: Path


def build_review_capture_plan(
    spec_path: str | Path = "templates/precision/model_spec.yaml",
    output_dir: str | Path | None = None,
    views: tuple[str, ...] | None = None,
) -> ReviewCapturePlan:
    spec = load_model_spec(spec_path)
    visual_qa = spec.get("visual_qa", {})
    configured_views = visual_qa.get("views") if isinstance(visual_qa, dict) else None
    configured_resolution = visual_qa.get("resolution") if isinstance(visual_qa, dict) else None

    selected_views = views or tuple(configured_views or DEFAULT_VIEWS)
    resolution = _resolution_tuple(configured_resolution)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    review_dir = Path(output_dir or Path("outputs") / "reviews" / run_id)

    return ReviewCapturePlan(
        output_dir=review_dir,
        views=tuple(str(view) for view in selected_views),
        resolution=resolution,
        manifest_path=review_dir / "review_manifest.json",
    )


def capture_review_views(
    spec_path: str | Path = "templates/precision/model_spec.yaml",
    output_dir: str | Path | None = None,
    views: tuple[str, ...] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    plan = build_review_capture_plan(spec_path=spec_path, output_dir=output_dir, views=views)
    plan.output_dir.mkdir(parents=True, exist_ok=True)

    artifacts: list[str] = []
    status = "planned"
    warnings: list[str] = []

    if dry_run:
        warnings.append("dry_run is true; review images were not captured.")
    else:
        try:
            artifacts = _capture_with_blender(plan)
            status = "captured"
        except RuntimeError as exc:
            warnings.append(str(exc))
            warnings.append("Run this tool inside Blender Python to capture actual viewport images.")

    if not artifacts:
        artifacts = [str(plan.output_dir / f"{view}.png") for view in plan.views]

    manifest = {
        "schema_version": "0.1",
        "status": status,
        "views": list(plan.views),
        "resolution": list(plan.resolution),
        "artifacts": artifacts,
        "warnings": warnings,
    }
    plan.manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest["manifest_path"] = str(plan.manifest_path)
    return manifest


def _capture_with_blender(plan: ReviewCapturePlan) -> list[str]:
    try:
        import bpy  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("Blender Python module bpy is not available.") from exc

    camera = _ensure_camera(bpy)
    scene = bpy.context.scene
    scene.render.resolution_x = plan.resolution[0]
    scene.render.resolution_y = plan.resolution[1]

    artifacts: list[str] = []
    for view in plan.views:
        _set_camera_view(camera, view)
        output_path = plan.output_dir / f"{view}.png"
        scene.render.filepath = str(output_path)
        bpy.ops.render.render(write_still=True)
        artifacts.append(str(output_path))
    return artifacts


def _ensure_camera(bpy_module: Any, name: str = "precision_review_camera") -> Any:
    camera_object = bpy_module.data.objects.get(name)
    if camera_object is None:
        camera_data = bpy_module.data.cameras.new(name)
        camera_object = bpy_module.data.objects.new(name, camera_data)
        bpy_module.context.collection.objects.link(camera_object)
    bpy_module.context.scene.camera = camera_object
    return camera_object


def _set_camera_view(camera: Any, view: str) -> None:
    positions = {
        "front": (0, -4, 1.5),
        "side": (4, 0, 1.5),
        "top": (0, 0, 5),
        "perspective": (3, -4, 2.5),
    }
    rotations = {
        "front": (1.5708, 0, 0),
        "side": (1.5708, 0, 1.5708),
        "top": (0, 0, 0),
        "perspective": (1.1, 0, 0.65),
    }
    camera.location = positions.get(view, positions["perspective"])
    camera.rotation_euler = rotations.get(view, rotations["perspective"])


def _resolution_tuple(value: Any) -> tuple[int, int]:
    if isinstance(value, list) and len(value) == 2:
        return int(value[0]), int(value[1])
    return 1280, 1280
