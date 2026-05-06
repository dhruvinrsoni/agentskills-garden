<#
.SYNOPSIS
    Link the agentskills-garden skills folder into a consumer repo as a live junction.

.DESCRIPTION
    Creates a Windows directory junction (mklink /J) inside the current directory
    pointing at the agentskills-garden's skills/ folder, so any repo can consume
    the garden's skills live without copying files. Pulling/editing in the garden
    is reflected instantly in every consumer repo.

    Garden discovery order:
      1. -Path CLI argument
      2. git config --global --get agentskills.path
      3. $env:AGENTSKILLS_GARDEN
      4. Fork-safe default: <root>\github\<gh-user>\agentskills-garden
         where <root>   = agentskills.root | $env:AGENTSKILLS_ROOT | $env:USERPROFILE\github
               <gh-user>= agentskills.ghUser | $env:GITHUB_USER
      5. Script's own parent (useful when invoked from a cloned garden)

.PARAMETER Target
    Named convention for the link location. One of:
      cursor  -> .cursor/skills     (default)
      claude  -> .claude/skills
      github  -> .github/skills
      generic -> skills
      custom  -> requires -LinkPath

.PARAMETER LinkPath
    Custom link path relative to the current directory. Required with -Target custom;
    also acts as an override for other targets.

.PARAMETER Path
    Explicit path to the agentskills-garden repo root (overrides discovery).

.PARAMETER Force
    Replace an existing junction at the link path (real folders are never overwritten).

.PARAMETER Unlink
    Remove an existing junction at the resolved link path.

.PARAMETER Status
    Show where the garden is resolved from and what is currently linked in $PWD.

.EXAMPLE
    .\link-skills.ps1

.EXAMPLE
    .\link-skills.ps1 -Target claude

.EXAMPLE
    .\link-skills.ps1 -Target custom -LinkPath ".agent/skills"

.EXAMPLE
    .\link-skills.ps1 -Unlink

.EXAMPLE
    .\link-skills.ps1 -Status

.LINK
    https://github.com/dhruvinrsoni/agentskills-garden
#>

[CmdletBinding(DefaultParameterSetName = 'Link')]
param(
    [Parameter(ParameterSetName = 'Link')]
    [Parameter(ParameterSetName = 'Unlink')]
    [ValidateSet('cursor', 'claude', 'github', 'generic', 'custom')]
    [string]$Target = 'cursor',

    [Parameter(ParameterSetName = 'Link')]
    [Parameter(ParameterSetName = 'Unlink')]
    [string]$LinkPath,

    [Parameter(ParameterSetName = 'Link')]
    [string]$Path,

    [Parameter(ParameterSetName = 'Link')]
    [switch]$Force,

    [Parameter(ParameterSetName = 'Unlink', Mandatory = $true)]
    [switch]$Unlink,

    [Parameter(ParameterSetName = 'Status', Mandatory = $true)]
    [switch]$Status
)

$ErrorActionPreference = 'Stop'

# ---------- output helpers ----------

function Write-Step([string]$msg)    { Write-Host "[skills-bridge] $msg" -ForegroundColor Cyan }
function Write-StepOk([string]$msg)  { Write-Host "[skills-bridge] $msg" -ForegroundColor Green }
function Write-StepWarn([string]$msg){ Write-Host "[skills-bridge] $msg" -ForegroundColor Yellow }
function Write-StepErr([string]$msg) { Write-Host "[skills-bridge] $msg" -ForegroundColor Red }

# ---------- resolution helpers ----------

function Get-GitConfigValue([string]$key) {
    try {
        $raw = & git config --global --get $key 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
        return $raw.Trim()
    } catch {
        return $null
    }
}

