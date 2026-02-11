---
name: refactoring-suite
description: >
  Complex refactoring operations with strict test verification.
  Every refactor follows: Test → Refactor → Test → Revert-on-Fail.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
  - unit-testing
reasoning_mode: plan-execute
---

# Refactoring Suite

> _"Change the structure, preserve the behavior."_

## Context

Invoked for structural code changes that must not alter external behavior.
Every micro-skill follows the **Red-Green-Refactor** safety net.

---

## The Iron Rule

```text
1. Run existing tests → all PASS (baseline)
2. Apply refactoring
3. Run tests again → all PASS (verification)
4. If any test FAILS → REVERT immediately, report failure
```

**No exceptions.** If no tests exist, invoke `unit-testing` first.

---

## Micro-Skills

### 1. Extract Method/Function ⚡ (Power Mode)

**Steps:**

1. Identify the code block to extract (user-selected or heuristic: >15 lines).
2. Determine parameters (variables used but defined outside the block).
3. Determine return values.
4. Create the new function with a descriptive name.
5. Replace the original block with a call to the new function.
6. Run tests.

### 2. Extract Class/Module ⚡ (Power Mode)

**Steps:**

1. Identify a class/module with >1 responsibility (SRP violation).
2. Group related methods and fields into a new class.
3. Move extracted members, update all references.
4. Add the new class as a dependency of the original.
5. Run tests.

### 3. Dependency Inversion ⚡ (Power Mode)

**Steps:**

1. Identify concrete dependencies (direct `new` calls, static method calls).
2. Extract an interface for each dependency.
3. Inject the dependency via constructor or factory.
4. Update all instantiation sites.
5. Run tests.

### 4. Rename Symbol ⚡ (Power Mode)

**Steps:**

1. Check `protected_terms` — abort if the symbol is protected.
2. Find all references across the codebase (not just the file).
3. Generate rename map with scope and risk level.
4. Apply rename, run tests, present diff.

### 5. Inline / Remove Dead Code ⚡ (Power Mode)

**Steps:**

1. Identify unused functions, variables, imports.
2. Verify "unused" by checking all call sites (including dynamic/reflection).
3. Remove dead code, run tests.
4. Present diff with a summary of what was removed and why.

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `diff`          | `string`   | Unified diff of all changes              |
| `test_results`  | `object`   | Before/after test run comparison         |
| `reverted`      | `boolean`  | Whether the refactor was reverted        |

---

## Edge Cases

- Refactoring across module boundaries — Flag as high-risk, require approval.
- Tests exist but don't cover the refactored code — Warn user, suggest adding
  tests before proceeding.
