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
$modeReportPath = Join-Path $OutputDir "smoke-mode.json"

Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class CodexWindowInterop
{
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
}
"@

function Get-VisibleBlenderProcess {
    $candidates = Get-Process -Name "blender" -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowHandle -ne 0 }
    if (-not $candidates) {
        return $null
    }
    return $candidates | Sort-Object StartTime -Descending | Select-Object -First 1
}

function Get-ForegroundProcessId {
    $hwnd = [CodexWindowInterop]::GetForegroundWindow()
    if ($hwnd -eq [IntPtr]::Zero) {
        return 0
    }

    [uint32]$processId = 0
    [void][CodexWindowInterop]::GetWindowThreadProcessId($hwnd, [ref]$processId)
    return [int]$processId
}

function Save-WindowScreenshot {
    param(
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $handle = [IntPtr]$Process.MainWindowHandle
    if ($handle -eq [IntPtr]::Zero) {
        throw "MainWindowHandle could not be resolved for Blender process $($Process.Id)."
    }

    $rect = New-Object CodexWindowInterop+RECT
    if (-not [CodexWindowInterop]::GetWindowRect($handle, [ref]$rect)) {
        throw "GetWindowRect failed for Blender process $($Process.Id)."
    }

    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) {
        throw "Resolved Blender window size is invalid: ${width}x${height}"
    }

    $bitmap = New-Object System.Drawing.Bitmap($width, $height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
        $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}

function Write-SmokeModeReport {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Mode,
        [Parameter(Mandatory = $true)]
        [int]$ProcessId,
        [Parameter(Mandatory = $true)]
        [string]$ServerUrl,
        [Parameter(Mandatory = $true)]
        [string]$ScreenshotPath,
        [Parameter(Mandatory = $true)]
        [double]$CaptureDelaySeconds
    )

    $payload = [ordered]@{
        mode = $Mode
        processId = $ProcessId
        serverUrl = $ServerUrl
        screenshotPath = $ScreenshotPath
        captureDelaySeconds = $CaptureDelaySeconds
        capturedAt = (Get-Date).ToString("o")
    }
    $payload | ConvertTo-Json -Depth 3 | Set-Content -Path $Path -Encoding UTF8
}

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
$screenshotPath = Join-Path $OutputDir "blender-mcp-ui.png"
$reportPath = Join-Path $OutputDir "blender-mcp-ui-report.json"
$existingBlender = Get-VisibleBlenderProcess
$blenderExitCode = 0
$captureMode = ""

if ($existingBlender) {
    $foregroundProcessId = Get-ForegroundProcessId
    if ($foregroundProcessId -ne $existingBlender.Id) {
        Write-Host "Existing Blender process found. Bringing it to the foreground: PID=$($existingBlender.Id)"
        $automationProcess = Start-Process `
            -FilePath $PythonExe `
            -ArgumentList $automationScript, "--pid", "$($existingBlender.Id)", "--delay-seconds", "$AutomationDelaySeconds", "--skip-click" `
            -WorkingDirectory $repoRoot `
            -WindowStyle Hidden `
            -RedirectStandardOutput $automationStdout `
            -RedirectStandardError $automationStderr `
            -PassThru
        Wait-Process -Id $automationProcess.Id
    }
    else {
        Write-Host "Existing Blender process is already the active window: PID=$($existingBlender.Id)"
    }

    Start-Sleep -Seconds ([Math]::Max(0, $CaptureDelaySeconds))
    Save-WindowScreenshot -Process $existingBlender -Path $screenshotPath
    Write-SmokeModeReport `
        -Path $modeReportPath `
        -Mode "existing_process" `
        -ProcessId $existingBlender.Id `
        -ServerUrl $ServerUrl `
        -ScreenshotPath $screenshotPath `
        -CaptureDelaySeconds $CaptureDelaySeconds
    $captureMode = "existing_process"
}
else {
    Write-Host "No visible Blender process found. Launching a controlled Blender instance."
    $blenderArgs = "`"$baseBlend`" --python-exit-code 1 --python `"$captureScript`" -- --output-dir `"$OutputDir`" --server-url `"$ServerUrl`" --prompt `"$Prompt`" --wait-seconds $CaptureDelaySeconds"
    $blenderProcess = Start-Process `
        -FilePath $BlenderExe `
        -ArgumentList $blenderArgs `
        -WorkingDirectory $repoRoot `
        -PassThru

    $automationProcess = Start-Process `
        -FilePath $PythonExe `
        -ArgumentList $automationScript, "--pid", "$($blenderProcess.Id)", "--delay-seconds", "$AutomationDelaySeconds", "--send-n" `
        -WorkingDirectory $repoRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $automationStdout `
        -RedirectStandardError $automationStderr `
        -PassThru

    Wait-Process -Id $blenderProcess.Id
    $blenderExitCode = $blenderProcess.ExitCode
    $captureMode = "controlled_launch"
}

if ($serverWasStarted -and -not $KeepServer -and $serverProcess -and -not $serverProcess.HasExited) {
    Stop-Process -Id $serverProcess.Id -Force
}

if ($blenderExitCode -ne 0) {
    throw "Blender exited with code $blenderExitCode"
}

if (-not (Test-Path $screenshotPath)) {
    throw "Screenshot was not generated: $screenshotPath"
}

if ($captureMode -eq "controlled_launch" -and -not (Test-Path $reportPath)) {
    throw "Report was not generated: $reportPath"
}

Write-Host "UI smoke completed."
Write-Host "Mode: $captureMode"
Write-Host "Screenshot: $screenshotPath"
if (Test-Path $reportPath) {
    Write-Host "Report: $reportPath"
}
if (Test-Path $modeReportPath) {
    Write-Host "Mode report: $modeReportPath"
}
