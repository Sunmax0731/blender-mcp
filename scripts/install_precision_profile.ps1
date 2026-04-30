param(
    [string]$CodexHome = "$env:USERPROFILE\.codex",
    [switch]$MergeCodexConfig,
    [switch]$PlanConfigMerge,
    [string]$UvExe = "uv",
    [switch]$SkipVenvInstall
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$TemplateRoot = Join-Path $RepoRoot "templates\precision"
$CodexRoot = [System.IO.Path]::GetFullPath($CodexHome)
$ProfileRoot = Join-Path $CodexRoot "blender-precision"
$SkillRoot = Join-Path $CodexRoot "skills\precise-blender-modeling"
$SubagentRoot = Join-Path $CodexRoot "subagents"
$CodexConfigPath = Join-Path $CodexRoot "config.toml"
$VenvDir = Join-Path $RepoRoot ".precision-mcp-venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

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

function Escape-TomlString {
    param(
        [string]$Value
    )

    return $Value.Replace('\', '\\').Replace('"', '\"')
}

function Install-PrecisionMcpVenv {
    param(
        [switch]$PlanOnly
    )

    if ($PlanOnly -or $SkipVenvInstall) {
        Write-Output "Plan only: would create/update precision MCP venv: $VenvDir"
        Write-Output "Plan only: would install local package from: $RepoRoot"
        return
    }

    if (-not (Test-Path $PythonExe)) {
        & $UvExe venv $VenvDir --python 3.11
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create precision MCP virtual environment: $VenvDir"
        }
    }

    & $UvExe pip install --python $PythonExe --upgrade $RepoRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install blender-precision-mcp package into: $VenvDir"
    }

    Write-Output "Precision MCP venv: $VenvDir"
    Write-Output "Installed blender-precision-mcp package from: $RepoRoot"
}

function Get-ManagedPrecisionMcpConfigBlock {
    $startScriptPath = Join-Path $RepoRoot "scripts\start_precision_blender_mcp.ps1"
    $configPath = Join-Path $ProfileRoot "blender_precision_config.yaml"
    $escapedStartScriptPath = Escape-TomlString $startScriptPath
    $escapedConfigPath = Escape-TomlString $configPath
    $escapedCwd = Escape-TomlString $ProfileRoot

    return @"
[mcp_servers.blender_precision]
command = "powershell"
args = [
  "-NoProfile",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  "$escapedStartScriptPath",
  "-ConfigPath",
  "$escapedConfigPath",
  "-Profile",
  "precise",
  "-ToolPack",
  "modeling,validation,visual_qa,addon_inspection"
]
cwd = "$escapedCwd"
startup_timeout_sec = 30
tool_timeout_sec = 180
required = true
enabled = true

enabled_tools = [
  "get_scene_snapshot",
  "create_parametric_object",
  "create_or_update_scene_from_spec",
  "assign_materials_from_spec",
  "validate_scene_against_spec",
  "analyze_mesh_quality",
  "apply_mesh_cleanup",
  "validate_retopology_result",
  "capture_review_views",
  "list_blender_addons",
  "inspect_addon_capabilities",
  "export_scene"
]

disabled_tools = [
  "execute_blender_code",
  "run_unapproved_addon_operator",
  "delete_all_objects_without_backup"
]
"@
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
        (
            $section -match 'command\s*=\s*"uvx"' -and
            $section -match '"blender-precision-mcp"' -and
            $section -match 'templates/precision/blender_precision_config\.yaml'
        ) -or (
            $section -match 'command\s*=\s*"powershell"' -and
            $section -match 'start_precision_blender_mcp\.ps1'
        )
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
    Install-PrecisionMcpVenv -PlanOnly:$PlanConfigMerge
    Remove-GeneratedPrecisionMcpConfig `
        -ConfigPath $CodexConfigPath `
        -PlanOnly:$PlanConfigMerge

    $configBlock = Get-ManagedPrecisionMcpConfigBlock
    Write-Output "Codex config merge preview: append [mcp_servers.blender_precision] to $CodexConfigPath"
    Write-Output $configBlock.Trim()

    if (-not $PlanConfigMerge) {
        if (-not (Test-Path $CodexRoot)) {
            New-Item -ItemType Directory -Force $CodexRoot | Out-Null
        }
        if (-not (Test-Path $CodexConfigPath)) {
            New-Item -ItemType File -Force $CodexConfigPath | Out-Null
        }
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = "$CodexConfigPath.backup-$timestamp"
        Copy-Item -Force $CodexConfigPath $backupPath
        Add-Content -Encoding UTF8 -Path $CodexConfigPath -Value "`r`n$configBlock`r`n"
        Write-Output "Codex config backup created: $backupPath"
        Write-Output "Codex config merged: [mcp_servers.blender_precision]"
    }
} else {
    Write-Output "Codex config merge skipped. Template copied to: $(Join-Path $ProfileRoot 'codex_config.toml')"
}

Write-Output "Precision profile templates installed to: $ProfileRoot"
Write-Output "Skill installed to: $SkillRoot"
Write-Output "Subagent templates installed to: $SubagentRoot"
Write-Output "Codex App restart is required before using newly installed skills or MCP profile examples."
