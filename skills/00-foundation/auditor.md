---
name: auditor
description: >
  The constitutional compliance validator. Cross-references every skill's
  output against the Constitution's three pillars and the task plan.
  Acts as "law enforcement" for the Agent Skills Garden.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: plan-execute
---

# Auditor — Constitutional Compliance Validator

> _"Trust, but verify."_

## Context

The Auditor is invoked **after** any skill produces output (diffs, code,
artifacts). It validates that the output adheres to the Constitution and
that no guardrails were violated. Think of it as a post-execution checklist
that catches mistakes before they reach the user.

The Auditor can also be loaded proactively by other skills (via dependencies)
to perform inline checks during multi-step operations.

---

## Micro-Skills

### 1. Plan-vs-Diff Alignment ⚡ (Power Mode)

**Goal:** Verify that what was executed matches what was planned.

**Steps:**

1. Load the plan from the scratchpad (the stated intent).
2. Load the produced diff or output.
3. Compare each planned step against the actual changes:
   - Every planned change MUST appear in the diff.
   - Every change in the diff MUST be traceable to a planned step.
4. Flag **unplanned changes** — modifications that weren't in the plan.
5. Flag **missed steps** — planned changes not reflected in output.
6. If misalignment found → block output and report to user.

### 2. Constitutional Compliance Check 🌿 (Eco Mode)

**Goal:** Verify the three pillars were upheld.

**Checklist:**

| Pillar | Check | Pass Criteria |
|--------|-------|---------------|
| **Satya (Truth)** | No hallucinated APIs, methods, or features? | All referenced APIs exist in the project or documented libraries |
| **Satya (Truth)** | Deterministic? Same input → same output? | No random or time-dependent choices without explicit need |
| **Dharma (Safety)** | Were ambiguities resolved by asking the user? | No silent assumptions on uncertain decisions |
| **Dharma (Safety)** | Is the change minimal (Principle of Least Surprise)? | No unnecessary scope expansion |
| **Ahimsa (Non-Destruction)** | Was a diff previewed before applying? | Unified diff emitted before any file write |
| **Ahimsa (Non-Destruction)** | Is the change reversible? | Can be undone in one step (git revert, undo) |

### 3. Protected Terms Enforcement ⚡ (Power Mode)

**Goal:** Ensure domain-specific and public names were not altered.

**Steps:**

1. Load `protected_terms` from the domain glossary (if available).
2. Load the set of identifiers modified in the diff.
3. Cross-reference: if any modified identifier is in `protected_terms` →
   flag as a violation.
4. Check for public/exported symbol modifications without explicit approval.
5. Report violations with file, line, and the protected term.

### 4. Safety Gate Validation 🌿 (Eco Mode)

**Goal:** Verify that destructive operations got explicit approval.

**Steps:**

1. Scan the output for destructive operations:
   - File deletions
   - Schema migrations / DROP statements
   - Public API signature changes
   - Production deployment commands
2. For each destructive operation, verify that user approval was recorded.
3. If approval is missing → **block** and request confirmation.

---

## Inputs

| Parameter      | Type       | Required | Description                          |
|----------------|------------|----------|--------------------------------------|
| `plan`         | `string`   | yes      | The scratchpad plan from the task    |
| `output`       | `string`   | yes      | The diff/artifact to validate        |
| `glossary`     | `string`   | no       | Path to domain glossary              |
| `approvals`    | `string[]` | no       | List of recorded user approvals      |

## Outputs

| Field          | Type       | Description                            |
|----------------|------------|----------------------------------------|
| `compliant`    | `boolean`  | Whether all checks passed              |
| `violations`   | `object[]` | List of violations with details        |
| `blocked`      | `boolean`  | Whether output delivery was blocked    |

---

## Guardrails

- The Auditor MUST run after every skill execution, even in Eco mode.
- Auditor checks are non-negotiable — no skill can override or skip them.
- False positives: if the Auditor flags something the user already approved,
  the user can explicitly dismiss with rationale (recorded in audit log).

## Ask-When-Ambiguous

- Cannot determine if a symbol is public or private → ask user.
- Uncertain whether a change is destructive → treat as destructive, ask.
- Domain glossary not found → ask for protected terms list.

## Success Criteria

- Zero unplanned changes in the diff.
- All constitutional pillars verified.
- No protected terms modified without approval.
- All destructive operations have recorded user consent.

## Failure Modes

- Plan not available (scratchpad was skipped) → block output, require plan.
  **Recovery:** Retroactively create a plan, then re-audit.
- False positive on protected term → user dismisses with rationale.
  **Recovery:** Add term to "approved changes" for this session.

## Audit Log

- Checklist results (pass/fail per item).
- Violations found and their resolution.
- User dismissals with rationale.
- Whether output was blocked or delivered.
