---
name: test-strategy
description: >
  Define the testing pyramid for a project: unit, integration, E2E.
  Set coverage targets and testing conventions.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: plan-execute
---

# Test Strategy

> _"Tests are a specification, not an afterthought."_

## Context

Invoked at project setup or when test coverage is inadequate. Establishes
a testing pyramid and conventions that all other testing skills follow.

---

## Micro-Skills

### 1. Pyramid Definition ⚡ (Power Mode)

**Steps:**

1. Define the testing pyramid for the project:

```text
        /  E2E  \        (few, slow, expensive)
       /----------\
      / Integration \    (moderate, medium speed)
     /----------------\
    /    Unit Tests     \  (many, fast, cheap)
   /____________________\
```

2. Set targets:
   - **Unit:** >= 80% line coverage, >= 70% branch coverage.
   - **Integration:** Cover all API endpoints, all DB queries.
   - **E2E:** Cover critical user journeys (happy path + top 3 error paths).

### 2. Convention Setup 🌿 (Eco Mode)

**Steps:**

1. Define test file naming: `*.test.ts`, `*_test.go`, `test_*.py`.
2. Define test directory structure: co-located or `__tests__/` directory.
3. Configure test runner (Jest, PyTest, Go test, JUnit).
4. Add test scripts to `package.json` / `Makefile` / `pyproject.toml`.

### 3. Coverage Gate 🌿 (Eco Mode)

**Steps:**

1. Configure coverage thresholds in the test runner config.
2. Fail CI if coverage drops below the threshold.
3. Generate coverage reports in both human-readable and machine-parseable
   formats (HTML + lcov).

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `strategy_doc`     | `string`   | Test strategy document                   |
| `config_files`     | `string[]` | Test runner configuration files          |
| `coverage_config`  | `string`   | Coverage threshold configuration         |

---

## Scope

### In Scope

- Defining the testing pyramid (unit / integration / E2E ratios and targets).
- Setting coverage thresholds (line, branch, function) per layer.
- Establishing test file naming conventions and directory structure.
- Configuring test runners and coverage reporters.
- Adding test scripts to build tool configs (`package.json`, `Makefile`, `pyproject.toml`).
- Creating the project-level test strategy document.

### Out of Scope

- Writing individual test cases (delegate to `unit-testing`, `integration-testing`).
- Mutation testing execution (delegate to `mutation-testing` skill).
- CI/CD pipeline setup for running tests (delegate to `ci-pipeline` skill).
- Performance or load testing strategy.
- Application source code changes.

---

## Guardrails

- Never lower existing coverage thresholds without explicit approval.
- Do not impose a single test framework if the project already uses one—adapt to the existing choice.
- Keep the strategy document under 2 pages; link to detailed skill docs for implementation.
- Do not configure coverage gates that block CI until the team has agreed on thresholds.
- Always generate both human-readable (HTML) and machine-parseable (lcov, cobertura) coverage reports.
- Do not mandate 100% coverage—set realistic, maintainable targets per layer.
- Preview all config file changes as diffs before applying.

---

## Ask-When-Ambiguous

### Triggers

- Project has no existing tests or test runner configuration.
- Multiple test frameworks are present (e.g., Jest and Mocha) and it is unclear which is canonical.
- Coverage targets conflict with team velocity constraints.
- Monorepo with multiple packages that may need independent strategies.
- Unclear whether E2E tests should be in-repo or in a separate test repository.

### Question Templates

- "No test runner is configured. Which framework should I set up (`{options based on language}`)?"
- "The project has both `{framework_a}` and `{framework_b}` configs. Which is the primary test runner?"
- "What coverage thresholds are acceptable? Recommended defaults: 80% line / 70% branch."
- "This is a monorepo—should each package have its own coverage gate, or should there be a single aggregate threshold?"
- "Should E2E tests live alongside application code or in a separate testing repository?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Greenfield project with no tests | Define full pyramid: unit ≥ 80%, integration for all APIs, E2E for critical journeys |
| Existing project with low coverage | Set incremental thresholds (e.g., +5% per sprint) rather than a hard gate |
| Microservice architecture | Per-service strategy with shared conventions; contract tests between services |
| Monolith application | Single strategy document; partition coverage by module/package |
| Team prefers co-located tests | Configure `*.test.{ext}` next to source files |
| Team prefers separate test directory | Configure `__tests__/` or `tests/` directory mirroring source structure |
| CI build time exceeds 10 minutes | Split into fast (unit) and slow (integration/E2E) pipelines |
| Coverage already meets targets | Focus on test quality (mutation testing) rather than quantity |

---

## Success Criteria

- [ ] Test strategy document is created and covers all three pyramid layers.
- [ ] Coverage thresholds are configured in the test runner (line, branch, function).
- [ ] Test file naming conventions and directory structure are documented and consistent.
- [ ] Test scripts are added to the project's build tool (`test`, `test:unit`, `test:integration`, `test:e2e`).
- [ ] Coverage reports generate in both HTML and machine-parseable formats.
- [ ] CI coverage gate is configured (or documented for future activation with team agreement).
- [ ] Existing tests pass after configuration changes.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Overly aggressive thresholds | Developers write low-quality tests just to hit coverage numbers | Set realistic targets; complement with mutation testing for quality |
| Framework mismatch | Tests fail after config changes because wrong runner was configured | Detect existing test framework from lockfile and config before choosing |
| Monorepo coverage bleed | Aggregate coverage masks under-tested packages | Configure per-package thresholds; report coverage per workspace |
| Missing test scripts | Developers don't know how to run tests | Add clearly named scripts to build config; document in README |
| Coverage report not generated | CI gate passes vacuously because no report is produced | Add explicit coverage reporter config; fail CI if report file is missing |
| Strategy drift | Strategy document becomes outdated as project evolves | Link strategy review to quarterly planning; add a "last reviewed" date |

---

## Audit Log

- `[{timestamp}]` Test strategy skill invoked for `{project/repo}`.
- `[{timestamp}]` Pyramid defined — Unit: `{target}%`, Integration: `{scope}`, E2E: `{journey count}` journeys.
- `[{timestamp}]` Test runner configured: `{framework}` with coverage reporter `{reporter}`.
- `[{timestamp}]` Config files created/modified: `{file list}`.
- `[{timestamp}]` Coverage thresholds set — Line: `{line}%`, Branch: `{branch}%`, Function: `{func}%`.
- `[{timestamp}]` Strategy document generated: `{doc path}`.
