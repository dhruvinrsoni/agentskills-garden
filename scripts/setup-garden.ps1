<#
.SYNOPSIS
    First-machine setup for agentskills-garden. Clones the garden to a fork-safe
    location, persists settings in ~/.gitconfig under the [agentskills] section, and
    optionally prepends <garden>\scripts to the user PATH.

    (Renamed from bootstrap.ps1 to setup-garden.ps1 — the action verb is clearer for
    end users. The old name lives on only in older blog posts and forks.)

.DESCRIPTION
    Designed to be runnable as a single web-install one-liner:

        iwr https://raw.githubusercontent.com/dhruvinrsoni/agentskills-garden/main/scripts/setup-garden.ps1 | iex

    What it does:
      1. Determines <gh-user> (from -GhUser, agentskills.ghUser, $env:GITHUB_USER,
         or prompts interactively).
      2. Determines <root> (from -Root, agentskills.root, $env:AGENTSKILLS_ROOT,
         or defaults to $env:USERPROFILE\github).
      3. Computes target path <root>\github\<gh-user>\agentskills-garden.
         (When <root> already ends in 'github', the 'github' segment is not duplicated.)
      4. Clones the garden there if missing (skipped if it already exists).
      5. Persists agentskills.path, agentskills.root, agentskills.ghUser in ~/.gitconfig.
      6. Optionally prepends <garden>\scripts to the User PATH (-AddToPath).
      7. Prints next-step guidance.

.PARAMETER GhUser
    GitHub username owning the fork of agentskills-garden to clone.
    Default resolution: agentskills.ghUser -> $env:GITHUB_USER -> interactive prompt.

.PARAMETER Root
    Base directory under which <gh-user>/agentskills-garden is placed.
    Default resolution: agentskills.root -> $env:AGENTSKILLS_ROOT -> $env:USERPROFILE\github.

.PARAMETER Branch
    Branch to clone. Defaults to main.

.PARAMETER AddToPath
    If set, prepends <garden>\scripts to the User PATH so link-skills.ps1 resolves
    without a full path.

.PARAMETER Force
    Re-run even if the garden folder already exists (will not re-clone; only re-persists
    git config).

.EXAMPLE
    iwr https://raw.githubusercontent.com/dhruvinrsoni/agentskills-garden/main/scripts/setup-garden.ps1 | iex

.EXAMPLE
    .\setup-garden.ps1 -GhUser dhruvinrsoni -AddToPath

.LINK
    https://github.com/dhruvinrsoni/agentskills-garden
#>

[CmdletBinding()]
param(
    [string]$GhUser,
    [string]$Root,
    [string]$Branch = 'main',
    [switch]$AddToPath,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Write-Step([string]$msg)    { Write-Host "[setup-garden] $msg" -ForegroundColor Cyan }
function Write-StepOk([string]$msg)  { Write-Host "[setup-garden] $msg" -ForegroundColor Green }
function Write-StepWarn([string]$msg){ Write-Host "[setup-garden] $msg" -ForegroundColor Yellow }
function Write-StepErr([string]$msg) { Write-Host "[setup-garden] $msg" -ForegroundColor Red }

function Get-GitConfigValue([string]$key) {
    try {
        $raw = & git config --global --get $key 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
        return $raw.Trim()
    } catch { return $null }
}

function Set-GitConfigValue([string]$key, [string]$value) {
    & git config --global $key $value
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to set git config $key=$value"
    }
}

# --- git presence check ---

try {
    $null = & git --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw "not found" }
} catch {
    Write-StepErr "git is not available on PATH. Install Git for Windows first: https://git-scm.com/download/win"
    exit 1
}

# --- resolve GhUser ---

if (-not $GhUser) { $GhUser = Get-GitConfigValue 'agentskills.ghUser' }
if (-not $GhUser) { $GhUser = $env:GITHUB_USER }
if (-not $GhUser) {
    $GhUser = Read-Host "GitHub username that owns your agentskills-garden fork"
}
if ([string]::IsNullOrWhiteSpace($GhUser)) {
    Write-StepErr "GitHub username is required."
    exit 1
}
$GhUser = $GhUser.Trim()

