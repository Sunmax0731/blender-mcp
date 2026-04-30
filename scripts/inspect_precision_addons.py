from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_precision_mcp.addons import get_addon_status  # noqa: E402
from blender_precision_mcp.addons import inspect_addon_capabilities  # noqa: E402
from blender_precision_mcp.addons import list_blender_addons  # noqa: E402
from blender_precision_mcp.addons import list_registered_operators  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect approved Blender precision add-ons.")
    parser.add_argument("--registry", default="templates/precision/addon_registry.yaml")
    parser.add_argument(
        "--mode",
        choices=["list", "status", "capabilities", "operators"],
        default="list",
    )
    parser.add_argument("--module", default=None)
    args = parser.parse_args()

    if args.mode == "list":
        result = list_blender_addons(args.registry)
    elif args.mode == "status":
        if not args.module:
            parser.error("--module is required for status mode")
        result = get_addon_status(args.module, args.registry)
    elif args.mode == "capabilities":
        result = inspect_addon_capabilities(args.module, args.registry)
    else:
        result = list_registered_operators(args.registry)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
