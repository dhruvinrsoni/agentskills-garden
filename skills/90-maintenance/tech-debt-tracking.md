````markdown
---
name: tech-debt-tracking
description: >
  Categorize, score, and prioritize technical debt with impact analysis,
  payoff estimation, and debt budget management.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: plan-execute
---

# Tech Debt Tracking

> _"Debt you can see is debt you can pay down."_

## Context

Invoked when technical debt needs to be identified, categorized, and
prioritized for remediation. Provides a systematic approach to making
debt visible, scoring its impact, and fitting payoff work into sprint
capacity through debt budgets.

---

## Micro-Skills

### 1. Debt Discovery 🌱 (Eco Mode)

**Steps:**

1. Scan for common debt indicators:
   - `TODO`, `FIXME`, `HACK`, `XXX` comments in source code.
   - Suppressed linter warnings and disabled rules.
   - Duplicated code blocks (DRY violations).
   - Outdated dependencies (invoke `dependency-updates` audit).
2. Review recent incident postmortems for systemic issues.
3. Collect developer pain points from code review comments and retro notes.

### 2. Debt Categorization ⚡ (Power Mode)

**Steps:**

1. Classify each debt item into a category:
   | Category         | Examples                                          |
   |------------------|---------------------------------------------------|
   | **Architecture** | Monolith coupling, missing abstraction layers     |
   | **Code Quality** | Duplicated code, complex conditionals, god classes|
   | **Testing**      | Missing test coverage, flaky tests, no E2E tests  |
   | **Infrastructure** | Manual deployments, outdated CI config          |
   | **Documentation**| Missing API docs, stale README, no onboarding guide|
   | **Dependencies** | Outdated packages, deprecated libraries           |
2. Tag each item with affected components and ownership.
3. Link debt items to related incidents or bugs where applicable.

### 3. Impact Scoring ⚡ (Power Mode)

**Steps:**

1. Score each debt item on two axes (1–5 scale):
   - **Impact:** How much does this debt slow the team or risk production?
   - **Effort:** How much work to pay it off?
2. Calculate priority score: `Priority = Impact × (1 / Effort)`.
3. Apply multipliers for:
   - Security risk: ×2
   - Blocking other work: ×1.5
   - Growing over time (compound debt): ×1.5
4. Rank items by final weighted score.

### 4. Debt Budget Management 🌱 (Eco Mode)

**Steps:**

1. Propose a debt budget: percentage of sprint capacity allocated to
   debt payoff (recommended: 15–20%).
2. Select top-priority items that fit within the budget.
3. Create trackable work items for selected debt payoff tasks.
4. After each sprint, update the debt registry:
   - Mark resolved items.
   - Re-score items whose context has changed.
   - Add newly discovered debt.

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `debt_registry`    | `object[]` | Full list of categorized debt items      |
| `priority_ranking` | `object[]` | Scored and ranked debt items             |
| `sprint_plan`      | `object[]` | Items selected for current sprint budget |
| `trend_report`     | `object`   | Debt count over time, resolved vs added  |

---

## Scope

### In Scope

- Scanning codebases for technical debt indicators (TODOs, suppressed warnings, duplication)
- Categorizing debt by type (architecture, code quality, testing, infrastructure, documentation, dependencies)
- Scoring debt items by impact and effort with weighted prioritization
- Managing sprint-level debt budgets and selecting payoff work
- Tracking debt trends over time (new debt vs resolved debt)
- Linking debt items to incidents, bugs, and code review feedback
- Maintaining a living debt registry

### Out of Scope

- Actually refactoring code to resolve debt items (delegate to `refactoring` or `refactoring-suite`)
- Making architectural changes (delegate to `system-design` or `adr-management`)
- Writing or fixing tests to close testing debt (delegate to `unit-testing` or `integration-testing`)
- Upgrading dependencies (delegate to `dependency-updates` or `legacy-upgrade`)
- Sprint planning or velocity forecasting beyond debt budget allocation

## Guardrails