# --- resolve Root ---

if (-not $Root) { $Root = Get-GitConfigValue 'agentskills.root' }
if (-not $Root) { $Root = $env:AGENTSKILLS_ROOT }
if (-not $Root) { $Root = Join-Path $env:USERPROFILE 'github' }
$Root = $Root.TrimEnd('\')

# --- compute target ---

# Avoid double 'github' segment when the root already ends with 'github'.
$rootLeaf = Split-Path -Leaf $Root
if ($rootLeaf -ieq 'github') {
    $userParent = Join-Path $Root $GhUser
} else {
    $userParent = Join-Path (Join-Path $Root 'github') $GhUser
}
$gardenPath = Join-Path $userParent 'agentskills-garden'

Write-Step "GitHub user:  $GhUser"
Write-Step "Root:         $Root"
Write-Step "Target path:  $gardenPath"

# --- clone if missing ---

if (Test-Path -LiteralPath $gardenPath) {
    if ((Test-Path -LiteralPath (Join-Path $gardenPath '.git')) -and
        (Test-Path -LiteralPath (Join-Path $gardenPath 'skills'))) {
        Write-StepOk "Garden already present at $gardenPath (skipping clone)"
    } else {
        Write-StepErr "Path $gardenPath exists but does not look like a garden clone (no .git or no skills/). Refusing to touch it."
        exit 1
    }
} else {
    if (-not (Test-Path -LiteralPath $userParent)) {
        New-Item -ItemType Directory -Path $userParent -Force | Out-Null
        Write-Step "Created parent directory: $userParent"
    }
    $repoUrl = "https://github.com/$GhUser/agentskills-garden.git"
    Write-Step "Cloning $repoUrl (branch $Branch) into $gardenPath ..."
    & git clone --branch $Branch $repoUrl $gardenPath
    if ($LASTEXITCODE -ne 0) {
        Write-StepErr "git clone failed. Verify https://github.com/$GhUser/agentskills-garden exists and is accessible."
        exit 1
    }
    Write-StepOk "Clone complete."
}

# --- persist config ---

Write-Step "Persisting settings in ~/.gitconfig under [agentskills] ..."
Set-GitConfigValue 'agentskills.path'   $gardenPath
Set-GitConfigValue 'agentskills.root'   $Root
Set-GitConfigValue 'agentskills.ghUser' $GhUser
Set-GitConfigValue 'agentskills.defaultTarget' 'cursor'
Write-StepOk "Saved: agentskills.path / agentskills.root / agentskills.ghUser / agentskills.defaultTarget"

# --- PATH update ---

$scriptsDir = Join-Path $gardenPath 'scripts'
if ($AddToPath) {
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if (-not $userPath) { $userPath = '' }
    $already = $userPath -split ';' | Where-Object { $_.TrimEnd('\') -ieq $scriptsDir.TrimEnd('\') }
    if ($already) {
        Write-Step "User PATH already contains $scriptsDir (skipped)"
    } else {
        $newPath = if ($userPath) { "$scriptsDir;$userPath" } else { $scriptsDir }
        [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
        Write-StepOk "Prepended $scriptsDir to User PATH (open a new shell for it to take effect)"
    }
}

# --- next steps ---

Write-Host ''
Write-StepOk 'Garden setup complete.'
Write-Host ''
Write-Host 'Next steps:' -ForegroundColor White
Write-Host "  1. Open any consumer repo." -ForegroundColor White
if ($AddToPath) {
    Write-Host "  2. Run:  link-skills.ps1           (defaults to .cursor/skills)" -ForegroundColor White
    Write-Host "          link-skills.ps1 -Target claude|github|generic|custom -LinkPath <path>" -ForegroundColor White
    Write-Host "          link-skills.ps1 -Status    (see what's linked)" -ForegroundColor White
    Write-Host "          link-skills.ps1 -Unlink    (remove the link)" -ForegroundColor White
} else {
    Write-Host "  2. Run:  & `"$scriptsDir\link-skills.ps1`"" -ForegroundColor White
    Write-Host "     Or re-run setup-garden with -AddToPath to get a shorter invocation." -ForegroundColor White
}
Write-Host ''
