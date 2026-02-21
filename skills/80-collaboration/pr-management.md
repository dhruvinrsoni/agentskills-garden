````markdown
---
name: pr-management
description: >
  Manage pull request lifecycle including templates, reviewer assignment,
  merge criteria, and stale PR handling for efficient code integration.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - code-review
reasoning_mode: plan-execute
---

# PR Management

> _"A well-managed PR process is the heartbeat of a shipping team."_

## Context

Invoked when establishing or improving the pull request workflow — from PR
creation templates to reviewer assignment policies, merge readiness checklists,
and stale PR triage. Ensures PRs flow through review and merge efficiently
without sacrificing quality or accountability.

---

## Micro-Skills

### 1. PR Template Design ⚡ (Power Mode)

**Steps:**

1. Create `.github/PULL_REQUEST_TEMPLATE.md` (or platform equivalent).
2. Include sections:
   - **Summary** — What and why (link to issue/ticket).
   - **Type of Change** — Feature, bugfix, refactor, docs, chore.
   - **Testing** — How changes were verified.
   - **Checklist** — Pre-merge items (tests pass, docs updated, no secrets).
   - **Screenshots/Recordings** — For UI changes.
3. Add optional sub-templates for specific PR types (`bug_fix.md`, `feature.md`).

### 2. Reviewer Assignment 🌿 (Eco Mode)

**Steps:**

1. Configure CODEOWNERS file mapping paths to responsible teams/individuals.
2. Set review policies:
   - Minimum 1 approval for standard PRs.
   - Minimum 2 approvals for changes touching `main`, infrastructure, or auth.
3. Implement round-robin or load-balanced assignment to avoid bottlenecks.
4. Auto-assign reviewers based on file ownership and recent activity.

### 3. Merge Criteria Enforcement ⚡ (Power Mode)

**Steps:**

1. Define merge readiness checklist:
   - All CI checks pass (lint, test, build, security scan).
   - Required number of approvals received.
   - No unresolved review threads.
   - Branch is up-to-date with target (no stale merges).
   - PR description and linked issue are complete.
2. Configure branch protection rules to enforce criteria.
3. Enable auto-merge for PRs that meet all criteria (optional).

### 4. Stale PR Triage 🌿 (Eco Mode)

**Steps:**

1. Define staleness threshold (e.g., no activity for 14 days).
2. Configure automated reminders:
   - Day 7: Friendly nudge to author and reviewers.
   - Day 14: Label as `stale`; ping team lead.
   - Day 21: Auto-close with comment explaining reopen process.
3. Exclude PRs labeled `wip`, `blocked`, or `on-hold` from staleness checks.
4. Generate weekly stale PR report for team standups.

---

## Inputs

| Parameter          | Type       | Required | Description                                      |
|--------------------|------------|----------|--------------------------------------------------|
| `repo_url`         | `string`   | yes      | Repository to configure PR management for        |
| `team_members`     | `string[]` | no       | List of team members for reviewer assignment      |
| `platform`         | `string`   | no       | GitHub, GitLab, Bitbucket, or Azure DevOps       |
| `merge_strategy`   | `string`   | no       | Default merge method (squash, merge, rebase)     |

## Outputs

| Field               | Type       | Description                                      |
|---------------------|------------|--------------------------------------------------|
| `pr_template`       | `string`   | Generated PR template content                    |
| `codeowners`        | `string`   | CODEOWNERS file content                          |
| `branch_rules`      | `object`   | Branch protection configuration                  |
| `stale_config`      | `object`   | Stale PR bot configuration                       |

---

## Edge Cases

- PR author is also the only available reviewer — Require at least one external reviewer; escalate to team lead.
- PR spans multiple CODEOWNERS areas — Require approval from each owning team.
- Draft PR receives review comments — Allow comments but do not count toward approval requirements.
- PR targets a release branch during code freeze — Require additional approval from release manager.

---

## Scope

### In Scope

- Designing and maintaining PR templates for consistent submission quality
- Configuring CODEOWNERS and automated reviewer assignment policies
- Defining and enforcing merge readiness criteria via branch protection rules
- Stale PR detection, notification, and automated lifecycle management
- PR labeling strategies (type, priority, size, status)
- Merge queue configuration and auto-merge policies
- PR metrics tracking (time-to-review, time-to-merge, review rounds)
- Draft PR workflows and "ready for review" transition policies

### Out of Scope

- Code review content and defect classification (handled by `code-review`)
- CI/CD pipeline configuration (handled by `ci-pipeline`)
- Git branching strategy and commit conventions (handled by `git-workflow`)
- Repository hosting platform administration
- Issue/ticket management and backlog grooming
- Deployment decisions triggered by PR merges

---

## Guardrails

