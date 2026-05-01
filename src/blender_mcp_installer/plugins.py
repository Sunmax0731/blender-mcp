from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ThirdPartyPlugin:
    key: str
    name: str
    install_method: str
    display_name: str
    payload_relpath: str
    fallback_url: str
    module_name_hints: tuple[str, ...]
    install_by_default: bool = True
    repository_id: str = "user_default"


def default_manifest_path(root: Path) -> Path:
    return root / "templates" / "installer" / "third_party_plugins.json"


def load_third_party_plugins(root: Path) -> list[ThirdPartyPlugin]:
    manifest_path = default_manifest_path(root)
    if not manifest_path.exists():
        return []

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    plugins: list[ThirdPartyPlugin] = []
    for item in data.get("plugins", []):
        plugins.append(
            ThirdPartyPlugin(
                key=str(item["key"]),
                name=str(item["name"]),
                install_method=str(item["install_method"]),
                display_name=str(item["display_name"]),
                payload_relpath=str(item["payload_relpath"]),
                fallback_url=str(item.get("fallback_url", "")),
                module_name_hints=tuple(str(value) for value in item.get("module_name_hints", [])),
                install_by_default=bool(item.get("install_by_default", True)),
                repository_id=str(item.get("repository_id", "user_default")),
            )
        )
    return plugins


def default_plugin_keys(root: Path) -> list[str]:
    return [plugin.key for plugin in load_third_party_plugins(root) if plugin.install_by_default]
