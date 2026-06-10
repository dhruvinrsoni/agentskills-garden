<#
.SYNOPSIS
    First-machine setup for agentskills-garden. Clones the garden to a fork-safe
    location on your machine, remembers where it is, and (optionally) makes its
    helper scripts callable from anywhere.

    (Renamed from bootstrap.ps1 to install-garden.ps1 — the action verb is clearer
    for end users. The old name lives on only in older blog posts and forks.)

.DESCRIPTION
    This is the first script you run when bringing the garden onto a new machine.

    What problem it solves
        The "agentskills-garden" is a registry of agent skills that you want to
        share live across many consumer repos. The garden has to live SOMEWHERE
        predictable so other tools (especially link-skills.ps1) can find it
        without you having to remember the path. This script does that one-time
        bookkeeping.

    What it does (step by step)
        1. Confirms `git` is on PATH.
        2. Resolves <gh-user> — the GitHub username that owns your fork of the
           agentskills-garden repo. Resolution order:
                a. -GhUser parameter
                b. `git config --global agentskills.ghUser`
                c. $env:GITHUB_USER
                d. Interactive prompt
        3. Resolves <root> — the base directory the garden lives under:
                a. -Root parameter
                b. `git config --global agentskills.root`
                c. $env:AGENTSKILLS_ROOT
                d. %USERPROFILE%\github  (e.g. C:\Users\you\github)
        4. Computes target path <root>\github\<gh-user>\agentskills-garden.
           (If <root> already ends in 'github', the segment is not duplicated.)
        5. Asks which default target (cursor / claude / github / generic) you
           usually want link-skills.ps1 to use. The chosen value is persisted so
           you only answer this once. Pre-populated from any previously saved
           choice, or 'claude' on first run.
        6. Prints a "Plan:" block describing every action it is about to take.
        7. Asks "Proceed? [y/N]". You can answer "n" to abort safely; no change
           is made until you confirm. Skip the prompt with -Yes.
        8. Clones <gh-user>/agentskills-garden into the target path (if the
           folder does not already look like a garden clone).
        9. Persists the resolved values to ~/.gitconfig under [agentskills].
       10. If -AddToPath was passed, prepends <garden>\scripts to your User
           PATH (you must open a new shell for that to take effect).

    What it deliberately does NOT do
        - Never writes outside ~/.gitconfig and (optionally) your User PATH.
        - Never edits a system-wide PATH or a Machine-scope environment variable.
        - Never re-clones over an existing clone. If the target folder already
          looks like a garden, the script only re-persists config (idempotent).
        - Never deletes anything.

    Safety model
        Without -Yes, the script PRINTS a plan and waits for y/N. With -Yes,
        every default is silently accepted. You can re-run the script as often
        as you like; the only persistent state lives in ~/.gitconfig under the
        [agentskills] section (which you can list with
        `git config --global --get-regexp ^agentskills` and reset with
        `git config --global --remove-section agentskills`).

    Web-install one-liner
        iwr https://raw.githubusercontent.com/dhruvinrsoni/agentskills-garden/main/scripts/install-garden.ps1 | iex

        The script reads from your terminal for prompts, so the interactive
        confirmation still works through `iex`. For unattended use, fetch the
        script first and pass -Yes, e.g.:

            $s = (iwr https://.../install-garden.ps1).Content
            & ([scriptblock]::Create("$s -GhUser yourname -Yes"))

.PARAMETER GhUser
    GitHub username that owns your fork of agentskills-garden.
    Resolution order: -GhUser → agentskills.ghUser → $env:GITHUB_USER → prompt.

.PARAMETER Root
    Base directory under which <gh-user>\agentskills-garden is placed.
    Resolution order: -Root → agentskills.root → $env:AGENTSKILLS_ROOT
    → %USERPROFILE%\github.

.PARAMETER Branch
    Branch to clone. Defaults to 'main'.

.PARAMETER AddToPath
    Prepends <garden>\scripts to your User PATH so link-skills.ps1 resolves
    without a full path. Open a new shell after this for the change to take
    effect. Affects User scope only, never Machine scope.

.PARAMETER Yes
    Aliases: -NonInteractive, -y.
    Skip the y/N confirmation prompt. Useful for `iwr | iex` automation and CI.
    The script still prompts for -GhUser if it cannot be resolved any other
    way — pass -GhUser explicitly to be fully unattended.

.PARAMETER Force
    Re-run setup even if the garden folder already exists. Will NOT re-clone;
    it only re-persists the git config values. Use this after moving the
    garden folder or changing your fork.

.PARAMETER Help
    Aliases: -h, --help, /?.
    Show the short usage block and exit. (PowerShell's native -? shows the
    longer comment-based help instead — both formats are intentional.)

.EXAMPLE
    .\install-garden.ps1 -GhUser dhruvinrsoni -AddToPath

    Recommended first-time interactive setup. You will see a target picker, a
    plan, and a y/N prompt before anything happens.

.EXAMPLE
    iwr https://raw.githubusercontent.com/dhruvinrsoni/agentskills-garden/main/scripts/install-garden.ps1 | iex

    Web one-liner. Asks for confirmation interactively in your shell.

.EXAMPLE
    .\install-garden.ps1 -GhUser dhruvinrsoni -AddToPath -Yes

    Fully unattended run (CI / scripting). No prompts.

.EXAMPLE
    .\install-garden.ps1 -GhUser dhruvinrsoni -Root D:\code -Force -Yes

    Re-persist config after moving the garden folder to D:\code. Skips clone
    because -Force is set on an existing garden.

.EXAMPLE
    .\install-garden.ps1 -Help

    Print the short usage block and exit. Same as -h, --help, /?.

.NOTES
    Prerequisites
        - Git for Windows installed and on PATH:
            https://git-scm.com/download/win
        - PowerShell 5.1 or PowerShell 7+ (this script targets both).
        - For -AddToPath: no special privileges needed (User scope).

    Exit codes
        0  success or user-aborted-at-prompt (both are non-failure outcomes)
        1  unrecoverable error (missing git, clone failed, refused to touch
           an unrecognised folder, etc.)

    Persisted state
        All persisted state lives in ~/.gitconfig under the [agentskills]
        section. Inspect or reset:
            git config --global --get-regexp ^agentskills
            git config --global --remove-section agentskills

    Full uninstall
        1. Run link-skills.ps1 -Unlink in every consumer repo that has a link.
        2. git config --global --remove-section agentskills
        3. Remove <garden>\scripts from User PATH if you added it.
        4. Delete the garden folder.

    Security note on `iwr | iex`
        Running scripts directly from the internet is convenient but means
        you're trusting whatever is at that URL at the moment of fetch. To
        pin to a specific commit for reproducibility, replace `/main/` in
        the URL with `/<commit-sha>/`.

.LINK
    https://github.com/dhruvinrsoni/agentskills-garden

.LINK
    docs/skills-bridge.md

.LINK
    link-skills.ps1
#>

[CmdletBinding()]
param(
    # Positional sink. Catches `--help`, `/?`, `-?` (when quoted), and any
    # other stray positional argument. Forces every other param below to be
    # NAMED ONLY, so `--help` can never silently land in `-GhUser`.
    [Parameter(Position = 0, DontShow = $true)]
    [string]$_PositionalSink,

    [string]$GhUser,
    [string]$Root,
    [string]$Branch = 'main',
    [switch]$AddToPath,
    [Alias('NonInteractive','y')]
    [switch]$Yes,
    [switch]$Force,
    [Alias('h')]
    [switch]$Help,
    [Parameter(ValueFromRemainingArguments = $true, DontShow = $true)]
    [string[]]$RemainingArgs
)

# Catch POSIX/cmd-style help variants. PowerShell's `-?` is intercepted by
# the engine before this code runs (it shows comment-based help); quoted
# `'-?'` and any `--help`/`/?` arrive here via $_PositionalSink.
$helpTokens = @('-h','--h','--help','-help','/?','/h','-?')
if ($_PositionalSink -and ($_PositionalSink -in $helpTokens)) { $Help = $true }
if (-not $Help -and $RemainingArgs) {
    foreach ($a in $RemainingArgs) {
        if ($a -in $helpTokens) { $Help = $true; break }
    }
}

$ErrorActionPreference = 'Stop'

# ---------- output helpers ----------

function Write-Step([string]$msg)    { Write-Host "[install-garden] $msg" -ForegroundColor Cyan }
function Write-StepOk([string]$msg)  { Write-Host "[install-garden] $msg" -ForegroundColor Green }
function Write-StepWarn([string]$msg){ Write-Host "[install-garden] $msg" -ForegroundColor Yellow }
function Write-StepErr([string]$msg) { Write-Host "[install-garden] $msg" -ForegroundColor Red }

# ---------- short usage block ----------

function Show-Usage {
    @'
install-garden.ps1
   First-time setup for the agentskills-garden. Clones the garden repo into a
   predictable location on your machine, remembers where it went, and
   (optionally) makes its scripts callable from anywhere.

   Safe to re-run: it detects an existing garden and only refreshes saved
   settings.

USAGE
   .\install-garden.ps1 [options]

   Options can be in any order. PowerShell parameters are case-INsensitive
   and accept -foo, -Foo, or -FOO identically.

OPTIONS
   -GhUser <name>     Your GitHub username (the account that owns your fork).
                      If omitted: agentskills.ghUser -> $env:GITHUB_USER ->
                      interactive prompt.

   -Root <dir>        Base directory the garden will live under. Final path is
                      <Root>\github\<GhUser>\agentskills-garden.
                      Default: %USERPROFILE%\github

   -Branch <name>     Git branch to clone. Default: main.

   -AddToPath         Prepend <garden>\scripts to your User PATH so you can
                      type "link-skills.ps1" from any folder. Open a NEW
                      shell after this for the change to take effect.

   -Yes               (Aliases: -NonInteractive, -y) Skip the y/N prompt.
                      Use for `iwr | iex` automation and CI. You should also
                      pass -GhUser to be fully unattended.

   -Force             Re-run even if the garden folder already exists. Will
                      NOT re-clone; only re-persists the git config values.

   -Help              (Aliases: -h, --help, /?) Show this short usage block.
                      Note: PowerShell's native -? shows the longer
                      comment-based help instead. Both are intentional.

WHAT IT WILL DO (printed as a plan before any change)
   - Clone https://github.com/<GhUser>/agentskills-garden into the target path
   - Persist to ~/.gitconfig:
       agentskills.path          = <full target path>
       agentskills.root          = <Root>
       agentskills.ghUser        = <GhUser>
       agentskills.defaultTarget = <claude|cursor|github|generic>
   - [if -AddToPath] Prepend <garden>\scripts to your User PATH

   Then asks "Proceed? [y/N]". Type "y" + Enter to continue.

EXAMPLES
   First-time interactive setup (recommended):
      .\install-garden.ps1 -GhUser dhruvinrsoni -AddToPath

   Web one-liner (asks for confirmation interactively):
      iwr https://raw.githubusercontent.com/dhruvinrsoni/agentskills-garden/main/scripts/install-garden.ps1 | iex

   Fully unattended:
      .\install-garden.ps1 -GhUser dhruvinrsoni -AddToPath -Yes

WHERE THINGS GO
   Garden folder:    <Root>\github\<GhUser>\agentskills-garden
   Persisted state:  ~/.gitconfig section [agentskills]
                     View:   git config --global --get-regexp ^agentskills
                     Reset:  git config --global --remove-section agentskills

TROUBLESHOOTING
   "git is not available"
       Install Git for Windows: https://git-scm.com/download/win

   "git clone failed"
       Verify https://github.com/<GhUser>/agentskills-garden exists and is
       reachable (public, or you are authenticated to GitHub).

   "Path exists but does not look like a garden clone"
       The target folder exists but has no .git/ or skills/. Move it aside
       or delete it, then re-run.

   "Execution of scripts is disabled on this system"
       Allow local scripts for the current user (one-time):
          Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

MORE
   For the full PowerShell-formatted reference (parameter types, all aliases,
   notes section, links), use either of:
      Get-Help .\install-garden.ps1 -Detailed
      Get-Help .\install-garden.ps1 -Full

   Project repo:        https://github.com/dhruvinrsoni/agentskills-garden
   Companion script:    link-skills.ps1   (run with -Help for details)
'@ | Write-Host
}

# ---------- git config helpers ----------

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

function Read-TargetChoice([string]$current) {
    $options = @(
        @{ Num = 1; Name = 'cursor';  Path = '.cursor/skills'  },
        @{ Num = 2; Name = 'claude';  Path = '.claude/skills'  },
        @{ Num = 3; Name = 'github';  Path = '.github/skills'  },
        @{ Num = 4; Name = 'generic'; Path = 'skills'          }
    )
    $defaultNum = ($options | Where-Object { $_.Name -eq $current } | Select-Object -First 1).Num
    if (-not $defaultNum) { $defaultNum = 2 }

    Write-Host ''
    Write-Host 'Pick the default link target for link-skills.ps1:' -ForegroundColor White
    foreach ($o in $options) {
        $marker = if ($o.Num -eq $defaultNum) { '  <- default (Enter accepts)' } else { '' }
        Write-Host ("  {0}) {1,-7}  -> {2,-16}{3}" -f $o.Num, $o.Name, $o.Path, $marker)
    }
    Write-Host '  (You can override per-invocation with link-skills.ps1 -Target <name>.)' -ForegroundColor DarkGray

    while ($true) {
        $raw = Read-Host ("Choice [{0}]" -f $defaultNum)
        if ([string]::IsNullOrWhiteSpace($raw)) { return ($options | Where-Object { $_.Num -eq $defaultNum }).Name }
        $trim = $raw.Trim()
        $byNum = $options | Where-Object { "$($_.Num)" -eq $trim } | Select-Object -First 1
        if ($byNum) { return $byNum.Name }
        $byName = $options | Where-Object { $_.Name -ieq $trim } | Select-Object -First 1
        if ($byName) { return $byName.Name }
        Write-StepWarn "Not a valid choice. Enter 1-4 or one of: cursor, claude, github, generic."
    }
}

# ---------- entry point ----------

if ($Help) { Show-Usage; exit 0 }

if ($_PositionalSink -and $_PositionalSink -notin $helpTokens) {
    Write-StepErr "Unknown argument: '$_PositionalSink'. All parameters must be named (e.g. -GhUser <name>)."
    Write-Host ''
    Show-Usage
    exit 1
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
    if (Test-NonInteractive) {
        Write-StepErr "GitHub username is required. Pass -GhUser <name> for unattended runs."
        exit 1
    }
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

$rootLeaf = Split-Path -Leaf $Root
if ($rootLeaf -ieq 'github') {
    $userParent = Join-Path $Root $GhUser
} else {
    $userParent = Join-Path (Join-Path $Root 'github') $GhUser
}
$gardenPath = Join-Path $userParent 'agentskills-garden'

# --- resolve default target ---

$defaultTarget = Get-GitConfigValue 'agentskills.defaultTarget'
if (-not $defaultTarget) { $defaultTarget = 'claude' }
if (-not (Test-NonInteractive)) {
    $defaultTarget = Read-TargetChoice -current $defaultTarget
}

# --- preview ---

Write-Host ''
Write-Step "GitHub user:       $GhUser"
Write-Step "Root:              $Root"
Write-Step "Target path:       $gardenPath"
Write-Step "Default target:    $defaultTarget"

# --- check existing garden ---

$gardenExists = $false
$gardenLooksValid = $false
if (Test-Path -LiteralPath $gardenPath) {
    $gardenExists = $true
    if ((Test-Path -LiteralPath (Join-Path $gardenPath '.git')) -and
        (Test-Path -LiteralPath (Join-Path $gardenPath 'skills'))) {
        $gardenLooksValid = $true
    }
}

if ($gardenExists -and -not $gardenLooksValid) {
    Write-StepErr "Path $gardenPath exists but does not look like a garden clone (no .git or no skills/). Refusing to touch it."
    exit 1
}

# --- build and confirm plan ---

$plan = @()
if ($gardenLooksValid) {
    $plan += "Garden already present at $gardenPath -- skip clone."
} else {
    $plan += "Clone https://github.com/$GhUser/agentskills-garden (branch $Branch)"
    $plan += "  into $gardenPath"
}
$plan += "Persist to ~/.gitconfig:"
$plan += "    agentskills.path          = $gardenPath"
$plan += "    agentskills.root          = $Root"
$plan += "    agentskills.ghUser        = $GhUser"
$plan += "    agentskills.defaultTarget = $defaultTarget"
if ($AddToPath) {
    $plan += "Prepend $gardenPath\scripts to your User PATH."
}

if (-not (Confirm-Plan $plan)) {
    Write-Step "Aborted by user. No changes made."
    exit 0
}

# --- clone if missing ---

if ($gardenLooksValid) {
    Write-StepOk "Garden already present at $gardenPath (skipping clone)"
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
Set-GitConfigValue 'agentskills.path'          $gardenPath
Set-GitConfigValue 'agentskills.root'          $Root
Set-GitConfigValue 'agentskills.ghUser'        $GhUser
Set-GitConfigValue 'agentskills.defaultTarget' $defaultTarget
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
    Write-Host "  2. Run:  link-skills.ps1                     (interactive — uses your default '$defaultTarget')" -ForegroundColor White
    Write-Host "          link-skills.ps1 -Target claude|cursor|github|generic|custom" -ForegroundColor White
    Write-Host "          link-skills.ps1 -Status              (see what's linked)" -ForegroundColor White
    Write-Host "          link-skills.ps1 -Unlink              (remove the link)" -ForegroundColor White
    Write-Host "          link-skills.ps1 -Help                (full help; also -h, --help, /?)" -ForegroundColor White
} else {
    Write-Host "  2. Run:  & `"$scriptsDir\link-skills.ps1`"" -ForegroundColor White
    Write-Host "     Or re-run install-garden with -AddToPath for a shorter invocation." -ForegroundColor White
}
Write-Host ''
