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
$tempScriptPath = Join-Path $scriptDir '..\tmp\enable_official_blender_mcp_addon.py'
$pythonScript = @'
import addon_utils
import bpy


def resolve_official_keys():
    candidate_keys = []
    for module in addon_utils.modules():
        module_name = module.__name__
        if module_name == "mcp" or module_name.endswith(".mcp"):
            candidate_keys.append(module_name)

    for addon_key in bpy.context.preferences.addons.keys():
        if addon_key == "mcp" or addon_key.endswith(".mcp"):
            if addon_key not in candidate_keys:
                candidate_keys.append(addon_key)

    if not candidate_keys:
        candidate_keys = ["mcp"]

    return candidate_keys


official_keys = resolve_official_keys()

before_states = {key: addon_utils.check(key) for key in official_keys}

enabled_key = None
for key in official_keys:
    addon_utils.enable(key, default_set=True, persistent=True)
    if addon_utils.check(key)[1]:
        enabled_key = key
        break

bpy.ops.wm.save_userpref()

after_states = {key: addon_utils.check(key) for key in official_keys}

print(f"OFFICIAL_KEYS={official_keys}")
print(f"OFFICIAL_BEFORE={before_states}")
print(f"ENABLED_KEY={enabled_key}")
print(f"OFFICIAL_AFTER={after_states}")

if enabled_key is not None:
    prefs = bpy.context.preferences.addons[enabled_key].preferences
    print(f"HOST={getattr(prefs, 'host', None)}")
    print(f"PORT={getattr(prefs, 'port', None)}")
    print(f"AUTOSTART={getattr(prefs, 'use_autostart', None)}")
'@

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $tempScriptPath) | Out-Null
$encoding = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($tempScriptPath, $pythonScript, $encoding)

& $resolvedBlenderExe --background --online-mode --python $tempScriptPath
exit $LASTEXITCODE
