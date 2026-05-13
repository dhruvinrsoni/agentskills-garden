<#
.SYNOPSIS
    Link the agentskills-garden skills folder into a consumer repo as a live
    Windows junction so any repo can consume the garden's skills without
    copying files.

.DESCRIPTION
    What problem it solves
        You have one canonical garden of agent skills, and you want many
        consumer repos to see those skills live (so pulling/editing the garden
        is reflected instantly in every consumer). Copying is fragile and
        drifts. Submodules are heavy. A Windows directory junction is the
        zero-overhead answer: programs see a real folder, but it actually
        points at the garden's `skills/` directory.

    What this script does
        1. Discovers WHERE the garden lives. Discovery order (each level is a
           fallback for the previous one):
                a. -Path command-line argument (overrides everything)
                b. `git config --global --get agentskills.path`
                c. $env:AGENTSKILLS_GARDEN
                d. Fork-safe default:
                      <root>\github\<gh-user>\agentskills-garden
                   where <root>   = agentskills.root | $env:AGENTSKILLS_ROOT
                                  | %USERPROFILE%\github
                         <gh-user>= agentskills.ghUser | $env:GITHUB_USER
                e. The script's own parent directory (useful when invoked from
                   inside a cloned garden, e.g. during dev/testing).
           Run `setup-garden.ps1` once on a new machine to populate (b).
        2. Picks WHERE inside the current directory the link should live. If
           you did NOT pass -Target on the CLI, the script auto-detects which
           agent convention this repo uses by looking for existing .claude/,
           .cursor/, or .github/ folders in $PWD, and presents a menu. The
           highlighted default is, in order of preference:
                a. The single agent-convention folder it detected (claude /
                   cursor / github), if exactly one is present.
                b. agentskills.defaultTarget from git config (set by
                   setup-garden.ps1).
                c. 'claude'  (the project's sensible first-run default).
           If -Target is on the CLI, the menu is skipped entirely.
        3. Prints a "Plan:" block describing every action it is about to take.
        4. Asks "Proceed? [y/N]". You can answer "n" to abort safely. Skip
           the prompt with -Yes.
        5. Creates a directory junction with `mklink /J`. If the garden and
           the consumer are on different drives, falls back to a directory
           symlink with `mklink /D`, which needs admin or Developer Mode.
        6. Appends an entry to the consumer's .gitignore so the link is not
           committed (only if the consumer directory contains a .git/ folder).

    Operation modes
        -Status   Read-only. Prints where the garden is resolved from, plus a
                  table of which conventions in $PWD are currently linked,
                  which are real folders, and which are absent.
        -Unlink   Removes an existing junction at the resolved link path.
                  Refuses to delete real folders or files (safety check).
        (default) Link mode. Creates the junction described above.

    What it deliberately does NOT do
        - Never overwrites a real folder. If a real (non-junction) folder
          exists at the link path, the script aborts and asks you to move
          it manually.
        - Never deletes the garden's `skills/` source folder.
        - Never modifies the consumer repo outside of (a) the junction itself
          and (b) one line in .gitignore.

.PARAMETER Target
    Named convention for the link location inside $PWD. One of:
        cursor  -> .cursor/skills
        claude  -> .claude/skills
        github  -> .github/skills
        generic -> skills
        custom  -> requires -LinkPath
    If not passed and the script is interactive, an auto-detect menu is shown.
    If not passed and -Yes is set (or stdin is redirected), falls back to
    `agentskills.defaultTarget` from git config, then to 'claude'.

.PARAMETER LinkPath
    Custom link path relative to the current directory. Required with
    `-Target custom`; also acts as an override for the other targets.

.PARAMETER Path
    Explicit path to the agentskills-garden repo root (overrides discovery).

.PARAMETER Force
    Replace an existing junction at the link path. Real folders are NEVER
    overwritten regardless of -Force.

.PARAMETER Unlink
    Remove an existing junction at the resolved link path.

.PARAMETER Status
    Show where the garden is resolved from and what is currently linked in
    $PWD. Read-only; no prompt.

.PARAMETER Yes
    Aliases: -NonInteractive, -y.
    Skip the y/N confirmation prompt and the auto-detect menu. The auto-detect
    menu is also skipped when stdin is redirected. -Status is always read-only
    and does not prompt regardless.

.PARAMETER Help
    Aliases: -h, --help, /?.
    Show the short usage block and exit. (PowerShell's native -? shows the
    longer comment-based help instead — both are intentional.)

.EXAMPLE
    .\link-skills.ps1

    Interactive run. Auto-detects which agent convention this repo uses,
    shows a menu, prints a plan, then asks for y/N.

.EXAMPLE
    .\link-skills.ps1 -Target claude

    Link straight to .claude/skills without showing the menu. Still asks for
    y/N confirmation; use -Yes to skip the prompt too.

.EXAMPLE
    .\link-skills.ps1 -Target claude -Yes

    Fully unattended link into .claude/skills. No menu, no prompt.

.EXAMPLE
    .\link-skills.ps1 -Target custom -LinkPath ".agent/skills"

    Link into a custom path inside $PWD.

.EXAMPLE
    .\link-skills.ps1 -Status

    Show resolution info and link status. Read-only, no prompts.

.EXAMPLE
    .\link-skills.ps1 -Unlink

    Remove the junction at the resolved link path (asks y/N first).

.EXAMPLE
    .\link-skills.ps1 -Help

    Print the short usage block and exit. Same as -h, --help, /?.

.NOTES
    Prerequisites
        - Windows (the script uses `mklink`).
        - For cross-drive links (consumer on D:\, garden on C:\): Administrator
          privileges OR Windows Developer Mode (Settings → Privacy & security
          → For developers → Developer Mode = On).
        - PowerShell 5.1 or PowerShell 7+.

    Exit codes
        0  success or user-aborted-at-prompt (both are non-failure outcomes)
        1  unrecoverable error (no garden found, mklink failed, refused to
           overwrite a real folder, etc.)

    Why .gitignore is touched
        A junction inside a git repo would otherwise be committed as a normal
        directory full of files. Adding /<link-path> to .gitignore prevents
        accidental commits while leaving the link fully usable locally.

    Full uninstall (per consumer repo)
        .\link-skills.ps1 -Unlink

        Optionally remove the .gitignore entry the script added.

.LINK
    https://github.com/dhruvinrsoni/agentskills-garden

.LINK
    docs/skills-bridge.md

.LINK
    setup-garden.ps1
#>

[CmdletBinding(DefaultParameterSetName = 'Link')]
param(
    # Positional sink. Catches `--help`, `/?`, `-?` (when quoted), and any
    # other stray positional argument. Forces every other param below to be
    # NAMED ONLY.
    [Parameter(Position = 0, ParameterSetName = 'Link',   DontShow = $true)]
    [Parameter(Position = 0, ParameterSetName = 'Unlink', DontShow = $true)]
    [Parameter(Position = 0, ParameterSetName = 'Status', DontShow = $true)]
    [string]$_PositionalSink,

    [Parameter(ParameterSetName = 'Link')]
    [Parameter(ParameterSetName = 'Unlink')]
    [ValidateSet('cursor', 'claude', 'github', 'generic', 'custom')]
    [string]$Target,

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
    [switch]$Status,

    [Parameter(ParameterSetName = 'Link')]
    [Parameter(ParameterSetName = 'Unlink')]
    [Alias('NonInteractive','y')]
    [switch]$Yes,

    [Alias('h')]
    [switch]$Help,

    [Parameter(ValueFromRemainingArguments = $true, DontShow = $true)]
    [string[]]$RemainingArgs
)

$helpTokens = @('-h','--h','--help','-help','/?','/h','-?')
if ($_PositionalSink -and ($_PositionalSink -in $helpTokens)) { $Help = $true }
if (-not $Help -and $RemainingArgs) {
    foreach ($a in $RemainingArgs) {
        if ($a -in $helpTokens) { $Help = $true; break }
    }
}

$ErrorActionPreference = 'Stop'

# ---------- output helpers ----------

function Write-Step([string]$msg)    { Write-Host "[skills-bridge] $msg" -ForegroundColor Cyan }
function Write-StepOk([string]$msg)  { Write-Host "[skills-bridge] $msg" -ForegroundColor Green }
function Write-StepWarn([string]$msg){ Write-Host "[skills-bridge] $msg" -ForegroundColor Yellow }
function Write-StepErr([string]$msg) { Write-Host "[skills-bridge] $msg" -ForegroundColor Red }

# ---------- short usage block ----------

function Show-Usage {
    @'
link-skills.ps1
   Create a live link from a consumer repo into the agentskills-garden's
   skills/ folder, so any repo can consume the garden's skills without
   copying files. Pulling or editing the garden is reflected instantly in
   every consumer.

   It does this with a Windows directory JUNCTION (mklink /J) — a directory
   shortcut that programs see as a real folder, with no extra disk usage.

USAGE
   .\link-skills.ps1 [options]

   Options can be in any order; case does not matter.

OPERATION MODES (mutually exclusive)
   (default)    Link mode. Creates the junction.
   -Status      Read-only. Shows where the garden lives and which
                conventions in $PWD are currently linked.
   -Unlink      Removes an existing junction at the resolved link path.

OPTIONS
   -Target <name>
       Convention for the link location inside $PWD. One of:
           cursor  -> .cursor/skills       (Cursor IDE)
           claude  -> .claude/skills       (Claude Code / claude.md flows)
           github  -> .github/skills       (GitHub-flavoured agents)
           generic -> skills               (no opinion)
           custom  -> requires -LinkPath
       If omitted, the script auto-detects which of .claude/ / .cursor/ /
       .github/ already exist in $PWD and shows a menu. The default
       highlighted option comes from (in order):
           1. The single agent-convention folder it found in $PWD
           2. agentskills.defaultTarget from git config (set by setup-garden)
           3. 'claude'

   -LinkPath <path>
       Custom link path relative to $PWD. Required with -Target custom.
       Also acts as an override for the named targets.

   -Path <dir>
       Explicit path to the agentskills-garden repo root. Overrides the
       5-level garden discovery order. Useful for testing.

   -Force
       Replace an existing junction at the link path. Real (non-junction)
       folders are NEVER overwritten regardless of -Force.

   -Yes
       (Aliases: -NonInteractive, -y) Skip the y/N prompt and the
       auto-detect menu. Also implied when stdin is redirected.

   -Help
       (Aliases: -h, --help, /?) Show this short usage block.
       PowerShell's native -? shows the longer comment-based help instead.

WHAT IT WILL DO (printed as a plan before any change)
   - Source:  <garden>\skills
   - Target:  .<convention>\skills  (inside $PWD)
   - Method:  Windows directory junction (mklink /J) — same drive
              or directory symlink (mklink /D) — cross drive (admin / Dev Mode)
   - If $PWD has a .git/ folder, add the link path to .gitignore.

   Then asks "Proceed? [y/N]" (skipped with -Yes).

EXAMPLES
   Interactive — let the script auto-detect and ask:
      .\link-skills.ps1

   I know what I want — link to .claude/skills, ask only for confirm:
      .\link-skills.ps1 -Target claude

   Unattended (CI, scripting):
      .\link-skills.ps1 -Target claude -Yes

   Custom path:
      .\link-skills.ps1 -Target custom -LinkPath ".agent/skills"

   See what's currently linked here:
      .\link-skills.ps1 -Status

   Undo the link:
      .\link-skills.ps1 -Unlink

GARDEN DISCOVERY ORDER
   1. -Path <dir>                         (CLI override)
   2. git config --global agentskills.path
   3. $env:AGENTSKILLS_GARDEN
   4. <root>\github\<gh-user>\agentskills-garden  (computed from git config
                                                   / env / %USERPROFILE%)
   5. The script's own parent directory          (only if it looks like a
                                                   garden — has skills/ and
                                                   registry.yaml)
   Run setup-garden.ps1 once on a new machine to populate level 2.

TROUBLESHOOTING
   "Could not locate agentskills-garden"
       Run setup-garden.ps1 once (it populates the git-config values), or
       pass -Path <full-path-to-garden>.

   "A junction already exists at <path> pointing to '<other>'"
       Pass -Force to replace it, or run with -Unlink first.

   "exists as a real file/folder. Refusing to overwrite"
       Move or delete the real folder yourself, then re-run.

   "mklink /J failed" or "mklink /D failed"
       Same drive: usually a permissions issue or the parent path doesn't
       exist (the script creates parents, so this is rare).
       Different drives: junctions can't cross drives. Either move the
       garden to the same drive, OR run from an elevated shell, OR enable
       Windows Developer Mode:
           Settings → Privacy & security → For developers → Developer Mode

   "Execution of scripts is disabled on this system"
       Allow local scripts for the current user (one-time):
           Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

MORE
   For the full PowerShell-formatted reference (parameter types, all aliases,
   notes section, links), use either of:
      Get-Help .\link-skills.ps1 -Detailed
      Get-Help .\link-skills.ps1 -Full

   Project repo:        https://github.com/dhruvinrsoni/agentskills-garden
   Companion script:    setup-garden.ps1   (run with -Help for details)
'@ | Write-Host
}

