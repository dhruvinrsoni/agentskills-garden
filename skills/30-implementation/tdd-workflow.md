---
name: tdd-workflow
description: >
  Drive implementation through the Red-Green-Refactor cycle.
  Write failing tests first, implement minimal code to pass, then refactor.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
  - unit-testing
reasoning_mode: tdd
---

# TDD Workflow

> _"Red, Green, Refactor — the heartbeat of reliable code."_

## Context

Invoked when the user wants to build a feature or fix a bug using test-driven
development. The skill enforces the strict Red-Green-Refactor cycle: write a
failing test first, write the minimum code to make it pass, then refactor
while keeping all tests green.

---

## The TDD Cycle

```text
┌─────────┐     ┌─────────┐     ┌───────────┐
│   RED   │ ──▶ │  GREEN  │ ──▶ │ REFACTOR  │
│(failing │     │(minimal │     │(clean up, │
│  test)  │     │  pass)  │     │tests stay │
└─────────┘     └─────────┘     │  green)   │
     ▲                          └─────┬─────┘
     └────────────────────────────────┘
```

**Discipline:** Never write production code without a failing test first.

---

## Micro-Skills

### 1. Red — Write Failing Test ⚡ (Power Mode)

**Goal:** Capture the next behavior increment as a failing test.

**Steps:**

1. Identify the smallest next behavior to implement from the spec or user story.
2. Write a single, focused test that asserts the expected behavior.
3. Run the test — confirm it **fails** (red).
4. If the test passes immediately, it's not testing new behavior — revise or skip.

---

### 2. Green — Minimal Implementation 🌿 (Eco Mode)

**Goal:** Write the simplest code that makes the failing test pass.

**Steps:**

1. Write the least amount of production code needed to make the test pass.
2. Hardcode values, use simple conditionals — do not over-engineer.
3. Run all tests — confirm the new test **passes** and no existing tests break.
4. If tests fail, fix the implementation (not the test) until green.

---

### 3. Refactor — Clean Up ⚡ (Power Mode)

**Goal:** Improve code quality while keeping all tests green.

**Steps:**

1. Look for duplication, unclear names, or structural issues in the new code.
2. Apply small, safe refactorings (extract method, rename, simplify conditionals).
3. Run all tests after each refactoring step — must stay green.
4. If any test fails during refactor, revert the last refactoring step immediately.

---

### 4. Coverage Gate 🌿 (Eco Mode)

**Goal:** Ensure the TDD cycle maintains adequate coverage targets.

**Steps:**

1. After each Red-Green-Refactor cycle, measure code coverage.
2. Flag any production code paths not exercised by tests.
3. If coverage drops below the project threshold (default: 80%), add targeted tests.
4. Report coverage delta compared to the cycle start.

---

## Inputs

| Parameter          | Type       | Required | Description                                      |
|--------------------|------------|----------|--------------------------------------------------|
| `spec`             | `string`   | yes      | Feature spec, user story, or bug description     |
| `test_framework`   | `string`   | no       | Test framework to use (auto-detected if omitted) |
| `coverage_target`  | `number`   | no       | Minimum coverage percentage (default: 80)        |
| `file_path`        | `string`   | no       | Path to the file under development               |

## Outputs

| Field            | Type      | Description                                    |
|------------------|-----------|------------------------------------------------|
| `tests_written`  | `number`  | Count of new tests created                     |
| `impl_diff`      | `string`  | Unified diff of production code changes        |
| `test_diff`      | `string`  | Unified diff of test code changes              |
| `coverage`       | `object`  | Coverage report (before/after, delta)          |
| `cycles`         | `number`  | Number of Red-Green-Refactor cycles completed  |
| `summary`        | `string`  | Human-readable summary of the TDD session      |

---

## Scope

### In Scope
- Writing new test cases that capture expected behavior before implementation
- Implementing minimal production code to satisfy failing tests
- Refactoring production code while maintaining passing test suite
- Measuring and reporting code coverage after each cycle
- Detecting and flagging untested code paths
- Guiding the decomposition of a feature into testable increments
- Selecting and configuring the appropriate test framework for the project

### Out of Scope
- Writing integration tests or end-to-end tests (delegate to `integration-testing`)
- Performance testing or load testing (delegate to `profiling-analysis`)
- Modifying existing tests that are unrelated to the current feature
- Refactoring code that has no test coverage (delegate to `refactoring` which will create tests first)
- Generating API contracts or specifications (delegate to `api-contract-design`)
- Deploying or running the application in non-test environments
- Modifying CI/CD pipeline configuration

---

## Guardrails

