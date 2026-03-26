---
name: prd
description: >
  Adaptive PRD authoring — selects the right format (lean 1-pager, full
  structured, working backwards, or hypothesis-driven), guides section-by-section
  completion, and manages document lifecycle with versioning, status transitions,
  and amendment logging.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, requirements-elicitation"
  reasoning_mode: plan-execute
  skill_type: standard
  activation_triggers: "PRD, product requirements, spec, specification, feature document, write requirements document"
---


# PRD — Product Requirement Document

> _"Structure the ambiguity. Ship the clarity."_

## Context

Invoked after requirements elicitation (or in parallel when requirements are already
known) to produce a formal, versioned Product Requirement Document. The PRD transforms
raw goals, constraints, and acceptance criteria into a structured artifact that aligns
stakeholders, guides implementation, and serves as the contract between product intent
and engineering execution.

Supports four formats — Lean 1-Pager, Full Structured, Working Backwards, and
Hypothesis-Driven — selected adaptively based on project complexity, audience, and
uncertainty level.

## Scope

### In Scope

- Selecting the appropriate PRD format based on project context.
- Ingesting outputs from `requirements-elicitation` (goals, constraints, acceptance criteria).
- Guiding section-by-section composition with embedded quality checks (INVEST, MoSCoW, SMART, RICE).
- Producing fillable PRD templates in markdown.
- Managing PRD lifecycle: versioning, status transitions (Draft → Review → Approved → In Progress → Done), amendment logging.
- Adapting language and section depth to the audience (PM, engineer, solo dev, AI agent).

### Out of Scope

- Gathering requirements interactively (see `requirements-elicitation`).
- Domain modeling or entity extraction (see `domain-modeling`).
- System architecture or technology selection (see `system-design`).
- Task decomposition or sprint planning from the PRD (see `task-decomposition`).
- Writing code, tests, or implementation artifacts.
- Project management activities (assignment, tracking, standups).

---

## Micro-Skills

### 1. Format Selection ⚡ (Power Mode)

**Goal:** Choose the optimal PRD format for the project context.

**Steps:**

1. Assess project context: team size, timeline, product maturity, stakeholder count,
   regulatory environment.
2. **Nano: Format Decision Matrix** — Score each format against 5 weighted criteria:

   | Criterion (Weight) | Lean 1-Pager | Full Structured | Working Backwards | Hypothesis-Driven |
   |---------------------|--------------|-----------------|-------------------|--------------------|
   | Scope complexity (0.30) | Low (single feature) | High (multi-feature) | Any (new product) | Low-Med (experiment) |
   | Stakeholder count (0.20) | 1–3 | 4+ | 3+ (press release audience) | 1–3 |
   | Regulatory/compliance (0.20) | None | High | Medium | None |
   | Timeline pressure (0.15) | Hours–days | Weeks | Weeks | Hours–days |
   | Uncertainty level (0.15) | Low | Low–Med | High (market) | High (hypothesis) |

3. **Nano: Audience Calibration** — Detect the reader's role and adjust language density:

   | Audience | Adjustment |
   |----------|-----------|
   | PM / Manager | Business outcomes, metrics, timelines front-and-center |
   | Senior Dev / Engineering | Technical constraints, API needs, dependencies prominent |
   | Solo Dev | Collapse to essential sections, skip organizational overhead |
   | AI Agent | Tables over prose, boolean-evaluable acceptance criteria, explicit I/O contracts |

4. Present format recommendation with rationale. If scores are within 10%, present both
   options (Dharma: no silent decisions).
5. If user overrides recommendation, proceed with chosen format but note the override in
   the audit log.

**Decision tree summary:**

| Context | Format |
|---------|--------|
| Small feature, tight timeline, few stakeholders | Lean 1-Pager |
| Complex feature, multiple teams, compliance needs | Full Structured PRD |
| New product, market uncertainty, customer-facing | Working Backwards |
| Rapid experiment, need validation, high uncertainty | Hypothesis-Driven |

