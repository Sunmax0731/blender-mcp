param(
    [string]$Version = 'v1.0.0',
    [string]$BlenderExe,
    [string]$RepositoryId = 'user_default',
    [switch]$ForceDownload
)

$ErrorActionPreference = 'Stop'

function Resolve-BlenderExe {
    param([string]$ExplicitPath)

    $candidates = @(
        $ExplicitPath,
        $env:BLENDER_PATH,
        $env:BLENDER_EXE,
        'F:\Steam\steamapps\common\Blender\blender.exe',
        'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe',
        'C:\Program Files\Blender Foundation\Blender\blender.exe'
    ) | Where-Object { $_ }

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    $registryRoots = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )

    foreach ($root in $registryRoots) {
        $apps = Get-ItemProperty $root -ErrorAction SilentlyContinue |
            Where-Object { $_.DisplayName -like '*Blender*' }
        foreach ($app in $apps) {
            $installLocation = $app.InstallLocation
            if (-not $installLocation) {
                continue
            }

            $candidate = Join-Path $installLocation 'blender.exe'
            if (Test-Path $candidate) {
                return $candidate
            }
        }
    }

    throw 'Blender executable could not be resolved. Set -BlenderExe or BLENDER_PATH.'
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$tmpRoot = Join-Path $repoRoot 'tmp\official-blender-mcp'
$distRoot = Join-Path $repoRoot 'dist\official-blender-mcp'
$legacyInstallRoot = Join-Path $env:APPDATA 'Blender Foundation\Blender\5.1\scripts\addons\mcp'

$zipName = "mcp-$($Version.TrimStart('v')).zip"
$downloadUrl = "https://projects.blender.org/lab/blender_mcp/releases/download/$Version/$zipName"
$zipPath = Join-Path $distRoot $zipName

New-Item -ItemType Directory -Force -Path $tmpRoot | Out-Null
New-Item -ItemType Directory -Force -Path $distRoot | Out-Null

if ($ForceDownload -or -not (Test-Path $zipPath)) {
    Invoke-WebRequest -UseBasicParsing -Uri $downloadUrl -OutFile $zipPath
    Write-Host "Downloaded official package: $zipPath"
}
else {
    Write-Host "Using cached official package: $zipPath"
}

$resolvedBlenderExe = Resolve-BlenderExe -ExplicitPath $BlenderExe

if (Test-Path $legacyInstallRoot) {
    Remove-Item -LiteralPath $legacyInstallRoot -Recurse -Force
    Write-Host "Removed legacy add-on path: $legacyInstallRoot"
}

& $resolvedBlenderExe --command extension remove mcp | Out-Null

& $resolvedBlenderExe --command extension install-file -r $RepositoryId -e $zipPath
if ($LASTEXITCODE -ne 0) {
    throw "Blender extension install failed with exit code $LASTEXITCODE"
}

$repoList = & $resolvedBlenderExe --command extension repo-list
$repoDirectoryLine = $repoList |
    Select-String -Pattern "^$([regex]::Escape($RepositoryId)):" -Context 0,3 |
    ForEach-Object { $_.Context.PostContext } |
    Select-String -Pattern 'directory: "(.+)"' |
    Select-Object -First 1

$installRoot = $null
if ($repoDirectoryLine) {
    $installRoot = [regex]::Match($repoDirectoryLine.Line, 'directory: "(.+)"').Groups[1].Value
}

if ($installRoot) {
    Write-Host "Installed official Blender MCP extension: $(Join-Path $installRoot 'mcp')"
}
Write-Host "Repository: $RepositoryId"
Write-Host "Version: $Version"
Write-Host "Source: $downloadUrl"
