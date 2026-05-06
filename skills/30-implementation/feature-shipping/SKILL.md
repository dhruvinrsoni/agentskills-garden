---
name: feature-shipping
description: >
  Master workflow for shipping a feature end-to-end. Orchestrates PRD
  authoring, task decomposition, TDD implementation, code review, and
  the release pipeline as a single named sequence ending in an audit.
  Contains no implementation logic.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "0.1.0"
  dependencies: "constitution, scratchpad, pragya, librarian, auditor"
  reasoning_mode: plan-execute
  skill_type: master
---

# Feature Shipping — Master Workflow

> _"Spec it. Slice it. Test-drive it. Review it. Ship it. Audit the trail."_

## Context

Invoked when the user asks to "ship a feature" end-to-end — from idea to
released artefact — and wants the canonical, repeatable shape rather than
ad-hoc step ordering. Composes one master from another (`release-pipeline`
is invoked as the final delivery sub-workflow).

## Scope

**In scope:**

- Sequencing the five orchestration steps and the closing audit.
- Forwarding outputs of each step into the next.
- Pausing for `pragya` checkpoints when scope or design ambiguity arises.

**Out of scope:**

- The PRD format selection (delegated to `prd`).
- The decomposition heuristics (delegated to `task-decomposition`).
- Red-green-refactor mechanics (delegated to `tdd-workflow`).
- Review checklists (delegated to `code-review`).
- Test plan, changelog, and CI execution (delegated to `release-pipeline`, which is itself a master).

---

## Micro-Skills (orchestration steps)

### 1. Author PRD
**Mode:** power
**Invokes:** `prd`
**Inputs:** `feature_intent`, `audience`, `constraints`
**Outputs:** `prd_doc`, `acceptance_criteria`, `success_metrics`
**Steps:**
1. Load `prd` via the librarian.
2. Pass `feature_intent` and any user-supplied background.
3. Collect `prd_doc`, `acceptance_criteria`, `success_metrics`.
4. If acceptance criteria conflict with constraints → route to `pragya` for resolution before proceeding.

### 2. Decompose Work
**Mode:** power
**Invokes:** `task-decomposition`
**Inputs:** `prd_doc`, `acceptance_criteria`
**Outputs:** `task_dag` (dependency-ordered subtasks with sizing)
**Steps:**
1. Load `task-decomposition`.
2. Pass `prd_doc` and `acceptance_criteria`.
3. Collect `task_dag`.

### 3. Implement Test-First
**Mode:** power
**Invokes:** `tdd-workflow` (per task in the DAG)
**Inputs:** `task_dag`, repository context
**Outputs:** `implementation_diff`, `test_suite`, `coverage_summary`
**Steps:**
1. For each task in `task_dag` (respecting dependencies), load `tdd-workflow` and run the red-green-refactor cycle.
2. Aggregate the per-task diffs into `implementation_diff`.
3. Aggregate the per-task tests into `test_suite`.
4. Collect overall `coverage_summary`.

### 4. Code Review
**Mode:** power
**Invokes:** `code-review` (or `pr-review-flow` master if a thorough multi-lens review is required)
**Inputs:** `implementation_diff`, `acceptance_criteria` (as the review's intent reference)
**Outputs:** `review_report`, `decision` (`approve` | `request-changes` | `block`)
**Steps:**
1. Load `code-review` (default) or escalate to `pr-review-flow` for high-risk features.
2. Pass `implementation_diff` and the acceptance criteria.
3. If `decision == request-changes` → loop back to step 3 with the requested changes; cap at 2 review rounds before escalating to `pragya`.

### 5. Release
**Mode:** power
**Invokes:** `release-pipeline`
**Inputs:** approved `implementation_diff`, `test_suite`, `coverage_summary`
**Outputs:** `release_artefact`, `version`, `changelog_entry`
**Steps:**
1. Load `release-pipeline` (itself a master).
2. Pass the approved diff and tests.
3. Collect the release artefact and version.

### 6. Audit
**Mode:** power
**Invokes:** `auditor`
**Inputs:** scratchpad plan, all step outputs
**Outputs:** `compliant`, `violations`, `blocked`
**Steps:**
1. Load `auditor`.
2. Verify the chain: PRD ↔ tasks ↔ diff ↔ tests ↔ release artefact all trace consistently and acceptance criteria are covered by tests.
3. Block delivery on any violation.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `feature_intent` | `string` | yes | Plain-language feature description. |
| `audience` | `string` | no | Who the feature is for (drives PRD format). |
| `constraints` | `object` | no | Hard constraints: deadline, scope cap, must-have integrations. |
| `review_mode` | `enum` | no | `code-review` (default) or `pr-review-flow` for thorough multi-lens. |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `prd_doc` | `string` | The authored PRD. |
| `task_dag` | `object` | Decomposed tasks with sizes and dependencies. |
| `implementation_diff` | `string` | Aggregated diff across all tasks. |
| `test_suite` | `object` | New/updated tests with coverage data. |
| `release_artefact` | `string` | Path to the built artefact. |
| `version` | `string` | Semver string. |
| `compliant` | `boolean` | Whether the auditor passed. |

---

## Guardrails

- Step 3 cannot start before step 2 produces a non-empty `task_dag`.
- Review-rework loops (step 4 ↔ step 3) cap at 2 rounds; further rounds require `pragya` escalation.
- The release step delegates to a master, not to `ci-pipeline` directly — composing masters is intentional.
- The auditor MUST verify every acceptance criterion has at least one corresponding test in `test_suite`.

## Decision Criteria

| Situation | Action |
|-----------|--------|
| PRD acceptance criteria are unmeasurable | `prd` raises an Ask-When-Ambiguous; chain pauses. |
| `task_dag` has cycles | `task-decomposition` flags; route to `pragya`. |
| Coverage below project threshold after step 3 | Loop back into `tdd-workflow` for the under-covered tasks before review. |
| `pr-review-flow` returns `block` at step 4 | Abort feature shipping; surface to user with the aggregated findings. |

## Success Criteria

- Every acceptance criterion has tests; every test passes.
- `decision` from review is `approve`.
- `release_artefact` exists and the auditor returns `compliant == true`.
- Audit log shows every step including any review-rework loops.

## Audit Log

```
[feature-shipping-started] intent="{feature_intent}"
[step-completed]           step={1..5} skill={invoked} outcome={summary}
[review-loop]              iteration={N} requested_changes={count}
[escalation]               step={N} target=pragya reason="{trigger}"
[feature-shipping-completed] version={version} compliant={bool}
```
