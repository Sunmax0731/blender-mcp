param(
    [string]$CodexHome = "$env:USERPROFILE\.codex",
    [switch]$MergeCodexConfig,
    [switch]$PlanConfigMerge
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$TemplateRoot = Join-Path $RepoRoot "templates\precision"
$CodexRoot = [System.IO.Path]::GetFullPath($CodexHome)
$ProfileRoot = Join-Path $CodexRoot "blender-precision"
$SkillRoot = Join-Path $CodexRoot "skills\precise-blender-modeling"
$SubagentRoot = Join-Path $CodexRoot "subagents"
$CodexConfigPath = Join-Path $CodexRoot "config.toml"

if (-not (Test-Path $TemplateRoot)) {
    throw "Precision template root not found: $TemplateRoot"
}

New-Item -ItemType Directory -Force $ProfileRoot | Out-Null
New-Item -ItemType Directory -Force $SkillRoot | Out-Null
New-Item -ItemType Directory -Force $SubagentRoot | Out-Null

Copy-Item -Recurse -Force (Join-Path $TemplateRoot "blender_precision_config.yaml") $ProfileRoot
Copy-Item -Recurse -Force (Join-Path $TemplateRoot "model_spec.yaml") $ProfileRoot
Copy-Item -Recurse -Force (Join-Path $TemplateRoot "addon_registry.yaml") $ProfileRoot
Copy-Item -Recurse -Force (Join-Path $TemplateRoot "validation_report.example.json") $ProfileRoot
Copy-Item -Recurse -Force (Join-Path $TemplateRoot "codex_config.toml") $ProfileRoot
Copy-Item -Recurse -Force (Join-Path $TemplateRoot ".mcp.json") $ProfileRoot
Copy-Item -Recurse -Force (Join-Path $TemplateRoot "plugin.json") $ProfileRoot
Copy-Item -Recurse -Force (Join-Path $TemplateRoot "skills\precise-blender-modeling\*") $SkillRoot
Copy-Item -Recurse -Force (Join-Path $TemplateRoot "subagents\*") $SubagentRoot

function Get-PrecisionMcpConfigBlock {
    param(
        [string]$TemplateConfigPath
    )

    $lines = Get-Content -Encoding UTF8 $TemplateConfigPath
    $start = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i].Trim() -eq "[mcp_servers.blender_precision]") {
            $start = $i
            break
        }
    }
    if ($start -lt 0) {
        throw "Precision MCP config block not found in template: $TemplateConfigPath"
    }
    return ($lines[$start..($lines.Count - 1)] -join [Environment]::NewLine)
}

function Merge-PrecisionMcpConfig {
    param(
        [string]$ConfigPath,
        [string]$TemplateConfigPath,
        [switch]$PlanOnly
    )

    $block = Get-PrecisionMcpConfigBlock -TemplateConfigPath $TemplateConfigPath
    if (Test-Path $ConfigPath) {
        $existing = Get-Content -Raw -Encoding UTF8 $ConfigPath
        if ($existing -match '(?m)^\[mcp_servers\.blender_precision\]\s*$') {
            Write-Output "Codex config already contains [mcp_servers.blender_precision]. No merge needed."
            return
        }
    } else {
        $existing = ""
    }

    Write-Output "Codex config merge preview: append [mcp_servers.blender_precision] to $ConfigPath"
    Write-Output $block

    if ($PlanOnly) {
        Write-Output "Plan only: Codex config was not modified."
        return
    }

    if (Test-Path $ConfigPath) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = "$ConfigPath.backup-$timestamp"
        Copy-Item -Force $ConfigPath $backupPath
        Write-Output "Codex config backup created: $backupPath"
    } else {
        New-Item -ItemType Directory -Force (Split-Path -Parent $ConfigPath) | Out-Null
        New-Item -ItemType File -Force $ConfigPath | Out-Null
        Write-Output "Codex config created: $ConfigPath"
    }

    $prefix = ""
    if ((Get-Item $ConfigPath).Length -gt 0) {
        $prefix = [Environment]::NewLine + [Environment]::NewLine
    }
    Add-Content -Encoding UTF8 -Path $ConfigPath -Value ($prefix + $block)
    Write-Output "Codex config merged: [mcp_servers.blender_precision]"
}

if ($MergeCodexConfig -or $PlanConfigMerge) {
    Merge-PrecisionMcpConfig `
        -ConfigPath $CodexConfigPath `
        -TemplateConfigPath (Join-Path $TemplateRoot "codex_config.toml") `
        -PlanOnly:$PlanConfigMerge
} else {
    Write-Output "Codex config merge skipped. Template copied to: $(Join-Path $ProfileRoot 'codex_config.toml')"
}

Write-Output "Precision profile templates installed to: $ProfileRoot"
Write-Output "Skill installed to: $SkillRoot"
Write-Output "Subagent templates installed to: $SubagentRoot"
Write-Output "Codex App restart is required before using newly installed skills or MCP profile examples."