- Never delete or archive a debt item without explicit resolution evidence or user approval.
- Always preserve historical scores when re-scoring — append new scores, do not overwrite.
- Do not inflate impact scores to force prioritization; scoring must follow the defined rubric.
- Debt budget must not exceed 30% of sprint capacity without explicit team agreement.
- Never auto-assign debt items to individuals — ownership is at the team or component level.
- Always link debt items to concrete code locations or architectural components.
- Do not count feature work as debt payoff unless it directly eliminates a registered debt item.

## Ask-When-Ambiguous

### Triggers

- A debt item could reasonably be categorized in multiple categories
- The impact score is unclear because the affected component has no recent usage data
- A proposed debt budget exceeds 25% of sprint capacity
- A debt item appears to duplicate an existing registry entry
- The effort estimate varies significantly between team members

### Question Templates

1. "Debt item `{description}` could be categorized as `{cat_a}` or `{cat_b}`. Which category better reflects the primary concern?"
2. "Component `{component}` has no recent usage metrics. Should I score impact based on code complexity alone, or defer scoring until usage data is available?"
3. "The proposed debt budget is `{percent}%` of sprint capacity, which exceeds the recommended 20%. Should I proceed with this allocation or reduce to the recommended level?"
4. "Existing debt item `{existing}` appears similar to new item `{new}`. Should I merge them or track separately?"
5. "Effort estimates for `{item}` range from `{low}` to `{high}`. Should I use the average, the conservative (high) estimate, or ask the team to re-estimate?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Debt item is linked to a production incident | Escalate to top priority regardless of effort score |
| Debt item blocks a planned feature | Include in the next sprint's debt budget |
| Debt is compound (grows worse over time if ignored) | Apply ×1.5 multiplier and surface in weekly report |
| Debt effort exceeds one sprint | Break into smaller payoff tasks; schedule across multiple sprints |
| Multiple debt items affect the same component | Group and prioritize as a single remediation initiative |
| Debt budget is unused in a sprint | Carry forward to next sprint, do not reallocate to features |
| New debt is introduced in a PR | Log immediately in the registry with the PR as source reference |
| Debt item has been in registry for 6+ months with no progress | Escalate in trend report; reassess whether it should be accepted |
| Security-related debt is discovered | Apply ×2 multiplier; flag for immediate review |
| Team disputes a debt item's validity | Keep in registry as "contested" status; resolve in next retro |

## Success Criteria

- [ ] All known debt items are registered with category, impact score, effort score, and priority
- [ ] Debt registry is reviewed and updated at least once per sprint
- [ ] Sprint debt budget is defined and tracked against actual time spent
- [ ] Trend report shows debt count is stable or decreasing over time
- [ ] Every debt item links to at least one concrete code location or component
- [ ] No critical or security-related debt items remain unaddressed for more than two sprints
- [ ] Newly introduced debt is captured at PR review time

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Debt registry becomes stale | Items reference deleted files or resolved issues | Schedule mandatory registry review every sprint; auto-check code references |
| Impact score inflation | Everything is scored 5/5, making prioritization meaningless | Enforce calibration by requiring at least one item per score level |
| Debt budget consistently skipped | Sprint retrospectives show 0% debt work for 3+ sprints | Escalate to engineering leadership; make debt budget a sprint planning gate |
| Duplicate debt entries | Same issue tracked under different descriptions | Run deduplication check when adding new items; merge confirmed duplicates |
| Effort chronically underestimated | Debt payoff tasks consistently overflow sprint capacity | Apply historical correction factor to effort estimates; use conservative scoring |
| Debt introduced faster than resolved | Trend report shows accelerating debt growth | Increase debt budget or institute a debt-freeze sprint; review code review standards |

## Audit Log

- `[{timestamp}] debt-discovered: {count} new items found — {categories_summary}`
- `[{timestamp}] debt-scored: {item_id} "{description}" — impact={impact}, effort={effort}, priority={priority}`
- `[{timestamp}] debt-budget-set: sprint {sprint_id} — {percent}% capacity ({hours} hours) allocated`
- `[{timestamp}] debt-resolved: {item_id} "{description}" — resolved via {resolution_method}`
- `[{timestamp}] debt-trend: registry total={total}, added={added}, resolved={resolved}, net_change={net}`
- `[{timestamp}] debt-escalated: {item_id} "{description}" — reason: {reason}`
````
