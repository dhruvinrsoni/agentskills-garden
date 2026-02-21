```markdown
---
name: inline-documentation
description: >
  Analyze, generate, and improve inline code documentation including
  JSDoc, docstrings, type annotations, and comment quality.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# Inline Documentation

> _"Code tells you how; comments tell you why."_

## Context

Invoked when source code needs inline documentation improvements — adding
or updating JSDoc/TSDoc comments, Python docstrings, Javadoc, or similar
per-language documentation conventions. Focuses on making code self-documenting
while ensuring comments explain intent, edge cases, and non-obvious behavior.

---

## Micro-Skills

### 1. Documentation Gap Detection 🌿 (Eco Mode)

**Steps:**

1. Scan source files for public functions, classes, methods, and exported symbols.
2. Identify undocumented or under-documented entities (missing param descriptions, return types, etc.).
3. Flag overly complex functions (cyclomatic complexity > threshold) that lack explanatory comments.
4. Generate a coverage report: documented vs undocumented public API surface.

### 2. Docstring/JSDoc Generation 🌿 (Eco Mode)

**Steps:**

1. Analyze function signatures, type annotations, and usage patterns.
2. Generate language-appropriate doc comments:
   - JavaScript/TypeScript → JSDoc/TSDoc with `@param`, `@returns`, `@throws`, `@example`.
   - Python → Google/NumPy/Sphinx-style docstrings.
   - Java/Kotlin → Javadoc/KDoc.
   - Go → Godoc-style comments.
3. Include parameter descriptions inferred from names, types, and usage.
4. Add `@example` blocks for non-trivial functions.

### 3. Comment Quality Audit ⚡ (Power Mode)

**Steps:**

1. Detect anti-patterns in existing comments:
   - Redundant comments that restate the code (`// increment i` above `i++`).
   - Stale comments that contradict the current implementation.
   - TODO/FIXME/HACK markers without issue references.
   - Commented-out code blocks.
2. Suggest replacements: remove noise, add "why" explanations.
3. Verify self-documenting naming (suggest renames where comments compensate for poor names).

---

## Inputs

| Parameter        | Type       | Required | Description                                     |
|------------------|------------|----------|-------------------------------------------------|
| `source_files`   | `string[]` | yes      | Files or directories to analyze                  |
| `language`       | `string`   | no       | Override language detection                      |
| `style`          | `string`   | no       | Docstring style: `google`, `numpy`, `jsdoc`, etc.|
| `include_private`| `boolean`  | no       | Whether to document private/internal symbols     |

## Outputs

| Field              | Type     | Description                                    |
|--------------------|----------|------------------------------------------------|
| `documented_files` | `string[]` | Files with added/updated documentation       |
| `coverage_report`  | `string` | Documentation coverage before and after        |
| `quality_report`   | `string` | Comment quality audit findings                 |

---

## Scope

### In Scope
- Generating JSDoc, TSDoc, Javadoc, KDoc, Godoc, and Python docstrings
- Auditing existing comments for staleness, redundancy, and noise
- Detecting undocumented public functions, classes, methods, and constants
- Suggesting self-documenting renames to replace compensatory comments
- Adding `@param`, `@returns`, `@throws`, `@example`, `@deprecated` tags
- Flagging TODO/FIXME/HACK comments without associated issue references

### Out of Scope
- Generating external API reference documentation (use api-documentation skill)
- Writing architectural decision records or design docs
- Modifying function logic or signatures (only documentation is touched)
- Generating README files or project-level documentation
- Enforcing code style or formatting rules beyond doc comments

## Guardrails

- Preview diffs before applying any changes.
- Never touch generated, vendor, third_party, build, or dist folders unless explicitly allowed.
- Run formatter and linter after changes; revert if errors introduced.
- Never modify function logic, signatures, or behavior — only add or update documentation.
- Preserve existing accurate doc comments; only augment or correct, never remove without cause.
- Do not generate misleading descriptions — if intent is unclear, mark as `TODO: describe purpose`.
- Respect the project's established docstring style (Google vs NumPy vs Sphinx); do not mix styles.
- Never add comments that merely restate what the code does syntactically.

## Ask-When-Ambiguous

### Triggers
- Multiple docstring conventions detected in the same project
- Function has complex behavior that cannot be reliably inferred from signature alone
- Existing comment contradicts the implementation
- Private/internal symbols have no documentation and `include_private` is not set

### Question Templates
1. "Both Google-style and NumPy-style docstrings are used in this project. Which should be the standard going forward?"
2. "Function `{name}` has complex branching logic. I can infer parameter purposes from types, but the overall intent is unclear. Can you describe what this function is meant to do?"
3. "Comment on line {line} says `{comment_text}` but the code does `{actual_behavior}`. Should I update the comment to match the code, or flag this as a potential bug?"
4. "Should I add docstrings to private/internal methods in `{module}`, or only document the public API?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Public function with no documentation | Generate full docstring with params, returns, and throws |
| Comment restates code (`// set x to 5` above `x = 5`) | Remove the redundant comment |
| Stale comment contradicts code | Flag for review; do not auto-correct without confirmation |
| Complex algorithm with no explanation | Add a block comment explaining the approach and any references |
| TODO/FIXME without issue reference | Append `// TODO(untracked):` prefix and include in quality report |
| Private function used in ≥ 3 call sites | Document it even if `include_private` is false |

## Success Criteria

- [ ] All public functions, classes, and methods have complete doc comments
- [ ] Doc comments include `@param`, `@returns`, and `@throws` where applicable
- [ ] No redundant comments remain (comments that restate obvious code)
- [ ] All TODO/FIXME comments reference an issue tracker ID
- [ ] Documentation coverage increases by ≥ 20% after the skill runs
- [ ] No stale or contradictory comments remain unflagged

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Incorrect parameter descriptions | Generated docs describe a param's purpose inaccurately | Cross-reference param usage at call sites before generating description |
| Style inconsistency | New docstrings use a different convention than existing ones | Detect project convention in pre-scan phase and enforce it throughout |
| Noise addition | Trivial getters/setters get verbose doc comments | Skip documentation for single-line accessor methods unless they have side effects |
| Stale comment left uncorrected | Audit identifies contradiction but replacement is wrong | Flag contradictions for human review instead of auto-replacing |
| Commented-out code not removed | Dead code blocks remain after audit | List commented-out blocks in report; require explicit approval to delete |

## Audit Log

- `[{timestamp}] doc-scan-completed: Scanned {file_count} files — {undocumented_count} undocumented public symbols found`
- `[{timestamp}] docstrings-generated: Added {added_count} doc comments across {file_count} files using {style} convention`
- `[{timestamp}] quality-audit: Found {redundant_count} redundant, {stale_count} stale, {todo_count} untracked TODO comments`
- `[{timestamp}] comments-removed: Removed {removed_count} redundant comments`
- `[{timestamp}] coverage-delta: Documentation coverage changed from {before_pct}% to {after_pct}%`
```
