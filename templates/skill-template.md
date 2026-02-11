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
