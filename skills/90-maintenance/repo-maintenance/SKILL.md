---
name: repo-maintenance
description: >
  Adaptive cleanup framework for repo-wide structural optimization.
  Embodies the principle: start simple, explore, discover value, pivot
  strategy toward the greater good. Deletion is the last resort.
  Cleanup is the example — adaptive direction-seeking is the lesson.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, token-efficiency, pragya"
  reasoning_mode: plan-execute
---

# Repo Maintenance — Adaptive Cleanup Framework

> _"A manager who wastes nothing. Before deleting any file, ask: can it be
> activated, archived, or merged? Deletion is the last resort — not the first."_

## Context

Invoked when the goal is to reduce repo size, clean up stale content, or
optimize repository structure. This is the **repo-wide structural** counterpart
to `cleanup` (which operates at the file/module level).

The deeper lesson: everyone starts with a simple strategy ("fewer files"), but
exploration reveals that value exists in unexpected places. The skill that
matters most is not "how to delete" but **"how to recognize value and adapt
your strategy to preserve it."**

This skill implements the Pragya principle at the repo level: take the first
step with a simple plan, explore, discover, pivot — and let the human steer
at every checkpoint.

## Scope

**In scope:**

- Repo-wide file inventory and classification
- Value assessment for dormant, dead, and duplicate files
- Content consolidation (merge, trim, optimize)
- Structural audits (stale configs, orphaned tests, doc rot)
- Adaptive strategy evolution with pragya checkpoints
- Commit patterns for clean git history

**Out of scope:**

- File-level code cleanup (formatting, renaming) — owned by `cleanup`
- Code-level tech debt scoring — owned by `tech-debt-tracking`
- Dependency vulnerability scanning — owned by `dependency-scanning`
- Framework/runtime upgrades — owned by `legacy-upgrade`

---

## Micro-Skills

### 1. Inventory Scan

**Mode:** Eco

Build a complete map of every tracked file, classified by liveness.

**Steps:**

1. List all tracked files: `git ls-files | sort`
2. For each file, determine its status:
   - **Active:** Imported, referenced in config, used in builds/tests
   - **Dormant:** Exists but has no imports, no config references, not wired up
   - **Dead:** Zero references AND superseded by another file
   - **Duplicate:** Overlapping logic or content with another file
3. Output: categorized file inventory with status and reference count.

**Classification commands:**

```bash
# Find imports/references for a file
grep -r "filename" src/ --include="*.ts"

# Check if a script is wired into package.json
grep "script-name" package.json

# Check if an asset is referenced in config
grep "asset-name" manifest.json *.config.*

# Find untracked files
git status --short
```

### 2. Value Assessment — The 4 Cleanup Questions

**Mode:** Power

For each file flagged as dormant, dead, or duplicate, ask these questions
**in order**. Each "yes" adds weight toward keeping.

**Question 1: Is it referenced anywhere?**
- Grep for the filename AND the exported symbol names.
- Check `package.json` scripts, workflow YAML, manifest, imports in `src/`.
- If referenced → **KEEP. Do not touch.**

**Question 2: Does it have unique value not already covered?**
- Compare against existing files with similar purpose.
- Look for: unique logic, unique signals, different trade-offs, unique
  narrative or branding content.
- If it adds something → **MERGE or KEEP.** Extract the useful parts.

**Question 3: Can it be activated with minimal effort?**
- Scripts without a `package.json` entry are sleeping, not dead.
- A one-line addition can wake them up.
- Docs without a link from README are hidden, not useless.
- If activatable → **ACTIVATE.** Don't delete working code/content.

**Question 4: Is it historical or irreplaceable effort?**
- Design artifacts (icons, prompts, sketches) took human effort.
- Branding narratives, algorithm philosophy docs — can't be regenerated.
- If worth preserving → **ARCHIVE to a `legacy/` subfolder.**

**If all four answers are "no"** → safe to **DELETE.** Truly dead: duplicate
logic + zero references + no unique value + cheap to regenerate.

### 3. Content Consolidation

**Mode:** Power

When multiple files cover overlapping ground, merge them into one crisp
document.

**Steps:**

