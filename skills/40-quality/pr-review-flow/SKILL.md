---
name: pr-review-flow
description: >
  Master workflow for a thorough PR review. Orchestrates code review,
  security review, and performance review in parallel, then routes the
  findings into PR management for triage and merge decisioning. No
  implementation logic.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "0.1.0"
  dependencies: "constitution, scratchpad, pragya, librarian, auditor"
  reasoning_mode: plan-execute
  skill_type: master
---

# PR Review Flow — Master Workflow

> _"Three lenses in parallel. One verdict at the end. Nothing slips through because everyone assumed someone else looked."_

## Context

Invoked when the user asks for a comprehensive PR review or when a PR
has been opened against a protected branch. Freezes the canonical review
sequence so every PR receives the same three-lens treatment regardless of
who routed it.

## Scope

**In scope:**

- Running `code-review`, `security-review`, and `performance-review` in parallel.
- Aggregating their findings under a single PR-management decision step.
- Closing with an audit so the orchestration itself is verifiable.

**Out of scope:**

- Authoring the actual code-review checklist (delegated to `code-review`).
- OWASP scanning logic (delegated to `security-review`).
- Bottleneck detection (delegated to `performance-review`).
- Merging the PR (delegated to `pr-management` based on the verdict).

---

## Micro-Skills (orchestration steps)

### 1. Static Quality Gates (parallel)
**Mode:** power
**Invokes:** `code-review`, `security-review`, `performance-review`
**Inputs:** `pr_diff`, `pr_metadata` (target branch, author, labels)
**Outputs:** `code_review.report`, `security_review.report`, `performance_review.report`
**Steps:**
1. Load all three skills in parallel via the librarian.
2. Pass `pr_diff` and `pr_metadata` to each.
3. Collect each report under its namespaced output field.

### 2. Aggregate Findings
**Mode:** eco
**Invokes:** `pragya`
**Inputs:** all three reports from step 1
**Outputs:** `aggregated_findings`, `decision` (`approve` | `request-changes` | `block`)
**Steps:**
1. Load `pragya`.
2. Combine findings into a single ordered list, severity-first.
3. If any finding is `safety-critical` or `irreversible` → `decision = block`.
4. If any finding is non-trivial but recoverable → `decision = request-changes` and present the list to the user as a checkpoint.
5. If all findings are advisory → `decision = approve`.

### 3. Apply PR Management
**Mode:** eco
**Invokes:** `pr-management`
**Inputs:** `aggregated_findings`, `decision`
**Outputs:** `pr_action` (`approved`, `comment-posted`, `blocked-and-labelled`)
**Steps:**
1. Load `pr-management`.
2. Apply the action matching `decision`: post the aggregated comment, set labels, request reviewers, or merge if approved and policy allows.
3. Collect `pr_action`.

### 4. Audit
**Mode:** power
**Invokes:** `auditor`
**Inputs:** scratchpad plan, all three reports, `decision`, `pr_action`
**Outputs:** `compliant`, `violations`, `blocked`
**Steps:**
1. Load `auditor`.
2. Verify all three review skills produced a report (none was silently skipped), the decision matches the severity of findings, and the pr-management action matches the decision.
3. Block delivery on any violation.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pr_diff` | `string` | yes | Unified diff of the PR. |
| `pr_metadata` | `object` | yes | Target branch, author, labels, base SHA. |
| `policy` | `object` | no | Org-specific policy: required reviewers, auto-merge rules. |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `code_review.report` | `object` | Defect categories, severity, line refs. |
| `security_review.report` | `object` | OWASP findings, severity, recommendations. |
| `performance_review.report` | `object` | Hotspots, complexity flags, caching review. |
| `decision` | `string` | `approve` \| `request-changes` \| `block`. |
| `pr_action` | `string` | What was applied to the PR. |
| `compliant` | `boolean` | Whether the auditor passed. |

---

## Guardrails

- The three review skills MUST run in parallel; running them sequentially is a workflow violation (slows the chain without adding value).
- A `block` decision is final for this run; only the user (via `pragya`) can downgrade it.
- The `pr-management` step never auto-merges unless `policy.auto_merge_allowed == true` AND the decision is `approve`.
- The auditor MUST verify every named report is present; missing a lens (e.g. security) is a hard fail.

## Decision Criteria

| Finding profile | Decision |
|-----------------|----------|
| Any safety-critical / irreversible defect | `block` |
| Multiple non-trivial defects across lenses | `request-changes` |
| Single non-trivial defect | `request-changes` |
| Only advisory comments | `approve` |
| No findings at all | `approve` |

## Success Criteria

- Three parallel reports collected, each with a clear severity tally.
- `decision` reflects the worst finding's severity.
- `pr_action` matches `decision`.
- Audit log shows all four orchestration steps.

## Audit Log

```
[pr-review-started]   pr={id} diff_size={N}
[parallel-batch]      skills=[code-review, security-review, performance-review] mode=parallel
[step-completed]      step={N} skill={invoked} severity_summary={summary}
[decision-made]       decision={approve|request-changes|block} rationale="{summary}"
[pr-review-completed] pr_action={action} compliant={bool}
```