function Test-IsReparsePoint([string]$p) {
    if (-not (Test-Path -LiteralPath $p)) { return $false }
    try {
        $item = Get-Item -LiteralPath $p -Force
        return (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
    } catch {
        return $false
    }
}

function Get-JunctionTarget([string]$p) {
    if (-not (Test-IsReparsePoint $p)) { return $null }
    try {
        $item = Get-Item -LiteralPath $p -Force
        if ($null -ne $item.Target) {
            if ($item.Target -is [array]) { return $item.Target[0] }
            return $item.Target
        }
    } catch {}
    return $null
}

function Resolve-GardenPath {
    # 1. explicit -Path
    if ($Path) {
        if (-not (Test-Path -LiteralPath $Path)) {
            throw "Explicit -Path does not exist: $Path"
        }
        return (Resolve-Path -LiteralPath $Path).ProviderPath
    }

    # 2. git config
    $cfg = Get-GitConfigValue 'agentskills.path'
    if ($cfg -and (Test-Path -LiteralPath $cfg)) {
        return (Resolve-Path -LiteralPath $cfg).ProviderPath
    }

    # 3. env var
    if ($env:AGENTSKILLS_GARDEN -and (Test-Path -LiteralPath $env:AGENTSKILLS_GARDEN)) {
        return (Resolve-Path -LiteralPath $env:AGENTSKILLS_GARDEN).ProviderPath
    }

    # 4. fork-safe default
    $root = Get-GitConfigValue 'agentskills.root'
    if (-not $root) { $root = $env:AGENTSKILLS_ROOT }
    if (-not $root) { $root = Join-Path $env:USERPROFILE 'github' }

    $ghUser = Get-GitConfigValue 'agentskills.ghUser'
    if (-not $ghUser) { $ghUser = $env:GITHUB_USER }

    if ($ghUser) {
        $candidate = Join-Path (Join-Path $root $ghUser) 'agentskills-garden'
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).ProviderPath
        }
    }

    # 5. script's own parent (if invoked from inside a cloned garden)
    if ($PSCommandPath) {
        $scriptDir = Split-Path -Parent $PSCommandPath
        if ($scriptDir) {
            $maybeGarden = Split-Path -Parent $scriptDir
            if ((Test-Path (Join-Path $maybeGarden 'skills')) -and
                (Test-Path (Join-Path $maybeGarden 'registry.yaml'))) {
                return (Resolve-Path -LiteralPath $maybeGarden).ProviderPath
            }
        }
    }

    $hint = @(
        "Could not locate agentskills-garden.",
        "Configure it once via one of:",
        "  git config --global agentskills.path `"<full-path-to-garden>`"",
        "  `$env:AGENTSKILLS_GARDEN = `"<full-path-to-garden>`"",
        "  Or pass -Path <full-path> explicitly.",
        "Run scripts/setup-garden.ps1 from the garden repo to auto-configure."
    ) -join [Environment]::NewLine
    throw $hint
}

function Resolve-LinkRelPath([string]$t, [string]$explicit) {
    if ($explicit) { return ($explicit -replace '\\', '/') }
    switch ($t) {
        'cursor'  { '.cursor/skills' }
        'claude'  { '.claude/skills' }
        'github'  { '.github/skills' }
        'generic' { 'skills' }
        'custom'  { throw "-Target custom requires -LinkPath" }
    }
}

# ---------- gitignore helper ----------

function Add-GitignoreEntry([string]$relLinkPath) {
    $gi = Join-Path $PWD '.gitignore'
    $normalized = ($relLinkPath -replace '\\', '/').TrimStart('/')
    $line = "/$normalized"
    $header = '# agentskills-garden bridge link (junction to live skills folder)'

    if (-not (Test-Path -LiteralPath $gi)) {
        Set-Content -Path $gi -Value @($header, $line) -Encoding UTF8
        Write-StepOk "Created .gitignore with entry '$line'"
        return
    }

    $existing = Get-Content -LiteralPath $gi
    $hit = $existing | Where-Object {
        $trimmed = ($_.Trim())
        $trimmed -eq $line -or $trimmed -eq $normalized -or $trimmed -eq "$normalized/"
    }
    if ($hit) {
        Write-Step ".gitignore already contains an entry for '$normalized' (skipped)"
        return
    }

    Add-Content -LiteralPath $gi -Value ''
    Add-Content -LiteralPath $gi -Value $header
    Add-Content -LiteralPath $gi -Value $line
    Write-StepOk "Added '$line' to .gitignore"
}

