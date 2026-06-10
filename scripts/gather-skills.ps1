<#
.SYNOPSIS
    Bulk-pull finalized skill drafts from ALL known consumer repos up into the
    garden, in one shot. Run from the garden (the central side of the push/pull).

.DESCRIPTION
    The garden-side counterpart to promote-skills.ps1. Instead of pushing from one repo,
    this discovers every consumer repo and imports each one's `status: ready`
    drafts (under .agentskills/drafts/) into the correct garden domain/category.

    Consumer discovery (union of):
      1. -Repos <paths...>                       (explicit, highest priority)
      2. git config --global --get-all agentskills.consumers  (repos anywhere)
      3. <root>\github\<ghUser>\*                 (siblings of the garden) that
         contain a .agentskills\drafts folder
         where <root>=agentskills.root|$env:AGENTSKILLS_ROOT|%USERPROFILE%\github
               <ghUser>=agentskills.ghUser|$env:GITHUB_USER

    Idempotent: a draft already marked `status: promoted` is skipped, so this is
    safe to re-run. Never overwrites an existing garden skill unless -OnConflict
    overwrite|rename is given.

.PARAMETER Garden     Explicit path to the garden (default: auto-discovered / this repo).
.PARAMETER Root       Override the scan root for sibling repos.
.PARAMETER Repos      Explicit consumer repo paths to include.
.PARAMETER OnConflict skip (default) | overwrite | rename.
.PARAMETER DryRun     Print the combined plan and touch nothing.
.PARAMETER Yes        (Aliases -y, -NonInteractive) skip the y/N prompt.
.PARAMETER Help       (Aliases -h) show usage.

.EXAMPLE
    .\gather-skills.ps1 -DryRun
.EXAMPLE
    .\gather-skills.ps1 -Repos C:\work\app-a, C:\work\app-b -Yes
.LINK
    docs/skills-bridge.md
#>
[CmdletBinding()]
param(
    [string]$Garden,
    [string]$Root,
    [string[]]$Repos,
    [ValidateSet('skip','overwrite','rename')][string]$OnConflict = 'skip',
    [switch]$DryRun,
    [Alias('NonInteractive','y')][switch]$Yes,
    [Alias('h')][switch]$Help
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\_common.ps1"

if ($Help) {
    @'
gather-skills.ps1 — bulk-collect ready drafts from every consumer repo.

USAGE
   .\gather-skills.ps1 [-Repos <p1>,<p2>] [-Root <dir>] [-Garden <dir>]
                       [-OnConflict skip|overwrite|rename] [-DryRun] [-Yes]

   Discovers consumer repos (explicit -Repos + git config agentskills.consumers
   + siblings under <root>\github\<ghUser> that have .agentskills\drafts),
   scans each for SKILL.md with `status: ready`, and imports them into the
   garden. Idempotent (already-promoted drafts are skipped).
'@ | Write-Host
    exit 0
}

try { $garden = Resolve-AgentskillsGarden $Garden }
catch { Write-StepErr $_.Exception.Message; exit 1 }
Write-Step "Garden: $garden"

# ---- discover consumer repos ----
$repoSet = [System.Collections.Generic.List[string]]::new()
function Add-Repo([string]$p) {
    if ([string]::IsNullOrWhiteSpace($p)) { return }
    if (-not (Test-Path -LiteralPath $p)) { return }
    $full = (Resolve-Path -LiteralPath $p).ProviderPath
    if (-not $repoSet.Contains($full)) { [void]$repoSet.Add($full) }
}

foreach ($r in ($Repos | Where-Object { $_ })) { Add-Repo $r }
foreach ($r in (Get-GitConfigMulti 'agentskills.consumers')) { Add-Repo $r }

if (-not $Root) { $Root = Get-GitConfigValue 'agentskills.root' }
if (-not $Root) { $Root = $env:AGENTSKILLS_ROOT }
if (-not $Root) { $Root = Join-Path $env:USERPROFILE 'github' }
$ghUser = Get-GitConfigValue 'agentskills.ghUser'
if (-not $ghUser) { $ghUser = $env:GITHUB_USER }
$scanBase = if ($ghUser) { Join-Path $Root $ghUser } else { $Root }
if (Test-Path -LiteralPath $scanBase) {
    Get-ChildItem -LiteralPath $scanBase -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        if (Test-Path -LiteralPath (Join-Path $_.FullName '.agentskills/drafts')) { Add-Repo $_.FullName }
    }
}

if ($repoSet.Count -eq 0) {
    Write-Step "No consumer repos with .agentskills/drafts found (scanned $scanBase)."
    Write-Step "Add one explicitly: -Repos <path>, or 'git config --global --add agentskills.consumers <path>'."
    exit 0
}
Write-Step "Consumer repos: $($repoSet.Count)"

# ---- gather ready drafts across all repos ----
$jobs = @()
foreach ($repo in $repoSet) {
    $draftsDir = Join-Path $repo '.agentskills/drafts'
    foreach ($d in (Find-ReadyDrafts $draftsDir)) {
        if ($d.Status -eq 'ready') { $jobs += [pscustomobject]@{ Repo = $repo; Draft = $d } }
    }
}

if ($jobs.Count -eq 0) {
    Write-Step "No drafts with status: ready across $($repoSet.Count) repo(s)."
    exit 0
}

# ---- combined plan ----
$plan = @()
foreach ($j in $jobs) {
    try { $t = Get-GardenTargetDir $garden $j.Draft } catch { Write-StepErr $_.Exception.Message; exit 1 }
    $rel = $t.Substring($garden.Length).TrimStart('\','/') -replace '\\','/'
    $repoName = Split-Path -Leaf $j.Repo
    $plan += "[$repoName] $($j.Draft.Name)  ->  $rel" + $(if (Test-Path -LiteralPath $t) { "   [exists -> $OnConflict]" } else { '' })
}

$apply = -not $DryRun
if ($apply) {
    if (-not (Confirm-AgentPlan $plan ([bool]$Yes))) { Write-Step 'Aborted by user. No changes made.'; exit 0 }
} else {
    Write-Host ''; Write-Host 'Plan (dry-run):' -ForegroundColor White
    foreach ($l in $plan) { Write-Host "  $l" }
}

$imported = 0; $conflicts = 0
foreach ($j in $jobs) {
    try {
        $r = Import-ReadyDraft $garden $j.Draft $OnConflict $false $apply
        if ($r -eq 'imported') { $imported++ } elseif ($r -eq 'conflict') { $conflicts++ }
    } catch { Write-StepErr "pull $($j.Draft.Name): $($_.Exception.Message)"; $conflicts++ }
}

Write-Host ''
if ($apply) { Write-StepOk "Done. Imported $imported, conflicts/skipped $conflicts from $($repoSet.Count) repo(s)." }
else        { Write-Step  "Dry run complete. Would import $($jobs.Count) from $($repoSet.Count) repo(s)." }
exit 0