- Never write production code without a corresponding failing test — Red always comes first.
- Each test must assert exactly one behavior; no multi-assertion tests that test unrelated things.
- The Green step must use the simplest possible implementation — resist the urge to over-engineer.
- Run the full test suite (not just the new test) after each Green and Refactor step.
- Revert immediately if any existing test breaks during Refactor — do not debug in a broken state.
- Never modify a test to make it pass — fix the production code instead.
- Do not skip the Refactor step; technical debt compounds quickly without it.
- Coverage must not decrease across a TDD session; if it does, add missing tests before proceeding.
- Do not generate tests for `vendor/`, `node_modules/`, `generated/`, or third-party code.

## Ask-When-Ambiguous

### Triggers
- The spec or user story is vague about expected behavior or edge cases
- Multiple test frameworks are available in the project and none is clearly primary
- The feature touches code with no existing test infrastructure
- Coverage target conflicts with project timeline or user preference
- The next behavior increment is unclear — multiple valid decompositions exist

### Question Templates
1. "The spec doesn't define what happens when `{input}` is `{edge_case}`. Should the function throw, return a default, or handle it silently?"
2. "I found both `{framework_a}` and `{framework_b}` in the project. Which should I use for these tests?"
3. "This feature can be decomposed into `{n}` testable increments. Should I start with `{increment_a}` (simplest) or `{increment_b}` (most critical)?"
4. "The current coverage is `{current}%` which is below the `{target}%` target. Should I add tests for existing code first or proceed with the new feature?"
5. "The behavior for `{scenario}` could reasonably be `{option_a}` or `{option_b}` — which is correct?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| No test framework configured in the project | Detect language, recommend the standard framework, ask user to confirm |
| Test passes immediately after writing it (no red phase) | The test is not testing new behavior — revise or discard it |
| Green step requires changing more than 20 lines | The increment is too large — break the test into smaller behavioral steps |
| Refactoring causes a test failure | Revert the refactoring step; try a smaller transformation |
| Coverage drops below target after a cycle | Add targeted tests for the uncovered paths before starting the next cycle |
| Multiple valid decompositions of the feature | Start with the simplest, most isolated increment |
| Existing tests are flaky or non-deterministic | Stabilize flaky tests before starting TDD — unreliable baseline undermines the cycle |
| Feature spec has ambiguous edge cases | Ask the user for clarification before writing the test |

## Success Criteria

- [ ] Every piece of production code was preceded by a failing test
- [ ] All tests pass at the end of every Green and Refactor step
- [ ] Code coverage meets or exceeds the project target (default: 80%)
- [ ] No test was modified to make it pass — only production code was changed
- [ ] Each test asserts a single, clearly defined behavior
- [ ] Refactoring was performed after each Green step (no skipped Refactor phases)
- [ ] The final code is clean, readable, and free of duplication

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Test written after production code | Test always passes, never goes red | Enforce discipline: write test first, confirm it fails, then implement |
| Over-engineered Green step | Large diff with unnecessary abstractions in the Green phase | Constrain Green to the absolute minimum; defer design to Refactor phase |
| Refactoring breaks tests | Existing tests fail after cleanup | Revert immediately; apply smaller, isolated refactoring steps |
| Flaky baseline tests | Tests pass and fail non-deterministically | Stabilize flaky tests before starting TDD; quarantine unreliable tests |
| Coverage regression | Coverage percentage drops across the session | Add missing tests immediately; do not proceed until coverage is restored |
| Overly large test increments | Test requires 50+ lines of production code to pass | Decompose into smaller behavioral increments; each test should need ≤20 lines of new code |
| Tests coupled to implementation details | Refactoring breaks tests that assert on internals | Write tests against public interfaces and observable behavior, not implementation details |

## Audit Log

```
- [{{timestamp}}] tdd:session-start — spec={{spec_summary}}, framework={{framework}}, coverage_target={{target}}%
- [{{timestamp}}] tdd:red — test={{test_name}}, assertion={{expected_behavior}}, status=FAIL (confirmed)
- [{{timestamp}}] tdd:green — test={{test_name}}, status=PASS, impl_lines={{count}}, all_tests_pass={{bool}}
- [{{timestamp}}] tdd:refactor — transformation={{type}}, all_tests_pass={{bool}}, reverted={{bool}}
- [{{timestamp}}] tdd:coverage — before={{before}}%, after={{after}}%, delta={{delta}}%, target_met={{bool}}
- [{{timestamp}}] tdd:session-complete — cycles={{count}}, tests_written={{count}}, coverage={{final}}%, all_green={{bool}}
```
