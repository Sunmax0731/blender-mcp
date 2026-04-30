param(
    [string]$ConfigPath = "$env:USERPROFILE\.codex\blender-precision\blender_precision_config.yaml",
    [string]$Profile = "precise",
    [string]$ToolPack = "modeling,validation,visual_qa,addon_inspection",
    [string]$VenvDir
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
if (-not $VenvDir) {
    $VenvDir = Join-Path $repoRoot ".precision-mcp-venv"
}
$pythonExe = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Precision MCP virtual environment was not found: $VenvDir. Re-run the installer with precision profile enabled."
}
if (-not (Test-Path $ConfigPath)) {
    throw "Precision MCP config was not found: $ConfigPath. Re-run the installer with precision profile enabled."
}

& $pythonExe -m blender_precision_mcp.main `
    --config $ConfigPath `
    --profile $Profile `
    --tool-pack $ToolPack
