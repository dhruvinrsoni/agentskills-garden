```markdown
---
name: estimation
description: >
  Produce effort estimates with confidence intervals, calibrate against
  historical data, and communicate uncertainty clearly.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - task-decomposition
reasoning_mode: plan-execute
---

# Estimation

> _"An estimate without a confidence interval is just a guess wearing a suit."_

## Context

Invoked after task decomposition (or alongside it) to attach realistic
effort estimates to work items. Uses multiple estimation techniques,
expresses uncertainty as confidence intervals, and calibrates against
historical project data when available.

---

## Micro-Skills

### 1. Three-Point Estimation ⚡ (Power Mode)

**Steps:**

1. For each subtask, solicit or determine three values: Optimistic (O), Most Likely (M), Pessimistic (P).
2. Calculate the PERT estimate: `E = (O + 4M + P) / 6`.
3. Calculate standard deviation: `σ = (P − O) / 6`.
4. Report the estimate as `E ± σ` (68 % confidence) and `E ± 2σ` (95 % confidence).

### 2. Relative Sizing 🌿 (Eco Mode)

**Steps:**

1. Select a reference subtask that is well understood as the baseline (size = 1).
2. Size every other subtask relative to the baseline (0.5×, 1×, 2×, 3×, 5×, 8×).
3. Convert relative sizes to hours using the baseline's time estimate.
4. Present results as a comparison table.

### 3. Historical Calibration ⚡ (Power Mode)

**Steps:**

1. Retrieve past estimates and actuals from the scratchpad or project history.
2. Compute the calibration ratio: `actual / estimated` for each historical item.
3. Derive an adjustment factor (median calibration ratio).
4. Apply the adjustment factor to current estimates and note the correction.

### 4. Confidence Communication 🌿 (Eco Mode)

**Steps:**

1. Classify the overall estimate confidence: High (≤ 20 % variance), Medium (20–50 %), Low (> 50 %).
2. List the top 3 sources of uncertainty driving the confidence level.
3. Recommend actions to reduce uncertainty (spikes, prototypes, expert consultation).
4. Present a summary table with point estimate, range, and confidence level.

---

## Outputs

| Field                  | Type       | Description                                          |
|------------------------|------------|------------------------------------------------------|
| `estimates`            | `object[]` | Per-subtask: point estimate, range, confidence level |
| `total_estimate`       | `object`   | Aggregated point estimate and range for the whole    |
| `calibration_factor`   | `number`   | Historical adjustment multiplier (if data available) |
| `uncertainty_drivers`  | `string[]` | Top sources of estimation uncertainty                |
| `confidence_level`     | `string`   | High / Medium / Low with explanation                 |

---

## Edge Cases

- No historical data available — Skip calibration; note confidence as
  "uncalibrated" and recommend tracking actuals going forward.
- Single subtask dominates total estimate — Flag concentration risk; a
  miss on that subtask skews the entire plan.
- User demands a single number — Provide it, but always accompany with the
  range and a disclaimer about uncertainty.

---

## Scope

### In Scope

- Producing effort estimates (time-based) for subtasks and aggregated totals.
- Applying three-point (PERT) estimation with optimistic, likely, and pessimistic scenarios.
- Expressing uncertainty as confidence intervals (68 % and 95 %).
- Relative sizing against a known baseline subtask.
- Calibrating estimates against historical actuals when data is available.
- Classifying overall confidence (High / Medium / Low) with supporting rationale.
- Identifying and communicating the top sources of estimation uncertainty.
- Recommending uncertainty-reduction actions (spikes, prototypes, expert input).

### Out of Scope

- Task decomposition itself (see `task-decomposition`) — estimation assumes subtasks are already defined.
- Calendar scheduling or resource allocation (mapping effort to dates/people).
- Cost estimation (converting effort hours to monetary values).
- Risk assessment beyond noting uncertainty drivers (see `risk-assessment`).
- Tracking actual time spent during execution (time tracking tools).
- Commitment or promise-making — estimates are probabilistic, not guarantees.

---

## Guardrails

- Never present a point estimate without an accompanying confidence interval or range.
- All estimates must state their basis (three-point, relative sizing, historical, or expert judgement).
- Calibration factors must be derived from at least 3 historical data points; fewer triggers an "uncalibrated" warning.
- Do not round estimates to false precision (e.g., "4.37 hours" → use "4–5 hours").
- Optimistic estimates must not be zero; pessimistic estimates must not be unbounded — clamp to realistic boundaries.
- Never lock estimates — they are living artefacts updated as information improves.
- Record all estimation assumptions and basis in the scratchpad for future calibration.
- When a user insists on a specific number, log it as a "directed estimate" with the user's override noted.

---

## Ask-When-Ambiguous

### Triggers

- The subtask's complexity is unknown and no analogous historical task exists.
- The user provides only a deadline without indicating desired confidence level.
- Optimistic and pessimistic values are very close, suggesting the estimator may not have considered unknowns.
- The scope of a subtask is loosely defined, making estimation unreliable.
- Historical calibration data is available but from a different team or tech stack.
- The user asks for an estimate on a task that hasn't been decomposed yet.

### Question Templates

1. "I don't have enough context to estimate [subtask]. Can you describe the expected complexity or point me to a similar past task?"
2. "You've given a deadline of [date]. What confidence level are you targeting — 68 % (likely) or 95 % (conservative)?"
3. "Your optimistic and pessimistic values for [subtask] are very close ([O] and [P]). Have you considered [specific risk]?"
4. "Should I estimate [task] as-is, or would you like to decompose it into subtasks first for better accuracy?"
5. "I have historical data from [other project/team]. Is it comparable enough to use for calibration?"
6. "This subtask's scope is loosely defined. Should I estimate based on the best-case interpretation or the broadest reading?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Subtask is well-understood with historical data | Use three-point estimation with calibration factor applied |
| Subtask is novel with no precedent | Use relative sizing against the closest known baseline; flag confidence as Low |
| Fewer than 3 historical data points | Skip calibration; label estimate as "uncalibrated" |
| Variance exceeds 50 % of the point estimate | Classify confidence as Low; recommend a spike or prototype to reduce uncertainty |
| Single subtask accounts for > 50 % of total estimate | Flag concentration risk; recommend further decomposition |
| User overrides the estimate | Record both the calculated estimate and the user's directed estimate with rationale |
| Estimate is for a deadline check | Present the 95 % confidence range and state probability of meeting the deadline |

---

## Success Criteria

- [ ] Every subtask has a point estimate, range (optimistic–pessimistic), and confidence level.
- [ ] The estimation technique used for each subtask is stated (PERT, relative, historical, expert).
- [ ] An aggregated total estimate with overall confidence level is provided.
- [ ] Confidence intervals (68 % and 95 %) are calculated and presented.
- [ ] Top uncertainty drivers are identified and listed.
- [ ] Historical calibration is applied where ≥ 3 data points are available, or "uncalibrated" is noted.
- [ ] The user has reviewed the estimates and acknowledged the uncertainty ranges.
- [ ] Estimation assumptions and basis are recorded in the scratchpad.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Anchoring bias | Estimate gravitates toward the first number mentioned | Always generate three-point range before settling on a point estimate |
| False precision | Estimate presented as "12.4 hours" when uncertainty is ± 50 % | Round to meaningful granularity; never imply precision the data doesn't support |
| Optimism bias | Consistently underestimating — actuals exceed estimates | Apply historical calibration factor; track calibration ratio over time |
| Scope ambiguity | Estimate doesn't match what's actually built because scope was unclear | Require subtask scope to be defined before estimating; link estimate to specific subtask ID |
| Stale calibration data | Adjustment factor based on a different tech stack or team | Validate that historical data is from a comparable context; flag otherwise |
| Missing uncertainty communication | Stakeholders treat point estimate as a guarantee | Always present range and confidence level; never provide a bare number |

---

## Audit Log

Every estimation session must produce an entry in the project's audit log:

```
- [<ISO8601>] estimation-started: Began estimation for "<task/project>"
- [<ISO8601>] technique-selected: Using [PERT | relative sizing | historical calibration] for N subtasks
- [<ISO8601>] estimates-calculated: N subtasks estimated — total point estimate = X hours, 95% range = [Y–Z] hours
- [<ISO8601>] calibration-applied: Historical adjustment factor = F (based on K data points) | skipped (uncalibrated)
- [<ISO8601>] confidence-classified: Overall confidence = [High | Medium | Low] — top drivers: [list]
- [<ISO8601>] user-review: User reviewed estimates — accepted | overrode [subtask IDs] with directed values
- [<ISO8601>] estimation-complete: Final estimates saved to scratchpad
```

Log entries are append-only. Re-estimations are recorded as new rows, never as overwrites.
```
