---
name: refactoring
description: >
  Safely restructure code while preserving external behavior.
  Applies proven refactoring patterns with mandatory test verification.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
  - unit-testing
reasoning_mode: plan-execute
---

# Refactoring

> _"Change the structure, preserve the behavior."_

## Context

Invoked when the user wants to restructure code for improved readability,
maintainability, or performance — without changing its observable behavior.
Every refactoring follows the safety protocol: baseline tests → apply change →
verify tests → revert on failure.

---

## The Safety Protocol

```text
1. Run existing tests → all PASS (establish baseline)
2. Apply the refactoring transformation
3. Run tests again → all PASS (verify behavior preserved)
4. If any test FAILS → REVERT immediately and report failure
```

**No exceptions.** If no tests exist for the affected code, invoke
`unit-testing` to create them before refactoring.

---

## Micro-Skills

### 1. Extract Method/Function ⚡ (Power Mode)

**Goal:** Break a long function into smaller, focused units.

**Steps:**

1. Identify the code block to extract (user-selected or heuristic: >15 lines or distinct responsibility).
2. Determine input parameters (variables used but defined outside the block).
3. Determine return values (variables modified inside and used after the block).
4. Create the new function with a descriptive name reflecting its purpose.
5. Replace the original block with a call to the new function.
6. Run tests — revert if any fail.

---

### 2. Simplify Conditionals 🌿 (Eco Mode)

**Goal:** Reduce nested or complex conditional logic.

**Steps:**

1. Identify deeply nested conditionals (>3 levels) or long if-else chains.
2. Apply guard clauses to flatten nesting.
3. Replace if-else chains with lookup tables, polymorphism, or strategy pattern where appropriate.
4. Ensure all branches are still covered.
5. Run tests.

---

### 3. Dependency Inversion ⚡ (Power Mode)

**Goal:** Replace concrete dependencies with abstractions for testability.

**Steps:**

1. Identify concrete dependencies (direct `new` calls, static method calls, hard-coded config).
2. Extract an interface or abstract type for each dependency.
3. Inject the dependency via constructor, factory, or parameter.
4. Update all instantiation sites to provide the concrete implementation.
5. Run tests.

---

### 4. Rename Symbol ⚡ (Power Mode)

**Goal:** Give identifiers clear, intention-revealing names.

**Steps:**

1. Check protected terms list — abort if the symbol is protected or public API.
2. Find all references across the entire codebase (not just the current file).
3. Generate a rename map with scope and risk level.
4. Apply rename across all references, run tests, present diff.

---

### 5. Move / Reorganize ⚡ (Power Mode)

**Goal:** Move functions, classes, or modules to more logical locations.

**Steps:**

1. Identify the target location based on cohesion and coupling analysis.
2. Move the code unit to the new location.
3. Update all imports, references, and re-exports across the codebase.
4. Verify no circular dependencies were introduced.
5. Run tests.

---

## Inputs

| Parameter       | Type       | Required | Description                                     |
|-----------------|------------|----------|-------------------------------------------------|
| `file_path`     | `string`   | yes      | Path to the file to refactor                    |
| `refactor_type` | `string`   | no       | Specific micro-skill to apply (default: auto)   |
| `target_symbol` | `string`   | no       | Symbol to refactor (for rename/extract)         |
| `new_name`      | `string`   | no       | New name for rename operations                  |

## Outputs

| Field          | Type      | Description                              |
|----------------|-----------|------------------------------------------|
| `diff`         | `string`  | Unified diff of all changes              |
| `test_results` | `object`  | Before/after test run comparison         |
| `reverted`     | `boolean` | Whether the refactor was reverted        |
| `summary`      | `string`  | Human-readable summary of changes        |

---

## Scope

### In Scope
- Restructuring internal implementation of functions, classes, and modules
- Extracting methods, classes, or modules from existing code
- Simplifying conditionals and reducing cyclomatic complexity
- Renaming private and internal identifiers for clarity
- Moving code units to improve cohesion and reduce coupling
- Injecting dependencies to replace hard-coded concrete references
- Removing dead code paths identified during restructuring

