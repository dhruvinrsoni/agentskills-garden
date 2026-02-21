---
name: mutation-testing
description: >
  Verify test suite quality by injecting faults (mutants) into
  the code and checking if tests catch them.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - unit-testing
reasoning_mode: plan-execute
---

# Mutation Testing

> _"Your tests are only as good as the bugs they catch."_

## Context

Invoked when test coverage is high but confidence in test quality is low.
Mutation testing reveals tests that pass by accident (weak assertions).

---

## Micro-Skills

### 1. Mutant Generation ⚡ (Power Mode)

**Steps:**

1. Select the target module/file.
2. Apply mutation operators:
   - **Arithmetic:** `+` → `-`, `*` → `/`
   - **Conditional:** `<` → `<=`, `==` → `!=`, `&&` → `||`
   - **Return value:** `return x` → `return null/0/true`
   - **Void method:** Remove method call
   - **Negation:** `if (cond)` → `if (!cond)`
3. Generate one mutant per operator per target expression.

### 2. Mutant Execution ⚡ (Power Mode)

**Steps:**

1. For each mutant, run the test suite.
2. Classify the result:
   - **Killed** — at least one test failed (good).
   - **Survived** — all tests passed (bad — test gap).
   - **Timeout** — tests hung (treat as killed).
   - **Equivalent** — mutation doesn't change behavior (ignore).

### 3. Gap Analysis ⚡ (Power Mode)

**Steps:**

1. For each surviving mutant, identify:
   - Which line was mutated.
   - What assertion is missing.
2. Generate a recommended test case to kill the mutant.
3. Calculate the **mutation score**: `killed / (total - equivalent)`.
4. Target: >= 80% mutation score.

---

## Tools by Language

| Language   | Tool                           |
|------------|--------------------------------|
| Java       | PIT (pitest.org)               |
| JavaScript | Stryker                        |
| Python     | mutmut, cosmic-ray             |
| Go         | gremlins, ooze                 |
| C#         | Stryker.NET                    |

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `mutation_score`| `number` | Percentage of killed mutants             |
| `survivors`     | `object[]`| Surviving mutants with locations         |
| `recommended`   | `string[]`| Suggested tests to kill survivors        |

---

## Scope

### In Scope

- Selecting target modules/files for mutation analysis.
- Configuring and running mutation testing tools (PIT, Stryker, mutmut, etc.).
- Classifying mutants as killed, survived, equivalent, or timed-out.
- Generating gap-analysis reports with recommended test cases for survivors.
- Creating or modifying test files to kill surviving mutants.

### Out of Scope

- Writing the initial test suite from scratch (delegate to `unit-testing` skill).
- Modifying application source code to make it "more testable."
- Integration or E2E test mutation (focus is on unit-level mutants).
- CI/CD pipeline changes (delegate to `ci-pipeline` skill).
- Code coverage measurement without mutation (delegate to `test-strategy` skill).

---

## Guardrails

- Never mutate generated code, vendor dependencies, or third-party libraries.
- Run mutation testing on a clean, passing test suite—abort if any test already fails.
- Limit mutation scope to one module or file at a time to keep execution time under 10 minutes.
- Do not count equivalent mutants against the mutation score; document them explicitly.
- Only modify test files to kill survivors—never alter application source code.
- Preview recommended test cases as diffs before writing them.
- If mutation score is already ≥ 80%, report success without forcing unnecessary tests.

---

## Ask-When-Ambiguous

### Triggers

- Target file or module is not specified.
- Multiple mutation testing tools are available for the project's language.
- Test suite takes > 5 minutes, making full mutation analysis expensive.
- Unclear whether a surviving mutant is equivalent or a genuine test gap.
- Project uses multiple test frameworks (e.g., Jest + Vitest) and tool selection is ambiguous.

### Question Templates

- "Which file or module should I run mutation testing against?"
- "The test suite takes `{duration}`—should I limit mutations to a specific set of operators (e.g., conditionals only)?"
- "Mutant on line `{line}` of `{file}` survived. The mutation `{description}` may be equivalent—should I mark it as equivalent or write a test?"
- "Multiple tools are available (`{tool_a}`, `{tool_b}`). Do you have a preference, or should I choose based on project conventions?"
- "The current mutation score is `{score}%`. Is that acceptable, or should I target a higher threshold?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Mutation score < 60% | Focus on killing high-impact survivors (conditionals, return values) first |
| Mutation score 60–80% | Target remaining survivors systematically; prioritize business-logic files |
| Mutation score ≥ 80% | Report success; only address survivors in critical paths |
| Test suite > 5 minutes | Use incremental mutation (only mutate changed files) or limit operators |
| Surviving mutant is in a trivial getter/setter | Mark as low-priority; do not write a test unless explicitly requested |
| Surviving mutant changes a business rule conditional | High priority—write a targeted assertion immediately |
| Tool not installed for the project language | Recommend and configure the appropriate tool before running |
| Equivalent mutant suspected | Document the rationale and exclude from score calculation |

---

## Success Criteria

- [ ] Mutation testing tool runs successfully against the target module.
- [ ] Mutation score meets or exceeds the 80% threshold.
- [ ] Every surviving mutant is classified: test gap, equivalent, or low-priority.
- [ ] Recommended test cases are generated for all non-equivalent survivors.
- [ ] New tests kill their targeted mutants when re-run.
- [ ] No application source code was modified—only test files.
- [ ] Gap-analysis report is generated with mutant locations and missing assertions.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Pre-existing test failures | Mutation tool aborts or produces unreliable results | Run the test suite first; fix failures before starting mutation analysis |
| Timeout on large codebase | Mutation run exceeds 10-minute budget | Narrow scope to a single file/module; reduce mutation operators |
| False survivors (equivalent mutants) | Score appears artificially low | Manually review survivors; mark confirmed equivalents; document reasoning |
| Tool misconfiguration | Zero mutants generated or all mutants skipped | Verify tool config (source paths, test patterns, excluded files) |
| Flaky tests | Mutants randomly killed/survived across runs | Stabilize flaky tests before mutation analysis; exclude flaky tests from scope |
| Incompatible tool version | Runtime errors or missing mutation operators | Pin tool version in project config; verify compatibility with language/framework version |

---

## Audit Log

- `[{timestamp}]` Mutation testing invoked for `{file/module}` using `{tool}`.
- `[{timestamp}]` Total mutants generated: `{count}` using operators: `{operator list}`.
- `[{timestamp}]` Results — Killed: `{k}`, Survived: `{s}`, Equivalent: `{e}`, Timeout: `{t}`.
- `[{timestamp}]` Mutation score: `{score}%` (target: `{threshold}%`).
- `[{timestamp}]` Tests written to kill survivors: `{test file list}`.
- `[{timestamp}]` Re-run confirmation — all targeted mutants now killed: `{yes/no}`.
