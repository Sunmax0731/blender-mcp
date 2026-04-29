param(
    [string]$ConfigPath = "$env:USERPROFILE\.codex\config.toml"
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startScriptPath = Join-Path $scriptDir 'start_official_blender_mcp.ps1'
$escapedStartScriptPath = $startScriptPath.Replace('\', '\\')
$sectionHeader = '[mcp_servers.blender-official]'
$entry = @"
[mcp_servers.blender-official]
command = "powershell"
args = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "$escapedStartScriptPath"]
"@

if (-not (Test-Path $ConfigPath)) {
    throw "Codex config was not found: $ConfigPath"
}

$content = Get-Content -Raw $ConfigPath
if ($content -match [regex]::Escape($sectionHeader)) {
    Write-Host 'Codex MCP entry already exists.'
    exit 0
}

$backupPath = "$ConfigPath.bak-$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item $ConfigPath $backupPath -Force
Add-Content -Encoding UTF8 $ConfigPath "`r`n$entry`r`n"
Write-Host "Updated Codex config: $ConfigPath"
Write-Host "Backup: $backupPath"
