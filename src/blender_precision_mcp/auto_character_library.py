from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LIBRARY_ROOT = ROOT / "templates" / "precision" / "libraries"
SUPPORTED_CHARACTER_TYPES = ("humanoid", "chibi", "creature")
LIBRARY_FILE_NAMES = {
    "shape_template": "shape_template.yaml",
    "rig_template": "rig_template.yaml",
    "expression_library": "expression_library.yaml",
    "pose_test_library": "pose_test_library.yaml",
    "material_preset": "material_preset.yaml",
    "hair_preset": "hair_preset.yaml",
}


@dataclass(frozen=True, slots=True)
class CharacterLibraryBundle:
    character_type: str
    shape_template: dict[str, Any]
    rig_template: dict[str, Any]
    expression_library: dict[str, Any]
    pose_test_library: dict[str, Any]
    material_preset: dict[str, Any]
    hair_preset: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "character_type": self.character_type,
            "shape_template": self.shape_template,
            "rig_template": self.rig_template,
            "expression_library": self.expression_library,
            "pose_test_library": self.pose_test_library,
            "material_preset": self.material_preset,
            "hair_preset": self.hair_preset,
        }


def load_character_library(
    character_type: str,
    base_path: str | Path = DEFAULT_LIBRARY_ROOT,
) -> CharacterLibraryBundle:
    if character_type not in SUPPORTED_CHARACTER_TYPES:
        known = ", ".join(SUPPORTED_CHARACTER_TYPES)
        raise ValueError(f"unsupported character_type '{character_type}'. Known: {known}")

    library_dir = Path(base_path) / character_type
    return CharacterLibraryBundle(
        character_type=character_type,
        shape_template=_load_yaml_mapping(library_dir / LIBRARY_FILE_NAMES["shape_template"]),
        rig_template=_load_yaml_mapping(library_dir / LIBRARY_FILE_NAMES["rig_template"]),
        expression_library=_load_yaml_mapping(library_dir / LIBRARY_FILE_NAMES["expression_library"]),
        pose_test_library=_load_yaml_mapping(library_dir / LIBRARY_FILE_NAMES["pose_test_library"]),
        material_preset=_load_yaml_mapping(library_dir / LIBRARY_FILE_NAMES["material_preset"]),
        hair_preset=_load_yaml_mapping(library_dir / LIBRARY_FILE_NAMES["hair_preset"]),
    )


def load_all_character_libraries(
    base_path: str | Path = DEFAULT_LIBRARY_ROOT,
) -> dict[str, CharacterLibraryBundle]:
    return {
        character_type: load_character_library(character_type, base_path=base_path)
        for character_type in SUPPORTED_CHARACTER_TYPES
    }


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"library file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"library file must be a mapping: {path}")
    return data
