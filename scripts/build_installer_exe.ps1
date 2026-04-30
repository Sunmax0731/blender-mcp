param(
    [string]$OutputDir
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$mainScript = Join-Path $repoRoot "src\blender_mcp_installer\main.py"
$workPath = Join-Path $repoRoot "tmp\pyinstaller-build"

if (-not $OutputDir) {
    $OutputDir = Join-Path $repoRoot "dist\one-click-installer"
}

if (-not (Test-Path $mainScript)) {
    throw "Installer entrypoint was not found: $mainScript"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path $workPath | Out-Null

uv run pyinstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name blender-mcp-installer `
    --paths (Join-Path $repoRoot "src") `
    --add-data "$repoRoot\scripts;scripts" `
    --add-data "$repoRoot\templates;templates" `
    --add-data "$repoRoot\src;src" `
    --add-data "$repoRoot\pyproject.toml;." `
    --distpath $OutputDir `
    --workpath $workPath `
    $mainScript

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Write-Host "Built installer exe:"
Write-Host (Join-Path $OutputDir "blender-mcp-installer.exe")
