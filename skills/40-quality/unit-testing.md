---
name: unit-testing
description: >
  Generate unit tests following AAA pattern (Arrange-Act-Assert).
  Supports Jest, JUnit, Go Test, PyTest, and more.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - test-strategy
reasoning_mode: linear
---

# Unit Testing

> _"A test that doesn't assert anything is just a waste of electricity."_

## Context

Invoked when new code is written without tests, when refactoring needs a
safety net, or when coverage gaps are identified.

---

## Micro-Skills

### 1. Test Generation 🌿 (Eco Mode)

**Steps:**

1. Analyze the target function/method:
   - Input types and edge values.
   - Return type and possible exceptions.
   - Side effects (DB writes, API calls, file I/O).
2. Generate test cases using the AAA pattern:
   ```
   // Arrange — set up inputs and mocks
   // Act — call the function
   // Assert — verify the result
   ```
3. Include test cases for:
   - **Happy path** (valid inputs, expected output).
   - **Boundary values** (0, -1, MAX_INT, empty string, null).
   - **Error cases** (invalid input, missing dependencies, timeouts).

### 2. Mock Generation 🌿 (Eco Mode)

**Steps:**

1. Identify external dependencies (DB, HTTP, file system).
2. Create mocks/stubs that return controlled responses.
3. Use the project's mocking library:
   - JS/TS: `jest.mock()`, `sinon`
   - Python: `unittest.mock`, `pytest-mock`
   - Go: interfaces + test doubles
   - Java: `Mockito`

### 3. Snapshot Testing 🌿 (Eco Mode)

**Steps:**

1. For complex output (HTML, JSON, serialized objects), use snapshot tests.
2. Generate initial snapshots.
3. Document when snapshots should be updated vs investigated.

---

## Inputs

| Parameter     | Type       | Required | Description                      |
|---------------|------------|----------|----------------------------------|
| `file_path`   | `string`   | yes      | Path to the file to test         |
| `functions`   | `string[]` | no       | Specific functions (default: all)|
| `framework`   | `string`   | no       | Test framework override          |

## Outputs

| Field          | Type     | Description                              |
|----------------|----------|------------------------------------------|
| `test_file`    | `string` | Generated test file path                 |
| `test_count`   | `number` | Number of test cases generated           |
| `coverage`     | `string` | Coverage report for the tested file      |

---

## Edge Cases

- Function has no return value (void/side-effect only) — Assert on side
  effects (mock was called, DB state changed).
- Global state dependency — Refactor first (invoke `refactoring-suite`).
