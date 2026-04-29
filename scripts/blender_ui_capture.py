from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

import addon_utils
import bpy


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Blender MCP UI の自動キャプチャ")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--server-url", default="http://127.0.0.1:8765")
    parser.add_argument("--prompt", default="UI スモーク確認")
    parser.add_argument("--prompt-file")
    parser.add_argument("--screenshot-name", default="blender-mcp-ui.png")
    parser.add_argument("--report-name", default="blender-mcp-ui-report.json")
    parser.add_argument("--wait-seconds", type=float, default=5.0)
    parser.add_argument("--send-prompt", action="store_true")
    return parser.parse_args(argv)


ARGS = parse_args()
OUTPUT_DIR = Path(ARGS.output_dir)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_PATH = OUTPUT_DIR / ARGS.screenshot_name
REPORT_PATH = OUTPUT_DIR / ARGS.report_name
CAPTURE_CONTEXT = {}

PROMPT_TEXT = ARGS.prompt
if ARGS.prompt_file:
    PROMPT_TEXT = Path(ARGS.prompt_file).read_text(encoding="utf-8-sig")

RUNTIME = {
    "outputDir": str(OUTPUT_DIR),
    "screenshotPath": str(SCREENSHOT_PATH),
    "reportPath": str(REPORT_PATH),
    "prompt": PROMPT_TEXT,
    "serverUrl": ARGS.server_url,
}


def _write_report(extra: dict[str, object]) -> None:
    payload = dict(RUNTIME)
    payload.update(extra)
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
def _find_view3d_context():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            window_region = next((region for region in area.regions if region.type == "WINDOW"), None)
            ui_region = next((region for region in area.regions if region.type == "UI"), None)
            if window_region is None:
                continue
            return window, area, window_region, ui_region
    raise RuntimeError("VIEW_3D area was not found.")


def _ensure_addon_enabled() -> None:
    module_name = "blender_mcp"
    is_enabled, is_loaded = addon_utils.check(module_name)
    if is_enabled and is_loaded:
        return
    addon_utils.enable(module_name, default_set=True, persistent=False)
    is_enabled, is_loaded = addon_utils.check(module_name)
    if not (is_enabled and is_loaded):
        raise RuntimeError("blender_mcp add-on could not be enabled.")


def _prepare_ui_state() -> dict[str, object]:
    _ensure_addon_enabled()
    bpy.context.preferences.view.show_splash = False
    window, area, window_region, ui_region = _find_view3d_context()

    ui_region = next((region for region in area.regions if region.type == "UI"), ui_region)
    if ui_region is not None and hasattr(ui_region, "active_panel_category"):
        try:
            ui_region.active_panel_category = "Blender MCP"
        except AttributeError:
            pass

    state = bpy.context.scene.blender_mcp_state
    state.server_url = ARGS.server_url
    state.prompt_text = PROMPT_TEXT
    state.last_result_text = "UI smoke capture completed."

    with bpy.context.temp_override(window=window, area=area, region=window_region):
        connect_result = bpy.ops.blendermcp.connect()
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)
        send_result = None
        if ARGS.send_prompt:
            send_result = bpy.ops.blendermcp.send_prompt()
            bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

    CAPTURE_CONTEXT.update({"window": window, "area": area, "region": window_region})

    report = {
        "connectResult": list(connect_result),
        "uiState": state.ui_state,
        "connectionLabel": state.connection_label,
        "historyText": state.history_text,
        "lastResultText": state.last_result_text,
        "lastError": state.last_error,
        "blenderVersion": state.blender_version,
        "addonVersion": state.addon_version,
        "sendPromptEnabled": bool(ARGS.send_prompt),
        "sendResult": list(send_result) if send_result is not None else None,
        "kirbyBaseExists": "Kirby_Base" in bpy.data.objects,
    }
    if "Kirby_Base" in bpy.data.objects:
        report["kirbyBaseType"] = getattr(bpy.data.objects["Kirby_Base"], "type", "UNKNOWN")
    return report


def _capture_and_exit() -> None:
    try:
        status = _prepare_ui_state()
        bpy.ops.screen.screenshot(filepath=str(SCREENSHOT_PATH))
        _write_report({"success": True, **status})
    except Exception as exc:  # noqa: BLE001
        _write_report(
            {
                "success": False,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
        )
    finally:
        bpy.ops.wm.quit_blender()


def main() -> None:
    bpy.app.timers.register(_capture_and_exit, first_interval=max(0.1, ARGS.wait_seconds))


main()
