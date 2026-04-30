# Legacy

Files in this folder are kept for **historical reference only**. They are not part of the supported install or use path of the garden.

## Why is this folder here?

Some artefacts shipped early in the garden's life and were superseded by better mechanisms. We do not delete them, because:

1. **External users may still reference them.** Old blog posts, forks, or scripts may still curl-pipe these into a shell. Leaving them in place (and clearly marked deprecated) is friendlier than a 404.
2. **They document where the project came from.** The flat-file installer shape captures one historical idea of "how to ship a skill library"; preserving it makes the design evolution visible.
3. **`git mv` keeps history intact.** Moving them here rather than deleting them keeps the per-line `git blame` chain unbroken.

## What lives here

| File | Original purpose | Why it's deprecated |
|------|------------------|---------------------|
| [`setup_skills.sh`](setup_skills.sh) | Bash installer that wrote ~35 skill files from embedded heredocs into a flat layout. | The current garden has 88 skills across a hierarchical category tree, master skills, a foundation kernel, and a closed tag taxonomy. The installer's heredocs are significantly out of sync and are not regenerated as new skills land. |
| [`setup_skills.ps1`](setup_skills.ps1) | The PowerShell-native equivalent of the Bash installer. | Same reason as above. The two installers shared the same authoring source, so they drifted in lock-step. |

## What replaced them

The **bridge-link** workflow. One Windows junction (or POSIX symlink) makes the live `skills/` folder visible inside any consumer repo. Editing or `git pull`ing in the garden propagates to every consumer with no copy step. See:

- [`README.md`](../README.md) — the supported install path.
- [`docs/skills-bridge.md`](../docs/skills-bridge.md) — design rationale.
- [`scripts/`](../scripts/) — the active scripts (`bootstrap.ps1` for first-machine setup, `link-skills.ps1` for per-repo linking).

## What about people who still want a one-shot installer?

If a regenerated single-file installer is genuinely needed in the future, the right approach is to:

1. Write a small generator script in [`scripts/`](../scripts/) that walks `skills/` and the registry and emits a fresh installer.
2. Wire that generator into CI so the installer cannot drift.
3. Replace the files in this folder with the freshly-generated ones.

Until then, do not edit the files in this folder. They are reference artefacts.