# ---------- early help path ----------

if ($Help) { Show-Usage; exit 0 }

if ($_PositionalSink -and $_PositionalSink -notin $helpTokens) {
    Write-StepErr "Unknown argument: '$_PositionalSink'. All parameters must be named (e.g. -Target claude)."
    Write-Host ''
    Show-Usage
    exit 1
}

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
    if ($Path) {
        if (-not (Test-Path -LiteralPath $Path)) {
            throw "Explicit -Path does not exist: $Path"
        }
        return (Resolve-Path -LiteralPath $Path).ProviderPath
    }

    $cfg = Get-GitConfigValue 'agentskills.path'
    if ($cfg -and (Test-Path -LiteralPath $cfg)) {
        return (Resolve-Path -LiteralPath $cfg).ProviderPath
    }

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
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).ProviderPath
        }
    }

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

# ---------- plan + confirm ----------

function Test-NonInteractive {
    if ($Yes) { return $true }
    try { return [Console]::IsInputRedirected } catch { return $false }
}

function Confirm-Plan([string[]]$planLines) {
    Write-Host ''
    Write-Host 'Plan:' -ForegroundColor White
    foreach ($line in $planLines) { Write-Host "  $line" -ForegroundColor White }
    Write-Host ''
    if (Test-NonInteractive) {
        Write-Step 'Auto-confirmed (-Yes or non-interactive stdin).'
        return $true
    }
    $ans = Read-Host 'Proceed? [y/N]'
    return ($ans -match '^(y|yes)$')
}

