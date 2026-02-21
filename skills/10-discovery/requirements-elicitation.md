---
name: requirements-elicitation
description: >
  Interview the user to extract goals, constraints, success metrics,
  and acceptance criteria before any code is written.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: plan-execute
---

# Requirements Elicitation

> _"Define the problem before solving it."_

## Context

Invoked at the **start** of any greenfield feature or project. Prevents
wasted effort by ensuring alignment between user expectations and the
agent's understanding.

---

## Micro-Skills

### 1. Goal Extraction ⚡ (Power Mode)

**Steps:**

1. Ask the user: "What problem are you trying to solve?"
2. Restate the goal in your own words and ask for confirmation.
3. Identify the **primary actor** (who benefits) and **scope boundary**
   (what is explicitly out of scope).

### 2. Constraint Discovery ⚡ (Power Mode)

**Steps:**

1. Ask about **technical constraints**: language, framework, deployment target.
2. Ask about **business constraints**: timeline, budget, compliance (GDPR, SOC2).
3. Ask about **non-functional requirements**: latency, throughput, uptime SLA.

### 3. Success Metrics ⚡ (Power Mode)

**Steps:**

1. Ask: "How will you know this is done?"
2. Convert answers into **measurable acceptance criteria**.
3. Format as a checklist the user can sign off on.

### 4. Assumptions Log 🌿 (Eco Mode)

**Steps:**

1. List all assumptions made during the conversation.
2. Ask the user to confirm or correct each one.
3. Record confirmed assumptions in a `assumptions.md` file.

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `goals`            | `string[]` | List of stated goals                     |
| `constraints`      | `object`   | Technical, business, non-functional      |
| `acceptance`       | `string[]` | Measurable success criteria              |
| `assumptions`      | `string[]` | Confirmed assumptions                    |
| `out_of_scope`     | `string[]` | Explicitly excluded items                |

---

## Edge Cases

- User says "just build it" — Invoke Dharma: present a minimal question set
  (3 questions max) before proceeding.
- Conflicting requirements — Flag the conflict and ask user to prioritize.

---

## Scope

### In Scope

- Interviewing users/stakeholders to extract goals, constraints, and acceptance criteria.
- Capturing functional and non-functional requirements.
- Documenting assumptions, priorities, and scope boundaries.
- Producing a structured requirements artifact (checklist, table, or spec).
- Clarifying ambiguous or conflicting requirements before implementation begins.

### Out of Scope

- Writing code or generating implementation artifacts.
- Making architectural or technology-stack decisions (see `system-design`).
- Performing domain modeling (see `domain-modeling`).
- Validating requirements against a running system (see `integration-testing`).
- Stakeholder management or organizational politics.

---

## Guardrails

1. **Never assume requirements** — Every requirement must be explicitly stated or confirmed by the user.
2. **No implementation leakage** — Do not propose solutions, frameworks, or designs during elicitation.
3. **Minimum viable question set** — Ask no more than 5 open-ended questions per round to avoid question fatigue.
4. **Plain language** — Frame questions in domain language, not technical jargon, unless the user is technical.
5. **Immutable record** — Once the user confirms a requirement, it cannot be silently changed; amendments must be logged.
6. **Conflict resolution before proceeding** — If two requirements contradict, halt and ask the user to prioritize before continuing.

---

## Ask-When-Ambiguous

Pause and ask the user when:

- A stated goal can be interpreted in more than one way.
- The user provides a solution instead of a problem ("I need a Redis cache" vs. "responses are too slow").
- Success criteria are subjective or unmeasurable ("it should be fast").
- Scope boundaries are unclear ("handle all edge cases").
- Stakeholders with conflicting priorities are mentioned.
- Compliance or regulatory requirements are hinted at but not detailed.

---

## Decision Criteria

| Situation | Decision | Rationale |
|-----------|----------|-----------|
| User skips a question | Record as "TBD" and revisit before sign-off | Prevents silent gaps in requirements |
| User gives a solution, not a problem | Reframe as a problem statement and confirm | Keeps requirements solution-agnostic |
| Non-functional requirement is vague | Propose a concrete metric and ask for confirmation | Ensures measurability |
| Requirements exceed a single session | Save progress to scratchpad and resume later | Prevents context loss |
| User says "just build it" | Present 3 essential questions before proceeding | Balances speed with minimal due diligence |

---

## Success Criteria

- [ ] All stated goals are captured and restated for user confirmation.
- [ ] At least one measurable acceptance criterion exists per goal.
- [ ] Technical, business, and non-functional constraints are documented.
- [ ] All assumptions are listed and confirmed or corrected by the user.
- [ ] Out-of-scope items are explicitly recorded.
- [ ] No conflicting requirements remain unresolved.
- [ ] The user has signed off on the final requirements artifact.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Assumed requirements | Implementation doesn't match user intent | Always restate and confirm; never infer silently |
| Question fatigue | User disengages or gives terse answers | Limit to 5 questions per round; offer to continue later |
| Solution bias | Requirements are tied to a specific technology | Reframe in problem terms; flag solution language |
| Scope creep | Requirements grow unbounded across sessions | Lock scope after sign-off; new items go to a backlog |
| Missing non-functionals | System meets features but fails under load or compliance | Explicitly prompt for latency, uptime, security, and compliance |
| Unresolved conflicts | Two requirements contradict silently | Flag conflicts immediately; do not proceed until resolved |

---

## Audit Log

Every elicitation session must produce an entry in the project's audit log:

```markdown
| Timestamp | Skill | Action | Detail | Confirmed By |
|-----------|-------|--------|--------|--------------|
| <ISO8601> | requirements-elicitation | session-started | Initial elicitation session begun | — |
| <ISO8601> | requirements-elicitation | goals-captured | N goals recorded | user |
| <ISO8601> | requirements-elicitation | constraints-captured | Technical, business, non-functional constraints logged | user |
| <ISO8601> | requirements-elicitation | assumptions-confirmed | N assumptions confirmed, M corrected | user |
| <ISO8601> | requirements-elicitation | sign-off | User approved final requirements artifact | user |
```

Log entries are append-only. Corrections are recorded as new rows, never as overwrites.
