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

---

## Scope

### In Scope
- Extracting methods, functions, classes, and modules from existing code
- Inverting dependencies by extracting interfaces and injecting via constructor/factory
- Renaming symbols across the entire codebase with reference tracking
- Identifying and removing dead code (unused functions, variables, imports)
- Applying structural transformations that preserve external behavior
- Running the full test suite before and after every refactoring step
- Reverting changes immediately when tests fail after a refactoring step
- Generating unified diffs and before/after test comparison reports

### Out of Scope
- Changing external behavior, public API signatures, or observable outputs (that's a feature change, not a refactor)
- Adding new functionality during a refactor (new behavior requires tests first via `tdd-workflow`)
- Writing new tests from scratch (delegate to `unit-testing`; this skill only runs existing tests)
- Performance optimization refactors (delegate to `profiling-analysis`, `caching-strategy`)
- Refactoring database schemas or migrations (delegate to `data-access`, `database-design`)
- Refactoring CI/CD pipelines or infrastructure code (delegate to `ci-pipeline`, `terraform-iac`)
- Refactoring code in `vendor/`, `node_modules/`, `generated/`, or third-party directories

---

## Guardrails

- The Iron Rule is absolute: Test → Refactor → Test → Revert-on-Fail. No exceptions.
- Never refactor code that has zero test coverage — invoke `unit-testing` first to establish a safety net.
- Never change external behavior during a refactor — if behavior needs to change, stop and write a test first.
- Each refactoring step must be atomic: one extract, one rename, one inline at a time.
- Preview all diffs before applying; never write changes without user review.
- Never rename symbols listed in `protected_terms` or public API contracts.
- If a test fails after refactoring, revert immediately — do not attempt to fix the test.
- Do not refactor into `vendor/`, `node_modules/`, `dist/`, `build/`, or `generated/` directories.
- Limit each refactoring session to one structural concern (e.g., SRP violation OR dead code, not both simultaneously).

## Ask-When-Ambiguous

### Triggers
- The code to refactor has no test coverage and the user wants to proceed anyway
- Multiple valid extraction boundaries exist (e.g., the method could be split two different ways)
- A symbol rename would affect a public API or external consumers
- The refactoring would move code across module or package boundaries
- Dead code detection finds code that appears unused but may be called via reflection or dynamic dispatch
- The refactoring conflicts with an ongoing feature branch or PR

### Question Templates
1. "This code has no test coverage. Should I write tests first (via `unit-testing`) or proceed with the refactor at your own risk?"
2. "I can extract `{block}` into `{option_a}` (smaller, more focused) or `{option_b}` (broader, fewer calls). Which do you prefer?"
3. "Renaming `{symbol}` would affect the public API consumed by `{consumers}`. Should I proceed or treat it as a breaking change?"
4. "Moving `{class}` from `{module_a}` to `{module_b}` crosses a module boundary. Should I flag this as high-risk and require additional review?"
5. "The function `{func}` appears unused, but it has a `@reflect` / dynamic dispatch annotation. Should I remove it or keep it?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Code has no test coverage | Abort refactoring; invoke `unit-testing` to add tests, then retry |
| Code block exceeds 15 lines and has a clear single responsibility | Extract into a named function with descriptive name |
| Class has >1 responsibility (SRP violation) | Extract the secondary responsibility into a new class; inject as dependency |
| Concrete dependency is instantiated with `new` inside a method | Extract interface, inject via constructor (Dependency Inversion) |
| Symbol name is misleading or abbreviated | Rename across all references; verify no protected terms are affected |
| Function/variable has zero call sites and no dynamic dispatch | Remove as dead code; present diff with justification |
| Refactoring step causes a test failure | Revert immediately; try a smaller, more isolated transformation |
| Refactoring would cross a module or package boundary | Flag as high-risk; require user approval before proceeding |

## Success Criteria

- [ ] All tests pass before the refactoring begins (valid baseline established)
- [ ] All tests pass after the refactoring is complete (behavior preserved)
- [ ] No external behavior or public API signature has changed
- [ ] The unified diff clearly shows a structural improvement (fewer lines, clearer names, better separation)
- [ ] No dead code remains that was identified during the session
- [ ] No protected terms or public API symbols were renamed without approval
- [ ] Each refactoring step was atomic and independently reversible
- [ ] The refactoring was reverted zero times in the final result (all transformations succeeded)

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Test failure after refactoring | One or more tests break after applying a transformation | Revert immediately per the Iron Rule; retry with a smaller step |
| Behavior change introduced | Refactored code produces different output for the same input | Run regression tests; diff output before/after; revert on mismatch |
| No baseline tests exist | Cannot verify behavior preservation — refactoring is unsafe | Abort; invoke `unit-testing` to establish coverage before refactoring |
| Rename affects public API | External consumers break after symbol rename | Check `protected_terms` and public exports before renaming; ask user if in doubt |
| Dead code removed was actually used via reflection | Runtime errors in production after deployment | Verify "unused" status by searching for string-based references, annotations, and dynamic dispatch |
| Cross-module extraction breaks encapsulation | Internal implementation details become visible across module boundaries | Keep extracted code at the same visibility level; use internal/package-private access where possible |
| Refactoring session scope creep | Multiple unrelated concerns refactored simultaneously, hard to review | Limit each session to one structural concern; create separate tasks for additional refactors |

## Audit Log

```
- [{{timestamp}}] refactoring-suite:start — target={{file_or_module}}, test_baseline={{pass_count}}/{{total_count}}
- [{{timestamp}}] refactor:extract-method — source={{file}}, method={{name}}, params={{param_list}}, lines_extracted={{count}}
- [{{timestamp}}] refactor:extract-class — source={{file}}, new_class={{name}}, members_moved={{count}}
- [{{timestamp}}] refactor:dependency-inversion — class={{name}}, interface={{interface_name}}, injection_sites={{count}}
- [{{timestamp}}] refactor:rename — old={{old_name}}, new={{new_name}}, references_updated={{count}}, scope={{scope}}
- [{{timestamp}}] refactor:dead-code-removed — items={{item_list}}, lines_removed={{count}}
- [{{timestamp}}] test:verification — status={{pass|fail}}, passed={{count}}, failed={{count}}, reverted={{bool}}
- [{{timestamp}}] refactoring-suite:complete — transformations={{count}}, tests_pass={{bool}}, reverted={{bool}}, diff_lines={{count}}
```
