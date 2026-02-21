````markdown
---
name: root-cause-analysis
description: >
  Systematically trace symptoms back to their underlying cause using
  5-whys, fault trees, bisection, and symptom-to-cause mapping.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: plan-execute
---

# Root Cause Analysis

> _"Treat the disease, not the symptom."_

## Context

Invoked when a defect, regression, or unexpected behavior is observed and
the surface-level symptoms do not immediately reveal the underlying cause.
This skill provides structured techniques to trace from observable symptoms
to the true root cause so fixes are durable, not cosmetic.

---

## Micro-Skills

### 1. Symptom Collection 🌿 (Eco Mode)

**Steps:**

1. Gather all observable symptoms: error messages, stack traces, failing
   tests, user reports, metric anomalies.
2. Record the exact environment: OS, runtime version, commit SHA, config.
3. Note when the symptom first appeared and any recent changes (deploys,
   config updates, dependency bumps).

### 2. Five-Whys Analysis 🌿 (Eco Mode)

**Steps:**

1. State the problem clearly in one sentence.
2. Ask "Why did this happen?" and record the answer.
3. Repeat up to five times, each time asking why the previous answer
   occurred.
4. Stop when the answer points to a systemic, actionable root cause
   (process, design, or infrastructure flaw).
5. Document the chain in a numbered list.

### 3. Fault-Tree Construction ⚡ (Power Mode)

**Steps:**

1. Define the top-level undesired event (the symptom).
2. Decompose into intermediate events using AND/OR gates:
   - **AND gate:** All child events must occur for the parent.
   - **OR gate:** Any one child event is sufficient.
3. Continue expanding until leaf nodes are basic events (code bugs,
   misconfigurations, external failures).
4. Identify the minimal cut sets — the smallest combinations of basic
   events that cause the top-level failure.

### 4. Git Bisection ⚡ (Power Mode)

**Steps:**

1. Identify a known-good commit and a known-bad commit.
2. Run `git bisect start <bad> <good>`.
3. At each step, test the reproduction case and mark `git bisect good`
   or `git bisect bad`.
4. When bisect identifies the first bad commit, inspect the diff for
   the causal change.
5. Run `git bisect reset` to restore HEAD.

### 5. Symptom-to-Cause Mapping 🌿 (Eco Mode)

**Steps:**

1. List all observed symptoms in a table.
2. For each symptom, brainstorm candidate causes.
3. Cross-reference: which candidate causes explain multiple symptoms?
4. Rank candidates by explanatory power (covers more symptoms = higher).
5. Validate the top candidate by targeted test or code inspection.

---

## Inputs

| Parameter        | Type       | Required | Description                              |
|------------------|------------|----------|------------------------------------------|
| `symptoms`       | `string[]` | yes      | List of observed symptoms or errors      |
| `codebase_path`  | `string`   | yes      | Path to the affected codebase            |
| `good_commit`    | `string`   | no       | Last known-good commit SHA for bisection |
| `bad_commit`     | `string`   | no       | Known-bad commit SHA for bisection       |
| `logs`           | `string`   | no       | Relevant log output                      |

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `root_cause`       | `string`   | Description of the identified root cause |
| `evidence`         | `string[]` | Supporting evidence for the conclusion   |
| `analysis_method`  | `string`   | Which technique was used (5-whys, etc.)  |
| `fix_suggestion`   | `string`   | Recommended fix or next step             |
| `fault_tree`       | `string`   | Fault tree diagram (if constructed)      |

---

## Edge Cases

- Symptom is intermittent (heisenbug) — Use statistical correlation and
  increase observation window before applying 5-whys.
- Multiple root causes contribute to the same symptom — Build a fault tree
  with AND gates to capture the multi-factor causality.
- Bisection is impractical (non-linear history, merge commits) — Fall back
  to manual commit-range inspection and diff analysis.

## Scope

### In Scope

- Analyzing stack traces, error messages, and failing test output to trace root causes.
- Performing 5-whys analysis on bug reports and regression descriptions.
- Constructing fault trees for complex, multi-factor failures.
- Running `git bisect` to identify the exact commit that introduced a defect.
- Building symptom-to-cause mapping tables for broad investigations.
- Reading source code, test files, config files, and log output relevant to the failure.
- Suggesting targeted fixes based on identified root cause.

### Out of Scope

- Applying fixes to production systems directly (hand off to implementation skills).
- Performance profiling or optimization (defer to `profiling-analysis`).
- Writing comprehensive test suites (defer to `unit-testing` or `integration-testing`).
- Incident communication, stakeholder updates, or postmortem authoring (defer to `incident-response`).
- Modifying CI/CD pipelines or deployment configurations.
- Analyzing infrastructure-level failures outside the application codebase (network, DNS, cloud provider outages).

