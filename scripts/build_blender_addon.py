from __future__ import annotations

import argparse
from pathlib import Path

from blender_automation import ADDON_SOURCE_DIR
from blender_automation import DEFAULT_ZIP_PATH
from blender_automation import build_addon_zip


def main() -> int:
    parser = argparse.ArgumentParser(description="Blender MCP add-on zip ???????")
    parser.add_argument("--source-dir", default=str(ADDON_SOURCE_DIR))
    parser.add_argument("--zip-path", default=str(DEFAULT_ZIP_PATH))
    args = parser.parse_args()

    zip_path = build_addon_zip(source_dir=Path(args.source_dir), zip_path=Path(args.zip_path))
    print(f"Generated add-on zip: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
