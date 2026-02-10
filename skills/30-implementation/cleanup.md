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
- **Remove:** Commented-out code blocks (≥ 2 consecutive lines of code in
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

1. **Identify Candidates**
   - Scan for single-letter variables (except loop counters `i`, `j`, `k`).
   - Scan for abbreviations not in the domain glossary.
   - Scan for names that violate project naming conventions.

2. **Check Protected Terms**
   - Load `domain-glossary` (if available).
   - If a candidate is in `protected_terms`, skip it.

3. **Check Visibility**
   - If the identifier is `public` or `exported`, flag it as high-risk.
   - Public renames require explicit user approval.

4. **Generate Rename Map**
   ```json
   {
     "old_name": "new_name",
     "scope": "local | module | public",
     "risk": "low | medium | high",
     "reason": "..."
   }
   ```

5. **Produce Diff**
   - Apply renames across all references in scope.
   - Present unified diff to user.
   - Wait for approval before applying.

---

## Inputs

| Parameter       | Type       | Required | Description                          |
|-----------------|------------|----------|--------------------------------------|
| `file_path`     | `string`   | yes      | Path to the file to clean up         |
| `micro_skills`  | `string[]` | no       | Subset to run (default: all)         |
| `domain_glossary` | `string` | no       | Path to domain glossary file         |

## Outputs

| Field         | Type     | Description                              |
|---------------|----------|------------------------------------------|
| `diff`        | `string` | Unified diff of all changes              |
| `rename_map`  | `object` | Map of old → new names (if renaming ran) |
| `summary`     | `string` | Human-readable summary of changes        |

---

## Examples

### Example — Comment Cleanup

**Input:**
```json
{
  "file_path": "src/utils.py",
  "micro_skills": ["comment-policy"]
}
```

**Output:**
```json
{
  "summary": "Removed 3 dead-code comment blocks (12 lines). Preserved 2 TODOs.",
  "diff": "--- a/src/utils.py\n+++ b/src/utils.py\n@@ -14,8 +14,2 @@\n-# old_value = compute()\n-# if old_value > threshold:\n-#     ...\n"
}
```