## Guardrails

- Never modify source code during analysis — this skill is read-only and diagnostic.
- Preserve the original reproduction state; do not `git stash`, `git reset`, or alter working tree without user consent.
- Always run `git bisect reset` after completing a bisection to restore HEAD.
- Do not assume correlation is causation; require at least two independent pieces of evidence before declaring a root cause.
- Stop after 7 levels of "why" — if no actionable cause is found, escalate and widen the investigation scope.
- Never access secrets, credentials, or PII while inspecting logs or config files.
- Record all analysis steps in the audit log for reproducibility.

## Ask-When-Ambiguous

### Triggers

- Multiple symptoms are reported, and it is unclear which is the primary failure vs. a cascading side effect.
- The failure cannot be reproduced in the current environment.
- Bisection requires running a test suite, but no automated reproduction script exists.
- The symptom spans multiple services or repositories.
- Recent changes include both code changes and infrastructure/config changes.

### Question Templates

1. "Which symptom is the most impactful or was observed first? This helps prioritize the analysis starting point."
2. "Can you provide a reliable reproduction script or steps, or should I attempt to reproduce from the symptoms described?"
3. "The failure may span services X and Y — should I investigate both, or is one more likely the origin?"
4. "Both a code deploy and a config change happened near the failure onset — should I bisect the code history or investigate the config change first?"
5. "No known-good commit was provided — do you have an approximate date or release version when this last worked correctly?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Single clear error with a stack trace pointing to one location | Use symptom-to-cause mapping; inspect the code path directly |
| Regression after a recent deploy with known-good baseline | Use git bisection to isolate the offending commit |
| Complex failure with multiple interacting components | Construct a fault tree to model the failure modes |
| Vague symptom like "it's slow" or "it sometimes fails" | Start with symptom collection, then apply 5-whys to refine |
| Bisection is impractical (100+ commits, no automated test) | Use 5-whys combined with manual diff review of suspect commits |
| Root cause identified but fix is non-trivial | Document the root cause and evidence, hand off to implementation skill |

## Success Criteria

- [ ] A single, specific root cause statement has been identified and documented.
- [ ] At least two independent pieces of evidence support the root cause conclusion.
- [ ] The analysis method used is recorded (5-whys, fault tree, bisection, or mapping).
- [ ] The root cause explains all (or the majority of) observed symptoms.
- [ ] A concrete fix suggestion or next-step recommendation has been provided.
- [ ] The analysis is reproducible — another engineer can follow the documented steps.
- [ ] No source code was modified during the investigation.
- [ ] Git bisect state has been cleaned up (if bisection was used).

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Premature root cause declaration | Fix is applied but the symptom recurs | Require two independent evidence points; verify the cause experimentally before declaring |
| Infinite 5-whys loop | Analysis goes deeper than 7 levels without converging | Cap at 7 levels; switch to fault tree or bisection for structured decomposition |
| Bisection on wrong branch | `git bisect` completes but identified commit is unrelated | Verify the reproduction case is deterministic before starting bisection |
| Correlation mistaken for causation | A coincidental change is blamed | Cross-reference the suspect change with the symptom mechanism; require a causal explanation |
| Heisenbug disappears during analysis | Cannot reproduce under investigation conditions | Increase logging, use statistical methods, and analyze in the original environment |
| Scope creep into unrelated issues | Investigation expands to cover tangential problems | Stay focused on the original symptom set; log tangential findings for separate investigation |

## Audit Log

- `[{{timestamp}}] rca:start — began root cause analysis for symptoms: {{symptom_summary}}`
- `[{{timestamp}}] rca:method-selected — analysis method: {{method_name}}`
- `[{{timestamp}}] rca:bisect-started — bisecting between {{good_commit}} and {{bad_commit}}`
- `[{{timestamp}}] rca:bisect-completed — offending commit identified: {{commit_sha}}`
- `[{{timestamp}}] rca:fault-tree-built — fault tree with {{node_count}} nodes, {{cut_set_count}} minimal cut sets`
- `[{{timestamp}}] rca:five-whys-completed — reached root cause at depth {{depth}}`
- `[{{timestamp}}] rca:root-cause-identified — cause: {{root_cause_summary}}, evidence: {{evidence_count}} items`
- `[{{timestamp}}] rca:complete — analysis finished, fix suggestion provided`
````
