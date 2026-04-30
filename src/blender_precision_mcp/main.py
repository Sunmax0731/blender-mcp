from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH
from .config import load_precision_config
from .config import parse_tool_packs
from .server import create_mcp_server


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blender-precision-mcp",
        description="Sidecar MCP server for precision Blender workflows.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--profile", default="precise")
    parser.add_argument(
        "--tool-pack",
        default=None,
        help="Comma-separated tool pack list. Defaults to the selected profile.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load config and print the resolved summary without starting stdio MCP.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    config = load_precision_config(args.config)
    resolved = config.resolve_profile(
        args.profile,
        requested_tool_packs=parse_tool_packs(args.tool_pack),
    )

    if args.dry_run:
        print(json.dumps(resolved.to_summary(), ensure_ascii=False, indent=2))
        return 0

    server = create_mcp_server(resolved)
    server.run("stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
