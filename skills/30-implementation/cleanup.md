---
name: cleanup
description: >
  Remove noise, enforce formatting, and safely rename identifiers.
  A mixed-mode skill: cosmetic fixes run in Eco, renaming runs in Power.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: mixed
---

# Cleanup

> _"Leave the codebase better than you found it."_

## Context

Invoked when the user wants to clean up a file or module — remove dead code,
fix formatting, or rename unclear identifiers. The skill automatically selects
Eco or Power mode per micro-skill.

---

## Micro-Skills

### 1. Comment Policy 🌿 (Eco Mode)

**Goal:** Remove noise while preserving intent markers.

**Rules:**

- **Keep:** `TODO`, `FIXME`, `HACK`, `NOTE`, `WARN` — these carry intent.
- **Remove:** Commented-out code blocks (>= 2 consecutive lines of code in
  comments).
- **Preserve:** License headers, JSDoc/docstrings, and `@param`/`@returns`
  annotations.

**Steps:**

1. Scan file for comment blocks.
2. Classify each block: `intent-marker | dead-code | documentation`.
3. Remove `dead-code` blocks.
4. Emit diff for user review.

---

### 2. Formatting 🌿 (Eco Mode)

**Goal:** Apply project-specific linter/formatter.

**Steps:**

1. Detect project formatter from config files:
   - `.prettierrc`, `.eslintrc` → Prettier / ESLint
   - `pyproject.toml`, `setup.cfg` → Black / Ruff
   - `.clang-format` → clang-format
2. Run the detected formatter.
3. If no formatter config found, **ask the user** (Dharma principle).
4. Emit diff.

---

### 3. Safe Renaming ⚡ (Power Mode)

**Goal:** Rename unclear identifiers without breaking anything.

**Steps:**

1. **Identify Candidates** — single-letter vars (except `i`, `j`, `k`),
   abbreviations not in the domain glossary.
2. **Check Protected Terms** — load `domain-glossary`, skip protected.
3. **Check Visibility** — public/exported identifiers are high-risk,
   require explicit user approval.
4. **Generate Rename Map:**
   ```json
   {
     "old_name": "new_name",
     "scope": "local | module | public",
     "risk": "low | medium | high"
   }
   ```
5. **Produce Diff** — apply renames across all references, present to user.

---

## Inputs

| Parameter         | Type       | Required | Description                    |
|-------------------|------------|----------|--------------------------------|
| `file_path`       | `string`   | yes      | Path to the file to clean up   |
| `micro_skills`    | `string[]` | no       | Subset to run (default: all)   |
| `domain_glossary` | `string`   | no       | Path to domain glossary file   |

## Outputs

| Field        | Type     | Description                              |
|--------------|----------|------------------------------------------|
| `diff`       | `string` | Unified diff of all changes              |
| `rename_map` | `object` | Map of old → new names                   |
| `summary`    | `string` | Human-readable summary of changes        |

---

## Scope

### In Scope
- Removing commented-out dead code blocks (≥2 consecutive lines)
- Removing unused imports, variables, and unreachable code paths
- Applying project-configured formatters and linters
- Renaming unclear local and module-scoped identifiers
- Organizing and sorting import statements
- Removing trailing whitespace, fixing line endings, and normalizing indentation
- Cleaning up redundant type annotations or casts that add no value

### Out of Scope
- Changing public API signatures or exported interfaces
- Restructuring code architecture or extracting classes (delegate to `refactoring`)
- Adding new functionality or business logic
- Modifying test files or test infrastructure
- Changing build configuration, CI/CD pipelines, or infrastructure code
- Removing or modifying intent markers (TODO, FIXME, HACK, NOTE, WARN)
- Cleaning up generated code, vendor code, or third-party dependencies

---

## Guardrails

