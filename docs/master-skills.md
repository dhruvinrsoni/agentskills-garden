# Master Skills

A **master skill** is the fourth level of the [skill hierarchy](concepts.md#1-the-four-level-hierarchy): a workflow that orchestrates other skills in a specific order to deliver an end-to-end outcome (a release, a PR review, an incident response, a feature shipping cycle).

A master skill is to ordinary skills what a Makefile is to a compiler invocation: it composes, sequences, and verifies — it never implements.

This page is the authoring guide. The hard rules are mirrored in [`templates/skill-template.md`](../templates/skill-template.md) under "Master Skill Variant".

---

## Why master skills exist

Without orchestration, common multi-step workflows — "ship a release", "review this PR", "respond to this incident" — get re-derived ad hoc on every invocation. The agent picks a different chain each time, the auditor sees a different plan each time, and consistency suffers.

A master skill freezes the chain. It says: *"this is how 'ship a release' looks in this garden — every time."*

Three properties follow from this:

| Property | Consequence |
|----------|-------------|
| **Predictable shape** | Reviewers, the auditor, and downstream automation can expect the same step ordering across invocations. |
| **Reuse over reinvention** | Each step delegates to a category skill that already encodes its own best practices, guardrails, and failure modes. |
| **Single point of evolution** | Improving the workflow is a matter of editing one master skill, not chasing call sites. |

---

## Hard rules (non-negotiable)

These are enforced by the [`auditor`](../skills/00-foundation/auditor/SKILL.md). Violation = the master is rejected.

1. **Frontmatter `skill_type: master`.** This is what makes the file a master. Without it, the auditor treats it as a standard skill and the orchestration enforcement does not fire.
2. **Every micro-skill starts with `**Invokes:**` line.** Names the skill(s) the step delegates to. This is the orchestration contract.
3. **No implementation logic.** Steps describe routing, inputs, invocation, and output collection. Anything that resembles algorithm, regex, AST traversal, library call, or diff authoring belongs in the invoked skill, not the master.
4. **No `**Nano:**` markers.** Nano-skills are atomic techniques that live in the implementation skills. A master that introduces its own nano is duplicating logic.
5. **Final step is always `**Invokes:** auditor`.** The auditor compares the original plan to the full diff produced across the orchestrated chain and blocks on misalignment.
6. **Inputs and outputs are explicit per step.** This makes the data flow auditable and prevents implicit shared-state magic.

---

## Master-skill micro-skill anatomy

Every micro-skill in a master follows the same shape:

```markdown
### N. <Step Title>
**Mode:** eco | power
**Invokes:** `<skill-1>`[, `<skill-2>` if a parallel sub-batch]
**Inputs:** `<param>` (from step M) | `<external-input>`
**Outputs:** `<field-1>`, `<field-2>`
**Steps:**
1. Load `<skill-name>` via the librarian.
2. Pass `<inputs>` to the skill.
3. Collect `<outputs>` and forward to the next step.
```

The `**Steps:**` block is intentionally thin. Three substeps cover almost every case:

1. Load the invoked skill.
2. Pass the prepared inputs.
3. Collect the named outputs.

If you find yourself writing a fourth substep, ask whether that logic belongs inside the invoked skill instead.

---

## Branching and conditional invocation

Real workflows have conditionals ("if security review fails, route to fix-and-retry"). Express them at the orchestration level, not the implementation level:

```markdown
### 4. Decide on Security-Review Outcome
**Mode:** power
**Invokes:** `pragya`
**Inputs:** `security_review.violations` (from step 3)
**Outputs:** `decision` (one of: `proceed` | `fix-and-retry` | `abort`)
**Steps:**
1. If `violations` is empty → `decision = proceed`.
2. If `violations` is non-empty → load `pragya` and present a checkpoint
   with options (fix now, defer with ticket, abort the workflow).
3. Forward `decision` to step 5.
```

This is still orchestration: it routes between named outcomes; it does not encode security-review logic itself.

---

## Parallel invocation

When two skills can run on independent inputs, declare the parallel sub-batch in `**Invokes:**`:

```markdown
### 2. Static Quality Gates (parallel)
**Mode:** eco
**Invokes:** `code-review`, `security-review`, `performance-review`
**Inputs:** `pr_diff`
**Outputs:** `code_review.report`, `security_review.report`, `performance_review.report`
**Steps:**
1. Load all three skills in parallel.
2. Pass `pr_diff` to each.
3. Collect their reports under namespaced output fields.
```

The auditor recognises namespaced outputs and verifies each invoked skill produced its own report.

---

## Interaction with the auditor

The [`auditor`](../skills/00-foundation/auditor/SKILL.md) is mandatory as the **last** step of every master. It receives:

- The original scratchpad plan that triggered the master.
- The aggregated diff across every step's invoked skill.
- The list of `**Invokes:**` declarations from the master itself.

It checks:

- Every declared `Invokes:` actually fired.
- Every produced diff hunk traces back to one of the declared invocations.
- No step skipped its own audit (e.g. `code-review` produced no report when it was supposed to).
- No constitutional violation appeared in any sub-step.

A failed audit blocks delivery of the master's output and surfaces the violation to the user.

---

## Naming and registration

| Convention | Detail |
|------------|--------|
| **File location** | Master skills live under their natural category. `release-pipeline` lives under `skills/70-devops/release-pipeline/SKILL.md`; `pr-review-flow` under `skills/40-quality/pr-review-flow/SKILL.md`; etc. The `master` scope tag (see [`docs/tags.md`](tags.md)) is what marks them, not the directory. |
| **Name shape** | `<noun>-<workflow|flow|pipeline>`: `release-pipeline`, `pr-review-flow`, `incident-response-flow`, `aparigraha-task`. |
| **Registry entry** | Standard `name`, `path`, `description`, `tags`, `reasoning_mode` — plus `tags` MUST include `master` (scope axis). |

---

## When to write a master skill

Three sanity checks before authoring a new master:

1. **Is this workflow re-derived on every invocation?** If yes, freezing it as a master saves re-derivation cost on every run.
2. **Are the constituent skills already implemented?** Masters only orchestrate. If half the chain doesn't exist yet, build the leaves first; the master comes last.
3. **Is the chain stable enough to commit to?** If the chain shape changes weekly, leave it ad hoc; freezing a moving target produces stale masters.

If all three are yes — write the master.

---

## See also

- [`templates/skill-template.md`](../templates/skill-template.md) — the scaffold including the master-variant section.
- [`docs/concepts.md`](concepts.md) — the four-level hierarchy.
- [`docs/tags.md`](tags.md) — the `master` scope tag.
- [`skills/00-foundation/constitution/SKILL.md`](../skills/00-foundation/constitution/SKILL.md) — definition of master skills in the hierarchy table.
- [`skills/00-foundation/auditor/SKILL.md`](../skills/00-foundation/auditor/SKILL.md) — the validator masters must terminate with.
