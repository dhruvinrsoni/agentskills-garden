# Getting Started — Bridge-Link Walkthrough

A linear walk-through of using the agentskills-garden on a fresh Windows
machine, with **no prior PowerShell knowledge assumed**. If you can paste
commands into a terminal and answer `y` to a prompt, you can follow this.

The end state: your other repos can see this garden's `skills/` folder
**live** at a conventional path (`.claude/skills`, `.cursor/skills`, etc.),
with no copying and no sync step.

---

## Prerequisites

You need exactly two things:

1. **Git for Windows** — install from <https://git-scm.com/download/win> if
   you don't already have it. After install, opening a new PowerShell window
   and typing `git --version` should print a version number.
2. **PowerShell** — already on Windows. Either PowerShell 5.1 (built in) or
   PowerShell 7+ works.

That's it. No Node, no Python, no chocolatey, no admin rights.

> If you ever see "*Execution of scripts is disabled on this system*",
> allow local scripts for your user account one time:
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

---

## Step 1 — One-time machine setup

Open PowerShell and paste this one-liner:

```powershell
iwr https://raw.githubusercontent.com/dhruvinrsoni/agentskills-garden/main/scripts/setup-garden.ps1 | iex
```

What that does: downloads `setup-garden.ps1` and runs it. The script is
defensive — **it will not change anything on your machine until you
confirm**.

You'll see, in order:

1. **GitHub username prompt** (only if it can't figure out your username):
   ```
   GitHub username that owns your agentskills-garden fork:
   ```
   Type your GitHub username and press Enter. If you haven't forked the
   garden yet, fork it on GitHub first.

2. **Default target picker:**
   ```
   Pick the default link target for link-skills.ps1:
     1) cursor   -> .cursor/skills
     2) claude   -> .claude/skills    <- default (Enter accepts)
     3) github   -> .github/skills
     4) generic  -> skills
   Choice [2]:
   ```
   Pick the agent you use most. If you use Claude Code, press Enter. If you
   use Cursor, type `1`. You can change this later — this is just the
   default that `link-skills.ps1` will offer when you don't tell it
   otherwise.

3. **Plan + confirm:**
   ```
   Plan:
     Clone https://github.com/<you>/agentskills-garden (branch main)
       into C:\Users\<you>\github\<you>\agentskills-garden
     Persist to ~/.gitconfig:
         agentskills.path          = ...
         agentskills.root          = ...
         agentskills.ghUser        = ...
         agentskills.defaultTarget = claude
   Proceed? [y/N]:
   ```
   Read the plan. If it looks right, type `y` and press Enter. To abort
   safely, type `n` or just press Enter — nothing has been changed yet.

The script then clones the garden and writes four small keys to
`~/.gitconfig`. That's all of the global state it ever creates.

### Optional: make the scripts callable from any folder

Re-run setup-garden once with `-AddToPath`:

```powershell
.\setup-garden.ps1 -AddToPath
```

This prepends `<garden>\scripts` to your User PATH. **Open a new
PowerShell window** for the change to take effect. After that you can type
`link-skills.ps1 ...` from any folder.

---

## Step 2 — Link the garden into one of your repos

`cd` into any repo where you want the skills available:

```powershell
cd C:\work\my-app
```

Then:

```powershell
link-skills.ps1
```

(If you skipped `-AddToPath`, use the full path:
`& "C:\Users\<you>\github\<you>\agentskills-garden\scripts\link-skills.ps1"`.)

You'll see:

1. **Auto-detect + menu:**
   ```
   Pick link target (in C:\work\my-app):
     1) cursor   -> .cursor/skills
     2) claude   -> .claude/skills          [detected in $PWD; default — Enter accepts]
     3) github   -> .github/skills
     4) generic  -> skills
     5) custom   -> <your custom path>
   Choice [2]:
   ```
   The `[detected in $PWD]` tag appears next to a convention if that folder
   already exists in your repo. Press Enter to accept the default, or type
   a number for a different one.

2. **Plan + confirm:**
   ```
   Plan:
     Garden source:   C:\Users\<you>\github\<you>\agentskills-garden\skills
     Link target:     .claude/skills   (in C:\work\my-app)
     Method:          junction (/J)
     Add '/.claude/skills' to .gitignore (with a header comment).
   Proceed? [y/N]:
   ```
   Type `y` and Enter. The script creates a Windows directory junction at
   `.claude/skills` pointing at the garden's `skills/` folder. To your IDE
   and to git, it looks like a normal directory full of skills.

3. **Verification message:**
   ```
   [skills-bridge] Created junction: ...\.claude\skills  ->  ...\agentskills-garden\skills
   [skills-bridge] Verified: '00-foundation' is visible through the link.
   [skills-bridge] Done. The garden's skills folder is now live at '.claude/skills'.
   ```

That's it. Try `ls .claude\skills` — you'll see the garden's skill
categories. Edit a file in the garden, refresh the consumer repo — the
edit shows up live, with no copy or pull.

---

## Step 3 — Useful follow-ups

| Goal | Command |
|------|---------|
| See what's currently linked here | `link-skills.ps1 -Status` |
| Change which convention is linked | `link-skills.ps1 -Unlink` then `link-skills.ps1 -Target cursor` |
| Remove the link from this repo | `link-skills.ps1 -Unlink` |
| Get short help | `link-skills.ps1 -h` |
| Get the full PowerShell help | `Get-Help .\link-skills.ps1 -Detailed` |
| Change your persisted default target | `git config --global agentskills.defaultTarget claude` |
| See all persisted bridge settings | `git config --global --get-regexp ^agentskills` |

---

## Unattended use (CI, scripting)

Both scripts accept `-Yes` to skip the confirmation prompt. `link-skills.ps1`
also skips the auto-detect menu when `-Yes` is set, falling back to your
persisted `agentskills.defaultTarget`.

```powershell
# fully unattended setup
.\setup-garden.ps1 -GhUser yourname -AddToPath -Yes

# fully unattended link
link-skills.ps1 -Target claude -Yes
```

---

## Full uninstall

1. In every consumer repo that has a bridge link:
   ```powershell
   link-skills.ps1 -Unlink
   ```
2. Remove the persisted settings:
   ```powershell
   git config --global --remove-section agentskills
   ```
3. If you used `-AddToPath`, remove `<garden>\scripts` from your User PATH
   (Windows Settings → System → About → Advanced system settings →
   Environment Variables → User PATH → Edit).
4. Delete the garden folder.

---

## Where to read next

- [docs/skills-bridge.md](skills-bridge.md) — design notes, junction vs symlink, full troubleshooting.
- [README.md](../README.md) — what skills are, the constitution, the full skill list.
- [docs/concepts.md](concepts.md) — the hierarchy (nano → micro → skill → master) and Eco/Power mode.
