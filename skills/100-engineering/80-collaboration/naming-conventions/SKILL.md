---
name: naming-conventions
description: >
  Name scripts, tools, and files so their name tells you when and how to use
  them. CLI tools you run are verb-noun; imported libraries are nouns; internal
  helpers start with an underscore. Apply when adding or renaming any script.
license: Apache-2.0
domain: engineering
status: published
tags: [category, build, collaboration, advisory]
keywords: [naming, scripts, files, cli, conventions, rename, intuitive, ergonomics]
metadata:
  version: 1.0.0
  reasoning_mode: linear
  skill_type: standard
---


# Naming Conventions

> _"A good name is the shortest documentation there is."_

## Context

Invoke when creating a new script/tool, renaming an existing one, or reviewing a
folder of scripts that feel inconsistent. A name should answer *"when and how do
I use this?"* before the reader opens the file. Inconsistent names (`build_site`
next to `pull-from-all` next to `scale_bench`) cost onboarding time and make a
toolbox feel ad-hoc.

---

## Micro-Skills

### 1. Classify the file by how it's used 🌿 (Eco Mode)

**Goal:** Pick the right shape before picking words.

| Kind | How it's used | Name shape | Example |
|------|---------------|-----------|---------|
| **CLI tool** | a human/CI *runs* it | `verb-noun`, hyphens | `link-skills.ps1`, `install-garden.ps1` |
| **Library** | *imported* by other code | noun, underscores (valid identifier) | `taxonomy.py`, `skill_lib.py` |
| **Internal helper** | shared by siblings, never run/imported alone | leading `_` | `_common.ps1` |
| **One-shot / rare** | run once (migration, benchmark) | plain verb/noun | `migrate.py`, `benchmark.py` |

### 2. Name a CLI tool for the action 🌿 (Eco Mode)

**Steps:**
1. Start with the **verb** the user thinks in: *build, validate, link, promote, gather, install*.
2. Add the **noun** it acts on when the verb alone is ambiguous: `link-skills`, `promote-skills`, `gather-skills`. Drop the noun when the tool *is* the thing: `build`, `validate`, `benchmark`.
3. Keep a **family** consistent: if you have `link-skills` and `promote-skills`, don't add `pull-from-all` — make it `gather-skills`.
4. Prefer the word you'd type: `build.py --serve` reads as "build, then serve."

### 3. Name a library for the thing it holds 🌿 (Eco Mode)

- Libraries are **nouns**, not verbs: `taxonomy.py` (the vocabulary), `skill_lib.py` (skill model). They must be valid import identifiers — **underscores, never hyphens**.
- An internal helper only its siblings use gets a leading `_` so tooling and humans know "don't run/import me directly": `_common.ps1`.

### 4. Don't rename what's already published ⚡ (Power Mode)

**Nano: Blast-radius check.** Before renaming, grep every reference — imports, CI workflows, docs, and any *external* entry point (a web-install URL, a documented command). A name that is wrong but *published* (people have it in muscle memory or scripts) may cost more to change than it's worth. Rename it only if the clarity gain outweighs breaking those references, and update them all in the same change.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_purpose` | `string` | yes | What the file does and who uses it |
| `existing_names` | `string[]` | no | Sibling file names, to stay consistent with the family |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `proposed_name` | `string` | The intuitive name following the rules above |
| `references_to_update` | `string[]` | Every place that must change if this is a rename |

## Scope

- **In scope:** names of scripts, CLI tools, importable modules, and helper files.
- **Out of scope:** variable/function names *inside* code (a code-style concern), and skill `name` fields (those are governed by `docs/tags.md`).

## Guardrails

- Library/module files MUST be valid identifiers (no hyphens) — they are imported.
- Never rename a published external entry point without updating its URL/docs in the same change.
- One verb per tool; if a tool needs two verbs, it is doing two things — split it.

## Decision Criteria

| Situation | Action |
|-----------|--------|
| File is run by a human/CI | `verb-noun` (hyphens) |
| File is imported | noun (underscores) |
| File is a shared helper | leading `_` |
| Renaming a published tool | Do blast-radius check first; update all refs atomically |

## Success Criteria

- A newcomer can guess what each script does from its name alone.
- Sibling tools share a consistent family pattern.
- No broken imports/links/CI after a rename.

## Failure Modes

- **Hyphen in an imported module** → import error. **Recovery:** use underscores for libraries.
- **Renamed a published command** without updating its URL/docs → users hit 404s. **Recovery:** grep + fix every reference, or revert the rename.

## Examples

```text
Before (ad-hoc)            After (intuitive family)
build_site.py          ->  build.py            (you run it to build)
validate_skills.py     ->  validate.py         (you run it to validate)
scale_bench.py         ->  benchmark.py        (you run it to benchmark)
tag_axes.py            ->  taxonomy.py         (imported: the vocabulary)
skill_model.py         ->  skill_lib.py        (imported: the model)
pull-from-all.ps1      ->  gather-skills.ps1   (verb-noun family)
_agentskills-common.ps1->  _common.ps1         (internal helper)
```

## Edge Cases

- **Generic verb collision** (`build`, `run`): fine if the folder has only one — add the noun only when two builders coexist.
- **Acronyms** (`ci`, `db`, `iac`): keep lowercase, treat as one word: `ci-pipeline`, not `CI-pipeline`.
