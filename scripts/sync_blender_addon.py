from __future__ import annotations

import argparse
from pathlib import Path

from blender_automation import ADDON_SOURCE_DIR
from blender_automation import resolve_addons_dir
from blender_automation import sync_addon_directory


def main() -> int:
    parser = argparse.ArgumentParser(description="Blender add-ons ??????? add-on ???????")
    parser.add_argument("--source-dir", default=str(ADDON_SOURCE_DIR))
    parser.add_argument("--target-root", default=str(resolve_addons_dir()))
    args = parser.parse_args()

    target_dir = sync_addon_directory(
        source_dir=Path(args.source_dir),
        target_root=Path(args.target_root),
    )
    print(f"Synchronized add-on directory: {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
