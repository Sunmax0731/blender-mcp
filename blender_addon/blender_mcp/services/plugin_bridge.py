from __future__ import annotations

from dataclasses import dataclass
import json


@dataclass(frozen=True, slots=True)
class PluginBridgeDefinition:
    service_key: str
    addon_display_names: tuple[str, ...]
    addon_module_hints: tuple[str, ...]
    required_operator_ids: tuple[str, ...]


PLUGIN_BRIDGE_DEFINITIONS: dict[str, PluginBridgeDefinition] = {
    "meshy": PluginBridgeDefinition(
        service_key="meshy",
        addon_display_names=("Meshy official plugin", "Meshy"),
        addon_module_hints=("bl_ext.user_default.meshy", "meshy"),
        required_operator_ids=("meshy.bridge_start",),
    ),
    "tripo": PluginBridgeDefinition(
        service_key="tripo",
        addon_display_names=("Tripo 3D",),
        addon_module_hints=("tripo-3d-for-blender",),
        required_operator_ids=("tripo3d.generate_text_model", "tripo3d.download_task"),
    ),
    "rodin": PluginBridgeDefinition(
        service_key="rodin",
        addon_display_names=("RodinBridge",),
        addon_module_hints=("a_Rodin",),
        required_operator_ids=("rodin.submit",),
    ),
}


def inspect_plugin_bridge(bpy_module, service_key: str) -> dict[str, object]:
    definition = PLUGIN_BRIDGE_DEFINITIONS.get(service_key)
    if definition is None:
        return {
            "available": False,
            "ready": False,
            "summary": "plugin bridge 定義なし",
            "addon_module": "",
            "missing_operators": [],
        }

    addon_module_name, display_name = _find_addon_module_name(
        bpy_module,
        definition.addon_display_names,
        definition.addon_module_hints,
    )
    enabled = False
    if addon_module_name:
        enabled = addon_module_name in bpy_module.context.preferences.addons

    missing_operators = [
        operator_id for operator_id in definition.required_operator_ids if not _operator_exists(bpy_module, operator_id)
    ]
    ready = bool(addon_module_name and enabled and not missing_operators)

    if ready:
        summary = f"plugin_bridge ready ({display_name})"
    elif addon_module_name and enabled:
        summary = f"plugin_bridge operator不足: {', '.join(missing_operators)}"
    elif addon_module_name:
        summary = f"plugin_bridge add-on無効: {display_name}"
    else:
        summary = f"plugin_bridge add-on未検出: {definition.addon_display_names[0]}"

    return {
        "available": bool(addon_module_name),
        "ready": ready,
        "summary": summary,
        "addon_module": addon_module_name or "",
        "missing_operators": missing_operators,
    }


def submit_via_plugin_bridge(
    *,
    bpy_module,
    service_key: str,
    api_key: str,
    prompt: str,
    payload_json: str = "",
) -> dict[str, object]:
    bridge = inspect_plugin_bridge(bpy_module, service_key)
    if not bridge["ready"]:
        raise ValueError(str(bridge["summary"]))

    payload = json.loads(payload_json) if payload_json.strip() else {}
    if payload and not isinstance(payload, dict):
        raise ValueError("plugin_bridge の追加 JSON はオブジェクト形式で指定してください。")

    if service_key == "tripo":
        return _submit_tripo_text_generation(bpy_module, api_key=api_key, prompt=prompt, payload=payload)
    if service_key == "rodin":
        return _submit_rodin_text_generation(bpy_module, prompt=prompt, payload=payload)
    if service_key == "meshy":
        getattr(bpy_module.ops.meshy, "bridge_start")()
        return {
            "status": "bridge_started",
            "raw": {"service": "meshy", "bridge_action": "start"},
        }
    raise ValueError(f"plugin_bridge submit is not supported for {service_key}")


