param(
    [string]$BlenderExe,
    [string]$AddonSourceRoot
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

function Copy-AddonSource {
    param(
        [string]$SourceRoot,
        [string]$StageRoot
    )

    $sourceDir = Join-Path $SourceRoot 'blender_mcp'
    if (-not (Test-Path $sourceDir)) {
        throw "Supplemental add-on source was not found: $sourceDir"
    }

    Get-ChildItem -Path $sourceDir -Recurse -File |
        Where-Object {
            $_.FullName -notmatch '\\__pycache__\\' -and
            $_.Extension -notin @('.pyc', '.pyo', '.pyd')
        } |
        ForEach-Object {
            $relative = $_.FullName.Substring($sourceDir.Length).TrimStart('\')
            $destination = Join-Path (Join-Path $StageRoot 'blender_mcp') $relative
            $destinationDir = Split-Path -Parent $destination
            New-Item -ItemType Directory -Force -Path $destinationDir | Out-Null
            Copy-Item $_.FullName $destination -Force
        }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
if (-not $AddonSourceRoot) {
    $AddonSourceRoot = Join-Path $repoRoot 'blender_addon'
}

$workDir = Join-Path $repoRoot 'tmp\supplemental-addon'
$stageDir = Join-Path $workDir 'stage'
$zipPath = Join-Path $workDir 'blender_mcp_addon.zip'
$scriptPath = Join-Path $workDir 'install_supplemental_blender_addon.py'
New-Item -ItemType Directory -Force -Path $stageDir | Out-Null
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}
if (Test-Path (Join-Path $stageDir 'blender_mcp')) {
    Remove-Item (Join-Path $stageDir 'blender_mcp') -Recurse -Force
}

Copy-AddonSource -SourceRoot $AddonSourceRoot -StageRoot $stageDir
Compress-Archive -Path (Join-Path $stageDir 'blender_mcp') -DestinationPath $zipPath -Force

$pythonScript = @'
import addon_utils
import bpy


MODULE_NAME = "blender_mcp"


def main() -> int:
    bpy.ops.preferences.addon_install(filepath=ZIP_PATH, overwrite=True)
    addon_utils.enable(MODULE_NAME, default_set=True, persistent=True)
    bpy.ops.wm.save_userpref()

    enabled = addon_utils.check(MODULE_NAME)
    print(f"SUPPLEMENTAL_ADDON_MODULE={MODULE_NAME}")
    print(f"SUPPLEMENTAL_ADDON_ENABLED={enabled}")
    return 0 if enabled[1] else 1


if __name__ == "__main__":
    raise SystemExit(main())
'@

$pythonScript = $pythonScript.Replace('ZIP_PATH', [System.String]::Concat('"', $zipPath.Replace('\', '\\'), '"'))
$encoding = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($scriptPath, $pythonScript, $encoding)

$resolvedBlenderExe = Resolve-BlenderExe -ExplicitPath $BlenderExe
& $resolvedBlenderExe --background --python $scriptPath
if ($LASTEXITCODE -ne 0) {
    throw "Supplemental Blender add-on install failed with exit code $LASTEXITCODE"
}
