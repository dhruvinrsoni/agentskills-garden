---
name: code-review
description: >
  Perform structured code reviews with checklists, PR feedback, defect
  categorization, and severity classification.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: 1.0.0
  dependencies: "constitution, scratchpad, test-strategy"
  reasoning_mode: plan-execute
---


# Code Review

> _"Code review is not about finding faults — it's about raising the floor."_

## Context

Invoked when a pull request is opened, when code changes need peer review
before merge, or when a post-merge audit is requested. Ensures code quality,
consistency, and knowledge sharing across the team.

---

## Micro-Skills

### 1. PR Readiness Check 🌿 (Eco Mode)

**Steps:**

1. Verify the PR has a clear title and description explaining **what** and **why**.
2. Check that the changeset is appropriately sized (< 400 lines preferred).
3. Confirm linked issue/ticket exists.
4. Verify CI pipeline passes (tests, lint, build).

### 2. Structural Review ⚡ (Power Mode)

**Steps:**

1. Walk the diff file-by-file, checking:
   - **Naming:** Variables, functions, classes follow project conventions.
   - **Single Responsibility:** Each function/class does one thing well.
   - **DRY:** No copy-paste duplication; extract shared logic.
   - **Error Handling:** All error paths covered, no swallowed exceptions.
   - **Logging:** Adequate observability without leaking sensitive data.
2. Classify each finding by defect category:
   - 🐛 **Bug** — Incorrect behavior.
   - ⚠️ **Risk** — Works now but fragile under change.
   - 📐 **Design** — Structural improvement opportunity.
   - 🧹 **Style** — Formatting, naming, conventions.
   - 📝 **Docs** — Missing or stale documentation/comments.
3. Assign severity to each finding:
   - **Critical** — Must fix before merge (bugs, security, data loss).
   - **Major** — Should fix before merge (design flaws, missing tests).
   - **Minor** — Nice to fix (style, readability).
   - **Nit** — Optional suggestion (preference, micro-optimization).

### 3. Feedback Composition 🌿 (Eco Mode)

**Steps:**

1. Write actionable, respectful comments:
   - Lead with **what** is wrong and **why** it matters.
   - Suggest a concrete fix or alternative.
   - Use "Consider…" or "What about…" for subjective suggestions.
2. Group related comments into a single review thread.
3. Summarize the review with an overall verdict:
   - ✅ **Approve** — No blockers.
   - 🔄 **Request Changes** — Blocking issues listed.
   - 💬 **Comment** — Non-blocking observations only.

---

## Inputs

| Parameter       | Type       | Required | Description                              |
|-----------------|------------|----------|------------------------------------------|
| `pr_diff`       | `string`   | yes      | The unified diff or changeset to review  |
| `pr_description`| `string`   | no       | PR title and description for context     |
| `language`      | `string`   | no       | Primary language of the changeset        |
| `checklist`     | `string[]` | no       | Custom review checklist items            |

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `findings`       | `object[]` | List of findings with category & severity|
| `verdict`        | `string`   | Approve, Request Changes, or Comment     |
| `summary`        | `string`   | Human-readable review summary            |

---

## Edge Cases

- PR is too large (> 1000 lines) — Recommend splitting into smaller PRs
  before reviewing; flag as a process issue.
- Generated code in diff (protobuf, OpenAPI stubs) — Skip generated files,
  review only the source definitions.
- Merge conflict markers present — Reject review until conflicts resolved.

---

## Scope

### In Scope

- Reviewing application source code diffs for correctness, style, and design
- Classifying defects by category (Bug, Risk, Design, Style, Docs) and severity (Critical, Major, Minor, Nit)
- Providing actionable PR feedback with concrete suggestions
- Validating PR metadata (description, linked issues, size)
- Checking adherence to project coding conventions and patterns
- Reviewing test coverage adequacy for changed code

### Out of Scope

