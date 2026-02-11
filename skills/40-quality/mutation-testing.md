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
