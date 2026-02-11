# ============================================================================
# Agent Skills Garden — Mega Installer (PowerShell)
# Run: pwsh ./setup_skills.ps1
# ============================================================================

Write-Host "🌱 Creating Agent Skills Garden (Full Suite)..." -ForegroundColor Green

# Check if WSL is available
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    Write-Host "   Using WSL bash for installation (ensures consistency with setup_skills.sh)..." -ForegroundColor Cyan
    wsl bash ./setup_skills.sh
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Installation complete!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "`n❌ WSL installation failed. Falling back to PowerShell native..." -ForegroundColor Yellow
    }
}

# Fallback: PowerShell native implementation
Write-Host "   Using PowerShell native installation..." -ForegroundColor Cyan

# Create directories
$directories = @(
    "skills/00-foundation",
    "skills/10-discovery", 
    "skills/20-architecture",
    "skills/30-implementation",
    "skills/40-quality",
    "skills/50-performance",
    "skills/60-security",
    "skills/70-devops",
    "skills/80-docs",
    "skills/90-maintenance",
    "templates"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

Write-Host "`n⚠️  Warning: PowerShell native mode generates basic skill templates only." -ForegroundColor Yellow
Write-Host "   For full skill content, please run: wsl bash ./setup_skills.sh" -ForegroundColor Yellow
Write-Host "`n   Or install WSL: wsl --install" -ForegroundColor Cyan

# Create basic skill structure (simplified - full content is in bash script)
$basicSkills = @{
    "skills/00-foundation/constitution.md" = @"
---
name: constitution
description: The foundational constitution of the Agent Skills Garden
version: "1.0.0"
---

# Constitution

Please run the bash script for full content: ``````bash setup_skills.sh``````
"@
}

Write-Host "`n📝 Creating skill files..." -ForegroundColor Cyan
foreach ($file in $basicSkills.Keys) {
    $basicSkills[$file] | Out-File -FilePath $file -Encoding UTF8
    Write-Host "  ✔ $file" -ForegroundColor Green
}

Write-Host "`n⚠️  Installation incomplete. Please run:" -ForegroundColor Yellow
Write-Host "   wsl bash ./setup_skills.sh" -ForegroundColor Cyan
Write-Host "`nOr install complete skills from the repository." -ForegroundColor Yellow