### 2. Input Ingestion 🌿 (Eco Mode)

**Goal:** Import prior elicitation outputs and detect gaps.

**Steps:**

1. Check if `requirements-elicitation` has been run. If outputs exist (goals, constraints,
   acceptance criteria, assumptions, out-of-scope), import them directly.
2. If no prior elicitation exists, present a pragya checkpoint:
   "Requirements haven't been formally gathered. Should I run requirements-elicitation
   first, or proceed with what you can provide now?"
3. **Nano: Gap Detection** — Compare imported data against the minimum required fields for
   the chosen format. Flag gaps as "TBD" items that must be resolved before the PRD exits
   Draft status.
4. Map imported data to PRD sections:

   | Elicitation Output | PRD Section |
   |--------------------|-------------|
   | `goals` | Goals / Objectives |
   | `constraints.technical` | Technical Constraints |
   | `constraints.business` | Business Context |
   | `constraints.non_functional` | Non-Functional Requirements |
   | `acceptance` | Success Metrics |
   | `assumptions` | Assumptions subsection |
   | `out_of_scope` | Scope / Out of Scope |

### 3. Section Composition ⚡ (Power Mode)

**Goal:** Draft each section with embedded quality checks.

**Steps:**

1. Walk through each section in the chosen format template (see Format Templates below).
2. For each section:
   a. State what the section needs.
   b. Draft content from ingested inputs.
   c. **Nano: INVEST Check** — For user stories and functional requirements, verify each
      is Independent, Negotiable, Valuable, Estimable, Small, Testable. Flag violations.
   d. **Nano: MoSCoW Tag** — For each functional requirement, prompt for priority:
      Must-have / Should-have / Could-have / Won't-have (this time). Record as inline tags.
3. **Nano: RICE Score** — For features competing for priority, compute
   Reach × Impact × Confidence / Effort. Present as a prioritization aid, not a mandate.
4. For the User Journeys section, apply **Nano: Jobs-to-Be-Done Frame** — express each
   journey as "When [situation], I want to [motivation], so I can [expected outcome]."