def _find_addon_module_name(
    bpy_module,
    addon_display_names: tuple[str, ...],
    addon_module_hints: tuple[str, ...],
) -> tuple[str | None, str]:
    addon_keys = set(getattr(bpy_module.context.preferences, "addons", {}).keys())
    for module_hint in addon_module_hints:
        if module_hint in addon_keys:
            return module_hint, addon_display_names[0]

    try:
        import addon_utils
    except ImportError:
        return None, addon_display_names[0]

    for module in addon_utils.modules():
        module_name = getattr(module, "__name__", "")
        bl_info = getattr(module, "bl_info", {}) or {}
        display_name = str(bl_info.get("name") or addon_display_names[0])
        if display_name in addon_display_names or module_name in addon_module_hints:
            return module_name, display_name

    return None, addon_display_names[0]


def _operator_exists(bpy_module, operator_id: str) -> bool:
    namespace, _, name = operator_id.partition(".")
    if not namespace or not name:
        return False
    namespace_obj = getattr(bpy_module.ops, namespace, None)
    return hasattr(namespace_obj, name)


def _submit_tripo_text_generation(bpy_module, *, api_key: str, prompt: str, payload: dict[str, object]) -> dict[str, object]:
    if not prompt.strip():
        raise ValueError("Tripo plugin_bridge では prompt が必須です。")

    scene = bpy_module.context.scene
    scene.api_key = api_key
    scene.api_key_confirmed = True
    scene.text_prompts = prompt
    scene.enable_negative_prompts = bool(payload.get("enable_negative_prompts", False))
    scene.negative_prompts = str(payload.get("negative_prompts", ""))
    scene.model_version = str(payload.get("model_version", getattr(scene, "model_version", "v2.5-20250123")))
    scene.texture = bool(payload.get("texture", getattr(scene, "texture", True)))
    scene.pbr = bool(payload.get("pbr", getattr(scene, "pbr", True)))
    scene.texture_quality = str(payload.get("texture_quality", getattr(scene, "texture_quality", "standard")))
    scene.auto_size = bool(payload.get("auto_size", getattr(scene, "auto_size", False)))
    scene.quad = bool(payload.get("quad", getattr(scene, "quad", False)))
    if "style" in payload:
        scene.style = str(payload["style"])
    if "orientation" in payload:
        scene.orientation = str(payload["orientation"])
    if "multiview_generate_mode" in payload:
        scene.multiview_generate_mode = bool(payload["multiview_generate_mode"])

    getattr(bpy_module.ops.tripo3d, "generate_text_model")()
    return {
        "status": "submitted_via_plugin_bridge",
        "raw": {
            "service": "tripo",
            "prompt": prompt,
            "model_version": scene.model_version,
            "texture_quality": scene.texture_quality,
        },
    }


def _submit_rodin_text_generation(bpy_module, *, prompt: str, payload: dict[str, object]) -> dict[str, object]:
    if not prompt.strip():
        raise ValueError("Rodin plugin_bridge では prompt が必須です。")

    rodin_prop = bpy_module.context.scene.rodin_prop
    rodin_prop.textTo = "Text"
    rodin_prop.condition_type = "image"
    rodin_prop.prompt = prompt
    rodin_prop.text_input = prompt
    if "gen_type" in payload:
        rodin_prop.gen_type = str(payload["gen_type"])
    if "version" in payload:
        rodin_prop.version = str(payload["version"])
    if "mode" in payload:
        rodin_prop.mode = str(payload["mode"])
    if "quality" in payload:
        rodin_prop.quality = int(payload["quality"])
    if "bypass" in payload:
        rodin_prop.bypass = bool(payload["bypass"])
    if "polygons" in payload:
        rodin_prop.polygons = str(payload["polygons"])

    getattr(bpy_module.ops.rodin, "submit")()
    return {
        "status": "submitted_via_plugin_bridge",
        "raw": {
            "service": "rodin",
            "prompt": prompt,
            "version": rodin_prop.version,
            "mode": rodin_prop.mode,
        },
    }
