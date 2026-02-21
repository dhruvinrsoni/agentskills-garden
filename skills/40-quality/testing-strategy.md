````markdown
---
name: testing-strategy
description: >
  Define test pyramid structure, coverage analysis, test type selection,
  and boundary condition identification for comprehensive quality assurance.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - test-strategy
reasoning_mode: plan-execute
---

# Testing Strategy

> _"The right test in the right layer catches bugs before they compound."_

## Context

Invoked when a project needs a testing plan, when coverage gaps are
identified, or when the team must decide which test types to apply for
new features. Builds on the test pyramid model to ensure efficient
allocation of testing effort across unit, integration, and E2E layers.

---

## Micro-Skills

### 1. Test Pyramid Analysis ⚡ (Power Mode)

**Steps:**

1. Assess the current test distribution across layers:

```text
        /   E2E    \        target: 5-10% of test suite
       /------------\
      / Integration  \      target: 15-25% of test suite
     /----------------\
    /   Unit Tests     \    target: 65-80% of test suite
   /____________________\
```

2. Calculate the pyramid health ratio:
   - **Healthy:** Unit > Integration > E2E (pyramid shape).
   - **Ice cream cone:** E2E > Integration > Unit (anti-pattern — invert).
   - **Hourglass:** Unit and E2E heavy, thin integration (fill the middle).
3. Map each module/service to its dominant test layer based on:
   - Pure logic → Unit tests.
   - Cross-module communication → Integration tests.
   - Critical user journeys → E2E tests.

### 2. Coverage Gap Analysis 🌿 (Eco Mode)

**Steps:**

1. Collect coverage metrics: line, branch, function, and statement coverage.
2. Identify uncovered code paths:
   - Error handlers and catch blocks.
   - Conditional branches (especially `else` and `default` cases).
   - Edge-case guards and validation logic.
3. Prioritize gaps by risk:
   - **High risk:** Business-critical paths, payment/auth flows.
   - **Medium risk:** Data transformation, API serialization.
   - **Low risk:** UI formatting, logging, debug utilities.

### 3. Test Type Selection 🌿 (Eco Mode)

**Steps:**

1. For each feature or module, select the appropriate test types:
   - **Unit:** Pure functions, calculations, data transformations.
   - **Integration:** Database queries, API client calls, message queues.
   - **Contract:** API boundaries between services.
   - **E2E:** Multi-step user workflows, critical business flows.
   - **Snapshot:** UI components, serialized output stability.
   - **Property-based:** Functions with large input domains (parsers, validators).
2. Document the rationale for each selection.

### 4. Boundary Condition Identification ⚡ (Power Mode)

**Steps:**

1. For each function under test, enumerate boundary values:
   - **Numeric:** 0, -1, 1, MAX_INT, MIN_INT, NaN, Infinity.
   - **String:** empty `""`, single char, max length, unicode, special chars.
   - **Collection:** empty `[]`, single element, max capacity, duplicates.
   - **Null/undefined:** null, undefined, missing optional fields.
   - **Date/time:** epoch, leap year, DST transitions, timezone boundaries.
2. Generate equivalence classes:
   - Valid inputs → expected output.
   - Boundary inputs → edge behavior.
   - Invalid inputs → error/rejection.
3. Cross-reference with existing tests to find untested boundaries.

---

## Inputs

| Parameter         | Type       | Required | Description                                  |
|-------------------|------------|----------|----------------------------------------------|
| `project_root`    | `string`   | yes      | Root directory of the project                |
| `coverage_report` | `string`   | no       | Path to existing coverage report (lcov/json) |
| `target_modules`  | `string[]` | no       | Specific modules to analyze (default: all)   |
| `test_framework`  | `string`   | no       | Test framework in use (Jest, PyTest, etc.)   |

## Outputs

| Field               | Type       | Description                                  |
|---------------------|------------|----------------------------------------------|
| `pyramid_assessment`| `object`   | Current vs target test distribution          |
| `coverage_gaps`     | `object[]` | Uncovered paths ranked by risk               |
| `test_plan`         | `object[]` | Recommended test types per module            |
| `boundary_cases`    | `object[]` | Identified boundary conditions to test       |

---

## Edge Cases

- No existing tests at all — Start with unit tests for the highest-risk
  modules; do not attempt full coverage in one pass.
- Monorepo with multiple frameworks — Analyze each package independently
  using its own test runner and coverage tool.
- Legacy code with no clear module boundaries — Use file-level coverage
  as a proxy until modules are extracted.

---

## Scope

### In Scope

- Analyzing test pyramid shape and recommending rebalancing
- Identifying coverage gaps by line, branch, function, and statement metrics
- Selecting appropriate test types (unit, integration, contract, E2E, snapshot, property-based) per module
- Enumerating boundary conditions and equivalence classes for functions under test
- Prioritizing coverage gaps by business risk
- Generating test plans with rationale for test type selection

