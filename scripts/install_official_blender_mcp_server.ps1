param(
    [string]$Version = 'v1.0.0',
    [string]$VenvDir,
    [string]$UvExe = 'uv'
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
if (-not $VenvDir) {
    $VenvDir = Join-Path $repoRoot '.official-mcp-venv'
}
$pythonExe = Join-Path $VenvDir 'Scripts\python.exe'

if (-not (Test-Path $pythonExe)) {
    & $UvExe venv $VenvDir --python 3.11
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create official MCP virtual environment: $VenvDir"
    }
}

$package = "git+https://projects.blender.org/lab/blender_mcp.git@$Version#subdirectory=mcp"
& $UvExe pip install --python $pythonExe --upgrade $package
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install official Blender MCP server package."
}

Write-Host "Official Blender MCP server venv: $VenvDir"
Write-Host "Installed official Blender MCP server package: $package"
