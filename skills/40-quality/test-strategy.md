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
