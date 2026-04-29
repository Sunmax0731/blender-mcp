param(
    [string]$BlenderExe
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

$resolvedBlenderExe = Resolve-BlenderExe -ExplicitPath $BlenderExe
$process = Start-Process -FilePath $resolvedBlenderExe -PassThru
Write-Host "Started Blender: $resolvedBlenderExe"
Write-Host "Blender PID: $($process.Id)"
