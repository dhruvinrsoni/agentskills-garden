---
name: <skill-name>
description: >
  <One-line description of what this skill does.>
version: "0.1.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear | plan-execute | tdd | mixed
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

1. ...
2. ...
3. ...

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