# ---------- junction helpers ----------

function Get-DriveRoot([string]$p) {
    $full = [IO.Path]::GetFullPath($p)
    return ([IO.Path]::GetPathRoot($full)).TrimEnd('\').ToLowerInvariant()
}

function New-BridgeLink([string]$linkFullPath, [string]$targetFullPath) {
    $linkParent = Split-Path -Parent $linkFullPath
    $linkDrive   = Get-DriveRoot $linkParent
    $targetDrive = Get-DriveRoot $targetFullPath
    $sameVolume  = ($linkDrive -eq $targetDrive)

    if ($sameVolume) {
        $out = & cmd /c "mklink /J `"$linkFullPath`" `"$targetFullPath`"" 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "mklink /J failed ($LASTEXITCODE): $out"
        }
        Write-StepOk "Created junction: $linkFullPath  ->  $targetFullPath"
        return
    }

    Write-StepWarn "Consumer and garden live on different drives ($linkDrive vs $targetDrive)."
    Write-StepWarn "Junctions (/J) do not work across volumes. Falling back to directory symlink (/D)."
    Write-StepWarn "This requires Administrator privileges OR Windows Developer Mode enabled."

    $out = & cmd /c "mklink /D `"$linkFullPath`" `"$targetFullPath`"" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "mklink /D failed ($LASTEXITCODE): $out  -- try an elevated shell or enable Developer Mode."
    }
    Write-StepOk "Created directory symlink: $linkFullPath  ->  $targetFullPath"
}

