from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

from blender_precision_mcp.visual_qa import analyze_review_image
from blender_precision_mcp.visual_qa import build_review_capture_plan
from blender_precision_mcp.visual_qa import capture_review_views


ROOT = Path(__file__).resolve().parents[1]
MODEL_SPEC = ROOT / "templates" / "precision" / "model_spec.yaml"


def test_build_review_capture_plan_uses_spec_views(tmp_path):
    plan = build_review_capture_plan(MODEL_SPEC, output_dir=tmp_path)

    assert plan.output_dir == tmp_path
    assert plan.views == ("front", "side", "top", "perspective")
    assert plan.resolution == (1280, 1280)
    assert plan.manifest_path == tmp_path / "review_manifest.json"
    assert plan.target_objects == ("example_body",)


def test_capture_review_views_dry_run_writes_manifest(tmp_path):
    result = capture_review_views(
        spec_path=MODEL_SPEC,
        output_dir=tmp_path,
        views=("front", "top"),
        dry_run=True,
    )

    manifest_path = Path(result["manifest_path"])
    saved = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result["status"] == "planned"
    assert saved["views"] == ["front", "top"]
    assert saved["target_objects"] == ["example_body"]
    assert saved["captures"][0]["view"] == "front"
    assert saved["captures"][0]["camera"] == "precision_review_camera"
    assert saved["artifacts"] == [str(tmp_path / "front.png"), str(tmp_path / "top.png")]


def test_capture_review_views_reports_unsupported_view(tmp_path):
    result = capture_review_views(
        spec_path=MODEL_SPEC,
        output_dir=tmp_path,
        views=("front", "diagonal"),
        dry_run=True,
    )

    assert result["status"] == "failed"
    assert result["errors"][0]["code"] == "VIEW_NOT_SUPPORTED"
    assert Path(result["manifest_path"]).exists()


def test_analyze_review_image_detects_blank_png(tmp_path):
    image_path = tmp_path / "blank.png"
    _write_rgb_png(image_path, 16, 16, lambda _x, _y: (0, 0, 0))

    result = analyze_review_image(image_path)

    assert result["status"] == "failed"
    check_statuses = {check["name"]: check["status"] for check in result["checks"]}
    assert check_statuses["blank_check"] == "failed"
    assert check_statuses["bounding_box_check"] == "failed"


def test_analyze_review_image_accepts_visible_subject_png(tmp_path):
    image_path = tmp_path / "subject.png"

    def pixel(x: int, y: int) -> tuple[int, int, int]:
        if 4 <= x <= 11 and 4 <= y <= 11:
            return 255, 255, 255
        return 0, 0, 0

    _write_rgb_png(image_path, 16, 16, pixel)

    result = analyze_review_image(image_path)

    assert result["status"] == "ok"
    bbox_check = next(check for check in result["checks"] if check["name"] == "bounding_box_check")
    assert bbox_check["evidence"]["bbox"] == {"x": 4, "y": 4, "width": 8, "height": 8}


def _write_rgb_png(path: Path, width: int, height: int, pixel_func) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixel_func(x, y))

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        checksum = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", checksum)

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
    png.extend(chunk(b"IDAT", zlib.compress(bytes(raw))))
    png.extend(chunk(b"IEND", b""))
    path.write_bytes(bytes(png))
