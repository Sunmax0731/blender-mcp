from __future__ import annotations

import json
import struct
import zlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_VIEWS = ("front", "side", "top", "perspective")


@dataclass(frozen=True, slots=True)
class ReviewCapturePlan:
    output_dir: Path
    views: tuple[str, ...]
    resolution: tuple[int, int]
    manifest_path: Path
    target_objects: tuple[str, ...]


class VisualQaError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def build_review_capture_plan(
    spec_path: str | Path = "templates/precision/model_spec.yaml",
    output_dir: str | Path | None = None,
    views: tuple[str, ...] | None = None,
) -> ReviewCapturePlan:
    spec = _load_model_spec_for_visual_qa(spec_path)
    visual_qa = spec.get("visual_qa", {})
    configured_views = visual_qa.get("views") if isinstance(visual_qa, dict) else None
    configured_resolution = visual_qa.get("resolution") if isinstance(visual_qa, dict) else None

    selected_views = tuple(str(view) for view in (views or tuple(configured_views or DEFAULT_VIEWS)))
    if not selected_views:
        raise VisualQaError("VIEW_CONFIG_INVALID", "At least one review view is required.")

    unsupported_views = [view for view in selected_views if view not in DEFAULT_VIEWS]
    if unsupported_views:
        raise VisualQaError(
            "VIEW_NOT_SUPPORTED",
            f"Unsupported review view(s): {', '.join(unsupported_views)}",
        )

    resolution = _resolution_tuple(configured_resolution)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    review_dir = Path(output_dir or Path("outputs") / "reviews" / run_id)
    target_objects = tuple(
        str(obj["name"])
        for obj in spec.get("objects", [])
        if isinstance(obj, dict) and isinstance(obj.get("name"), str)
    )

    return ReviewCapturePlan(
        output_dir=review_dir,
        views=selected_views,
        resolution=resolution,
        manifest_path=review_dir / "review_manifest.json",
        target_objects=target_objects,
    )


