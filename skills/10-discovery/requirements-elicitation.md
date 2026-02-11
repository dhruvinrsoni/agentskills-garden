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
