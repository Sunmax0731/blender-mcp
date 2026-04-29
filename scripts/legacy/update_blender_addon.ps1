param(
    [string]$PythonExe,
    [string]$ServerUrl = "http://127.0.0.1:8765",
    [switch]$SkipReload,
    [switch]$SkipServerRestart,
    [double]$ReloadDelaySeconds = 1.0,
    [double]$ServerStartupTimeoutSeconds = 20.0
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$serverStdoutPath = Join-Path $repoRoot "artifacts\server\stdout.log"
$serverStderrPath = Join-Path $repoRoot "artifacts\server\stderr.log"

if (-not $PythonExe) {
    $PythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
}

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

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

function Get-ListeningProcessId {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $connections) {
        return $null
    }

    return ($connections | Select-Object -First 1).OwningProcess
}

function Get-ProcessCommandLine {
    param([int]$ProcessId)

    $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" -ErrorAction SilentlyContinue
    if (-not $processInfo) {
        return ""
    }
    return [string]$processInfo.CommandLine
}

function Stop-ExistingServer {
    param([string]$Url)

    $port = [System.Uri]$Url
    $processId = Get-ListeningProcessId -Port $port.Port
    if (-not $processId) {
        return
    }

    $commandLine = Get-ProcessCommandLine -ProcessId $processId
    if ($commandLine -and $commandLine -notmatch "blender_mcp_server\.main" -and $commandLine -notmatch "blender-mcp-server") {
        throw "Port $($port.Port) is used by an unexpected process: PID=$processId CommandLine=$commandLine"
    }

    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if (-not $process) {
        return
    }

    try {
        Stop-Process -Id $processId -Force -ErrorAction Stop
    }
    catch {
        if (Test-ServerHealth -Url $Url) {
            Write-Warning "Existing MCP server could not be stopped (PID=$processId). Continuing with the healthy running server. $($_.Exception.Message)"
            return $false
        }
        throw
    }
    $deadline = (Get-Date).AddSeconds(10)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 250
        if (-not (Get-ListeningProcessId -Port $port.Port)) {
            return $true
        }
    }

    throw "Timed out while stopping existing MCP server on port $($port.Port)."
}

function Start-Server {
    param([string]$Url)

    New-Item -ItemType Directory -Force -Path (Split-Path $serverStdoutPath) | Out-Null
    $process = Start-Process `
        -FilePath $PythonExe `
        -ArgumentList "-m", "blender_mcp_server.main" `
        -WorkingDirectory $repoRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $serverStdoutPath `
        -RedirectStandardError $serverStderrPath `
        -PassThru

    $deadline = (Get-Date).AddSeconds($ServerStartupTimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-ServerHealth -Url $Url) {
            return $process
        }
        Start-Sleep -Milliseconds 500
    }

    if (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
    }
    throw "Blender MCP server did not become healthy: $Url"
}

& $PythonExe (Join-Path $scriptDir "build_blender_addon.py")
if ($LASTEXITCODE -ne 0) {
    throw "Failed to build Blender add-on zip."
}

& $PythonExe (Join-Path $scriptDir "sync_blender_addon.py")
if ($LASTEXITCODE -ne 0) {
    throw "Failed to synchronize Blender add-on directory."
}

if (-not $SkipServerRestart) {
    $stopResult = Stop-ExistingServer -Url $ServerUrl
    if ($stopResult -eq $false) {
        Write-Host "Using existing healthy Blender MCP server: URL=$ServerUrl"
    }
    else {
        $serverProcess = Start-Server -Url $ServerUrl
        Write-Host "Blender MCP server restarted: PID=$($serverProcess.Id) URL=$ServerUrl"
    }
}
else {
    Write-Host "Server restart skipped by request."
}

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
