from __future__ import annotations

import bpy

from .service_definitions import SERVICE_DEFINITIONS
from .service_definitions import VISIBLE_SERVICE_DEFINITIONS
from .service_definitions import ExternalServiceDefinition
from .service_definitions import get_service_definition
from .services.plugin_bridge import inspect_plugin_bridge


def addon_package_name() -> str:
    return __package__.split(".", 1)[0]


def get_addon_preferences(context) -> "BLENDERMCP_AP_preferences":
    return context.preferences.addons[addon_package_name()].preferences


def get_service_settings(preferences: "BLENDERMCP_AP_preferences", service_key: str) -> dict[str, object]:
    definition = get_service_definition(service_key)
    return {
        "key": definition.key,
        "label": definition.label,
        "enabled": bool(getattr(preferences, f"{service_key}_enabled")),
        "api_key": str(getattr(preferences, f"{service_key}_api_key")),
        "endpoint": str(getattr(preferences, f"{service_key}_endpoint")),
        "mode": str(getattr(preferences, f"{service_key}_mode")),
        "requires_api_key": definition.requires_api_key,
        "notes": definition.notes,
        "visible_in_ui": definition.visible_in_ui,
    }


def build_service_overview(preferences: "BLENDERMCP_AP_preferences", bpy_module=None) -> str:
    lines: list[str] = []
    for definition in VISIBLE_SERVICE_DEFINITIONS:
        settings = get_service_settings(preferences, definition.key)
        api_key_state = "設定済み" if settings["api_key"] else ("不要" if not definition.requires_api_key else "未設定")
        enabled_label = "有効" if settings["enabled"] else "無効"
        line = f"{definition.label}: {enabled_label} / mode={settings['mode']} / api_key={api_key_state}"
        if bpy_module is not None and settings["mode"] == "plugin_bridge":
            bridge = inspect_plugin_bridge(bpy_module, definition.key)
            line = f"{line} / {bridge['summary']}"
        lines.append(line)
    return "\n".join(lines)


def _service_mode_items(_: ExternalServiceDefinition) -> tuple[tuple[str, str, str], ...]:
    return (
        ("cloud_api", "Cloud API", "クラウド API を使います。"),
        ("direct_api", "Direct API", "公開 API を直接呼び出します。"),
        ("plugin_bridge", "Plugin Bridge", "既存プラグイン連携を使います。"),
        ("disabled", "Disabled", "このサービス連携を明示的に無効化します。"),
    )


class BLENDERMCP_AP_preferences(bpy.types.AddonPreferences):
    bl_idname = addon_package_name()

    meshy_enabled: bpy.props.BoolProperty(name="Meshy Enabled", default=False)
    meshy_api_key: bpy.props.StringProperty(name="Meshy API Key", default="", subtype="PASSWORD")
    meshy_endpoint: bpy.props.StringProperty(name="Meshy Endpoint", default="https://api.meshy.ai")
    meshy_mode: bpy.props.EnumProperty(
        name="Meshy Mode",
        items=_service_mode_items(get_service_definition("meshy")),
        default="cloud_api",
    )

    tripo_enabled: bpy.props.BoolProperty(name="Tripo Enabled", default=False)
    tripo_api_key: bpy.props.StringProperty(name="Tripo API Key", default="", subtype="PASSWORD")
    tripo_endpoint: bpy.props.StringProperty(name="Tripo Endpoint", default="https://api.tripo3d.ai/v2/openapi")
    tripo_mode: bpy.props.EnumProperty(
        name="Tripo Mode",
        items=_service_mode_items(get_service_definition("tripo")),
        default="cloud_api",
    )

    rodin_enabled: bpy.props.BoolProperty(name="Rodin Enabled", default=False)
    rodin_api_key: bpy.props.StringProperty(name="Rodin API Key", default="", subtype="PASSWORD")
    rodin_endpoint: bpy.props.StringProperty(name="Rodin Endpoint", default="https://api.hyper3d.com")
    rodin_mode: bpy.props.EnumProperty(
        name="Rodin Mode",
        items=_service_mode_items(get_service_definition("rodin")),
        default="cloud_api",
    )

    spar3d_enabled: bpy.props.BoolProperty(name="SPAR3D Enabled", default=False)
    spar3d_api_key: bpy.props.StringProperty(name="SPAR3D API Key", default="", subtype="PASSWORD")
    spar3d_endpoint: bpy.props.StringProperty(
        name="SPAR3D Endpoint",
        default="https://platform.stability.ai/v1/3d/stable-point-aware-3d",
    )
    spar3d_mode: bpy.props.EnumProperty(
        name="SPAR3D Mode",
        items=_service_mode_items(get_service_definition("spar3d")),
        default="cloud_api",
    )

    polyhaven_enabled: bpy.props.BoolProperty(name="Poly Haven Enabled", default=False)
    polyhaven_api_key: bpy.props.StringProperty(name="Poly Haven API Key", default="", subtype="PASSWORD")
    polyhaven_endpoint: bpy.props.StringProperty(name="Poly Haven Endpoint", default="https://api.polyhaven.com")
    polyhaven_mode: bpy.props.EnumProperty(
        name="Poly Haven Mode",
        items=_service_mode_items(get_service_definition("polyhaven")),
        default="direct_api",
    )

    def draw(self, context):
        del context
        layout = self.layout
        layout.label(text="External Services")
        layout.label(text="Preferences で API キーと endpoint をサービス単位で管理します。")

        for definition in VISIBLE_SERVICE_DEFINITIONS:
            self._draw_service_box(layout.box(), definition)

    def _draw_service_box(self, layout, definition: ExternalServiceDefinition) -> None:
        enabled_attr = f"{definition.key}_enabled"
        api_key_attr = f"{definition.key}_api_key"
        endpoint_attr = f"{definition.key}_endpoint"
        mode_attr = f"{definition.key}_mode"

        header = layout.row()
        header.prop(self, enabled_attr, text=definition.label)
        layout.prop(self, mode_attr, text="Mode")
        layout.prop(self, endpoint_attr, text="Endpoint")
        layout.prop(self, api_key_attr, text="API Key")
        layout.label(text=definition.notes)
