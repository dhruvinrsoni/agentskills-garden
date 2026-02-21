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

---

## Scope

### In Scope

- Generating unit test files for individual functions, methods, and classes.
- Creating mocks, stubs, and test doubles for external dependencies.
- Snapshot test generation for complex serialized output.
- Configuring test framework settings specific to unit testing (timeouts, matchers, plugins).
- Identifying and covering boundary values, error cases, and edge conditions.

### Out of Scope

- Integration tests that require real databases, HTTP servers, or containers (delegate to `integration-testing`).
- E2E or UI tests (browser automation, Playwright, Cypress).
- Mutation testing analysis (delegate to `mutation-testing` skill).
- Modifying application source code to fix bugs found by tests.
- Test strategy or coverage threshold decisions (delegate to `test-strategy` skill).
- Performance benchmarking or load testing.

---

## Guardrails

- Follow the project's existing test framework and conventions—never introduce a competing framework.
- Use the AAA pattern (Arrange-Act-Assert) consistently; each test must have at least one meaningful assertion.
- Never mock the unit under test—only mock its external dependencies.
- Avoid testing private/internal methods directly; test through the public API.
- Do not write tests that depend on execution order or shared mutable state.
- Keep each test under 20 lines; if a test is longer, decompose the arrangement into a helper or fixture.
- Run the full test suite after generating tests; revert if any pre-existing test breaks.
- Never hard-code file paths, timestamps, or random values—use deterministic fixtures.

---

## Ask-When-Ambiguous

### Triggers

- The target function has side effects and no return value—unclear what to assert.
- Multiple mocking libraries are available in the project and no convention is established.
- The function depends on global state or singletons that are difficult to isolate.
- Target file contains both pure logic and I/O; unclear which parts should be unit-tested vs. integration-tested.
- Snapshot testing is possible but the output format changes frequently.

### Question Templates

- "The function `{name}` has no return value. Should I assert on mock interactions (e.g., `toHaveBeenCalledWith`) or on state changes?"
- "I found both `{mock_lib_a}` and `{mock_lib_b}` in the project. Which should I use for new tests?"
- "The function depends on `{global/singleton}`. Should I refactor to inject the dependency, or mock the global directly?"
- "`{function}` mixes pure computation with database writes. Should I split it, or write a unit test that mocks the DB call?"
- "The output of `{function}` changes with locale/timezone. Should I pin the locale in tests or use snapshot matching?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Pure function with clear inputs/outputs | Generate standard AAA tests with boundary values |
| Function with external dependencies (DB, HTTP) | Create mocks for all external calls; assert on return values and mock interactions |
| Void function with side effects | Assert that side-effect targets (mocks, spies) were called with correct arguments |
| Complex object output (JSON, HTML) | Use snapshot testing; document update policy |
| Function already has tests but low branch coverage | Generate additional tests targeting uncovered branches |
| Global state or singleton dependency | Recommend refactoring to dependency injection; if refused, mock the global carefully |
| Function throws on invalid input | Write explicit error-case tests asserting on exception type and message |
| Test file exceeds 300 lines | Split into multiple test files by concern (happy path, errors, edge cases) |

---

## Success Criteria

- [ ] Every public function/method in the target file has at least one unit test.
- [ ] Happy path, boundary values, and error cases are all covered.
- [ ] All tests follow the AAA pattern with meaningful assertions.
- [ ] Mocks are minimal—only external dependencies are mocked, never the unit under test.
- [ ] Generated tests pass on first run without modification.
- [ ] No pre-existing tests are broken by the new test file.
- [ ] Line coverage for the target file is ≥ 80%; branch coverage is ≥ 70%.
- [ ] Test file follows the project's naming and directory conventions.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Over-mocking | Tests pass but don't catch real bugs; mocks replicate implementation details | Mock only at dependency boundaries; prefer stubs that return realistic data |
| Brittle tests | Tests break on every refactor even though behavior hasn't changed | Assert on outcomes, not implementation; avoid asserting call order unless critical |
| Missing edge cases | Bug reported for input the tests never exercised | Systematically cover: null, empty, zero, negative, MAX, unicode, whitespace |
| Snapshot rot | Snapshots auto-updated without review; regressions slip through | Require manual snapshot review; add snapshot update to PR checklist |
| Test interdependence | Test B fails when run alone but passes in suite order | Eliminate shared state; use `beforeEach` setup, not `beforeAll` for mutable state |
| Wrong mocking library | Generated mocks use a library not installed in the project | Detect mocking library from existing test files and `devDependencies` before generating |

---

## Audit Log

- `[{timestamp}]` Unit testing skill invoked for `{file_path}`.
- `[{timestamp}]` Functions analyzed: `{function list}`.
- `[{timestamp}]` Test cases generated: `{count}` (happy: `{h}`, boundary: `{b}`, error: `{e}`).
- `[{timestamp}]` Mocks created for: `{dependency list}`.
- `[{timestamp}]` Test file written: `{test_file_path}`.
- `[{timestamp}]` Test suite executed — **{passed}** passed, **{failed}** failed.
- `[{timestamp}]` Coverage for `{file}`: Line `{line}%`, Branch `{branch}%`.
