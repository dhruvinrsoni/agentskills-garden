```markdown
---
name: task-decomposition
description: >
  Break complex tasks into ordered subtasks with dependency mapping,
  effort estimation, and parallel execution opportunities.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - requirements-elicitation
reasoning_mode: plan-execute
---

# Task Decomposition

> _"A mountain is moved one stone at a time — but only if you pick the right stone first."_

## Context

Invoked when a user presents a complex, multi-step task that cannot be
completed atomically. Produces a structured work breakdown with dependency
ordering, parallelism hints, and per-subtask effort estimates so that
execution proceeds in the most efficient safe order.

---

## Micro-Skills

### 1. Work Breakdown ⚡ (Power Mode)

**Steps:**

1. Parse the top-level task into a flat list of candidate subtasks.
2. For each candidate, determine if it is independently verifiable — if not, split further.
3. Assign a short unique ID (e.g., `T-01`, `T-02`) and a one-line description to each subtask.
4. Stop splitting when every leaf subtask can be completed in a single focused session.

### 2. Dependency Ordering ⚡ (Power Mode)

**Steps:**

1. For each subtask, list its predecessors (subtasks that must finish first).
2. Build a directed acyclic graph (DAG) of dependencies.
3. Detect cycles — if found, flag and ask the user to clarify.
4. Compute a topological order and assign execution phases (parallel groups).

### 3. Effort Tagging 🌿 (Eco Mode)

**Steps:**

1. Tag each subtask with a T-shirt size: XS, S, M, L, XL.
2. Map sizes to approximate time ranges (XS ≤ 15 min, S ≤ 1 h, M ≤ 4 h, L ≤ 1 d, XL > 1 d).
3. Sum the critical-path durations to produce a total estimate.

### 4. Milestone Identification 🌿 (Eco Mode)

**Steps:**

1. Group contiguous subtasks into milestones (logical checkpoints).
2. Define a verification criterion for each milestone.
3. Output a milestone timeline with cumulative effort.

---

## Outputs

| Field              | Type       | Description                                  |
|--------------------|------------|----------------------------------------------|
| `subtasks`         | `object[]` | List of subtasks with IDs, descriptions, sizes |
| `dependency_graph` | `string`   | Mermaid DAG of subtask dependencies          |
| `execution_phases` | `object[]` | Ordered phases with parallelisable groups    |
| `milestones`       | `object[]` | Checkpoints with verification criteria       |
| `critical_path`    | `string[]` | Subtask IDs on the longest dependency chain  |

---

## Edge Cases

- User provides a single-sentence task — Still decompose; confirm with user
  if only one subtask results ("Is this truly atomic?").
- Circular dependency detected — Halt, visualise the cycle, and ask the user
  which dependency to break.
- Subtask is larger than XL — Recursively decompose until all leaves are ≤ XL.

---

## Scope

### In Scope

- Breaking a user-stated task into discrete, independently verifiable subtasks.
- Building and validating a dependency graph (DAG) across subtasks.
- Detecting circular dependencies and flagging them for resolution.
- Assigning T-shirt-size effort estimates to each subtask.
- Identifying the critical path and parallel execution opportunities.
- Grouping subtasks into milestones with verification criteria.
- Producing Mermaid diagrams of the dependency graph.

### Out of Scope

- Actually executing or implementing any subtask (see implementation skills).
- Estimating calendar duration accounting for team capacity or availability (see `estimation`).
- Risk analysis on individual subtasks (see `risk-assessment`).
- External dependency or third-party library analysis (see `dependency-analysis`).
- Project management activities such as assigning owners or tracking status.
- Altering requirements — decomposition works from the stated requirements as-is.

---

## Guardrails

- Never begin execution of subtasks; this skill only plans and decomposes.
- Preserve the user's original intent — do not add, remove, or reinterpret requirements during decomposition.
- Every subtask must have at least one verification criterion; reject subtasks that cannot be verified.
- Dependency graphs must be acyclic — halt and surface any cycle immediately.
- T-shirt size estimates are rough guides, not commitments; label them explicitly as estimates.
- Do not decompose beyond the point of usefulness — stop when subtasks are independently completable in a single session.
- Record all decomposition decisions in the scratchpad for traceability.

---

## Ask-When-Ambiguous

### Triggers

- The user's task description can be interpreted as two or more distinct goals.
- A subtask has an implicit dependency that is not obvious from the task statement.
- The desired granularity of decomposition is unclear (coarse milestones vs. fine-grained steps).
- The user references external systems or teams whose readiness is unknown.
- Ordering constraints conflict (subtask A "should" come before B, but B's output feeds A).

### Question Templates

1. "This task could mean [interpretation A] or [interpretation B] — which do you intend?"
2. "Does subtask [T-XX] depend on [external resource/team] being ready, or can it proceed independently?"
3. "How granular should the breakdown be — high-level milestones or step-by-step instructions?"
4. "I detected a potential circular dependency between [T-XX] and [T-YY]. Which dependency should I drop?"
5. "Should [T-XX] and [T-YY] run in parallel, or is there a hidden ordering constraint I'm missing?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Task has fewer than 3 obvious steps | Still decompose; confirm with user that the breakdown is complete |
| Subtask exceeds XL size | Recursively decompose until all leaves are ≤ XL |
| Two subtasks appear independent but touch the same file/resource | Mark as sequential to avoid conflicts; note the reason |
| User says "just do it in order" | Produce a linear chain but highlight parallelism opportunities for awareness |
| Ambiguous dependency direction | Pause and ask the user before assuming an order |
| Task involves unfamiliar domain | Invoke `requirements-elicitation` first to clarify before decomposing |

---

## Success Criteria

- [ ] Every subtask has a unique ID, one-line description, and T-shirt size estimate.
- [ ] A valid DAG (no cycles) of dependencies is produced.
- [ ] The critical path is identified and its total estimated effort is stated.
- [ ] Parallel execution groups are identified where possible.
- [ ] At least one milestone with a verification criterion exists.
- [ ] The user has reviewed and confirmed the decomposition.
- [ ] No subtask is larger than XL without further recursive breakdown.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Over-decomposition | Dozens of trivial subtasks that add overhead | Apply the "single session" rule — stop splitting when a subtask is completable in one sitting |
| Under-decomposition | Subtasks are too large to estimate or verify | Enforce XL ceiling; recursively split any subtask exceeding it |
| Missed dependency | Subtask fails because a prerequisite was not listed | Review each subtask's inputs/outputs explicitly; cross-check with the user |
| Circular dependency undetected | Execution stalls with no runnable subtask | Run cycle detection on the DAG before presenting results |
| Estimate drift | Actual effort far exceeds T-shirt estimate | Label estimates as rough; recommend re-estimation after each milestone |
| Scope injection | New subtasks appear that weren't in the original task | Freeze the decomposition after user sign-off; new work goes to a backlog |

---

## Audit Log

Every decomposition session must produce an entry in the project's audit log:

```
- [<ISO8601>] decomposition-started: Began decomposing task "<task title>"
- [<ISO8601>] subtasks-identified: N subtasks created (IDs: T-01 … T-NN)
- [<ISO8601>] dependency-graph-built: DAG validated, no cycles detected
- [<ISO8601>] critical-path-calculated: Critical path length = X hours (IDs: T-XX → T-YY → …)
- [<ISO8601>] milestones-defined: M milestones created
- [<ISO8601>] user-review: User confirmed decomposition — N subtasks, M milestones
- [<ISO8601>] decomposition-complete: Final artifact saved to scratchpad
```

Log entries are append-only. Amendments are recorded as new rows, never as overwrites.
```
