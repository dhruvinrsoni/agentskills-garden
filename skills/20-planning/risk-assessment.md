```markdown
---
name: risk-assessment
description: >
  Identify project and technical risks, evaluate probability and impact,
  build risk matrices, and define mitigation strategies.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - requirements-elicitation
reasoning_mode: plan-execute
---

# Risk Assessment

> _"Hope is not a strategy — name the risk before it names your deadline."_

## Context

Invoked before or during planning phases to surface threats that could
derail timelines, quality, or security. Produces a prioritised risk
register with probability/impact ratings and concrete mitigation plans.

---

## Micro-Skills

### 1. Risk Identification ⚡ (Power Mode)

**Steps:**

1. Review requirements, constraints, and assumptions for implicit threats.
2. Categorise risks: technical, schedule, resource, external/dependency, security, compliance.
3. For each risk, write a one-line description and assign a unique ID (e.g., `R-01`).
4. Cross-reference with known failure patterns (past incidents, common anti-patterns).

### 2. Probability / Impact Scoring ⚡ (Power Mode)

**Steps:**

1. Rate each risk's **probability** on a 5-point scale (Rare → Almost Certain).
2. Rate each risk's **impact** on a 5-point scale (Negligible → Catastrophic).
3. Compute a composite score: `score = probability × impact`.
4. Populate a probability/impact matrix (5 × 5 heat map).

### 3. Mitigation Planning ⚡ (Power Mode)

**Steps:**

1. For each risk with composite score ≥ 9 (High/Critical), define a mitigation action.
2. Classify the strategy: **avoid**, **transfer**, **mitigate**, or **accept**.
3. Assign an owner (or flag as unassigned for user decision).
4. Define a trigger condition that activates the contingency plan.

### 4. Risk Monitoring Setup 🌿 (Eco Mode)

**Steps:**

1. Define review cadence (per-milestone or weekly).
2. List leading indicators for each top risk (e.g., "build time > 10 min").
3. Create a risk dashboard section in the scratchpad.

---

## Outputs

| Field              | Type       | Description                                  |
|--------------------|------------|----------------------------------------------|
| `risk_register`    | `object[]` | List of risks with IDs, descriptions, scores |
| `risk_matrix`      | `string`   | Mermaid or text-based 5×5 heat map           |
| `mitigations`      | `object[]` | Mitigation plans for high/critical risks     |
| `monitoring_plan`  | `object`   | Review cadence and leading indicators        |

---

## Edge Cases

- User says "there are no risks" — Present at least 3 common risks for the
  project type and ask for confirmation.
- All risks score low — Document the assessment anyway; low risk today does
  not mean low risk tomorrow.
- Risk and requirement conflict — Flag the conflict and ask the user to
  reprioritise the requirement or accept the risk.

---

## Scope

### In Scope

- Identifying technical, schedule, resource, external, security, and compliance risks.
- Scoring risks using a probability/impact matrix (5-point scales).
- Categorising and prioritising risks by composite score.
- Defining mitigation strategies (avoid, transfer, mitigate, accept) for high-scoring risks.
- Setting up monitoring triggers and leading indicators for top risks.
- Producing a structured risk register and heat-map visualisation.
- Reviewing and updating the risk register at milestones.

### Out of Scope

- Implementing mitigations (see relevant implementation or security skills).
- Financial risk quantification (dollar-value expected loss calculations).
- Legal or contractual risk analysis requiring domain-specific legal expertise.
- Organisational or people-management risks (team morale, hiring).
- Threat modeling for security-specific attack vectors (see `threat-modeling`).
- Making go/no-go decisions — this skill informs decisions, it does not make them.

---

## Guardrails

- Never dismiss a risk without scoring it — all identified risks must appear in the register.
- Do not fabricate risks to inflate the register; every risk must be traceable to a requirement, assumption, or known pattern.
- Mitigation strategies must be actionable, not vague ("be careful" is not a mitigation).
- Probability and impact scores must use the defined 5-point scale; no custom scales without user agreement.
- Risk owners must be explicitly assigned or flagged as unassigned — never silently skip ownership.
- Do not alter risk scores after user sign-off without logging the change and rationale.
- Keep the risk register in the scratchpad; never store risks only in ephemeral conversation context.

---

## Ask-When-Ambiguous

### Triggers

- A requirement implies a risk but the severity is ambiguous (e.g., "we might need GDPR compliance").
- Two risks appear to be duplicates but have subtly different root causes.
- The user's risk tolerance is unknown (startup "move fast" vs. enterprise "zero defects").
- An external dependency's reliability is unknown.
- A mitigation strategy would significantly increase scope or cost.
- The user's definition of "catastrophic impact" is unclear.

### Question Templates

1. "You mentioned [requirement/constraint] — does this imply a [compliance/security/schedule] risk I should log?"
2. "Risks [R-XX] and [R-YY] look similar. Are they the same risk, or do they have different root causes?"
3. "What is your risk tolerance for this project — are you optimising for speed or safety?"
4. "How reliable is [external dependency]? Should I rate its failure probability as Likely or Possible?"
5. "Mitigating [R-XX] would add approximately [effort]. Is that acceptable, or should we accept the risk?"
6. "What does 'catastrophic' mean for this project — data loss, revenue loss, reputational damage, or all three?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Composite score ≥ 15 (Critical) | Mitigation is mandatory; escalate to user immediately |
| Composite score 9–14 (High) | Define mitigation; recommend action but allow user to accept |
| Composite score 4–8 (Medium) | Document the risk; mitigation is optional |
| Composite score 1–3 (Low) | Log and monitor; no active mitigation required |
| Two mitigations conflict | Present both options with trade-offs; let user decide |
| Risk cannot be mitigated | Classify as "accept" with explicit user acknowledgment |
| New information changes a score | Update the register, log the change, and notify the user |

---

## Success Criteria

- [ ] All identified risks have a unique ID, description, category, and probability/impact score.
- [ ] A probability/impact matrix (heat map) is produced.
- [ ] Every risk with composite score ≥ 9 has a defined mitigation strategy.
- [ ] Each mitigation has a trigger condition and an owner (or is flagged as unassigned).
- [ ] The risk register is stored in the scratchpad for persistence.
- [ ] The user has reviewed and acknowledged the risk register.
- [ ] Monitoring cadence and leading indicators are defined for top risks.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Risk blindness | Major risk materialises that was never identified | Use category checklists (technical, schedule, resource, external, security, compliance) to ensure coverage |
| Score inflation | Every risk is rated Critical, making prioritisation useless | Calibrate scores against concrete examples; require justification for any score ≥ 4 |
| Score deflation | Risks are under-rated and ignored until they materialise | Cross-check scores with historical data or analogous projects |
| Vague mitigations | "We'll handle it" without actionable steps | Enforce verb + object format ("add circuit breaker to payment API") |
| Stale register | Risks are assessed once and never revisited | Define review cadence at milestones; add reminders to scratchpad |
| Ownership vacuum | No one is responsible for monitoring or mitigating a risk | Require every high/critical risk to have an explicit owner or be flagged unassigned |

---

## Audit Log

Every risk assessment session must produce an entry in the project's audit log:

```
- [<ISO8601>] risk-assessment-started: Began risk identification for "<project/task>"
- [<ISO8601>] risks-identified: N risks catalogued across K categories
- [<ISO8601>] matrix-built: Probability/impact matrix generated — C critical, H high, M medium, L low
- [<ISO8601>] mitigations-defined: Mitigation plans created for N high/critical risks
- [<ISO8601>] monitoring-configured: Review cadence set to [per-milestone|weekly]; N leading indicators defined
- [<ISO8601>] user-review: User acknowledged risk register — N risks, M mitigations
- [<ISO8601>] risk-assessment-complete: Final register saved to scratchpad
```

Log entries are append-only. Score changes and new risks are recorded as new rows, never as overwrites.
```
