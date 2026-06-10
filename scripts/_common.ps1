<#
.SYNOPSIS
    Shared helpers for the agentskills-garden PowerShell scripts (promotion flow).

.DESCRIPTION
    Dot-source this file from a script:  . "$PSScriptRoot\_common.ps1"

    Provides one source of truth for: coloured step output, git-config reads,
    garden discovery (same order as link-skills.ps1), plan/confirm prompting,
    SKILL.md frontmatter read/patch, domain->folder mapping, and the core
    "import a ready draft into the garden" routine used by both promote-skills.ps1
    (push, run in a consumer repo) and gather-skills.ps1 (garden-side bulk).

    Not meant to be run directly — it only defines functions.
#>

# ---------- output helpers ----------
function Write-Step([string]$msg)     { Write-Host "[agentskills] $msg" -ForegroundColor Cyan }
function Write-StepOk([string]$msg)   { Write-Host "[agentskills] $msg" -ForegroundColor Green }
function Write-StepWarn([string]$msg) { Write-Host "[agentskills] $msg" -ForegroundColor Yellow }
function Write-StepErr([string]$msg)  { Write-Host "[agentskills] $msg" -ForegroundColor Red }

# ---------- git config ----------
function Get-GitConfigValue([string]$key) {
    try {
        $raw = & git config --global --get $key 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
        return $raw.Trim()
    } catch { return $null }
}

function Get-GitConfigMulti([string]$key) {
    try {
        $raw = & git config --global --get-all $key 2>$null
        if ($LASTEXITCODE -ne 0) { return @() }
        return @($raw | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_.Trim() })
    } catch { return @() }
}

# ---------- garden discovery (mirrors link-skills.ps1) ----------
function Resolve-AgentskillsGarden([string]$Path) {
    if ($Path) {
        if (-not (Test-Path -LiteralPath $Path)) { throw "Explicit -Garden path does not exist: $Path" }
        return (Resolve-Path -LiteralPath $Path).ProviderPath
    }
    $cfg = Get-GitConfigValue 'agentskills.path'
    if ($cfg -and (Test-Path -LiteralPath $cfg)) { return (Resolve-Path -LiteralPath $cfg).ProviderPath }

    if ($env:AGENTSKILLS_GARDEN -and (Test-Path -LiteralPath $env:AGENTSKILLS_GARDEN)) {
        return (Resolve-Path -LiteralPath $env:AGENTSKILLS_GARDEN).ProviderPath
    }
    $root = Get-GitConfigValue 'agentskills.root'
    if (-not $root) { $root = $env:AGENTSKILLS_ROOT }
    if (-not $root) { $root = Join-Path $env:USERPROFILE 'github' }
    $ghUser = Get-GitConfigValue 'agentskills.ghUser'
    if (-not $ghUser) { $ghUser = $env:GITHUB_USER }
    if ($ghUser) {
        $candidate = Join-Path (Join-Path $root $ghUser) 'agentskills-garden'
        if (Test-Path -LiteralPath $candidate) { return (Resolve-Path -LiteralPath $candidate).ProviderPath }
    }
    if ($PSCommandPath) {
        $maybe = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
        if ((Test-Path (Join-Path $maybe 'skills')) -and (Test-Path (Join-Path $maybe 'registry.yaml'))) {
            return (Resolve-Path -LiteralPath $maybe).ProviderPath
        }
    }
    throw @(
        "Could not locate agentskills-garden.",
        "Configure it once via one of:",
        "  git config --global agentskills.path `"<full-path-to-garden>`"",
        "  `$env:AGENTSKILLS_GARDEN = `"<full-path-to-garden>`"",
        "  Or pass -Garden <full-path> explicitly."
    ) -join [Environment]::NewLine
}

# ---------- plan + confirm ----------
function Test-AgentNonInteractive([bool]$Yes) {
    if ($Yes) { return $true }
    try { return [Console]::IsInputRedirected } catch { return $false }
}

function Confirm-AgentPlan([string[]]$planLines, [bool]$AutoYes) {
    Write-Host ''
    Write-Host 'Plan:' -ForegroundColor White
    foreach ($line in $planLines) { Write-Host "  $line" -ForegroundColor White }
    Write-Host ''
    if (Test-AgentNonInteractive $AutoYes) {
        Write-Step 'Auto-confirmed (-Yes or non-interactive stdin).'
        return $true
    }
    $ans = Read-Host 'Proceed? [y/N]'
    return ($ans -match '^(y|yes)$')
}

# ---------- domain -> numbered folder (mirror of taxonomy.REGISTERED_DOMAINS) ----------
$script:RegisteredDomains = [ordered]@{
    foundation  = '000'
    engineering = '100'
    writing     = '200'
    'data-ml'   = '300'
    business    = '400'
}
function Get-DomainFolder([string]$domain) {
    if ($script:RegisteredDomains.Contains($domain)) {
        return ("{0}-{1}" -f $script:RegisteredDomains[$domain], $domain)
    }
    return $null
}

# ---------- SKILL.md frontmatter (lightweight, top-level keys only) ----------
function Get-SkillFrontmatter([string]$path) {
    $text = Get-Content -LiteralPath $path -Raw
    $fields = @{}
    if ($text -match '(?s)^---\s*\r?\n(.*?)\r?\n---') {
        foreach ($line in ($matches[1] -split "\r?\n")) {
            # top-level keys only (no leading whitespace) — skips indented metadata
            if ($line -match '^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$') {
                $k = $matches[1]
                if (-not $fields.ContainsKey($k)) { $fields[$k] = $matches[2].Trim() }
            }
        }
    }
    return @{ Raw = $text; Fields = $fields }
}

