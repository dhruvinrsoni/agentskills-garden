# How it works (in plain words)

A 2-minute mental model of the garden. For the deep detail see
[`tags.md`](tags.md) (taxonomy) and [`skills-bridge.md`](skills-bridge.md) (sharing).

## What a skill is

One folder with one `SKILL.md` inside. The top of that file (between `---`
lines) is the **frontmatter** — the skill's info card:

```yaml
---
name: cleanup
description: Remove noise, format, safely rename.
domain: engineering            # which top-level area it belongs to
tags: [category, build, refactoring, reversible]
keywords: [tidy, lint, dead-code]
status: published
---
```

**The frontmatter is the single source of truth.** Nothing is listed twice — the
build reads every skill's frontmatter and *generates* the index and
`registry.yaml` for you. You never hand-edit those.

## Where skills live

Skills are grouped by **domain** (the big area), then by phase. Example:

```
skills/
  000-foundation/<skill>/            universal skills (always small, flat)
  100-engineering/30-implementation/<skill>/
  200-writing/ 300-data-ml/ 400-business/   (reserved for later)
```

## How a skill is found (without reading all of them)

Like finding a book in a library — you follow signs, you don't read every shelf:

```
map  →  domain index  →  category index  →  skill
```

- **map** (`skills/_index/MAP.md`) — lists the domains. Tiny.
- **domain index** (`skills/_index/<domain>/INDEX.md`) — lists that domain's
  categories (or, for a flat domain like foundation, its skills).
- **category index** (`skills/_index/<domain>/<category>.md`) — lists the skills
  in that category.
- **the skill** — the `SKILL.md` itself.

Because you only ever open the one branch you need, finding a skill costs about
the same whether the garden has 88 skills or 5,000. (Proven by
`python scripts/benchmark.py`.)

## Add a skill

1. Make a folder under the right domain: `skills/100-engineering/30-implementation/<name>/`.
2. Copy `templates/skill-template.md` to `SKILL.md`, fill in the frontmatter
   (`name` must match the folder; include `domain`, `tags`, `keywords`, `status`).
3. `python scripts/validate.py --strict` then `python scripts/build.py`. Done —
   it's auto-discovered. No registry edit.

## Share a skill you wrote in another repo

Draft it in that repo under `.agentskills/drafts/<name>/SKILL.md` with
`status: draft`. When ready, set `status: ready` and push it up:

```powershell
& "<garden>\scripts\promote-skills.ps1"        # from the consumer repo
.\scripts\gather-skills.ps1                     # from the garden: pull from ALL repos
```

Both preview first and ask before changing anything. See
[`scripts.md`](scripts.md) for the full tool list.
