from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
CHARACTER_SPEC_TEMPLATE = ROOT / "templates" / "precision" / "character_spec.yaml"
PIPELINE_SPEC_TEMPLATE = ROOT / "templates" / "precision" / "pipeline_spec.yaml"
CHARACTER_SPEC_SCHEMA = ROOT / "schemas" / "precision" / "character_spec.schema.json"
PIPELINE_SPEC_SCHEMA = ROOT / "schemas" / "precision" / "pipeline_spec.schema.json"


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def test_character_spec_template_matches_schema():
    template = _load_yaml(CHARACTER_SPEC_TEMPLATE)
    schema = _load_json(CHARACTER_SPEC_SCHEMA)

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=template, schema=schema)

    assert template["character_type"] == "humanoid"
    assert "required_expressions" in template["expression_spec"]


def test_pipeline_spec_template_matches_schema():
    template = _load_yaml(PIPELINE_SPEC_TEMPLATE)
    schema = _load_json(PIPELINE_SPEC_SCHEMA)

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=template, schema=schema)

    assert template["fallback_plan"]["live_execution_route"] == "blender_background"
    assert "shape_stage" in template