# Patch top-level frontmatter keys (replace if present, else insert before metadata:
# / closing ---). $patch is an ordered hashtable of key -> value.
function Set-SkillFrontmatterFields([string]$path, $patch) {
    $text = Get-Content -LiteralPath $path -Raw
    if ($text -notmatch '(?s)^(---\s*\r?\n)(.*?)(\r?\n---)') { return $false }
    $open = $matches[1]; $block = $matches[2]; $close = $matches[3]
    $rest = $text.Substring(($open + $block + $close).Length)

    $nl = "`n"
    $lines = $block -split "\r?\n"
    foreach ($key in $patch.Keys) {
        $val = [string]$patch[$key]
        $rx = "^$([regex]::Escape($key)):\s*.*$"
        $replaced = $false
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match $rx) { $lines[$i] = "${key}: $val"; $replaced = $true; break }
        }
        if (-not $replaced) {
            $idx = ($lines | Select-String -Pattern '^metadata:' | Select-Object -First 1).LineNumber
            if ($idx) { $lines = $lines[0..($idx-2)] + "${key}: $val" + $lines[($idx-1)..($lines.Count-1)] }
            else      { $lines += "${key}: $val" }
        }
    }
    $newText = $open + ($lines -join $nl) + $close + $rest
    Set-Content -LiteralPath $path -Value $newText -NoNewline -Encoding UTF8
    return $true
}

# ---------- ready-draft discovery + import ----------
function Find-ReadyDrafts([string]$draftsDir) {
    $out = @()
    if (-not (Test-Path -LiteralPath $draftsDir)) { return ,$out }
    Get-ChildItem -LiteralPath $draftsDir -Recurse -Filter 'SKILL.md' -File | ForEach-Object {
        $fm = Get-SkillFrontmatter $_.FullName
        $status = $fm.Fields['status']
        $out += [pscustomobject]@{
            SkillMd   = $_.FullName
            Dir       = Split-Path -Parent $_.FullName
            Name      = $fm.Fields['name']
            Domain    = $fm.Fields['domain']
            Category  = $fm.Fields['category']
            Status    = $status
            Promoted  = ($status -eq 'promoted')
        }
    }
    return ,$out
}

# Compute the garden target directory for a draft. Foundation is flat; other
# domains nest under their category folder when the draft declares one.
function Get-GardenTargetDir([string]$garden, $draft) {
    $folder = Get-DomainFolder $draft.Domain
    if (-not $folder) { throw "draft '$($draft.Name)' has unknown/missing domain '$($draft.Domain)'" }
    $parts = @($garden, 'skills', $folder)
    if ($draft.Domain -ne 'foundation' -and $draft.Category) { $parts += $draft.Category }
    $parts += $draft.Name
    return ($parts -join [IO.Path]::DirectorySeparatorChar)
}

# Returns one of: 'skipped-promoted','conflict','imported','dry'
function Import-ReadyDraft($garden, $draft, [string]$onConflict, [bool]$move, [bool]$apply) {
    if ($draft.Promoted) { return 'skipped-promoted' }
    if (-not $draft.Name)   { throw "draft at $($draft.Dir) has no 'name' in frontmatter" }
    if (-not $draft.Domain) { throw "draft '$($draft.Name)' has no 'domain' in frontmatter" }

    $target = Get-GardenTargetDir $garden $draft
    $rel = $target.Substring($garden.Length).TrimStart('\','/')

    if (Test-Path -LiteralPath $target) {
        switch ($onConflict) {
            'overwrite' { Write-StepWarn "overwriting existing $rel" }
            'rename'    {
                $n = 2
                while (Test-Path -LiteralPath ($target + "-$n")) { $n++ }
                $target = $target + "-$n"; $rel = $rel + "-$n"
                Write-StepWarn "target existed; importing as $rel"
            }
            default     { Write-StepWarn "SKIP $($draft.Name): target $rel already exists (use -OnConflict overwrite|rename)"; return 'conflict' }
        }
    }

    $relSlash = $rel -replace '\\','/'
    Write-Step "import $($draft.Name)  ->  $relSlash"
    if (-not $apply) { return 'dry' }

    if ((Test-Path -LiteralPath $target) -and $onConflict -eq 'overwrite') {
        Remove-Item -LiteralPath $target -Recurse -Force
    }
    $parent = Split-Path -Parent $target
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    Copy-Item -LiteralPath $draft.Dir -Destination $target -Recurse -Force

    # Mark the imported copy as published.
    Set-SkillFrontmatterFields (Join-Path $target 'SKILL.md') ([ordered]@{ status = 'published' }) | Out-Null

    # Mark the source so re-runs skip it (unless moving it away entirely).
    if ($move) {
        Remove-Item -LiteralPath $draft.Dir -Recurse -Force
        Write-Step "moved (removed) source draft $($draft.Name)"
    } else {
        $stamp = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssK')
        Set-SkillFrontmatterFields $draft.SkillMd ([ordered]@{
            status = 'promoted'; promoted_to = $relSlash; promoted_at = $stamp
        }) | Out-Null
    }
    Write-StepOk "imported $($draft.Name)"
    return 'imported'
}