- Never allow merging a PR with failing required CI checks, regardless of approval count.
- Do not auto-close PRs labeled `blocked` or `on-hold` via stale PR automation.
- CODEOWNERS changes must themselves be reviewed by a repository admin or lead.
- PR templates must not include sensitive information patterns (API keys, tokens) even as examples.
- Never bypass the minimum approval requirement except for documented emergency hotfix procedures.
- Ensure merge queue does not silently drop PRs — failed queue entries must notify the author.
- Do not assign reviewers who are listed as the PR author or co-author.

## Ask-When-Ambiguous

### Triggers

- Repository has no PR template and team size is unknown
- Multiple merge strategies are used inconsistently across the repository
- CODEOWNERS file exists but is outdated or has unresolvable owners
- Stale PR threshold is not defined and backlog size is unclear
- Team uses multiple platforms (e.g., GitHub for code, Jira for tracking) with unclear linking

### Question Templates

1. "How many reviewers should be required for standard PRs vs critical-path PRs (auth, infra, data migrations)?"
2. "What is your preferred stale PR threshold — 7, 14, or 21 days of inactivity?"
3. "Should auto-merge be enabled for PRs that pass all checks and have required approvals?"
4. "Do you use CODEOWNERS today, or should we generate one from recent commit history?"
5. "Are there specific PR label categories the team uses (e.g., `size/S`, `priority/high`, `type/bugfix`)?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Team has no PR template | Generate a standard template with Summary, Type, Testing, and Checklist sections |
| PR has been open > 14 days with no review | Send reminder to assigned reviewers; escalate to team lead after 7 more days |
| PR has been open > 21 days with no activity | Auto-close with reopen instructions unless labeled `blocked` or `wip` |
| PR touches CODEOWNERS-mapped paths | Auto-assign reviewers from matching CODEOWNERS entries |
| PR has 1000+ changed lines | Flag as oversized; recommend splitting before review |
| All CI checks pass and required approvals are met | Allow merge (or auto-merge if enabled) |
| PR targets `main` during release freeze | Require release manager approval in addition to standard reviewers |
| Reviewer has not responded in 48 hours | Re-assign or add additional reviewer to unblock |
| PR has merge conflicts with target branch | Block merge; notify author to resolve conflicts and update branch |

## Success Criteria

- [ ] Every repository has a PR template that is used consistently by contributors
- [ ] CODEOWNERS file is current and covers ≥ 80% of the codebase
- [ ] Branch protection enforces CI passage and minimum approvals before merge
- [ ] Average time-to-first-review is ≤ 24 hours for standard PRs
- [ ] Stale PR count (> 14 days inactive) is ≤ 5 at any given time
- [ ] No PRs are merged with unresolved blocking review threads
- [ ] PR labels are applied consistently for type, size, and status
- [ ] Merge queue processes PRs without silent failures

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Review bottleneck | PRs wait > 48 hours for first review; developers context-switch away | Implement round-robin assignment; set SLA alerts for unreviewed PRs |
| Rubber-stamp approvals | Reviewers approve without reading; defects reach main | Require review checklist completion; track approval-to-comment ratio |
| Stale PR accumulation | Repository has 20+ open PRs older than 30 days | Enable stale bot; surface stale PR count in team standups |
| CODEOWNERS drift | Assigned reviewers no longer work on the codebase | Schedule quarterly CODEOWNERS audit; flag reviews with unknown owners |
| Merge conflict spiral | Target branch moves fast; PRs constantly fall behind | Require branches to be up-to-date before merge; use merge queue |
| Auto-merge surprise | PR merges before author intended (e.g., during testing) | Require explicit opt-in label like `auto-merge`; disable for draft PRs |
| Template fatigue | Contributors skip template sections or fill with boilerplate | Keep templates concise; make only critical sections required |

## Audit Log

- `[timestamp]` pr-template-created: Generated PR template at `<file-path>` with sections `<section-list>`
- `[timestamp]` codeowners-updated: Modified CODEOWNERS — added `<path-pattern>` → `<owners>`
- `[timestamp]` branch-protection-set: Protected `<branch>` requiring `<review-count>` approvals and `<check-list>` checks
- `[timestamp]` stale-pr-notified: PR #`<pr-number>` inactive for `<days>` days — sent reminder to `<assignees>`
- `[timestamp]` stale-pr-closed: PR #`<pr-number>` auto-closed after `<days>` days of inactivity
- `[timestamp]` reviewer-assigned: Assigned `<reviewer>` to PR #`<pr-number>` via `<method>` (CODEOWNERS/round-robin/manual)
- `[timestamp]` merge-criteria-met: PR #`<pr-number>` passed all checks — `<merge-method>` merge executed

````
