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

function Resolve-BlenderPath {
    $candidates = @(
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

            $blenderExe = Join-Path $installLocation 'blender.exe'
            if (Test-Path $blenderExe) {
                return $blenderExe
            }
        }
    }

    return $null
}

if (-not $env:BLENDER_PATH) {
    $resolvedBlenderPath = Resolve-BlenderPath
    if ($resolvedBlenderPath) {
        $env:BLENDER_PATH = $resolvedBlenderPath
    }
}

$serverExe = Join-Path $VenvDir 'Scripts\blender-mcp.exe'
if (-not (Test-Path $serverExe)) {
    throw "Official blender-mcp executable not found. Run scripts\\install_official_blender_mcp_server.ps1 first."
}

& $serverExe @RemainingArgs
exit $LASTEXITCODE