- Always preview diffs before applying any cleanup changes.
- Never remove comments tagged with intent markers (TODO, FIXME, HACK, NOTE, WARN).
- Never touch `vendor/`, `node_modules/`, `dist/`, `build/`, or `generated/` directories unless explicitly allowed.
- Preserve license headers, docstrings, JSDoc, and `@param`/`@returns` annotations.
- Run the project formatter and linter after changes; revert if new errors are introduced.
- Renaming public or exported identifiers requires explicit user approval (high-risk).
- Each micro-skill operates independently — do not combine cosmetic and rename changes in one step.
- Verify that removed dead code is truly dead (check for dynamic references, reflection, or string-based lookups).

## Ask-When-Ambiguous

### Triggers
- No formatter or linter configuration is found in the project
- A comment block looks like dead code but contains partial logic or pseudocode
- An identifier flagged for renaming is part of a domain-specific glossary
- A variable appears unused but may be referenced dynamically or via reflection
- The user requests cleanup of a generated or vendor file

### Question Templates
1. "No formatter config found in this project. Should I use `{default_formatter}` or do you have a preference?"
2. "This comment block looks like dead code but contains `{snippet}`. Should I remove it or keep it?"
3. "`{identifier}` appears to be unused but could be referenced dynamically. Should I remove it?"
4. "`{symbol}` is exported/public — renaming it may break consumers. Should I proceed?"
5. "This file is in `{directory}` which appears to be generated. Should I clean it up anyway?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Comment block is ≥2 lines of commented-out code | Remove it (dead code) |
| Comment contains TODO, FIXME, HACK, NOTE, or WARN | Preserve it (intent marker) |
| Comment is a license header or docstring | Preserve it (documentation) |
| Formatter config exists in the project | Use the project's configured formatter |
| No formatter config found | Ask the user before applying any formatting |
| Identifier is single-letter and not `i`, `j`, `k`, or a conventional loop var | Flag for renaming |
| Identifier is in the domain glossary | Skip renaming (protected term) |
| Identifier is public/exported | Flag as high-risk; require user approval before renaming |
| Import is unused but is a side-effect import (e.g., CSS, polyfill) | Preserve it; do not remove |

## Success Criteria

- [ ] All commented-out dead code blocks have been removed
- [ ] Intent markers (TODO, FIXME, HACK, NOTE, WARN) are preserved
- [ ] License headers and documentation comments are intact
- [ ] Project formatter has been applied without introducing errors
- [ ] All unused imports have been removed (except side-effect imports)
- [ ] Renamed identifiers have clear, descriptive names matching project conventions
- [ ] All rename references are updated across the affected scope
- [ ] No new linting errors or warnings were introduced
- [ ] The file compiles/parses correctly after cleanup

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Removed a comment that carried intent | Useful TODO or NOTE is gone | Check for intent marker tags before removing any comment block |
| Removed a side-effect import | Runtime error — CSS missing, polyfill not loaded | Detect side-effect import patterns; never remove imports with no named bindings in relevant languages |
| Renamed a dynamically-referenced symbol | Runtime error — symbol not found via reflection or string lookup | Search for string-based references and dynamic access patterns before renaming |
| Formatter introduced style conflicts | Diff contains unexpected style changes unrelated to cleanup | Use only the project's configured formatter; never apply a different formatter's rules |
| Removed code that appeared dead but was used | Build or runtime failure after cleanup | Verify across entire codebase, including tests and configs, before removing any code |
| Public rename broke downstream consumers | Type errors or import failures in dependent packages | Always check symbol visibility; require explicit approval for public/exported renames |

## Audit Log

```
- [{{timestamp}}] cleanup:start — file={{file_path}}, micro_skills={{skills_list}}
- [{{timestamp}}] comment-policy:applied — dead_code_removed={{count}}, intent_markers_kept={{count}}, docs_preserved={{count}}
- [{{timestamp}}] formatting:applied — formatter={{name}}, changes={{count}}, errors_introduced={{count}}
- [{{timestamp}}] renaming:applied — renames={{count}}, risk_levels={{low/medium/high}}, user_approved={{bool}}
- [{{timestamp}}] imports:optimized — removed={{count}}, side_effects_kept={{count}}
- [{{timestamp}}] cleanup:complete — total_changes={{count}}, lint_clean={{bool}}, diff_size={{lines}}
```