1. Identify the overlap: what content appears in both files?
2. Identify the unique parts: what does each file contribute that the other
   doesn't?
3. Create the merged document:
   - Start with the best-structured file as the base.
   - Weave in unique content from the other(s).
   - Trim verbosity: replace 10-line explanations with 2-line summaries.
   - Preserve all unique insights, data points, and actionable guidance.
4. Delete the source files only after verifying the merge is complete.

**The consolidation principle:**

> Three bloated docs is worse than one crisp doc. But one doc with unique
> content is better than zero docs. Maximize value per file — not file count.

**What to trim:**

- Verbose AI-generated deep-dives → 2-line summary + link to source skill
- Duplicate explanations of concepts covered elsewhere
- Outdated sections that reference removed features
- Placeholder content never filled in

**What to preserve:**

- Unique branding/narrative content (product stories, algorithm philosophy)
- Actionable checklists and decision matrices
- Examples and concrete before/after demonstrations
- Historical context that informs future decisions

### 4. Structural Audit

**Mode:** Eco

Scan for repo-level structural issues beyond individual file liveness.

**Checklist:**

| Issue | How to detect | Action |
|-------|---------------|--------|
| Stale config files | Tool not in `package.json`/`requirements.txt` | Delete if fully replaced |
| Orphaned test files | Test file exists but source file was deleted | Delete test file |
| Documentation rot | README/docs reference features that no longer exist | Update or remove section |
| Dead CI workflows | Workflow references packages/services removed | Delete or update workflow |
| Empty directories | `find . -type d -empty` | Remove |
| Unused dependencies | In lockfile but not imported anywhere | Run dep audit tool |
| Scattered config | Same setting in 3 places | Consolidate to single source |

### 5. Adaptive Checkpoint — The Core Differentiator

**Mode:** Power

After each pass (inventory, assessment, consolidation, audit), **pause and
reassess.** This is a pragya direction checkpoint applied to the cleanup
journey.

**The adaptive strategy table:**

| Phase | Starting strategy | What exploration might reveal | Better action |
|-------|-------------------|------------------------------|---------------|
| Start | Reduce file count | — | Scan and classify first |
| After inventory | Delete dead files | Some "dead" files have unique value | Pivot to value-per-file maximization |
| After assessment | Merge duplicates | Narrative docs serve different audiences | Keep both, trim each |
| After consolidation | Finalize | Config audit reveals more stale files | Run structural audit pass |
| After audit | Done | New files were created during consolidation | Re-scan for completeness |

**At each checkpoint, present findings to the user:**

```
Inventory complete. Here's what I found:
- 12 active files (imported/referenced)
- 4 dormant files (exist but unwired)
- 2 dead files (zero refs, superseded)
- 1 duplicate (overlapping logic)

My initial goal was "reduce file count." After assessment:
- 2 dormant files have unique value → recommend KEEP + TRIM
- 1 dormant file is a sleeping script → recommend ACTIVATE
- 1 dormant file is truly dead → recommend DELETE

Should I pivot from "reduce files" to "maximize value per file"?
```

**The adaptive insight:**