### Out of Scope
- Changing public API signatures or external contracts (requires explicit approval)
- Adding new features or altering business logic
- Modifying test files (delegate to `unit-testing`)
- Refactoring generated code, vendor code, or third-party dependencies
- Database schema changes or data migration (delegate to `data-access`)
- Performance optimization that changes algorithmic behavior (delegate to `profiling-analysis`)
- Changing configuration files, CI/CD pipelines, or infrastructure code

---

## Guardrails

- Never apply a refactoring without passing baseline tests first.
- Revert immediately if any test fails after a refactoring step — no partial commits.
- Never change observable behavior; input/output contracts must remain identical.
- Preview full diffs before applying changes; require user approval for high-risk refactors.
- Do not refactor across module boundaries without flagging it as high-risk.
- Never touch `vendor/`, `node_modules/`, `dist/`, `build/`, or generated directories.
- Limit each refactoring step to a single transformation — do not combine extract + rename in one step.
- If no tests cover the affected code, create tests first before refactoring.
- Preserve all existing comments that carry intent (TODO, FIXME, HACK, NOTE).

## Ask-When-Ambiguous

### Triggers
- The affected code has no test coverage
- The symbol to rename is part of a public API or exported interface
- Multiple valid refactoring patterns could apply (e.g., extract method vs. extract class)
- The refactoring would cross module or package boundaries
- Moving code could introduce circular dependencies

### Question Templates
1. "There are no tests covering `{symbol}`. Should I generate tests first or proceed with the refactor at your own risk?"
2. "`{symbol}` is part of the public API — renaming it will break downstream consumers. Should I proceed?"
3. "This code could be extracted as a method or as a separate class — which approach do you prefer?"
4. "Moving `{symbol}` to `{target_module}` would cross a package boundary. Should I proceed with the move?"
5. "I found `{n}` references to `{symbol}` across `{m}` files. Should I apply the rename to all of them?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Tests exist and pass | Proceed with refactoring, verify after |
| No tests cover the affected code | Invoke `unit-testing` first, then refactor |
| Refactoring affects only local/private scope | Apply directly (low risk) |
| Refactoring affects exported/public symbols | Flag as high-risk, require explicit user approval |
| Multiple refactoring options are valid | Choose the simplest transformation; ask if tradeoffs are significant |
| Refactoring crosses module boundaries | Flag as high-risk, check for circular dependencies first |
| Test fails after refactoring | Revert immediately, report the failing test and probable cause |
| Cyclomatic complexity is reduced by ≥ 2 | Prefer the refactoring that achieves this |

## Success Criteria

- [ ] All tests pass after refactoring (identical to baseline)
- [ ] No observable behavior change — same inputs produce same outputs
- [ ] Cyclomatic complexity is equal or lower after the change
- [ ] No new linting errors or warnings introduced
- [ ] All references to renamed/moved symbols are updated across the codebase
- [ ] No circular dependencies introduced
- [ ] Diff was reviewed and approved by the user before finalization

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Test regression after refactoring | One or more tests fail post-change | Revert immediately; diff the failing test to identify the broken contract |
| Missed reference during rename | Runtime errors in unrelated modules | Search all files including strings, configs, and dynamic references before renaming |
| Circular dependency introduced | Build or import errors after move | Analyze dependency graph before moving; abort if cycle would be created |
| Partial refactoring applied | Code is in an inconsistent state | Ensure each refactoring step is atomic; revert the entire step on any failure |
| Public API broken | Downstream consumers fail or get type errors | Check symbol visibility before refactoring; require approval for public changes |
| Dead code incorrectly identified | Removed code was actually used via reflection/dynamic dispatch | Check for dynamic usage patterns (reflection, `getattr`, string-based lookups) before removing |

## Audit Log

```
- [{{timestamp}}] refactoring:start — file={{file_path}}, type={{refactor_type}}, symbol={{target_symbol}}
- [{{timestamp}}] baseline-tests:result — total={{count}}, passed={{count}}, failed={{count}}
- [{{timestamp}}] refactoring:applied — transformation={{type}}, lines_changed={{count}}, files_affected={{count}}
- [{{timestamp}}] verification-tests:result — total={{count}}, passed={{count}}, failed={{count}}
- [{{timestamp}}] refactoring:reverted — reason={{reason}} (only if reverted)
- [{{timestamp}}] refactoring:complete — success={{bool}}, complexity_delta={{delta}}, diff_size={{lines}}
```
