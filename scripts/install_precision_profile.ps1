param(
    [string]$CodexHome = "$env:USERPROFILE\.codex"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$TemplateRoot = Join-Path $RepoRoot "templates\precision"
$CodexRoot = [System.IO.Path]::GetFullPath($CodexHome)
$ProfileRoot = Join-Path $CodexRoot "blender-precision"
$SkillRoot = Join-Path $CodexRoot "skills\precise-blender-modeling"
$SubagentRoot = Join-Path $CodexRoot "subagents"

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

Write-Output "Precision profile templates installed to: $ProfileRoot"
Write-Output "Skill installed to: $SkillRoot"
Write-Output "Subagent templates installed to: $SubagentRoot"
Write-Output "Codex App restart is required before using newly installed skills or MCP profile examples."