function Remove-BridgeLink([string]$linkFullPath) {
    $out = & cmd /c "rmdir `"$linkFullPath`"" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "rmdir failed for $linkFullPath  -- $out"
    }
}

# ---------- Status command ----------

if ($Status) {
    Write-Step "Current directory: $PWD"
    try {
        $garden = Resolve-GardenPath
        Write-StepOk  "Garden resolved to: $garden"
        $skillsDir = Join-Path $garden 'skills'
        if (Test-Path -LiteralPath $skillsDir) {
            $count = (Get-ChildItem -LiteralPath $skillsDir -Directory -ErrorAction SilentlyContinue).Count
            Write-Step "Garden has $count top-level skill categories in $skillsDir"
        }
    } catch {
        Write-StepErr $_.Exception.Message
    }

    $conventions = @(
        @{ Name = 'cursor';  Path = '.cursor/skills'  },
        @{ Name = 'claude';  Path = '.claude/skills'  },
        @{ Name = 'github';  Path = '.github/skills'  },
        @{ Name = 'generic'; Path = 'skills'          }
    )
    Write-Step "Link status in $PWD :"
    foreach ($c in $conventions) {
        $full = Join-Path $PWD $c.Path
        if (Test-IsReparsePoint $full) {
            $tgt = Get-JunctionTarget $full
            Write-StepOk ("  {0,-7}  {1,-18}  ->  {2}" -f $c.Name, $c.Path, $tgt)
        } elseif (Test-Path -LiteralPath $full) {
            Write-StepWarn ("  {0,-7}  {1,-18}  (real folder, not a junction)" -f $c.Name, $c.Path)
        } else {
            Write-Host    ("               {0,-18}  (not present)" -f $c.Path) -ForegroundColor DarkGray
        }
    }
    exit 0
}

# ---------- resolve link path ----------

try {
    $relLink = Resolve-LinkRelPath -t $Target -explicit $LinkPath
} catch {
    Write-StepErr $_.Exception.Message
    exit 1
}
$fullLink = [IO.Path]::GetFullPath((Join-Path $PWD $relLink))

# ---------- Unlink command ----------

if ($Unlink) {
    if (-not (Test-Path -LiteralPath $fullLink)) {
        Write-Step "Nothing to remove: $relLink does not exist."
        exit 0
    }
    if (-not (Test-IsReparsePoint $fullLink)) {
        Write-StepErr "$relLink exists but is NOT a junction/symlink. Refusing to delete to avoid data loss."
        exit 1
    }
    try {
        Remove-BridgeLink $fullLink
        Write-StepOk "Removed junction: $relLink"
    } catch {
        Write-StepErr $_.Exception.Message
        exit 1
    }
    exit 0
}

# ---------- Link command (default) ----------

try {
    $garden = Resolve-GardenPath
} catch {
    Write-StepErr $_.Exception.Message
    exit 1
}
$gardenSkills = Join-Path $garden 'skills'
if (-not (Test-Path -LiteralPath $gardenSkills)) {
    Write-StepErr "Garden resolved to '$garden' but no 'skills' subfolder exists there."
    exit 1
}
$gardenSkills = (Resolve-Path -LiteralPath $gardenSkills).ProviderPath

Write-Step "Garden:     $garden"
Write-Step "Source:     $gardenSkills"
Write-Step "Link path:  $relLink  (in $PWD)"

# Ensure parent dir
$linkParent = Split-Path -Parent $fullLink
if ($linkParent -and -not (Test-Path -LiteralPath $linkParent)) {
    New-Item -ItemType Directory -Path $linkParent -Force | Out-Null
    Write-Step "Created parent directory: $linkParent"
}

# Handle existing target
if (Test-Path -LiteralPath $fullLink) {
    if (Test-IsReparsePoint $fullLink) {
        $existingTarget = Get-JunctionTarget $fullLink
        $sameTarget = $false
        if ($existingTarget) {
            try {
                $resolvedExisting = (Resolve-Path -LiteralPath $existingTarget -ErrorAction SilentlyContinue).ProviderPath
                if ($resolvedExisting -and ($resolvedExisting.TrimEnd('\') -ieq $gardenSkills.TrimEnd('\'))) {
                    $sameTarget = $true
                }
            } catch {}
        }
        if ($sameTarget) {
            Write-StepOk "Link already points to the right target. Nothing to change."
            if (Test-Path -LiteralPath (Join-Path $PWD '.git')) {
                Add-GitignoreEntry $relLink
            }
            exit 0
        }
        if (-not $Force) {
            Write-StepErr "A junction already exists at $relLink pointing to '$existingTarget'. Use -Force to replace."
            exit 1
        }
        try {
            Remove-BridgeLink $fullLink
            Write-Step "Removed existing junction (forced)."
        } catch {
            Write-StepErr $_.Exception.Message
            exit 1
        }
    } else {
        Write-StepErr "$relLink exists as a real file/folder. Refusing to overwrite. Move or delete it manually first."
        exit 1
    }
}

# Update gitignore if we're in a git repo
if (Test-Path -LiteralPath (Join-Path $PWD '.git')) {
    try { Add-GitignoreEntry $relLink } catch { Write-StepWarn "Could not update .gitignore: $($_.Exception.Message)" }
} else {
    Write-StepWarn "Current directory is not a git repo. Skipping .gitignore update."
}

# Create junction
try {
    New-BridgeLink -linkFullPath $fullLink -targetFullPath $gardenSkills
} catch {
    Write-StepErr $_.Exception.Message
    exit 1
}

# Verify
$sample = Get-ChildItem -LiteralPath $fullLink -Force -ErrorAction SilentlyContinue | Select-Object -First 1
if ($sample) {
    Write-StepOk "Verified: '$($sample.Name)' is visible through the link."
} else {
    Write-StepWarn "Link created but no entries visible through it. Inspect manually."
}
Write-StepOk "Done. The garden's skills folder is now live at '$relLink'."
