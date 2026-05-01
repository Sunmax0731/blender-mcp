param(
    [string]$OutputDir
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$mainScript = Join-Path $repoRoot "src\blender_mcp_installer\main.py"
$workPath = Join-Path $repoRoot "tmp\pyinstaller-build"
$pyprojectPath = Join-Path $repoRoot "pyproject.toml"

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
    --add-data "$repoRoot\blender_addon;blender_addon" `
    --add-data "$repoRoot\pyproject.toml;." `
    --distpath $OutputDir `
    --workpath $workPath `
    $mainScript

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

$exePath = Join-Path $OutputDir "blender-mcp-installer.exe"
$shaPath = Join-Path $OutputDir "blender-mcp-installer.exe.sha256"

$pyprojectText = Get-Content $pyprojectPath -Raw -Encoding UTF8
$versionMatch = [regex]::Match($pyprojectText, 'version = "([^"]+)"')
if (-not $versionMatch.Success) {
    throw "Could not read version from $pyprojectPath"
}
$version = $versionMatch.Groups[1].Value

$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $exePath
[System.IO.File]::WriteAllText(
    $shaPath,
    "$($hash.Hash.ToLowerInvariant())  blender-mcp-installer.exe`n",
    [System.Text.UTF8Encoding]::new($false)
)

$manifestPath = Join-Path $OutputDir "release-manifest-v$version.json"
$manifest = [ordered]@{
    version = $version
    generated_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
    assets = @(
        [ordered]@{
            name = "blender-mcp-installer.exe"
            path = $exePath
            sha256 = $hash.Hash.ToLowerInvariant()
        },
        [ordered]@{
            name = "blender-mcp-installer.exe.sha256"
            path = $shaPath
        }
    )
}
$manifestJson = $manifest | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($manifestPath, $manifestJson + "`n", [System.Text.UTF8Encoding]::new($false))

Write-Host "Built installer exe:"
Write-Host $exePath
Write-Host "Wrote checksum:"
Write-Host $shaPath
Write-Host "Wrote release manifest:"
Write-Host $manifestPath
