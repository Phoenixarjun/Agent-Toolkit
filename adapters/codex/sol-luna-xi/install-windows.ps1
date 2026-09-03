$ErrorActionPreference = "Stop"

$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillTarget = Join-Path $HOME ".agents\skills\sol-luna-xi"
$AgentTarget = Join-Path $HOME ".codex\agents"

New-Item -ItemType Directory -Force -Path $SkillTarget | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $SkillTarget "agents") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $SkillTarget "references") | Out-Null
New-Item -ItemType Directory -Force -Path $AgentTarget | Out-Null

Copy-Item (Join-Path $Source "SKILL.md") (Join-Path $SkillTarget "SKILL.md") -Force
Copy-Item (Join-Path $Source "agents\openai.yaml") (Join-Path $SkillTarget "agents\openai.yaml") -Force
Copy-Item (Join-Path $Source "references\*.md") (Join-Path $SkillTarget "references") -Force
Copy-Item (Join-Path $Source "runtime-agents\*.toml") $AgentTarget -Force

Write-Host ""
Write-Host "Installed Sol Luna XI."
Write-Host ""
Write-Host "Skill:"
Write-Host $SkillTarget
Write-Host ""
Write-Host "Luna-XI agents:"
Write-Host $AgentTarget
Write-Host ""
Write-Host "Start a fresh Codex task with GPT-5.6 Sol and High reasoning."
Write-Host "Invoke with:"
Write-Host '$sol-luna-xi Implement <task>.'
Write-Host ""
Write-Host "Optional parent config is in config-snippet.toml."