### Out of Scope

- Writing or generating actual test code (delegate to `unit-testing` / `integration-testing`)
- Executing test suites or collecting live coverage data
- Configuring CI pipelines or coverage gates (delegate to `ci-pipeline`)
- Performance or load testing strategy (delegate to `performance-review`)
- Security-specific test cases like fuzzing (delegate to `security-review`)
- Manual/exploratory testing session planning

---

## Guardrails

- Never recommend removing existing passing tests to "improve" the pyramid ratio.
- Do not set coverage targets above 95% — diminishing returns cause brittle test suites.
- Always consider test execution time when recommending additional test layers.
- Recommend property-based tests only when the input domain is well-defined and large.
- Do not count generated/snapshot tests toward unit test coverage metrics.
- Flag any E2E tests that duplicate integration-level assertions as candidates for removal.
- Boundary analysis must include null/undefined cases for dynamically-typed languages.

## Ask-When-Ambiguous

### Triggers

- Coverage report is unavailable and cannot be generated automatically
- Project uses multiple test frameworks with overlapping scope
- Business-critical paths are not documented or labeled in the codebase
- Team has explicit coverage requirements that differ from defaults
- Monorepo with shared dependencies across packages

### Question Templates

1. "No coverage report was found. Should I analyze code structure to infer coverage gaps, or can you provide a report path?"
2. "This project uses both {{framework_a}} and {{framework_b}}. Which framework covers integration tests, and which covers unit tests?"
3. "Which modules or user flows are considered business-critical? I need this to prioritize coverage gaps."
4. "Your current coverage target is {{current_target}}%. Should I use this or recommend an adjusted target?"
5. "The {{module}} package has zero tests. Should I include it in the test plan or is it intentionally untested (e.g., generated code)?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Pyramid is inverted (more E2E than unit) | Prioritize adding unit tests; flag E2E tests that can be pushed down |
| Coverage is below 50% overall | Focus on highest-risk modules first; do not spread effort thinly |
| Module is pure computation with no I/O | Recommend unit tests exclusively; skip integration layer |
| Module is an API gateway or controller | Recommend integration tests as primary; unit tests for validation logic only |
| Coverage is above 90% but bugs persist | Analyze branch coverage and boundary conditions — line coverage is misleading |
| New feature with unclear requirements | Recommend TDD approach — write test specifications first, then implement |
| Test suite takes > 10 minutes to run | Flag slow tests; recommend parallelization or layer-based splitting |

## Success Criteria

- [ ] Test pyramid distribution is documented with current vs target percentages
- [ ] Coverage gaps are identified and ranked by business risk (High/Medium/Low)
- [ ] Each module has a recommended test type with documented rationale
- [ ] Boundary conditions are enumerated for all high-risk functions
- [ ] No test layer is recommended without considering execution time impact
- [ ] Test plan is actionable — specific files and functions are named, not just categories
- [ ] Anti-patterns (ice cream cone, hourglass) are flagged with remediation steps

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Over-testing low-risk code | Test suite is slow but catches few real bugs | Prioritize by risk; cut low-value tests that test framework internals |
| Ignoring branch coverage | High line coverage but edge cases still fail in production | Always analyze branch coverage alongside line coverage |
| Wrong test layer | Integration tests testing pure logic; unit tests mocking everything | Apply the test type selection rubric from Micro-Skill 3 |
| Coverage target too aggressive | Team writes trivial tests to hit 100% — asserting constants, testing getters | Cap targets at 90%; focus on meaningful assertions |
| Boundary analysis too shallow | Only obvious values tested (0, null); misses domain-specific edges | Use domain knowledge to identify business-specific boundary values |
| Stale test plan | Plan references modules that have been refactored or removed | Re-run strategy analysis after major refactors; version the test plan |

## Audit Log

- `[{{timestamp}}] strategy-started: project={{project_name}}, modules={{module_count}}, framework={{test_framework}}`
- `[{{timestamp}}] pyramid-assessed: unit={{unit_pct}}%, integration={{integ_pct}}%, e2e={{e2e_pct}}% — shape={{shape}}`
- `[{{timestamp}}] coverage-gap-found: {{file_path}} — {{uncovered_type}} coverage at {{pct}}%, risk={{risk_level}}`
- `[{{timestamp}}] test-type-assigned: {{module}} → {{test_type}} — rationale: {{reason}}`
- `[{{timestamp}}] boundary-identified: {{function_name}} — {{boundary_count}} conditions, {{untested_count}} untested`
- `[{{timestamp}}] strategy-completed: gaps={{gap_count}}, recommendations={{rec_count}}, duration={{duration_minutes}}min`
````
