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

before_official = addon_utils.check('mcp')
before_legacy = addon_utils.check('blender_mcp')

addon_utils.enable('mcp', default_set=True, persistent=True)
if addon_utils.check('blender_mcp')[1]:
    addon_utils.disable('blender_mcp', default_set=True)

bpy.ops.wm.save_userpref()

prefs = bpy.context.preferences.addons['mcp'].preferences
print(f"OFFICIAL_BEFORE={before_official}")
print(f"LEGACY_BEFORE={before_legacy}")
print(f"OFFICIAL_AFTER={addon_utils.check('mcp')}")
print(f"LEGACY_AFTER={addon_utils.check('blender_mcp')}")
print(f"HOST={prefs.host}")
print(f"PORT={prefs.port}")
print(f"AUTOSTART={prefs.use_autostart}")
'@

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $tempScriptPath) | Out-Null
$encoding = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($tempScriptPath, $pythonScript, $encoding)

& $resolvedBlenderExe --background --online-mode --python $tempScriptPath
exit $LASTEXITCODE