# ---------- target picker ----------

function Get-PresentConventions {
    $present = @()
    if (Test-Path -LiteralPath (Join-Path $PWD '.cursor')) { $present += 'cursor' }
    if (Test-Path -LiteralPath (Join-Path $PWD '.claude')) { $present += 'claude' }
    if (Test-Path -LiteralPath (Join-Path $PWD '.github')) { $present += 'github' }
    return ,$present
}

function Get-DefaultTargetForMenu {
    $present = Get-PresentConventions
    if ($present.Count -eq 1) { return $present[0] }
    $persisted = Get-GitConfigValue 'agentskills.defaultTarget'
    if ($persisted -and ($persisted -in @('cursor','claude','github','generic'))) {
        return $persisted
    }
    return 'claude'
}

function Read-TargetChoice {
    $present = Get-PresentConventions
    $default = Get-DefaultTargetForMenu
    $options = @(
        @{ Num = 1; Name = 'cursor';  Path = '.cursor/skills'  },
        @{ Num = 2; Name = 'claude';  Path = '.claude/skills'  },
        @{ Num = 3; Name = 'github';  Path = '.github/skills'  },
        @{ Num = 4; Name = 'generic'; Path = 'skills'          },
        @{ Num = 5; Name = 'custom';  Path = '<your custom path>' }
    )
    $defaultNum = ($options | Where-Object { $_.Name -eq $default } | Select-Object -First 1).Num
    if (-not $defaultNum) { $defaultNum = 2 }

    Write-Host ''
    Write-Host "Pick link target (in $PWD):" -ForegroundColor White
    foreach ($o in $options) {
        $tags = @()
        if ($o.Name -in $present) { $tags += "detected in `$PWD" }
        if ($o.Num -eq $defaultNum) { $tags += 'default — Enter accepts' }
        $tagStr = if ($tags.Count) { '  [' + ($tags -join '; ') + ']' } else { '' }
        Write-Host ("  {0}) {1,-7}  -> {2,-22}{3}" -f $o.Num, $o.Name, $o.Path, $tagStr)
    }

    while ($true) {
        $raw = Read-Host ("Choice [{0}]" -f $defaultNum)
        if ([string]::IsNullOrWhiteSpace($raw)) {
            $chosen = ($options | Where-Object { $_.Num -eq $defaultNum }).Name
        } else {
            $trim = $raw.Trim()
            $hit = $options | Where-Object { "$($_.Num)" -eq $trim -or $_.Name -ieq $trim } | Select-Object -First 1
            if (-not $hit) {
                Write-StepWarn "Not a valid choice. Enter 1-5 or one of: cursor, claude, github, generic, custom."
                continue
            }
            $chosen = $hit.Name
        }
        if ($chosen -eq 'custom') {
            $cp = Read-Host "Custom link path (relative to `$PWD)"
            if ([string]::IsNullOrWhiteSpace($cp)) {
                Write-StepWarn "Custom path cannot be empty."
                continue
            }
            return @{ Target = 'custom'; LinkPath = $cp.Trim() }
        }
        return @{ Target = $chosen; LinkPath = $null }
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

function Get-LinkMethod([string]$linkFullPath, [string]$targetFullPath) {
    $linkParent  = Split-Path -Parent $linkFullPath
    $linkDrive   = Get-DriveRoot $linkParent
    $targetDrive = Get-DriveRoot $targetFullPath
    if ($linkDrive -eq $targetDrive) {
        return @{ Method = 'junction (/J)'; CrossDrive = $false }
    }
    return @{ Method = "directory symlink (/D) — cross-drive, needs admin or Developer Mode"; CrossDrive = $true }
}

function New-BridgeLink([string]$linkFullPath, [string]$targetFullPath) {
    $info = Get-LinkMethod -linkFullPath $linkFullPath -targetFullPath $targetFullPath
    if (-not $info.CrossDrive) {
        $out = & cmd /c "mklink /J `"$linkFullPath`" `"$targetFullPath`"" 2>&1
        if ($LASTEXITCODE -ne 0) { throw "mklink /J failed ($LASTEXITCODE): $out" }
        Write-StepOk "Created junction: $linkFullPath  ->  $targetFullPath"
        return
    }
    Write-StepWarn "Consumer and garden live on different drives. Falling back to mklink /D."
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

    $persisted = Get-GitConfigValue 'agentskills.defaultTarget'
    if ($persisted) {
        Write-Step "Persisted default target: $persisted"
    } else {
        Write-Step "Persisted default target: (none — first-run default is 'claude')"
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

# ---------- resolve target if not on CLI ----------

if (-not $Target) {
    if (Test-NonInteractive) {
        $Target = Get-GitConfigValue 'agentskills.defaultTarget'
        if (-not $Target) { $Target = 'claude' }
        if ($Target -notin @('cursor','claude','github','generic')) { $Target = 'claude' }
    } else {
        $picked = Read-TargetChoice
        $Target = $picked.Target
        if ($picked.LinkPath) { $LinkPath = $picked.LinkPath }
    }
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

    $existingTarget = Get-JunctionTarget $fullLink
    $plan = @(
        "Remove junction at $relLink",
        "  (currently points to: $existingTarget)"
    )
    if (-not (Confirm-Plan $plan)) {
        Write-Step "Aborted by user. Nothing removed."
        exit 0
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

# Build plan
$linkInfo = Get-LinkMethod -linkFullPath $fullLink -targetFullPath $gardenSkills

$existingJunction = $null
$existingReal = $false
if (Test-Path -LiteralPath $fullLink) {
    if (Test-IsReparsePoint $fullLink) {
        $existingJunction = Get-JunctionTarget $fullLink
    } else {
        $existingReal = $true
    }
}

if ($existingReal) {
    Write-StepErr "$relLink exists as a real file/folder. Refusing to overwrite. Move or delete it manually first."
    exit 1
}

$plan = @(
    "Garden source:   $gardenSkills",
    "Link target:     $relLink   (in $PWD)",
    "Method:          $($linkInfo.Method)"
)
if ($existingJunction) {
    $sameTarget = ($existingJunction.TrimEnd('\') -ieq $gardenSkills.TrimEnd('\'))
    if ($sameTarget) {
        $plan += "Existing link already points to the correct target -- will only ensure .gitignore is updated."
    } elseif ($Force) {
        $plan += "Existing junction points to '$existingJunction' -- will be REPLACED (-Force)."
    } else {
        Write-StepErr "A junction already exists at $relLink pointing to '$existingJunction'. Use -Force to replace."
        exit 1
    }
}
if (Test-Path -LiteralPath (Join-Path $PWD '.git')) {
    $plan += "Add '/$($relLink.TrimStart('/'))' to .gitignore (with a header comment)."
} else {
    $plan += "(Not a git repo — .gitignore will not be touched.)"
}

if (-not (Confirm-Plan $plan)) {
    Write-Step "Aborted by user. No changes made."
    exit 0
}

# Ensure parent dir
$linkParent = Split-Path -Parent $fullLink
if ($linkParent -and -not (Test-Path -LiteralPath $linkParent)) {
    New-Item -ItemType Directory -Path $linkParent -Force | Out-Null
    Write-Step "Created parent directory: $linkParent"
}

# Handle existing junction
if ($existingJunction) {
    $sameTarget = ($existingJunction.TrimEnd('\') -ieq $gardenSkills.TrimEnd('\'))
    if ($sameTarget) {
        Write-StepOk "Link already points to the right target. Nothing to change."
        if (Test-Path -LiteralPath (Join-Path $PWD '.git')) {
            Add-GitignoreEntry $relLink
        }
        exit 0
    }
    if ($Force) {
        try {
            Remove-BridgeLink $fullLink
            Write-Step "Removed existing junction (forced)."
        } catch {
            Write-StepErr $_.Exception.Message
            exit 1
        }
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
