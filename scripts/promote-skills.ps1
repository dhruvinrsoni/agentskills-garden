<#
.SYNOPSIS
    Promote finalized skill drafts from THIS repo up into the agentskills-garden
    (the git-like "push"). Run from inside a consumer repo.

.DESCRIPTION
    Workflow: draft a skill under .agentskills/drafts/<name>/SKILL.md with
    `status: draft`. When it is ready, set `status: ready` and run this script.
    It copies each ready draft into the correct garden domain/category and marks
    the source `status: promoted` so re-runs skip it.

    Drafts live in a SEPARATE real folder (.agentskills/drafts) — never the
    junctioned .github/.claude/.cursor 'skills' link — so the garden's canonical
    set and your local work-in-progress never collide.

    Garden discovery: -Garden, else git config agentskills.path, else
    $env:AGENTSKILLS_GARDEN, else the fork-safe default. Run install-garden.ps1
    once to populate the git config.

.PARAMETER Garden     Explicit path to the agentskills-garden repo (overrides discovery).
.PARAMETER DraftsDir  Where drafts live (default: .agentskills/drafts under the current dir).
.PARAMETER OnConflict skip (default) | overwrite | rename — what to do if the target exists.
.PARAMETER Move       Remove the source draft after a verified copy (default: keep + mark promoted).
.PARAMETER DryRun     Print the plan and touch nothing.
.PARAMETER Yes        (Aliases -y, -NonInteractive) skip the y/N prompt.
.PARAMETER Help       (Aliases -h) show usage.

.EXAMPLE
    .\promote-skills.ps1 -DryRun
.EXAMPLE
    .\promote-skills.ps1 -OnConflict overwrite -Yes
.LINK
    docs/skills-bridge.md
#>
[CmdletBinding()]
param(
    [string]$Garden,
    [string]$DraftsDir,
    [ValidateSet('skip','overwrite','rename')][string]$OnConflict = 'skip',
    [switch]$Move,
    [switch]$DryRun,
    [Alias('NonInteractive','y')][switch]$Yes,
    [Alias('h')][switch]$Help
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\_common.ps1"

if ($Help) {
    @'
promote-skills.ps1 — push finalized skill drafts from this repo into the garden.

USAGE
   .\promote-skills.ps1 [-DraftsDir <path>] [-Garden <path>]
                 [-OnConflict skip|overwrite|rename] [-Move] [-DryRun] [-Yes]

   Drafts are SKILL.md files under .agentskills/drafts/<name>/ with
   frontmatter `status: ready` and a `domain:` (and optional `category:`).
   Each is copied into skills/<NNN-domain>/[<category>/]<name>/ in the garden,
   marked `status: published`; the source is marked `status: promoted`.

   -DryRun shows the plan without changing anything.
'@ | Write-Host
    exit 0
}

if (-not $DraftsDir) { $DraftsDir = Join-Path $PWD '.agentskills/drafts' }

try { $garden = Resolve-AgentskillsGarden $Garden }
catch { Write-StepErr $_.Exception.Message; exit 1 }

if (-not (Test-Path -LiteralPath $DraftsDir)) {
    Write-Step "No drafts folder at $DraftsDir — nothing to promote."
    exit 0
}

$all = Find-ReadyDrafts $DraftsDir
$ready = @($all | Where-Object { $_.Status -eq 'ready' })
$already = @($all | Where-Object { $_.Promoted })

Write-Step "Garden:  $garden"
Write-Step "Drafts:  $DraftsDir"
Write-Step "Found $($ready.Count) ready, $($already.Count) already promoted, $($all.Count) total."

if ($ready.Count -eq 0) {
    Write-Step "Nothing with status: ready. (Set a draft's frontmatter to 'status: ready' to promote it.)"
    exit 0
}

# Build plan
$plan = @()
foreach ($d in $ready) {
    try { $t = Get-GardenTargetDir $garden $d } catch { Write-StepErr $_.Exception.Message; exit 1 }
    $rel = $t.Substring($garden.Length).TrimStart('\','/') -replace '\\','/'
    $plan += "$($d.Name)  ->  $rel" + $(if (Test-Path -LiteralPath $t) { "   [target exists -> $OnConflict]" } else { '' })
}
if ($Move) { $plan += "(-Move) source drafts will be REMOVED after copy." }
else       { $plan += "sources will be kept and marked status: promoted." }

$apply = -not $DryRun
if ($apply) {
    if (-not (Confirm-AgentPlan $plan ([bool]$Yes))) { Write-Step 'Aborted by user. No changes made.'; exit 0 }
} else {
    Write-Host ''; Write-Host 'Plan (dry-run):' -ForegroundColor White
    foreach ($l in $plan) { Write-Host "  $l" }
}

$imported = 0; $conflicts = 0
foreach ($d in $ready) {
    try {
        $r = Import-ReadyDraft $garden $d $OnConflict ([bool]$Move) $apply
        if ($r -eq 'imported') { $imported++ }
        elseif ($r -eq 'conflict') { $conflicts++ }
    } catch { Write-StepErr "promote $($d.Name): $($_.Exception.Message)"; $conflicts++ }
}

Write-Host ''
if ($apply) { Write-StepOk "Done. Imported $imported, conflicts/skipped $conflicts." }
else        { Write-Step  "Dry run complete. Would import $($ready.Count) (re-run without -DryRun to apply)." }
exit 0
