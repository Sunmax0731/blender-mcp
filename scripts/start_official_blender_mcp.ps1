param(
    [string]$VenvDir,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
if (-not $VenvDir) {
    $VenvDir = Join-Path $repoRoot '.official-mcp-venv'
}

$serverExe = Join-Path $VenvDir 'Scripts\blender-mcp.exe'
if (-not (Test-Path $serverExe)) {
    throw "Official blender-mcp executable not found. Run scripts\\install_official_blender_mcp_server.ps1 first."
}

& $serverExe @RemainingArgs
exit $LASTEXITCODE