- Executing or running tests (delegate to `unit-testing` / `integration-testing`)
- Modifying code directly — review is advisory only
- Security vulnerability scanning (delegate to `security-review`)
- Performance benchmarking (delegate to `performance-review`)
- Reviewing infrastructure-as-code or CI pipeline definitions
- Resolving merge conflicts on behalf of the author

---

## Guardrails

- Never approve a PR with known Critical-severity findings unresolved.
- Do not review generated, vendored, or third-party code unless explicitly requested.
- Limit nit-level comments to ≤ 3 per review to avoid noise.
- Always separate blocking issues from suggestions in the review summary.
- Do not rewrite the author's code wholesale — suggest targeted improvements.
- Respect existing project style even if it differs from personal preference.
- Flag but do not auto-dismiss findings in test files — test quality matters.

## Ask-When-Ambiguous

### Triggers

- PR description is missing or unclear about intent
- Changeset modifies both production and test code with unclear relationship
- Custom coding standards are referenced but not provided
- Diff includes unfamiliar domain logic requiring business context
- Multiple architectural patterns are used inconsistently across the changeset

### Question Templates

1. "This PR lacks a description. Can you summarize the intent and expected behavior change?"
2. "The changeset modifies {{file_count}} files across {{module_count}} modules. Should I review all modules or focus on a specific area?"
3. "I see conflicting patterns for error handling ({{pattern_a}} vs {{pattern_b}}). Which is the project standard?"
4. "This logic in `{{function_name}}` involves domain rules I can't verify. Can you confirm the expected behavior for {{edge_case}}?"
5. "Should generated files ({{file_list}}) be included in this review?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| PR has no linked issue or description | Request author to add context before starting review |
| PR exceeds 500 changed lines | Recommend splitting; review only if author confirms it's atomic |
| Finding is subjective (style preference) | Mark as Nit; do not block merge |
| Finding reveals a pre-existing bug not introduced by this PR | Log as a separate issue; do not block this PR |
| Test coverage for changed lines is < 60% | Classify as Major finding; request additional tests |
| Same defect pattern repeats 3+ times in the diff | Comment once with a general note instead of repeating on each instance |
| Author pushes back on a finding with valid reasoning | Accept and resolve; document the rationale |

## Success Criteria

- [ ] All Critical and Major findings are addressed or explicitly deferred with justification
- [ ] Review comments are actionable — each includes a **what**, **why**, and **suggestion**
- [ ] Defect categories and severities are assigned consistently
- [ ] Review summary accurately reflects the overall state of the changeset
- [ ] No generated or vendored files were reviewed unless requested
- [ ] Review completed within one pass (no repeated re-reviews for the same issues)
- [ ] Author can understand and act on feedback without follow-up clarification

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Rubber-stamp approval | Critical bugs merge to main | Enforce structured checklist; require at least one finding or explicit "no issues found" statement |
| Nitpick overload | Author ignores all feedback due to volume | Cap nits at 3; focus on Critical/Major findings first |
| Missing context | Reviewer misunderstands intent, flags false positives | Always read PR description and linked issue before reviewing code |
| Inconsistent severity | Same defect classified differently across reviews | Use the defect category and severity rubric defined in Micro-Skill 2 |
| Stale review | Review comments reference outdated code after force-push | Re-validate findings against the latest diff before submitting |
| Review scope creep | Reviewer flags pre-existing issues unrelated to the PR | Log pre-existing issues separately; keep review scoped to the changeset |

## Audit Log

- `[{{timestamp}}] review-started: PR #{{pr_number}} — {{file_count}} files, {{line_count}} changed lines`
- `[{{timestamp}}] finding-logged: {{category}}/{{severity}} in {{file_path}}:{{line}} — {{summary}}`
- `[{{timestamp}}] verdict-issued: {{verdict}} — {{critical_count}} critical, {{major_count}} major, {{minor_count}} minor, {{nit_count}} nit`
- `[{{timestamp}}] review-completed: duration={{duration_minutes}}min, findings={{total_findings}}`