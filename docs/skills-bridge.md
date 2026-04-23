# Skills Bridge: making this garden a live source of truth for every repo

Personal bookkeeping notes on the how/why of the `scripts/link-skills.ps1` bridge.
Treat this doc as a whiteboard: the "why" is as important as the "what".

---

## 1. The problem

This repo (`agentskills-garden`) curates the canonical library of agent skills.
Every other repo on my machine (consumer repos B, C, D, ...) needs the same
skills available at a conventional path (`.cursor/skills`, `.claude/skills`,
etc.) so Cursor / Claude / custom tools can pick them up.

Naive options:

| Approach          | Dynamic? | Duplicates files? | Sync burden    |
|-------------------|----------|-------------------|----------------|
| Copy into each repo | No     | Yes               | Manual/CI      |
| Git submodule     | No (pinned SHA) | No        | `submodule update` every time |
| Git subtree       | No (snapshot)   | Yes       | Re-pull on every change       |
| **Filesystem link** | **Yes** | **No**         | **Zero**       |

A filesystem link wins whenever we want "edit once, see everywhere, no sync step."
The trade-off is that the link is local-machine-only, so CI and teammates who
clone a consumer repo won't see the skills. That's acceptable: the garden is a
developer-side convenience, not a build artifact.

## 2. Junction vs symlink on Windows

Windows has three reparse-point flavors. For our use-case:

| Primitive        | Command           | Admin? | Same-volume only? | Our choice |
|------------------|-------------------|--------|-------------------|------------|
| Directory symlink | `mklink /D`      | Yes (or Developer Mode) | No | Fallback for cross-volume cases |
| **Junction**     | **`mklink /J`**   | **No** | **Yes**           | **Primary** |
| File symlink     | `mklink`          | Yes    | No                | Not used   |

`mklink /J` is our default: no admin, invisible to most tools (they just see a
folder), removable with `rmdir` without touching the target.

`link-skills.ps1` checks whether the garden and the consumer repo are on the
same drive. If yes, it uses `/J`. If no, it falls back to `/D` and warns that
admin or Developer Mode is needed.

## 3. Dynamic discovery: how repo B finds the garden

The garden can be cloned anywhere on disk, so `link-skills.ps1` needs a
discovery mechanism. Industry-standard pattern (`nvm`, `pyenv`, `rustup`,
`oh-my-zsh`, Homebrew): an env var with a sensible default.

We extend it slightly: the primary store is a named section in
`~/.gitconfig`, because git config travels with the user, survives shell
restarts, and naturally groups related keys together.

```ini
[agentskills]
    path = C:\root\github\dhruvinrsoni\agentskills-garden
    root = C:\root\github
    ghUser = dhruvinrsoni
    defaultTarget = cursor
```

Full resolution order in [scripts/link-skills.ps1](../scripts/link-skills.ps1):

1. `-Path` CLI arg (explicit override; used mostly for tests).
2. `git config --global --get agentskills.path` (primary).
3. `$env:AGENTSKILLS_GARDEN` (shell-level fallback).
4. Fork-safe default: `<root>\github\<gh-user>\agentskills-garden`.
5. The script's own parent (if invoked from inside a cloned garden).

### Fork-safe default, explained

When two people (or two machines, or one person with two forks) clone the
garden, the paths must not collide. Including `<gh-user>` in the default
guarantees this:

- `C:\root\github\dhruvinrsoni\agentskills-garden` (my fork)
- `C:\root\github\someoneElse\agentskills-garden` (their fork)

They coexist on the same machine without overwriting each other. This mirrors
the layout already in use for my regular clones, so nothing new to remember.

## 4. Why `[agentskills]` in `~/.gitconfig` instead of env vars alone

Env vars work fine, but they scatter: one var here, another there, different
per shell. A named git-config section keeps everything in one place:

```powershell
git config --global --list | Select-String '^agentskills\.'
```

prints everything in one shot. Extension is also trivial: want to add a
default namespace for Cursor skills vs Claude skills? Just add another key
under the same section. No new env var to document.

## 5. The `iwr | iex` one-liner

The brand-new-machine flow uses PowerShell's web-install pattern:

```powershell
iwr https://raw.githubusercontent.com/dhruvinrsoni/agentskills-garden/main/scripts/bootstrap.ps1 | iex
```

- `iwr` = `Invoke-WebRequest` (PowerShell's HTTP client, like `curl`).
- `iex` = `Invoke-Expression` (runs a string as PowerShell code).
- Pipe them together to download-and-execute in one step. This is the
  PowerShell equivalent of `curl <url> | bash`.

### Security note

`iwr | iex` runs whatever the URL returns. Only use it with sources you trust,
and consider pinning to a commit SHA rather than `main` to freeze what gets
executed:

```powershell
iwr https://raw.githubusercontent.com/dhruvinrsoni/agentskills-garden/<sha>/scripts/bootstrap.ps1 | iex
```

## 6. Industry precedents

The pattern used here is not invented; it's copied from tools I already use.
If any of these feels familiar, the mental model transfers directly:

| Tool          | Home env var        | Default location       | Config file       |
|---------------|---------------------|------------------------|-------------------|
| `nvm`         | `$NVM_DIR`          | `~/.nvm`               | `~/.nvmrc`        |
| `pyenv`       | `$PYENV_ROOT`       | `~/.pyenv`             | `~/.python-version` |
| `rustup`      | `$RUSTUP_HOME`      | `~/.rustup`            | `rust-toolchain`  |
| `oh-my-zsh`   | `$ZSH`              | `~/.oh-my-zsh`         | `~/.zshrc`        |
| Homebrew      | `$HOMEBREW_PREFIX`  | `/opt/homebrew`        | `~/.Brewfile`     |
| **this bridge** | `$AGENTSKILLS_GARDEN` | `<root>\github\<gh-user>\agentskills-garden` | `~/.gitconfig [agentskills]` |

## 7. Mac / Linux in the future

Only the link primitive changes:

| Platform    | Create        | Remove          |
|-------------|---------------|-----------------|
| Windows     | `mklink /J`   | `rmdir`         |
| macOS/Linux | `ln -s`       | `rm`            |

The git-config keys, env vars, resolution order, target conventions, and
command-line interface stay identical. When we add the `bash` sibling script,
it should be a 1:1 mirror of the PowerShell one at the user-facing level.

## 8. Troubleshooting

### "Could not locate agentskills-garden"
Run [scripts/bootstrap.ps1](../scripts/bootstrap.ps1), or set things manually:

```powershell
git config --global agentskills.path "C:\path\to\agentskills-garden"
```

### "mklink /J failed" on a different drive
Junctions are same-volume only. The script auto-falls-back to `/D` (directory
symlink) but that needs admin or Developer Mode. Enable Developer Mode at
`Settings > System > For developers`, or re-run in an elevated PowerShell.

### "A junction already exists ... pointing elsewhere"
Re-run with `-Force` to replace it.

### "exists as a real file/folder"
The script never overwrites real content. Move or delete the existing folder,
then re-run.

### `.gitignore` hygiene
The script auto-appends the link path to `.gitignore`. If you bypass this
(e.g. not in a git repo), remember to do it manually — otherwise git on
Windows will follow the junction and try to commit everything inside it.

## 9. Related files

- [scripts/link-skills.ps1](../scripts/link-skills.ps1) — per-consumer link/unlink/status.
- [scripts/bootstrap.ps1](../scripts/bootstrap.ps1) — first-machine setup.
- `~/.gitconfig` — stores the `[agentskills]` section.