def capture_review_views(
    spec_path: str | Path = "templates/precision/model_spec.yaml",
    output_dir: str | Path | None = None,
    views: tuple[str, ...] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    try:
        plan = build_review_capture_plan(spec_path=spec_path, output_dir=output_dir, views=views)
    except VisualQaError as exc:
        review_dir = Path(output_dir or Path("outputs") / "reviews" / datetime.now().strftime("%Y%m%d_%H%M%S"))
        review_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = review_dir / "review_manifest.json"
        manifest = {
            "schema_version": "0.1",
            "status": "failed",
            "views": list(views or []),
            "resolution": [1280, 1280],
            "target_objects": [],
            "captures": [],
            "artifacts": [],
            "quality_checks": [],
            "warnings": [str(exc)],
            "errors": [{"code": exc.code, "message": str(exc)}],
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest["manifest_path"] = str(manifest_path)
        return manifest

    plan.output_dir.mkdir(parents=True, exist_ok=True)

    artifacts: list[str] = []
    captures: list[dict[str, Any]] = []
    quality_checks: list[dict[str, Any]] = []
    status = "planned"
    warnings: list[str] = []
    errors: list[dict[str, str]] = []

    if dry_run:
        warnings.append("dry_run is true; review images were not captured.")
    else:
        try:
            artifacts = _capture_with_blender(plan)
            captures = _capture_entries(plan, artifacts)
            quality_checks = [analyze_review_image(path) for path in artifacts]
            status = _status_from_quality_checks(quality_checks)
        except VisualQaError as exc:
            errors.append({"code": exc.code, "message": str(exc)})
            warnings.append(str(exc))

    if not artifacts:
        artifacts = [str(plan.output_dir / f"{view}.png") for view in plan.views]
        captures = _capture_entries(plan, artifacts)

    manifest = {
        "schema_version": "0.1",
        "status": status,
        "views": list(plan.views),
        "resolution": list(plan.resolution),
        "target_objects": list(plan.target_objects),
        "captures": captures,
        "artifacts": artifacts,
        "quality_checks": quality_checks,
        "warnings": warnings,
        "errors": errors,
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
        raise VisualQaError("BLENDER_NOT_AVAILABLE", "Blender Python module bpy is not available.") from exc

    camera = _ensure_camera(bpy)
    scene = bpy.context.scene
    _validate_target_objects(bpy, plan.target_objects)
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


def analyze_review_image(
    image_path: str | Path,
    min_subject_ratio: float = 0.001,
    min_bbox_ratio: float = 0.05,
    background_threshold: int = 8,
) -> dict[str, Any]:
    path = Path(image_path)
    if not path.exists():
        return {
            "image": str(path),
            "status": "failed",
            "checks": [],
            "errors": [{"code": "IMAGE_NOT_FOUND", "message": f"Image not found: {path}"}],
        }

    try:
        width, height, pixels = _read_png_pixels(path)
    except VisualQaError as exc:
        return {
            "image": str(path),
            "status": "failed",
            "checks": [],
            "errors": [{"code": exc.code, "message": str(exc)}],
        }

    background = pixels[0]
    non_background: list[tuple[int, int]] = []
    for index, pixel in enumerate(pixels):
        if _pixel_distance(pixel, background) > background_threshold:
            non_background.append((index % width, index // width))

    subject_ratio = len(non_background) / max(1, width * height)
    checks: list[dict[str, Any]] = [
        {
            "name": "blank_check",
            "status": "ok" if subject_ratio >= min_subject_ratio else "failed",
            "evidence": {
                "subject_ratio": subject_ratio,
                "threshold": min_subject_ratio,
            },
        }
    ]

    bbox = None
    if non_background:
        xs = [point[0] for point in non_background]
        ys = [point[1] for point in non_background]
        bbox = {
            "x": min(xs),
            "y": min(ys),
            "width": max(xs) - min(xs) + 1,
            "height": max(ys) - min(ys) + 1,
        }
    bbox_width_ratio = (bbox["width"] / width) if bbox else 0.0
    bbox_height_ratio = (bbox["height"] / height) if bbox else 0.0
    checks.append(
        {
            "name": "bounding_box_check",
            "status": "ok"
            if bbox_width_ratio >= min_bbox_ratio and bbox_height_ratio >= min_bbox_ratio
            else "failed",
            "evidence": {
                "bbox": bbox,
                "width_ratio": bbox_width_ratio,
                "height_ratio": bbox_height_ratio,
                "threshold": min_bbox_ratio,
            },
        }
    )

    status = "ok" if all(check["status"] == "ok" for check in checks) else "failed"
    return {
        "image": str(path),
        "status": status,
        "width": width,
        "height": height,
        "checks": checks,
        "errors": [],
    }


def _ensure_camera(bpy_module: Any, name: str = "precision_review_camera") -> Any:
    camera_object = bpy_module.data.objects.get(name)
    if camera_object is None:
        camera_data = bpy_module.data.cameras.new(name)
        camera_object = bpy_module.data.objects.new(name, camera_data)
        bpy_module.context.collection.objects.link(camera_object)
    bpy_module.context.scene.camera = camera_object
    return camera_object


def _validate_target_objects(bpy_module: Any, target_objects: tuple[str, ...]) -> None:
    missing = [name for name in target_objects if bpy_module.data.objects.get(name) is None]
    if missing:
        raise VisualQaError(
            "TARGET_OBJECT_NOT_FOUND",
            f"Target object(s) not found in Blender scene: {', '.join(missing)}",
        )


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


def _load_model_spec_for_visual_qa(path: str | Path) -> dict[str, Any]:
    spec_path = Path(path)
    if not spec_path.exists():
        raise FileNotFoundError(f"model_spec not found: {spec_path}")
    text = spec_path.read_text(encoding="utf-8")
    if spec_path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = _load_yaml_with_fallback(text)
    if not isinstance(data, dict):
        raise ValueError(f"model_spec must be a mapping: {spec_path}")
    return data


def _load_yaml_with_fallback(text: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if isinstance(loaded, dict):
            return loaded
    except ModuleNotFoundError:
        pass

    return _parse_minimal_visual_qa_yaml(text)


def _parse_minimal_visual_qa_yaml(text: str) -> dict[str, Any]:
    spec: dict[str, Any] = {"objects": [], "visual_qa": {}}
    section: str | None = None
    current_object: dict[str, Any] | None = None

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if not line.startswith(" ") and stripped.endswith(":"):
            section = stripped[:-1]
            current_object = None
            continue
        if section == "objects":
            if stripped.startswith("- "):
                current_object = {}
                spec["objects"].append(current_object)
                item = stripped[2:]
                if ":" in item:
                    key, value = item.split(":", 1)
                    current_object[key.strip()] = _parse_minimal_yaml_value(value.strip())
            elif current_object is not None and ":" in stripped:
                key, value = stripped.split(":", 1)
                current_object[key.strip()] = _parse_minimal_yaml_value(value.strip())
        elif section == "visual_qa" and ":" in stripped:
            key, value = stripped.split(":", 1)
            spec["visual_qa"][key.strip()] = _parse_minimal_yaml_value(value.strip())

    return spec


def _parse_minimal_yaml_value(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        items = [item.strip() for item in value[1:-1].split(",") if item.strip()]
        parsed_items: list[Any] = []
        for item in items:
            try:
                parsed_items.append(int(item))
            except ValueError:
                parsed_items.append(item.strip("\"'"))
        return parsed_items
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value.strip("\"'")


def _capture_entries(plan: ReviewCapturePlan, artifacts: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "view": view,
            "image_path": artifact,
            "camera": "precision_review_camera",
            "target_objects": list(plan.target_objects),
        }
        for view, artifact in zip(plan.views, artifacts, strict=True)
    ]


def _status_from_quality_checks(quality_checks: list[dict[str, Any]]) -> str:
    if not quality_checks:
        return "captured"
    if any(check.get("status") == "failed" for check in quality_checks):
        return "failed"
    return "captured"


def _read_png_pixels(path: Path) -> tuple[int, int, list[tuple[int, int, int, int]]]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise VisualQaError("IMAGE_FORMAT_UNSUPPORTED", f"Not a PNG image: {path}")

    offset = 8
    width = 0
    height = 0
    bit_depth = 0
    color_type = 0
    compressed = bytearray()
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        offset += length + 12
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", chunk_data)
        elif chunk_type == b"IDAT":
            compressed.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    if bit_depth != 8 or color_type not in {0, 2, 6}:
        raise VisualQaError(
            "IMAGE_FORMAT_UNSUPPORTED",
            f"Unsupported PNG format: bit_depth={bit_depth}, color_type={color_type}",
        )

    channels = {0: 1, 2: 3, 6: 4}[color_type]
    row_size = width * channels
    raw = zlib.decompress(bytes(compressed))
    rows: list[bytes] = []
    cursor = 0
    previous = bytes(row_size)
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        row = bytearray(raw[cursor : cursor + row_size])
        cursor += row_size
        row = _unfilter_png_row(filter_type, row, previous, channels)
        rows.append(bytes(row))
        previous = bytes(row)

    pixels: list[tuple[int, int, int, int]] = []
    for row in rows:
        for x in range(width):
            start = x * channels
            if color_type == 0:
                value = row[start]
                pixels.append((value, value, value, 255))
            elif color_type == 2:
                pixels.append((row[start], row[start + 1], row[start + 2], 255))
            else:
                pixels.append((row[start], row[start + 1], row[start + 2], row[start + 3]))
    return width, height, pixels


def _unfilter_png_row(
    filter_type: int,
    row: bytearray,
    previous: bytes,
    bytes_per_pixel: int,
) -> bytearray:
    for index, value in enumerate(row):
        left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
        up = previous[index]
        upper_left = previous[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
        if filter_type == 0:
            restored = value
        elif filter_type == 1:
            restored = value + left
        elif filter_type == 2:
            restored = value + up
        elif filter_type == 3:
            restored = value + ((left + up) // 2)
        elif filter_type == 4:
            restored = value + _paeth_predictor(left, up, upper_left)
        else:
            raise VisualQaError("IMAGE_FORMAT_UNSUPPORTED", f"Unsupported PNG filter: {filter_type}")
        row[index] = restored & 0xFF
    return row


def _paeth_predictor(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    left_distance = abs(estimate - left)
    up_distance = abs(estimate - up)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= up_distance and left_distance <= upper_left_distance:
        return left
    if up_distance <= upper_left_distance:
        return up
    return upper_left


def _pixel_distance(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> int:
    return max(abs(a[channel] - b[channel]) for channel in range(4))
