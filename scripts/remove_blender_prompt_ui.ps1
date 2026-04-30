param(
    [string]$BlenderExe
)

$ErrorActionPreference = 'Stop'

function Resolve-BlenderExe {
    param([string]$ExplicitPath)

    $candidates = @(
        $ExplicitPath,
        $env:BLENDER_PATH,
        $env:BLENDER_EXE,
        'F:\Steam\steamapps\common\Blender\blender.exe',
        'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe',
        'C:\Program Files\Blender Foundation\Blender\blender.exe'
    ) | Where-Object { $_ }

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    $registryRoots = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )

    foreach ($root in $registryRoots) {
        $apps = Get-ItemProperty $root -ErrorAction SilentlyContinue |
            Where-Object { $_.DisplayName -like '*Blender*' }
        foreach ($app in $apps) {
            $installLocation = $app.InstallLocation
            if (-not $installLocation) {
                continue
            }

            $candidate = Join-Path $installLocation 'blender.exe'
            if (Test-Path $candidate) {
                return $candidate
            }
        }
    }

    throw 'Blender executable could not be resolved. Set -BlenderExe or BLENDER_PATH.'
}

$resolvedBlenderExe = Resolve-BlenderExe -ExplicitPath $BlenderExe
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$tempScriptPath = Join-Path $scriptDir '..\tmp\remove_blender_prompt_ui.py'
$pythonScript = @'
from pathlib import Path
import shutil

import addon_utils
import bpy


OFFICIAL_KEYS = {"mcp", "bl_ext.user_default.mcp"}
TARGET_KEYS = {"blender_mcp"}
TARGET_NAMES = {"Blender MCP"}
TARGET_AUTHORS = {"Sunmax0731"}


def is_official(module_name):
    return module_name in OFFICIAL_KEYS or module_name.endswith(".mcp")


def is_target_module(module):
    module_name = module.__name__
    if is_official(module_name):
        return False
    if module_name in TARGET_KEYS:
        return True

    info = getattr(module, "bl_info", {}) or {}
    name = info.get("name")
    author = info.get("author")
    location = info.get("location", "")
    return (
        name in TARGET_NAMES
        and (author in TARGET_AUTHORS or "Sidebar > Blender MCP" in location)
    )


def remove_preferences_entry(key):
    addons = bpy.context.preferences.addons
    if key not in addons:
        return False
    try:
        addons.remove(addons[key])
        return True
    except Exception as exc:
        print(f"PROMPT_UI_PREF_REMOVE_SKIPPED={key}: {exc}")
        return False


def backup_and_remove_module_file(path_text):
    if not path_text:
        return None

    path = Path(path_text).resolve()
    if path.name == "__init__.py":
        target = path.parent
    else:
        target = path

    if target.name != "blender_mcp" and target.name != "blender_mcp.py":
        return None

    backup = target.with_name(target.name + ".removed-by-blender-mcp-installer")
    if backup.exists():
        if backup.is_dir():
            shutil.rmtree(backup)
        else:
            backup.unlink()
    target.rename(backup)
    return str(backup)


target_modules = []
for module in addon_utils.modules():
    if is_target_module(module):
        target_modules.append(module)

removed_prefs = []
removed_files = []
checked_modules = []

for module in target_modules:
    key = module.__name__
    checked_modules.append(key)
    try:
        addon_utils.disable(key, default_set=True)
    except Exception as exc:
        print(f"PROMPT_UI_DISABLE_SKIPPED={key}: {exc}")
    if remove_preferences_entry(key):
        removed_prefs.append(key)
    try:
        backup = backup_and_remove_module_file(getattr(module, "__file__", None))
        if backup:
            removed_files.append(backup)
    except Exception as exc:
        print(f"PROMPT_UI_FILE_REMOVE_SKIPPED={key}: {exc}")

for key in list(bpy.context.preferences.addons.keys()):
    if key in TARGET_KEYS and not is_official(key):
        if remove_preferences_entry(key):
            removed_prefs.append(key)

bpy.ops.wm.save_userpref()

official_states = {
    key: addon_utils.check(key)
    for key in OFFICIAL_KEYS
    if key in bpy.context.preferences.addons.keys() or key == "mcp"
}

print(f"PROMPT_UI_CHECKED_MODULES={checked_modules}")
print(f"PROMPT_UI_REMOVED_PREFS={removed_prefs}")
print(f"PROMPT_UI_REMOVED_FILES={removed_files}")
print(f"OFFICIAL_MCP_STATES={official_states}")
'@

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $tempScriptPath) | Out-Null
$encoding = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($tempScriptPath, $pythonScript, $encoding)

& $resolvedBlenderExe --background --python $tempScriptPath
exit $LASTEXITCODE
