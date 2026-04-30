from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path("templates/precision/blender_precision_config.yaml")


@dataclass(frozen=True, slots=True)
class PrecisionServerConfig:
    name: str
    version: str
    log_dir: str
    strict: bool


@dataclass(frozen=True, slots=True)
class BlenderConnectionConfig:
    host: str
    port: int
    connection_timeout_sec: int
    operation_timeout_sec: int


@dataclass(frozen=True, slots=True)
class PrecisionProfile:
    name: str
    tool_packs: tuple[str, ...]
    allow_destructive_ops: bool
    allow_raw_code_execution: bool
    require_backup_for_destructive_ops: bool


@dataclass(frozen=True, slots=True)
class PrecisionPolicy:
    allow_unknown_addons: bool
    allow_enable_addon: str
    allow_modal_operator: bool
    require_backup_for_destructive_ops: bool
    require_license_metadata: bool
    block_tools: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PrecisionConfig:
    path: Path
    server: PrecisionServerConfig
    blender: BlenderConnectionConfig
    profiles: dict[str, PrecisionProfile]
    tool_packs: dict[str, tuple[str, ...]]
    policy: PrecisionPolicy
    approved_addons: tuple[dict[str, Any], ...]

    def resolve_profile(
        self,
        profile_name: str,
        requested_tool_packs: tuple[str, ...] | None = None,
    ) -> "ResolvedPrecisionConfig":
        if profile_name not in self.profiles:
            known = ", ".join(sorted(self.profiles))
            raise ValueError(f"unknown profile '{profile_name}'. Known profiles: {known}")

        profile = self.profiles[profile_name]
        selected_tool_packs = requested_tool_packs or profile.tool_packs
        unknown_tool_packs = [name for name in selected_tool_packs if name not in self.tool_packs]
        if unknown_tool_packs:
            known = ", ".join(sorted(self.tool_packs))
            raise ValueError(
                f"unknown tool pack(s): {', '.join(unknown_tool_packs)}. Known tool packs: {known}"
            )

        tools: list[str] = []
        for pack_name in selected_tool_packs:
            for tool_name in self.tool_packs[pack_name]:
                if tool_name not in tools and tool_name not in self.policy.block_tools:
                    tools.append(tool_name)

        return ResolvedPrecisionConfig(
            config=self,
            profile=profile,
            selected_tool_packs=selected_tool_packs,
            enabled_tools=tuple(tools),
        )


@dataclass(frozen=True, slots=True)
class ResolvedPrecisionConfig:
    config: PrecisionConfig
    profile: PrecisionProfile
    selected_tool_packs: tuple[str, ...]
    enabled_tools: tuple[str, ...]

    def to_summary(self) -> dict[str, Any]:
        return {
            "server": {
                "name": self.config.server.name,
                "version": self.config.server.version,
                "strict": self.config.server.strict,
            },
            "blender": {
                "host": self.config.blender.host,
                "port": self.config.blender.port,
                "connection_timeout_sec": self.config.blender.connection_timeout_sec,
                "operation_timeout_sec": self.config.blender.operation_timeout_sec,
            },
            "profile": self.profile.name,
            "tool_packs": list(self.selected_tool_packs),
            "control_tools": [
                "precision_status",
                "precision_get_config_summary",
            ],
            "enabled_tools": list(self.enabled_tools),
            "blocked_tools": list(self.config.policy.block_tools),
            "approved_addon_count": len(self.config.approved_addons),
        }


def load_precision_config(path: str | Path = DEFAULT_CONFIG_PATH) -> PrecisionConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"precision config not found: {config_path}")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"precision config must be a mapping: {config_path}")

    server_raw = _mapping(raw, "server")
    blender_raw = _mapping(raw, "blender")
    profiles_raw = _mapping(raw, "profiles")
    tool_packs_raw = _mapping(raw, "tool_packs")
    policy_raw = _mapping(raw, "policy")

    profiles = {
        name: PrecisionProfile(
            name=name,
            tool_packs=tuple(_string_list(value, "tool_packs")),
            allow_destructive_ops=bool(value.get("allow_destructive_ops", False)),
            allow_raw_code_execution=bool(value.get("allow_raw_code_execution", False)),
            require_backup_for_destructive_ops=bool(
                value.get("require_backup_for_destructive_ops", False)
            ),
        )
        for name, value in profiles_raw.items()
        if isinstance(value, dict)
    }
    if not profiles:
        raise ValueError("precision config must define at least one profile")

    tool_packs = {
        name: tuple(_string_list(value, "enabled_tools"))
        for name, value in tool_packs_raw.items()
        if isinstance(value, dict)
    }
    if not tool_packs:
        raise ValueError("precision config must define at least one tool pack")

    policy = PrecisionPolicy(
        allow_unknown_addons=bool(policy_raw.get("allow_unknown_addons", False)),
        allow_enable_addon=str(policy_raw.get("allow_enable_addon", "approved_only")),
        allow_modal_operator=bool(policy_raw.get("allow_modal_operator", False)),
        require_backup_for_destructive_ops=bool(
            policy_raw.get("require_backup_for_destructive_ops", True)
        ),
        require_license_metadata=bool(policy_raw.get("require_license_metadata", True)),
        block_tools=tuple(_string_list(policy_raw, "block_tools")),
    )

    return PrecisionConfig(
        path=config_path,
        server=PrecisionServerConfig(
            name=str(server_raw.get("name", "blender-precision-mcp")),
            version=str(server_raw.get("version", "0.1.0")),
            log_dir=str(server_raw.get("log_dir", "outputs/logs")),
            strict=bool(server_raw.get("strict", True)),
        ),
        blender=BlenderConnectionConfig(
            host=str(blender_raw.get("host", "127.0.0.1")),
            port=int(blender_raw.get("port", 9876)),
            connection_timeout_sec=int(blender_raw.get("connection_timeout_sec", 10)),
            operation_timeout_sec=int(blender_raw.get("operation_timeout_sec", 180)),
        ),
        profiles=profiles,
        tool_packs=tool_packs,
        policy=policy,
        approved_addons=tuple(raw.get("approved_addons", [])),
    )


def parse_tool_packs(value: str | None) -> tuple[str, ...] | None:
    if value is None or value.strip() == "":
        return None
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _mapping(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"precision config must define mapping '{key}'")
    return value


def _string_list(raw: dict[str, Any], key: str) -> list[str]:
    value = raw.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"'{key}' must be a list of strings")
    return value