> Start with a simple, measurable goal. As exploration reveals value, pivot
> the strategy to preserve it. What you start with is never what you finish
> with — and that's a feature, not a bug. Taking the first step matters more
> than having the perfect plan. The plan evolves as you learn.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_root` | `string` | no | Path to repository root (auto-detected) |
| `goal` | `string` | yes | The cleanup objective (e.g., "reduce file count", "trim docs") |
| `protected_paths` | `string[]` | no | Paths that must never be modified |
| `dry_run` | `boolean` | no | If true, report but don't modify (default: false) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `inventory` | `object` | Categorized file inventory (active/dormant/dead/duplicate) |
| `decisions` | `object[]` | Per-file decision (keep/merge/activate/archive/delete) with rationale |
| `strategy_log` | `string[]` | Trail of strategy evolutions during the cleanup |
| `changes_made` | `object[]` | List of files modified, deleted, moved, or created |

---

## Decision Matrix

| Condition | Action |
|-----------|--------|
| Referenced in imports / config / manifest | **KEEP — do not touch** |
| Has unique logic or content not elsewhere | **MERGE the valuable parts, then delete the source** |
| Works but not wired up (sleeping) | **ACTIVATE — add entry point** |
| Historical / human effort / irreplaceable | **ARCHIVE to `legacy/` subfolder** |
| Truly dead: duplicate + zero refs + cheap to regenerate | **DELETE** |

---

## Guardrails

- **Never delete in the first pass.** Inventory first, assess second, act
  third. Deletion happens in the final pass after user confirmation.
- **Every deletion needs grep justification.** Show the zero-reference
  evidence before removing. "Looks unused" is not justification.
- **Use `git mv` for archives.** Preserves git history so
  `git log -- legacy/old-file.md` still works. Never `rm` + `add`.
- **Group commits by intent.** Not by file. Examples:
  - `chore: remove dead code` — deleted unreferenced source files
  - `chore: archive legacy assets` — git mv to `legacy/` subfolder
  - `chore: activate dormant scripts` — added to package.json
- **Pragya checkpoint after every pass.** Present findings, let user redirect.
  If the user says "pivot," pivot.
- **Never delete branding/narrative docs** without confirming they have no
  audience. "Who reads this?" before deleting. Developer docs ≠ public docs.

## Ask-When-Ambiguous

**Triggers:**

- A file has mixed signals (some references but also appears superseded)
- Unique content exists but relevance is uncertain
- The cleanup goal conflicts with discovered value
- Developer docs vs public-facing docs distinction is unclear
- File appears dead but is in a domain you don't fully understand

**Question Templates:**

- "This file has [unique content] but [zero code references]. Is it a
  developer reference, a public-facing asset, or truly dead?"
- "We started with 'reduce file count' but I found [N] files with value.
  Should I shift to 'trim and consolidate' instead?"
- "This script isn't wired up, but it [does X]. Worth activating or safe
  to archive?"
- "These [N] docs overlap significantly. Should I merge them into one, or
  do they serve different audiences?"

## Decision Criteria

| File type | Assessment approach |
|-----------|---------------------|
| Source code (.ts, .py, .java) | Grep for imports. If zero → check if it's a standalone script. |
| Config files (.yml, .json, .toml) | Check if the tool it configures is in the dependency list. |
| Test files (.test.ts, _test.go) | Check if the source file being tested still exists. |
| Documentation (.md) | Ask "who reads this?" — developer, public, both, nobody? |
| Build scripts (.mjs, .sh) | Check if wired into package.json/Makefile. Sleeping ≠ dead. |
| Assets (images, icons, fonts) | Check if referenced in manifests/HTML/CSS. |
| CI/CD workflows (.yml in .github/) | Check if referenced services/packages still exist. |
| Lock files (package-lock, yarn.lock) | Never delete — always regenerate via package manager. |

## Success Criteria

- Every file in the repo has been assessed (no unexamined files).
- Zero files deleted without grep-based justification.
- Strategy evolution is documented (initial goal → discoveries → pivots).
- User approved every major decision via pragya checkpoints.
- Git history is clean: commits grouped by intent, archives use `git mv`.
- Value per file is maximized: nothing unique was lost, nothing bloated remains.

## Failure Modes

- **Aggressive deletion.** (The original lesson.) AI deletes valuable content
  because the goal was "fewer files."
  **Recovery:** Pragya checkpoint after inventory reveals unique content. Pivot
  to value-per-file maximization. If already deleted: `git checkout` to recover.

- **Over-preservation.** Keeping everything, nothing gets cleaned up.
  **Recovery:** Apply the 4 cleanup questions strictly. If ALL four answers
  are "no," the file is safe to delete. Don't let sentiment override evidence.

- **Missing the narrative.** Deleting a product story doc because it has zero
  code references — but it's the only public-facing description of the product.
  **Recovery:** Ask "who reads this?" before any doc deletion. Developer refs
  and public narratives serve different audiences.

- **Orphan creation.** Consolidating files but leaving dangling references
  in other files that pointed to the originals.
  **Recovery:** After every merge/delete, grep for references to the old
  file. Update or remove them.

- **Strategy lock-in.** Continuing with "delete everything unused" after
  discovering files with unique value — because "that was the plan."
  **Recovery:** Pragya principle — the plan serves the goal. If a better plan
  emerges, propose it. The user decides.

## Audit Log

```
[inventory-complete]   active={N} dormant={N} dead={N} duplicate={N}
[value-assessed]       file={path} questions=[{yes|no},{yes|no},{yes|no},{yes|no}] decision={keep|merge|activate|archive|delete}
[content-merged]       sources=[{paths}] target={path} unique_lines_preserved={N}
[structural-issue]     type={stale-config|orphan-test|doc-rot|dead-workflow} file={path}
[strategy-evolved]     from="{old}" to="{new}" trigger="{discovery}"
[file-action]          action={keep|merge|activate|archive|delete} file={path} justification="{reason}"
[checkpoint-presented] phase={inventory|assessment|consolidation|audit} findings="{summary}"
```

---

## Examples

### Example 1 — Sleeping Script: ACTIVATE, Don't Delete

**Situation:** `scripts/benchmark-performance.mjs` is not in `package.json`.
Appears "dead" in inventory scan.

**4 Cleanup Questions:**
1. Referenced? No — not imported or in package.json.
2. Unique value? Yes — reads dist/ bundle sizes, checks thresholds, CI-aware.
3. Activatable? Yes — one line in package.json: `"benchmark": "node scripts/benchmark-performance.mjs"`
4. Historical? Yes — hand-written tool, not trivially regenerated.

**Decision:** ACTIVATE. Add to package.json. The script was sleeping, not dead.

**Lesson:** A script without a package.json entry is a dormant tool. Check
what it does before calling it dead.

### Example 2 — Superseded Module: DELETE After Signal Comparison

**Situation:** `src/scorers/title-scorers.ts` has a similar name to the active
`title-scorer.ts`. Not imported anywhere.

**4 Cleanup Questions:**
1. Referenced? No — zero imports across all `src/`.
2. Unique value? No — compared signal-by-signal against the active scorer.
   Active scorer covers all signals plus position, phrase, and composition
   bonuses. Old file uses binary matching; new file uses graduated scoring.
3. Activatable? No — it's an older, less capable version.
4. Historical? Minimal — logic is fully captured in the active file.

**Decision:** DELETE. Fully superseded. Confirmed with evidence, not assumption.

**Lesson:** Even "core-sounding" files can be dead. Compare logic explicitly.

### Example 3 — Narrative Doc: RECOVER and TRIM

**Situation:** `docs/ALGORITHM_PHILOSOPHY.md` was deleted in a previous cleanup
under the "fewer docs" mandate.

**Discovery:** It was the ONLY document explaining the algorithm's philosophy
(Sanskrit naming, why graduated matching beats binary, the full story) in a
public-facing narrative form. Internal skill files cover the technical
details — not the story.

**Decision:** RECOVER from git history. Trim verbose AI deep-dives to 2-line
summaries. Fix any outdated examples. Result: 250 lines (from 408).

**Lesson:** Branding and narrative docs can't be replaced by developer-facing
references. Ask "who reads this?" before deleting.

---

## Edge Cases

- **Monorepo extraction.** When extracting a package from a monorepo, the
  "dead file" analysis must be scoped to the package being extracted — not
  the entire monorepo. A file unused in package A may be critical in package B.

- **Doc-vs-code value.** A markdown file with zero code references may have
  immense value as a product narrative, onboarding guide, or API story.
  Never judge docs purely by code reference counts.

- **Generated files.** Lock files, build outputs, and generated code should
  never be manually deleted. Use the appropriate tool (package manager,
  build system, `.gitignore`).

- **Files referenced only in tests.** A source file referenced only from
  test files (not production code) might still be valuable — it could be
  a test utility, fixture, or shared mock. Check the test context.

- **Git submodules and symlinks.** External references may not show up in
  simple grep. Check `.gitmodules`, symlinks, and any vendored dependencies.

- **Cultural/language artifacts.** Comments, docs, or naming conventions in
  non-English languages may appear "dead" to pattern matching but carry
  important meaning. Flag for human review instead of auto-classifying.
