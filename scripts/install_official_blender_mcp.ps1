param(
    [string]$Version = 'v1.0.0',
    [string]$InstallRoot,
    [switch]$ForceDownload
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$tmpRoot = Join-Path $repoRoot 'tmp\official-blender-mcp'
$distRoot = Join-Path $repoRoot 'dist\official-blender-mcp'

if (-not $InstallRoot) {
    $InstallRoot = Join-Path $env:APPDATA 'Blender Foundation\Blender\5.1\scripts\addons\mcp'
}

$zipName = "mcp-$($Version.TrimStart('v')).zip"
$downloadUrl = "https://projects.blender.org/lab/blender_mcp/releases/download/$Version/$zipName"
$zipPath = Join-Path $distRoot $zipName
$extractDir = Join-Path $tmpRoot $Version

New-Item -ItemType Directory -Force -Path $tmpRoot | Out-Null
New-Item -ItemType Directory -Force -Path $distRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $InstallRoot) | Out-Null

if ($ForceDownload -or -not (Test-Path $zipPath)) {
    Invoke-WebRequest -UseBasicParsing -Uri $downloadUrl -OutFile $zipPath
    Write-Host "Downloaded official package: $zipPath"
}
else {
    Write-Host "Using cached official package: $zipPath"
}

if (Test-Path $extractDir) {
    Remove-Item -Recurse -Force $extractDir
}
Expand-Archive -LiteralPath $zipPath -DestinationPath $extractDir

if (-not (Test-Path (Join-Path $extractDir 'blender_manifest.toml'))) {
    throw "Official package structure is unexpected: $extractDir"
}

if (Test-Path $InstallRoot) {
    Remove-Item -Recurse -Force $InstallRoot
}
New-Item -ItemType Directory -Force -Path $InstallRoot | Out-Null
Copy-Item -Path (Join-Path $extractDir '*') -Destination $InstallRoot -Recurse -Force

Write-Host "Installed official Blender MCP add-on: $InstallRoot"
Write-Host "Version: $Version"
Write-Host "Source: $downloadUrl"