5. **Nano: SMART Metric Gate** — Every success metric must be Specific, Measurable,
   Achievable, Relevant, Time-bound. Reject vague metrics ("improve performance") and
   propose concrete alternatives ("reduce p95 latency from 800ms to 200ms within 30 days
   of launch").
6. Cross-reference sections for consistency: goals must map to success metrics, functional
   requirements must map to scope, technical constraints must not contradict functional
   requirements.

### 4. Template Assembly 🌿 (Eco Mode)

**Goal:** Assemble drafted sections into the final document.

**Steps:**

1. Assemble sections in the canonical order for the chosen format.
2. Insert document metadata header:

   ```markdown
   | Field | Value |
   |-------|-------|
   | PRD ID | PRD-<project>-<NNN> |
   | Version | 0.1.0 |
   | Status | Draft |
   | Author | <user/agent> |
   | Created | <ISO8601> |
   | Last Modified | <ISO8601> |
   | Format | <Lean | Full | WorkingBackwards | Hypothesis> |
   ```

3. Insert TBD markers for any section with incomplete data:
   `<!-- TBD: [description of what's needed] -->`.
4. **Nano: Section Weight Check** — Verify no single section exceeds 40% of the document
   length (sign of imbalance; move excess detail to an appendix or separate doc).
5. Append the Amendment Log table (empty for new documents).
6. Output the complete PRD as a markdown file.

### 5. Review Cycle ⚡ (Power Mode)

**Goal:** Validate completeness and assign stakeholder reviews.

**Steps:**

1. Run a completeness audit:
   - All TBD items resolved? If not, list them.
   - Every Must-have requirement has a corresponding success metric?
   - Every success metric is SMART?
   - Scope section explicitly lists out-of-scope items?
   - Dependencies section is populated?
2. **Nano: Stakeholder Coverage Matrix** — For each section, identify which stakeholder
   role needs to review it:

   | Section | Primary Reviewer | Why |
   |---------|-----------------|-----|
   | Goals | PM / Product Owner | Owns business outcomes |
   | Technical Constraints | Lead Engineer | Owns feasibility |
   | Security / Privacy | Security Lead | Compliance accountability |
   | Revenue / Cost | Finance / BizOps | Budget impact |
   | User Journeys | UX / Design | User experience ownership |

3. Present the PRD to the user for review.
4. Collect feedback, apply revisions, bump minor version.
5. Repeat until the user signals readiness for status transition.

### 6. Lifecycle Management 🌿 (Eco Mode)

**Goal:** Manage PRD status transitions and versioning.

**Steps:**

1. Manage status transitions via a state machine:

   | Current Status | Valid Transitions | Trigger |
   |---------------|-------------------|---------|
   | Draft | → Review | Author marks ready for review |
   | Review | → Draft (revisions needed) | Reviewer requests changes |
   | Review | → Approved | All required reviewers sign off |
   | Approved | → In Progress | Development begins |
   | In Progress | → Done | All acceptance criteria verified |
   | In Progress | → Review (scope change) | Requirements change mid-build |
   | Any | → Archived | Project cancelled or superseded |

2. **Nano: Semantic Version Bump** — Version the PRD document itself:
   - PATCH (0.1.x): Typo fixes, clarification, formatting
   - MINOR (0.x.0): New section added, requirement modified, scope changed
   - MAJOR (x.0.0): Fundamental pivot in goals, audience, or approach

3. Maintain the Amendment Log at the bottom of the PRD:

   ```markdown
   ## Amendment Log

   | Version | Date | Author | Change Summary | Sections Affected |
   |---------|------|--------|---------------|-------------------|
   | 0.1.0 | <date> | <author> | Initial draft | All |
   | 0.2.0 | <date> | <author> | Added security section per review | Security/Privacy |
   ```

4. On every status transition, append an audit log entry.

---

## Format Templates

### Format A: Lean 1-Pager

**Target:** Small features, tight timelines, 1–3 stakeholders.

**Sections:**

| Section | Required | Source |
|---------|----------|--------|
| Problem Statement | Yes | Goals from requirements-elicitation |
| Proposed Solution | Yes | Author drafts |
| Target Users | Yes | Requirements-elicitation primary actor |
| Success Metrics (max 3) | Yes | Acceptance criteria from requirements-elicitation |
| Scope (In / Out) | Yes | Out-of-scope from requirements-elicitation |
| Key Risks | Yes | Constraints from requirements-elicitation |
| Timeline | Yes | Author provides |

**Omitted sections:** Competitive analysis, go-to-market, wireframes, A/B test plan,
revenue/cost impact, analytics plan, localization. These are explicitly out of scope for
a Lean 1-Pager.

### Format B: Full Structured PRD

**Target:** Complex features, multiple teams, compliance environments.

All sections included, organized into 6 groups:

**Group 1 — Problem & Context:**
Problem Statement, Business Context, Competitive Analysis, Target Users / Personas,
User Journeys (Jobs-to-be-Done format).

**Group 2 — Solution & Scope:**
Goals / Objectives (with MoSCoW tags), Functional Requirements (INVEST-checked),
Non-Functional Requirements, Technical Constraints, API / Data Needs, Scope (In / Out),
Dependencies (internal and external).

**Group 3 — Measurement & Validation:**
Success Metrics (SMART-gated), Analytics Plan, A/B Test Plan.

**Group 4 — Delivery & Operations:**
Timeline / Milestones, Security / Privacy, Rollback Strategy, Localization Needs.

**Group 5 — Business Impact:**
Revenue / Cost Impact, Go-to-Market, Wireframe References.

**Group 6 — Governance:**
Stakeholder Sign-off Matrix, Amendment Log, Version / Status Header.

### Format C: Working Backwards (Amazon Style)

**Target:** New products, high market uncertainty.

| Section | Required | Notes |
|---------|----------|-------|
| Press Release | Yes | Written as if the product already launched. 1 page max. Customer-facing language. |
| FAQ — Customer | Yes | 5–10 questions a customer would ask |
| FAQ — Internal | Yes | 5–10 questions stakeholders/engineers would ask |
| Target Customer | Yes | Specific persona, not "everyone" |
| Problem Statement | Yes | Why the customer cares |
| Solution Overview | Yes | How the product solves the problem |
| Success Metrics | Yes | Customer-centric (adoption, NPS, retention) |
| Key User Journeys | Yes | End-to-end from discovery to value |
| Technical Approach | Optional | Only if engineering constraints are known |
| Timeline / Milestones | Optional | If execution planning is in scope |
| Scope (In / Out) | Yes | Prevents scope creep |
| Revenue / Cost Impact | Optional | If business case is needed for approval |
| Go-to-Market | Yes | How customers will find and adopt the product |

### Format D: Hypothesis-Driven

**Target:** Rapid experiments, MVPs, uncertain value propositions.

| Section | Required | Notes |
|---------|----------|-------|
| Hypothesis | Yes | "We believe [action] will result in [outcome] for [users] because [reason]" |
| Experiment Design | Yes | What to build, what to measure, how long to run |
| Target Metric | Yes | Single primary metric (North Star for this experiment) |
| Success Threshold | Yes | Quantitative: "If metric improves by X%, hypothesis is validated" |
| Failure Threshold | Yes | When to stop: "If metric drops below Y, kill the experiment" |
| Minimal Scope | Yes | Absolute minimum to test the hypothesis |
| Test Plan (A/B or staged rollout) | Yes | Control group, sample size, duration |
| Rollback Strategy | Yes | How to undo if experiment harms users |
| Timeline | Yes | Experiment window (typically 1–4 weeks) |
| Decision Framework | Yes | What happens if validated? What happens if invalidated? |
| User Journeys | Optional | Only if the experiment changes UX flow |
| Dependencies | Optional | External dependencies that could delay the experiment |

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_name` | `string` | yes | Name of the project or feature |
| `elicitation_outputs` | `object` | no | Outputs from requirements-elicitation (goals, constraints, acceptance, assumptions, out_of_scope). If absent, skill prompts for manual input. |
| `format_override` | `string` | no | Force a specific format: "lean", "full", "working-backwards", "hypothesis". If absent, format is auto-selected. |
| `audience` | `string` | no | Primary reader: "pm", "engineering", "solo-dev", "agent". If absent, auto-detected from context. |
| `existing_prd` | `string` | no | Path to an existing PRD for revision or format upgrade. |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `prd_document` | `markdown` | The complete PRD in the chosen format |
| `format_used` | `string` | Which format was selected and why |
| `tbd_items` | `string[]` | List of incomplete sections requiring follow-up |
| `review_matrix` | `object` | Stakeholder-to-section review assignment |
| `version` | `string` | Semantic version of the PRD (e.g., 0.1.0) |
| `status` | `string` | Current lifecycle status (Draft, Review, Approved, In Progress, Done) |

---

## Guardrails

1. **Never fabricate requirements** — Every requirement in the PRD must trace back to user input, elicitation outputs, or an explicitly stated assumption. Hallucinated requirements are a Satya violation.
2. **No premature commitment** — A PRD in Draft status is not a contract. Do not let downstream skills treat Draft PRDs as approved specifications.
3. **TBD items block status transitions** — A PRD cannot transition from Draft to Review if any TBD items remain unresolved.
4. **Format selection is a recommendation, not a mandate** — Always present the recommendation with rationale and allow the user to override.
5. **Success metrics must be SMART** — Reject vague metrics. Propose concrete alternatives for every rejected metric.
6. **Scope creep detection** — If new requirements emerge during PRD composition that were not in the elicitation outputs, flag them as scope additions and require explicit approval.
7. **Audience-appropriate language** — Do not use engineering jargon in a PM-facing PRD; do not omit technical constraints in an engineering-facing PRD.
8. **Amendment log is append-only** — Corrections are new rows, never overwrites. This is an Ahimsa constraint (reversibility).
9. **Version must be bumped on every change** — No silent edits to an existing PRD version.
10. **Living document, not a one-shot artifact** — The skill must support iterative refinement, not just initial generation.

---

## Ask-When-Ambiguous

**Triggers:**

- Format decision scores are within 10% across two formats.
- Required input data is missing and no elicitation outputs are available.
- A functional requirement fails the INVEST check (not Independent, not Testable, etc.).
- Success metrics are subjective or unmeasurable.
- User provides a solution ("use Redis") rather than a requirement ("responses must be < 200ms").
- Scope boundary is unclear: a listed item could be in-scope or out-of-scope.
- Multiple stakeholders are mentioned with potentially conflicting priorities.
- The PRD is being written for an AI agent consumer and the level of specification granularity is unclear.

**Question Templates:**

- "This project could use a {Format A} or {Format B} PRD. {Format A} is lighter but may miss {sections}. {Format B} covers everything but takes longer. Which fits your timeline?"
- "The requirement '{X}' is not independently testable. Should I split it into sub-requirements, or is it acceptable as a composite?"
- "'{Metric}' is not measurable as stated. Did you mean something like '{concrete alternative}'?"
- "You mentioned '{solution}' — is that a hard constraint, or is the underlying requirement '{rephrased as problem}'?"
- "Should '{item}' be in scope or explicitly out of scope for this release?"
- "Who is the primary audience for this PRD — product/business stakeholders, engineering team, or both?"

---

## Decision Criteria

| Situation | Action | Rationale |
|-----------|--------|-----------|
| Single small feature, < 1 week effort | Lean 1-Pager | Minimal overhead, maximum speed |
| Multi-feature release, 4+ stakeholders, compliance | Full Structured PRD | Comprehensive coverage prevents downstream surprises |
| New product with unclear market fit | Working Backwards | Forces customer-centric thinking before building |
| Rapid experiment, need data-driven validation | Hypothesis-Driven | Structured to prove/disprove quickly |
| Format scores tied within 10% | Present both options with trade-offs | Dharma: let the user decide |
| User says "just give me a template" | Generate template with TBD markers, skip guided composition | Respect user autonomy; they can fill it themselves |
| Elicitation outputs are incomplete | Prompt for missing data OR mark sections as TBD | Never fabricate; gap visibility > gap concealment |
| User overrides format recommendation | Proceed with chosen format, log override | User steers; note the recommendation delta for posterity |
| PRD exceeds 10 pages (for non-Full format) | Suggest upgrading to Full Structured or splitting into sub-PRDs | Lean and Hypothesis formats lose value when bloated |
| Same requirement appears in multiple sections | Deduplicate; use cross-references | Single source of truth per requirement |
| Existing PRD needs major revision | Bump major version, preserve prior version in amendment log | Traceability over convenience |
| AI agent is the consumer | Maximize structure: tables over prose, explicit acceptance criteria, machine-parseable metrics | Agents need unambiguous, parseable specifications |

---

## Success Criteria

- [ ] A PRD format is selected with documented rationale.
- [ ] All sections required by the chosen format are present (or explicitly marked TBD with follow-up owners).
- [ ] Every functional requirement passes the INVEST check.
- [ ] Every Must-have requirement has at least one SMART success metric.
- [ ] MoSCoW priority is assigned to all functional requirements.
- [ ] Scope section explicitly lists both in-scope and out-of-scope items.
- [ ] Document metadata (ID, version, status, author, dates) is complete.
- [ ] The PRD is written at the appropriate language level for the declared audience.
- [ ] Amendment log is initialized.
- [ ] Stakeholder review matrix is produced (for Full and Working Backwards formats).
- [ ] The user has reviewed and accepted the PRD (or approved its current TBD state for iterative completion).

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Wrong format selected | PRD is too heavy for a small feature or too light for a complex one | Format Decision Matrix with weighted scoring; user override always available |
| Hallucinated requirements | PRD contains requirements nobody asked for | Trace every requirement to elicitation output or user input; flag untraced items |
| Vague success metrics | "Improve user experience" with no measurable target | SMART Metric Gate rejects non-measurable metrics; proposes concrete alternatives |
| Scope creep during composition | New features sneak in without approval | Flag any requirement not in original elicitation outputs; require explicit approval |
| Document bloat | Lean 1-Pager grows to 8 pages | Section Weight Check nano; suggest format upgrade if document exceeds format limits |
| Stale PRD | Document not updated as requirements evolve | Lifecycle management with versioning; status transitions require re-review |
| Missing stakeholder input | Security section written without security team review | Stakeholder Coverage Matrix ensures each section has an assigned reviewer |
| Template without guidance | User gets a blank template and doesn't know how to fill it | Guided composition mode walks through each section with prompts and examples |
| PRD treated as code spec | Engineers implement literally without exercising judgment | Guardrail: PRD states intent and constraints, not implementation details |
| Audience mismatch | Technical PRD shown to non-technical stakeholders causes confusion | Audience Calibration nano adjusts language density; Ask-When-Ambiguous triggers on audience uncertainty |

---

## Audit Log

Every PRD session must produce entries in the project's audit log:

```markdown
| Timestamp | Skill | Action | Detail | Confirmed By |
|-----------|-------|--------|--------|--------------|
| <ISO8601> | prd | session-started | PRD authoring begun for "<project>" | — |
| <ISO8601> | prd | format-selected | Format: <format>, Score: <score>, Override: <yes/no> | user |
| <ISO8601> | prd | inputs-ingested | Imported N goals, M constraints, K acceptance criteria from requirements-elicitation | — |
| <ISO8601> | prd | gaps-detected | N TBD items identified: [list] | — |
| <ISO8601> | prd | section-composed | Section "<name>" drafted, INVEST: pass/fail, MoSCoW: tagged | — |
| <ISO8601> | prd | prd-assembled | Version 0.1.0, Status: Draft, Format: <format>, Sections: N | user |
| <ISO8601> | prd | review-requested | Stakeholder matrix: N reviewers assigned | user |
| <ISO8601> | prd | status-transition | <old-status> → <new-status> | user |
| <ISO8601> | prd | version-bumped | <old-version> → <new-version>, Change: "<summary>" | user |
| <ISO8601> | prd | prd-finalized | Version <version>, Status: Approved, TBD items: 0 | user |
```

Log entries are append-only. Corrections are recorded as new rows, never as overwrites.

---

## Examples

### Example 1 — Small Feature (Lean 1-Pager)

**Context:** Solo developer adding dark mode to a personal project.

**Format Selected:** Lean 1-Pager (score: 0.92). Low complexity, single stakeholder, no
compliance, tight timeline.

**Output (abbreviated):**

| Field | Value |
|-------|-------|
| PRD ID | PRD-darkmode-001 |
| Version | 0.1.0 |
| Status | Draft |
| Format | Lean 1-Pager |

**Problem:** Users report eye strain during nighttime usage.

**Proposed Solution:** Add a dark mode toggle that persists user preference.

**Target Users:** Existing users who use the app in low-light environments.

**Success Metrics:**
1. Dark mode toggle accessible within 1 tap from any screen.
2. User preference persists across sessions.
3. WCAG AA contrast ratios maintained in dark theme.

**Scope:** In: color scheme toggle, persistent preference, all primary screens.
Out: scheduled auto-switching, per-screen themes, OLED-optimized black theme.

**Key Risks:** Color contrast may fail accessibility checks on some components.

**Timeline:** 3 days development, 1 day QA.

### Example 2 — Complex Feature (Full Structured PRD)

**Context:** E-commerce platform adding a recommendation engine. Multiple teams (ML,
backend, frontend, data), compliance requirements (GDPR for personalization data),
6+ stakeholders.

**Format Selected:** Full Structured PRD (score: 0.95). High complexity, many
stakeholders, compliance, multi-week timeline.

**Key sections demonstrated:**
- **Goals:** "Increase average order value by 15% within 90 days of launch" [Must-have, RICE: 8.5]
- **Functional Requirement:** "System shall display personalized product recommendations
  on product detail pages" [INVEST: pass, Must-have]
- **Non-functional:** "Recommendation response time < 200ms at p99"
- **Security/Privacy:** "All personalization data subject to GDPR Article 17 (right to erasure)"
- **A/B Test Plan:** "50/50 split, primary metric: AOV, guardrail metric: conversion rate, duration: 4 weeks"

### Example 3 — New Product (Working Backwards)

**Context:** Startup exploring a developer productivity tool.

**Format Selected:** Working Backwards (score: 0.88). New product, high market
uncertainty, need customer validation.

**Press Release (abbreviated):**
"Today we announce DevFlow, a tool that eliminates context-switching for developers by
unifying code review, CI status, and task management in a single pane. Developers spend
25% of their day switching between tools..."

**Customer FAQ sample:**
Q: "Do I have to change my existing workflow?"
A: "No. DevFlow integrates with your existing tools (GitHub, Jira, Slack) and surfaces
information without requiring you to change any process."

### Example 4 — Rapid Experiment (Hypothesis-Driven)

**Context:** Testing whether in-app onboarding tutorials reduce churn.

**Format Selected:** Hypothesis-Driven (score: 0.91). High uncertainty, need data,
rapid experiment.

**Hypothesis:** "We believe that adding a 3-step interactive onboarding tutorial will
reduce 7-day churn by 20% for new users because currently 60% of churned users never
complete core actions."

**Success Threshold:** 7-day churn drops from 35% to 28% (20% relative improvement).

**Failure Threshold:** If 7-day churn increases by more than 5% relative, kill
experiment immediately.

**Experiment:** A/B test, 50/50 split, 2-week window, 10,000 users per cohort minimum
for statistical significance.

---

## Edge Cases

- **User says "just give me a blank PRD"** — Generate the template for the recommended
  format with TBD markers and brief guidance comments in each section. Skip the guided
  composition workflow.
- **Requirements change after PRD is Approved** — Transition status back to Review, bump
  minor version, log the change in the Amendment Log. Never silently modify an Approved PRD.
- **Multiple competing formats score identically** — Present all tied formats with a
  comparison table. Ask the user to break the tie. Do not randomly select.
- **PRD for an AI agent consumer** — Maximize machine-parseable structure: use tables over
  prose, format all acceptance criteria as boolean-evaluable statements, provide explicit
  input/output contracts, avoid ambiguous language.
- **Existing PRD in a different format needs upgrade** — Import all sections from the old
  format, map them to the new format's structure, mark any new required sections as TBD.
  Treat as a major version bump.
- **Stakeholder refuses to review assigned section** — Log the refusal in the Amendment
  Log. Proceed with a note that the section was not reviewed by the assigned party. The
  PRD can still transition to Approved if the blocking review is waived by the author.
- **PRD has zero Must-have requirements** — Flag as suspicious. Ask: "All requirements are
  marked as Should-have or lower. Is there truly nothing that must be in the first release?"
- **Solo developer with no stakeholders** — Collapse review cycle to self-review. Skip
  Stakeholder Coverage Matrix. Audience defaults to "solo-dev" (minimal overhead).
- **User provides requirements in a non-standard format** — (email thread, Slack dump,
  meeting notes) Attempt to extract goals, constraints, and acceptance criteria. Present
  the extraction for user confirmation before proceeding.
