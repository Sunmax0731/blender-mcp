param(
    [string]$PythonExe,
    [switch]$SkipReload,
    [double]$ReloadDelaySeconds = 1.0
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

if (-not $PythonExe) {
    $PythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
}

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

& $PythonExe (Join-Path $repoRoot "scripts\build_blender_addon.py")
& $PythonExe (Join-Path $repoRoot "scripts\sync_blender_addon.py")

if ($SkipReload) {
    Write-Host "Add-on updated. Reload skipped by request."
    exit 0
}

$runningBlender = Get-Process -Name "blender" -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowHandle -ne 0 } |
    Sort-Object StartTime -Descending |
    Select-Object -First 1

if (-not $runningBlender) {
    Write-Host "Add-on updated. No visible Blender process found, so reload was not needed."
    exit 0
}

& $PythonExe (Join-Path $repoRoot "scripts\reload_running_blender.py") --pid $runningBlender.Id --delay-seconds $ReloadDelaySeconds
if ($LASTEXITCODE -ne 0) {
    throw "Failed to send reload command to Blender process $($runningBlender.Id)."
}
Write-Host "Add-on updated and reload command sent to Blender process $($runningBlender.Id)."
