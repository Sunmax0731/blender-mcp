from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_precision_mcp.visual_qa import capture_review_views  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture or plan Blender precision review views.")
    parser.add_argument("--spec", default="templates/precision/model_spec.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--views", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    views = tuple(part.strip() for part in args.views.split(",")) if args.views else None
    result = capture_review_views(
        spec_path=args.spec,
        output_dir=args.output_dir,
        views=views,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
