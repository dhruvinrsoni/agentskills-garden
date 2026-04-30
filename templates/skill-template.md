---
name: skill-name
description: >
  One-line description of what this skill does and when to use it.
  Should include specific keywords that help agents identify relevant tasks.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "0.1.0"
  dependencies: "constitution, scratchpad"
  reasoning_mode: linear
  skill_type: standard
---

# <Skill Name>

> _"<One-line philosophy or motto for this skill.>"_

## Context

<Describe when and why this skill is invoked. What problem does it solve?>

## Scope

**In scope:** <What this skill is allowed to read/modify.>

**Out of scope:** <What this skill must NEVER touch — public APIs, protected
terms, generated code, etc.>

---

## Micro-Skills

### 1. <Micro-Skill A>

**Mode:** eco | power

**Steps:**

1. **Nano: <Technique Name>** — 1-2 liner atomic building block.
   Example: `**Nano: Exponential Backoff**` — wait `base * 2^attempt + jitter`.
2. Apply the nano technique in context...
3. Verify the outcome...

### 2. <Micro-Skill B>

**Mode:** eco | power

**Steps:**

1. ...
2. ...
3. ...

---

## Inputs

| Parameter   | Type     | Required | Description            |
|-------------|----------|----------|------------------------|
| `<param>`   | `string` | yes      | <What it represents>   |

## Outputs

| Field       | Type     | Description                        |
|-------------|----------|------------------------------------|
| `<field>`   | `string` | <What the skill produces>          |

---

## Guardrails

- Preview diffs before applying any changes.
- Never touch generated, vendor, third_party, build, or dist folders
  unless explicitly allowed.
- Run formatter and linter after changes; revert if errors introduced.
- <Add skill-specific guardrails here.>

## Ask-When-Ambiguous

**Triggers:**

- <Condition that requires user input>
- <Another ambiguity trigger>

**Question Templates:**

- "<Question to ask the user when this trigger fires>"
- "<Another question template>"

## Decision Criteria

- <How to choose between options when multiple paths exist.>
- <When to escalate from Eco to Power mode.>

## Success Criteria

- <Acceptance check 1 — how to verify the skill succeeded.>
- <Acceptance check 2.>

## Failure Modes

- <What can go wrong and how to recover.>
  **Recovery:** <Specific recovery action.>
- <Another failure mode.>
  **Recovery:** <Specific recovery action.>

## Audit Log

- <What to record after this skill runs.>
- <Metrics, decisions, files changed, etc.>

---

## Examples

### Example 1 — <Scenario>

**Input:**
```json
{
  "<param>": "<value>"
}
```

**Output:**
```json
{
  "<field>": "<value>"
}
```

---

## Edge Cases

- <Edge case 1 and how the skill handles it.>
- <Edge case 2 and how the skill handles it.>

---

## Master Skill Variant

> For skills with `skill_type: master` in metadata. Master skills are
> **workflows** — they orchestrate multiple skills in sequence, equivalent to
> an AI agentic workflow. They contain no implementation logic, only invocation
> steps.

See [`docs/master-skills.md`](../docs/master-skills.md) for the full authoring
guide.

### Hard rules (non-negotiable)

1. **Frontmatter MUST declare `skill_type: master`.** No exceptions.
2. **Every micro-skill MUST start with an `**Invokes:**` line** naming the
   target skill(s). The presence of `**Invokes:**` is what the `auditor`
   uses to recognise a step as orchestration rather than implementation.
3. **No implementation logic.** Steps describe inputs, invocations, output
   collection, and routing — never algorithms, regex, code generation,
   diff construction, or any work that belongs in the invoked skill.
4. **No `**Nano:**` markers.** Nanos are atomic techniques and live in the
   skills being orchestrated, not in the master.
5. **No silent skill loads.** Every invocation runs through the `librarian`
   (or is named explicitly enough that the librarian can resolve it).
6. **Always include a final `auditor` step** to verify plan-vs-diff
   alignment across the orchestrated chain.

### Micro-skill template (master variant)

```markdown
### 1. Gather Requirements
**Mode:** eco
**Invokes:** `requirements-elicitation`
**Inputs:** `user_request`
**Outputs:** `scope`, `constraints`, `acceptance_criteria`
**Steps:**
1. Load the `requirements-elicitation` skill.
2. Pass `user_request` as input.
3. Collect outputs and pass forward to the next step.

### 2. Design Architecture
**Mode:** power
**Invokes:** `system-design`
**Inputs:** `scope` (from step 1), `constraints` (from step 1)
**Outputs:** `component_diagram`, `api_contracts`, `data_model`
**Steps:**
1. Load the `system-design` skill.
2. Pass step-1 outputs as input.
3. Collect outputs.

### N. Audit
**Mode:** power
**Invokes:** `auditor`
**Inputs:** scratchpad plan, complete diff across all preceding steps
**Outputs:** `compliant`, `violations`, `blocked`
**Steps:**
1. Load `auditor` with the original plan and the full chain diff.
2. Block delivery on any violation.
```

### Forbidden patterns

| Pattern | Why it's forbidden |
|---------|--------------------|
| Inline `if`/`for`/`while` pseudo-code in steps | Implementation logic — belongs in the invoked skill. |
| Raw regex, AST node names, library calls in steps | Implementation logic. |
| `**Nano: <name>**` inside a master | Atoms live in implementation skills, not orchestrators. |
| Skipping `**Invokes:**` for any micro-skill | Breaks the orchestration contract. |
| Steps that produce a diff directly | Masters orchestrate; they do not author code. |
