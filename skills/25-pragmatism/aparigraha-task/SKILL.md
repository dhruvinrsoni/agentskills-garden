---
name: aparigraha-task
description: >
  Master workflow for any change touching an existing project. Walks the
  Aparigraha gates end-to-end — onboarding, dependency awareness, style
  detection, reuse-first authoring, surgical diff, post-execution audit —
  by orchestrating the foundation `pragmatism` philosophy and the
  `25-pragmatism` category skills. Contains no implementation logic.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "0.1.0"
  dependencies: "constitution, scratchpad, pragmatism, pragya, librarian, auditor"
  reasoning_mode: plan-execute
  skill_type: master
---

# Aparigraha Task — Master Workflow

> _"Onboard once. Check before you create. Conform within scope. Stay surgical. Verify every reuse. Audit every diff."_

## Context

Invoked when the agent is asked to make any change to an unfamiliar or ongoing project — bug fix, small feature, utility addition, refactor — and the
[`pragmatism`](../../00-foundation/pragmatism/SKILL.md) foundation skill flags
the task as Aparigraha-relevant (i.e., touching existing code or adding new
capability that may already exist).

This master freezes the canonical Aparigraha workflow into a single named
sequence so it is reproducible across tasks.

## Scope

**In scope:**

- Sequencing the six steps of the Aparigraha workflow.
- Forwarding outputs of each step into the next.
- Routing into `pragya` checkpoints when a step asks for direction.
- Final audit before returning the change to the user.

**Out of scope:**

- The actual codebase scan (delegated to `reuse-first`).
- The actual dependency mining (delegated to `dependency-utility-scout`).
- The actual style detection (delegated to `style-conformance`).
- The actual edit production (the implementing skill of the user's task).

---

## Micro-Skills (orchestration steps)

### 1. Onboard
**Mode:** eco
**Invokes:** `brownfield-onboarding`
**Inputs:** `repo_root`
**Outputs:** `onboarding_cheatsheet` (build/test/CI commands, hot zones, entry points, test layout)
**Steps:**
1. Load `brownfield-onboarding` via the librarian.
2. Pass `repo_root` and any user-supplied project hints.
3. Collect `onboarding_cheatsheet` and forward to every later step.

### 2. Inventory Dependencies
**Mode:** eco
**Invokes:** `dependency-utility-scout`
**Inputs:** `repo_root`, `onboarding_cheatsheet.manifests`
**Outputs:** `utility_inventory` (per-capability map of what is already available)
**Steps:**
1. Load `dependency-utility-scout`.
2. Pass the discovered manifests.
3. Collect `utility_inventory`.

### 3. Detect House Style
**Mode:** eco
**Invokes:** `style-conformance`
**Inputs:** `repo_root`, `target_files` (best guess from user request)
**Outputs:** `style_profile` (naming, formatting, errors, logging, tests, comments)
**Steps:**
1. Load `style-conformance`.
2. Pass `repo_root` and `target_files`.
3. Collect `style_profile`.

### 4. Decide Reuse vs Author
**Mode:** power
**Invokes:** `reuse-first`
**Inputs:** `task_intent`, `utility_inventory` (from step 2), `style_profile` (from step 3)
**Outputs:** `reuse_decision` (one of `reuse`, `reuse-with-guards`, `author-fresh`), `edge_case_report`
**Steps:**
1. Load `reuse-first`.
2. Pass `task_intent` and the inventory + style context.
3. Collect `reuse_decision` and the populated edge-case checklist.
4. If any checklist row is unconfirmed, route into `pragya` for a direction checkpoint instead of proceeding silently.

### 5. Apply Surgical Diff
**Mode:** power
**Invokes:** `minimal-diff` (then the user-task implementation skill chosen by step 4)
**Inputs:** `reuse_decision`, `style_profile`, `task_intent`
**Outputs:** `diff`, `out_of_scope_suggestions`
**Steps:**
1. Load `minimal-diff` to set the diff-size cap and reversibility checks for the change.
2. Implement the change via the skill chosen in step 4 (e.g. `code-generation`, `refactoring`, `api-implementation`) — that skill produces the actual diff.
3. Collect `diff`. Any tangential improvement noticed during implementation is recorded in `out_of_scope_suggestions`, never inlined.

### 6. Audit
**Mode:** power
**Invokes:** `auditor`
**Inputs:** scratchpad plan, `diff` from step 5, `edge_case_report` from step 4
**Outputs:** `compliant`, `violations`, `blocked`
**Steps:**
1. Load `auditor` with the original plan and the full diff.
2. Verify plan-vs-diff alignment, the four pillars, no protected term modified, and Aparigraha gates 1-4 each have a logged outcome.
3. Block delivery on any violation; surface to the user via `pragya`.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_intent` | `string` | yes | The user's stated goal in plain language. |
| `repo_root` | `string` | yes | Path to the project being changed. |
| `target_files` | `string[]` | no | Files the task is expected to touch (best guess). |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `diff` | `string` | The unified diff produced by step 5. |
| `reuse_decision` | `string` | The chosen path: `reuse`, `reuse-with-guards`, or `author-fresh`. |
| `edge_case_report` | `object` | Per-row status of the Validate-Before-Trust checklist. |
| `out_of_scope_suggestions` | `string[]` | Tangential improvements deferred for follow-up. |
| `compliant` | `boolean` | Whether the auditor passed. |

---

## Guardrails

- Steps 1-3 may run in parallel only if their outputs are independent for this project; default to sequential to keep the audit log linear.
- No step may skip its named invocation; "I already know the answer" is not grounds to bypass a gate.
- The final `auditor` step is mandatory; if it does not run, the workflow result is not delivered.
- If any gate triggers an Ask-When-Ambiguous in its underlying skill, the master pauses the chain for `pragya` to handle, then resumes from the same step.

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Greenfield, single file, no dependencies | Skip steps 1-2, run 3-6 only. |
| User requests a sweeping refactor explicitly | Master still runs; `minimal-diff` widens its caps based on user-set scope. |
| Reuse decision returns `author-fresh` | Step 5's implementation skill is chosen by the task type (e.g. `api-implementation`, `code-generation`). |
| Auditor flags a violation | Block delivery; route to `pragya` with the violation as input. |

## Success Criteria

- Every gate has a logged outcome (covered, N/A with reason, or escalated).
- Diff is reversible in one `git revert`.
- No protected term modified without approval.
- `out_of_scope_suggestions` is delivered alongside the diff so nothing valuable is silently dropped.

## Audit Log

```
[aparigraha-task-started] intent="{task_intent}" repo="{repo_root}"
[step-completed]          step={1..6} skill={invoked} outcome={summary}
[checkpoint-paused]       step={N} reason="{ask-when-ambiguous trigger}"
[aparigraha-task-completed] compliant={bool} suggestions={N} diff_files={N}
```
