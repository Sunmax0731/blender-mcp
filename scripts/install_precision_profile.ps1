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

function Remove-GeneratedPrecisionMcpConfig {
    param(
        [string]$ConfigPath,
        [switch]$PlanOnly
    )

    if (-not (Test-Path $ConfigPath)) {
        Write-Output "Codex config not found. No precision MCP cleanup needed."
        return
    }

    $existing = Get-Content -Raw -Encoding UTF8 $ConfigPath
    $sectionPattern = '(?ms)^\[mcp_servers\.blender_precision\]\s*.*?(?=^\[|\z)'
    $match = [regex]::Match($existing, $sectionPattern)
    if (-not $match.Success) {
        Write-Output "Codex config does not contain [mcp_servers.blender_precision]. No cleanup needed."
        return
    }

    $section = $match.Value
    $looksGenerated = (
        $section -match 'command\s*=\s*"uvx"' -and
        $section -match '"blender-precision-mcp"' -and
        $section -match 'templates/precision/blender_precision_config\.yaml'
    )

    if (-not $looksGenerated) {
        Write-Output "Codex config contains [mcp_servers.blender_precision], but it does not match the generated experimental block. No automatic cleanup was applied."
        return
    }

    Write-Output "Codex config cleanup preview: remove generated [mcp_servers.blender_precision] from $ConfigPath"
    Write-Output $section.Trim()

    if ($PlanOnly) {
        Write-Output "Plan only: Codex config was not modified."
        return
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = "$ConfigPath.backup-$timestamp"
    Copy-Item -Force $ConfigPath $backupPath
    Write-Output "Codex config backup created: $backupPath"

    $updated = [regex]::Replace($existing, $sectionPattern, "")
    Set-Content -Encoding UTF8 -Path $ConfigPath -Value $updated.Trim()
    Write-Output "Codex config cleaned: removed generated [mcp_servers.blender_precision]"
}

if ($MergeCodexConfig -or $PlanConfigMerge) {
    Write-Output "Precision MCP server auto-registration is disabled in this release because blender-precision-mcp is an experimental scaffold and is not published as a standalone uvx package."
    Remove-GeneratedPrecisionMcpConfig `
        -ConfigPath $CodexConfigPath `
        -PlanOnly:$PlanConfigMerge
} else {
    Write-Output "Codex config merge skipped. Template copied to: $(Join-Path $ProfileRoot 'codex_config.toml')"
}

Write-Output "Precision profile templates installed to: $ProfileRoot"
Write-Output "Skill installed to: $SkillRoot"
Write-Output "Subagent templates installed to: $SubagentRoot"
Write-Output "Codex App restart is required before using newly installed skills or MCP profile examples."
