param(
    [string]$BlenderExe,
    [string]$PythonExe,
    [string]$ServerUrl = "http://127.0.0.1:8765",
    [string]$Prompt = "UI smoke capture",
    [double]$CaptureDelaySeconds = 5,
    [double]$AutomationDelaySeconds = 2,
    [string]$OutputDir,
    [switch]$SkipServer,
    [switch]$KeepServer
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

if (-not $BlenderExe) {
    $candidatePaths = @(
        $env:BLENDER_EXE,
        "F:\Steam\steamapps\common\Blender\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
        "C:\Program Files\Blender Foundation\Blender\blender.exe"
    ) | Where-Object { $_ }

    $BlenderExe = $candidatePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
}

if (-not $BlenderExe) {
    throw "Blender executable could not be resolved. Set -BlenderExe or BLENDER_EXE."
}

if (-not $OutputDir) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $OutputDir = Join-Path $repoRoot "artifacts\blender-ui-smoke\$timestamp"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$stdoutPath = Join-Path $OutputDir "server.stdout.log"
$stderrPath = Join-Path $OutputDir "server.stderr.log"
$baseBlend = Join-Path $repoRoot "tmp\ui_smoke_base.blend"
$automationStdout = Join-Path $OutputDir "automation.stdout.log"
$automationStderr = Join-Path $OutputDir "automation.stderr.log"

& $PythonExe (Join-Path $repoRoot "scripts\build_blender_addon.py")
& $PythonExe (Join-Path $repoRoot "scripts\sync_blender_addon.py")

if (-not (Test-Path $baseBlend)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $baseBlend) | Out-Null
    $bootstrapScript = Join-Path $OutputDir "create_ui_smoke_base.py"
    $bootstrap = @'
from pathlib import Path
import bpy
path = Path(r"D:/Claude/MCP/tmp/ui_smoke_base.blend").resolve()
path.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
'@
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($bootstrapScript, $bootstrap, $encoding)
    & $BlenderExe --background --factory-startup --python $bootstrapScript | Out-Null
}

$serverProcess = $null
$serverWasStarted = $false

function Test-ServerHealth {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "$Url/health" -TimeoutSec 2
        return ($response.StatusCode -eq 200)
    }
    catch {
        return $false
    }
}

if (-not $SkipServer) {
    if (-not (Test-ServerHealth -Url $ServerUrl)) {
        $serverProcess = Start-Process `
            -FilePath $PythonExe `
            -ArgumentList "-m", "blender_mcp_server.main" `
            -WorkingDirectory $repoRoot `
            -WindowStyle Hidden `
            -RedirectStandardOutput $stdoutPath `
            -RedirectStandardError $stderrPath `
            -PassThru
        $serverWasStarted = $true
    }

    $deadline = (Get-Date).AddSeconds(20)
    while ((Get-Date) -lt $deadline) {
        if (Test-ServerHealth -Url $ServerUrl) {
            break
        }
        Start-Sleep -Milliseconds 500
    }

    if (-not (Test-ServerHealth -Url $ServerUrl)) {
        if ($serverProcess -and -not $serverProcess.HasExited) {
            Stop-Process -Id $serverProcess.Id -Force
        }
        throw "Blender MCP server did not become healthy: $ServerUrl"
    }
}

$captureScript = Join-Path $repoRoot "scripts\blender_ui_capture.py"
$automationScript = Join-Path $repoRoot "scripts\prepare_blender_window.py"
$blenderArgs = "`"$baseBlend`" --python-exit-code 1 --python `"$captureScript`" -- --output-dir `"$OutputDir`" --server-url `"$ServerUrl`" --prompt `"$Prompt`" --wait-seconds $CaptureDelaySeconds"
$blenderProcess = Start-Process `
    -FilePath $BlenderExe `
    -ArgumentList $blenderArgs `
    -WorkingDirectory $repoRoot `
    -PassThru

$automationProcess = Start-Process `
    -FilePath $PythonExe `
    -ArgumentList $automationScript, "--pid", "$($blenderProcess.Id)", "--delay-seconds", "$AutomationDelaySeconds" `
    -WorkingDirectory $repoRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $automationStdout `
    -RedirectStandardError $automationStderr `
    -PassThru

Wait-Process -Id $blenderProcess.Id
$blenderExitCode = $blenderProcess.ExitCode

if ($serverWasStarted -and -not $KeepServer -and $serverProcess -and -not $serverProcess.HasExited) {
    Stop-Process -Id $serverProcess.Id -Force
}

if ($blenderExitCode -ne 0) {
    throw "Blender exited with code $blenderExitCode"
}

$screenshotPath = Join-Path $OutputDir "blender-mcp-ui.png"
$reportPath = Join-Path $OutputDir "blender-mcp-ui-report.json"

if (-not (Test-Path $screenshotPath)) {
    throw "Screenshot was not generated: $screenshotPath"
}

if (-not (Test-Path $reportPath)) {
    throw "Report was not generated: $reportPath"
}

Write-Host "UI smoke completed."
Write-Host "Screenshot: $screenshotPath"
Write-Host "Report: $reportPath"
