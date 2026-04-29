param(
    [string]$BlenderExe,
    [string]$PythonExe,
    [string]$ServerUrl = "http://127.0.0.1:8765",
    [string]$Prompt = "カービィを作ってください",
    [double]$CaptureDelaySeconds = 5,
    [string]$OutputDir
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

if (-not $PythonExe) {
    $PythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
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

if (-not $OutputDir) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $OutputDir = Join-Path $repoRoot "artifacts\blender-prompt-smoke\$timestamp"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

& (Join-Path $scriptDir "update_blender_addon.ps1") -PythonExe $PythonExe -ServerUrl $ServerUrl

$baseBlend = Join-Path $repoRoot "tmp\ui_smoke_base.blend"
if (-not (Test-Path $baseBlend)) {
    throw "Base blend file not found: $baseBlend"
}

$captureScript = Join-Path $repoRoot "scripts\blender_ui_capture.py"
$screenshotPath = Join-Path $OutputDir "blender-mcp-prompt.png"
$reportPath = Join-Path $OutputDir "blender-mcp-prompt-report.json"
$promptPath = Join-Path $OutputDir "prompt.txt"

Set-Content -Encoding UTF8 $promptPath $Prompt

$blenderArgs = "`"$baseBlend`" --python-exit-code 1 --python `"$captureScript`" -- --output-dir `"$OutputDir`" --server-url `"$ServerUrl`" --prompt-file `"$promptPath`" --screenshot-name `"blender-mcp-prompt.png`" --report-name `"blender-mcp-prompt-report.json`" --wait-seconds $CaptureDelaySeconds --send-prompt"
$process = Start-Process `
    -FilePath $BlenderExe `
    -ArgumentList $blenderArgs `
    -WorkingDirectory $repoRoot `
    -PassThru `
    -Wait

if ($process.ExitCode -ne 0) {
    throw "Blender prompt smoke failed with exit code $($process.ExitCode)."
}

if (-not (Test-Path $screenshotPath)) {
    throw "Prompt smoke screenshot was not generated: $screenshotPath"
}
if (-not (Test-Path $reportPath)) {
    throw "Prompt smoke report was not generated: $reportPath"
}

$report = Get-Content -Raw $reportPath | ConvertFrom-Json
if (-not $report.success) {
    throw "Prompt smoke reported failure: $($report.error)"
}

Write-Host "Prompt smoke completed."
Write-Host "Screenshot: $screenshotPath"
Write-Host "Report: $reportPath"
Write-Host "UI State: $($report.uiState)"
Write-Host "Kirby_Base exists: $($report.kirbyBaseExists)"

