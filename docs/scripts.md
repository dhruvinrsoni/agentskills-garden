# Scripts cheat-sheet

Every script, one line: what you run it for. Naming follows the
[`naming-conventions`](../skills/100-engineering/80-collaboration/naming-conventions/SKILL.md)
skill — CLI tools are `verb-noun`, imported libraries are nouns, `_` = internal.

## Run these (the garden, day to day)

| Command | Use it to… |
|---------|-----------|
| `python scripts/build.py` | Build the site + regenerate the index & `registry.yaml` from frontmatter. |
| `python scripts/build.py --serve` | Same, then preview locally at http://localhost:8000. |
| `python scripts/validate.py --strict` | Check every skill's frontmatter is valid before committing. |
| `python scripts/check-links.py` | Verify internal markdown links resolve. |
| `python scripts/benchmark.py --counts 1000,5000` | Prove lookup cost stays flat at scale (writes `.bench/report.md`). |
| `python scripts/migrate.py --apply` | One-shot: move v1 layout → domain namespaces (already run). |

## Bridge & promotion (PowerShell)

| Command | Run from | Use it to… |
|---------|----------|-----------|
| `install-garden.ps1` | any machine, once | Clone the garden and remember where it lives. |
| `link-skills.ps1` | a consumer repo | Make the garden's skills live-visible in that repo (junction). |
| `promote-skills.ps1` | a consumer repo | Push that repo's `status: ready` drafts up into the garden. |
| `gather-skills.ps1` | the garden | Pull ready drafts from **all** consumer repos at once. |

All four print a plan and ask before changing anything (`-DryRun` to preview, `-Yes` to skip the prompt).

## Libraries & helpers (you don't run these)

| File | What it is |
|------|-----------|
| `taxonomy.py` | The tag axes + domain allowlist (imported). |
| `skill_lib.py` | Shared skill reader + validator + tree-walk (imported by build & validate). |
| `_common.ps1` | Shared helpers for the promotion scripts (dot-sourced). |
