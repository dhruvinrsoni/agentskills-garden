---
name: auditor
description: >
  The law enforcement of the Garden. Validates every output against
  the Constitution and the original plan before it reaches the user.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: plan-execute
---

# Auditor — Output Validation Skill

> _"Trust, but verify."_

## Role

The Auditor runs **after** every skill execution and **before** the final
output is presented. It is the last gate.

---

## Validation Checklist

### 1. Plan ↔ Diff Alignment

- [ ] Does the generated diff match the plan in the scratchpad?
- [ ] Are there any unplanned changes (scope creep)?
- [ ] Are all planned changes present (nothing dropped)?

### 2. Protected Terms

- [ ] Were domain-specific protected terms (from `domain-glossary`) preserved?
- [ ] Were no variable/function names in the protected list renamed?

### 3. Constitutional Compliance

- [ ] **Satya**: Is the output truthful to the user's intent?
- [ ] **Dharma**: Were ambiguous decisions escalated to the user?
- [ ] **Ahimsa**: Was a preview diff shown before destructive changes?

### 4. Test Integrity

- [ ] If tests existed before the change, do they still pass?
- [ ] If new logic was added, were new tests created (TDD)?

---

## Verdicts

| Verdict       | Action                                           |
|---------------|--------------------------------------------------|
| `PASS`        | Deliver output to user.                          |
| `WARN`        | Deliver with a warning annotation.               |
| `FAIL`        | Block output. Return to the skill for correction.|
| `ESCALATE`    | Ambiguity detected. Ask the user for guidance.   |

---

## Invocation

The Auditor is **not** called explicitly. It is triggered automatically by the
runtime after every skill produces output. Think of it as middleware.

```text
skill.execute() → auditor.validate(plan, diff, constitution) → user
```
