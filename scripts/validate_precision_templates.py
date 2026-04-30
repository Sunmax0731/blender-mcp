from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> Any:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyYAML is required. Run with: "
            "uv run --with pyyaml --with jsonschema python scripts/validate_precision_templates.py"
        ) from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(instance_path: Path, schema_path: Path) -> None:
    try:
        import jsonschema
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "jsonschema is required. Run with: "
            "uv run --with pyyaml --with jsonschema python scripts/validate_precision_templates.py"
        ) from exc

    if instance_path.suffix.lower() in {".yaml", ".yml"}:
        instance = _load_yaml(instance_path)
    else:
        instance = _load_json(instance_path)
    schema = _load_json(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=instance, schema=schema)


def _validate_toml(path: Path) -> None:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    servers = data.get("mcp_servers")
    if not isinstance(servers, dict) or "blender_precision" not in servers:
        raise ValueError(f"{path} must define mcp_servers.blender_precision")

    server = servers["blender_precision"]
    for key in ("command", "args", "startup_timeout_sec", "tool_timeout_sec"):
        if key not in server:
            raise ValueError(f"{path} missing mcp_servers.blender_precision.{key}")

    if "execute_blender_code" not in server.get("disabled_tools", []):
        raise ValueError(f"{path} should disable execute_blender_code by default")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Blender precision templates and schemas."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    root = args.root.resolve()
    pairs = [
        (
            root / "templates/precision/model_spec.yaml",
            root / "schemas/precision/model_spec.schema.json",
        ),
        (
            root / "templates/precision/addon_registry.yaml",
            root / "schemas/precision/addon_registry.schema.json",
        ),
        (
            root / "templates/precision/validation_report.example.json",
            root / "schemas/precision/validation_report.schema.json",
        ),
    ]

    try:
        for instance_path, schema_path in pairs:
            _validate(instance_path, schema_path)
            print(f"ok: {instance_path.relative_to(root)}")
        _validate_toml(root / "templates/precision/codex_config.toml")
        print("ok: templates/precision/codex_config.toml")
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
