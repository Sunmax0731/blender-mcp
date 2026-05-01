param(
    [string]$BlenderExe,
    [string]$PluginKeys,
    [string]$ManifestPath,
    [string]$PayloadRoot
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

function Parse-KeyList {
    param([string]$RawValue)

    if (-not $RawValue) {
        return @()
    }

    return @(
        $RawValue.Split(',') |
            ForEach-Object { $_.Trim() } |
            Where-Object { $_ }
    )
}

function Resolve-PluginZip {
    param(
        [string]$RepoRoot,
        [string]$PayloadBase,
        [object]$Plugin
    )

    $payloadPath = Join-Path $PayloadBase $Plugin.payload_relpath
    if (Test-Path $payloadPath) {
        return $payloadPath
    }

    if (-not $Plugin.fallback_url) {
        throw "Plugin ZIP could not be resolved for $($Plugin.key): $payloadPath"
    }

    $downloadDir = Join-Path $RepoRoot "tmp\third-party-plugin-downloads\$($Plugin.key)"
    New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null
    $destination = Join-Path $downloadDir ([System.IO.Path]::GetFileName([string]$Plugin.payload_relpath))

    Invoke-WebRequest -UseBasicParsing -Uri $Plugin.fallback_url -OutFile $destination
    Write-Host "Downloaded plugin package: $destination"
    return $destination
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

if (-not $ManifestPath) {
    $ManifestPath = Join-Path $repoRoot 'templates\installer\third_party_plugins.json'
}
if (-not $PayloadRoot) {
    $PayloadRoot = Join-Path $repoRoot 'templates\installer'
}

if (-not (Test-Path $ManifestPath)) {
    throw "Plugin manifest was not found: $ManifestPath"
}

$selectedKeys = Parse-KeyList -RawValue $PluginKeys
$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$plugins = @($manifest.plugins)
if ($selectedKeys.Count -gt 0) {
    $selectedSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($key in $selectedKeys) {
        [void]$selectedSet.Add($key)
    }
    $plugins = @($plugins | Where-Object { $selectedSet.Contains([string]$_.key) })
}

if ($plugins.Count -eq 0) {
    Write-Host 'No third-party plugins selected.'
    exit 0
}

$pluginJobs = @()
foreach ($plugin in $plugins) {
    $zipPath = Resolve-PluginZip -RepoRoot $repoRoot -PayloadBase $PayloadRoot -Plugin $plugin
    $pluginJobs += [ordered]@{
        key = [string]$plugin.key
        name = [string]$plugin.name
        display_name = [string]$plugin.display_name
        install_method = [string]$plugin.install_method
        repository_id = [string]$plugin.repository_id
        module_name_hints = @($plugin.module_name_hints)
        zip_path = $zipPath
    }
}

$resolvedBlenderExe = Resolve-BlenderExe -ExplicitPath $BlenderExe

foreach ($pluginJob in $pluginJobs) {
    if ($pluginJob.install_method -ne 'extension') {
        continue
    }

    & $resolvedBlenderExe --command extension remove $pluginJob.key | Out-Null
    & $resolvedBlenderExe --command extension install-file -r $pluginJob.repository_id -e $pluginJob.zip_path
    if ($LASTEXITCODE -ne 0) {
        throw "Blender extension install failed for $($pluginJob.key) with exit code $LASTEXITCODE"
    }
}

$workDir = Join-Path $repoRoot 'tmp\third-party-plugin-install'
New-Item -ItemType Directory -Force -Path $workDir | Out-Null

$pluginListPath = Join-Path $workDir 'selected_plugins.json'
$reportPath = Join-Path $workDir 'install_report.json'
$blenderScriptPath = Join-Path $workDir 'install_third_party_plugins.py'
$encoding = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText(
    $pluginListPath,
    ($pluginJobs | ConvertTo-Json -Depth 8),
    $encoding
)

$pythonScript = @'
import addon_utils
import json
import sys
from pathlib import Path
import zipfile

import bpy


def parse_args() -> tuple[Path, Path]:
    if "--" not in sys.argv:
        raise SystemExit("Expected arguments after --")
    args = sys.argv[sys.argv.index("--") + 1 :]
    if len(args) != 2:
        raise SystemExit("Expected plugin list path and report path")
    return Path(args[0]), Path(args[1])


def infer_module_hint(job: dict[str, object]) -> list[str]:
    hints = [str(value) for value in job.get("module_name_hints", []) if str(value).strip()]
    zip_path = Path(str(job["zip_path"]))
    if not zip_path.exists():
        return hints

    try:
        with zipfile.ZipFile(zip_path) as archive:
            top_names: list[str] = []
            for name in archive.namelist():
                if not name or name.startswith("__MACOSX/"):
                    continue
                top = name.split("/", 1)[0]
                if top not in top_names:
                    top_names.append(top)
            for top_name in top_names:
                stem = Path(top_name).stem
                if stem and stem not in hints:
                    hints.append(stem)
    except zipfile.BadZipFile:
        pass

    return hints


def install_addon_zip(job: dict[str, object]) -> None:
    bpy.ops.preferences.addon_install(filepath=str(job["zip_path"]), overwrite=True)


def find_module_name(job: dict[str, object], hints: list[str]) -> str | None:
    display_name = str(job.get("display_name") or "")
    candidate_modules: list[str] = []
    for hint in hints:
        if hint not in candidate_modules:
            candidate_modules.append(hint)

    for module in addon_utils.modules():
        module_name = getattr(module, "__name__", "")
        bl_info = getattr(module, "bl_info", {}) or {}
        if display_name and bl_info.get("name") == display_name:
            return module_name
        if module_name in candidate_modules:
            return module_name

    for module_name in bpy.context.preferences.addons.keys():
        if module_name in candidate_modules:
            return module_name

    return None


def enable_module(module_name: str) -> None:
    addon_utils.enable(module_name, default_set=True, persistent=True)


def main() -> int:
    plugin_list_path, report_path = parse_args()
    jobs = json.loads(plugin_list_path.read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []

    for job in jobs:
        result: dict[str, object] = {
            "key": job["key"],
            "name": job["name"],
            "install_method": job["install_method"],
            "zip_path": job["zip_path"],
            "status": "pending",
        }
        try:
            if job["install_method"] == "addon_zip":
                install_addon_zip(job)
            elif job["install_method"] != "extension":
                raise ValueError(f"Unsupported install method: {job['install_method']}")

            hints = infer_module_hint(job)
            module_name = find_module_name(job, hints)
            if module_name:
                enable_module(module_name)
            result["module_name"] = module_name or ""
            result["status"] = "ok" if module_name else "installed_without_module"
        except Exception as exc:  # pragma: no cover - Blender runtime path
            result["status"] = "failed"
            result["error"] = str(exc)
        results.append(result)

    bpy.ops.wm.save_userpref()
    report = {
        "success": all(item["status"] in {"ok", "installed_without_module"} for item in results),
        "results": results,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
'@

[System.IO.File]::WriteAllText($blenderScriptPath, $pythonScript, $encoding)

& $resolvedBlenderExe --background --online-mode --python $blenderScriptPath -- $pluginListPath $reportPath
if (Test-Path $reportPath) {
    Get-Content $reportPath

    $report = Get-Content $reportPath -Raw | ConvertFrom-Json
    if ($report.success) {
        exit 0
    }
}

if ($LASTEXITCODE -ne 0) {
    throw "Third-party Blender plugin install failed with exit code $LASTEXITCODE"
}

throw 'Third-party Blender plugin install did not produce a successful report.'
