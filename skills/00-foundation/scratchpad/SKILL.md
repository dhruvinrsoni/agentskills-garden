---
name: scratchpad
description: >
  Defines the agent's internal monologue protocol. Before producing any
  output, the agent reasons privately in a scratchpad block, selects Eco
  or Power mode, and applies the appropriate reasoning depth.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: 1.0.0
  dependencies: constitution
  reasoning_mode: linear
---


# Scratchpad — Internal Monologue Protocol

> _"Think before you act. Think silently, act precisely."_

## Kernel

Open a private `<scratchpad>` block before any file read, edit, or response. State the task in your own words, complexity, cognitive mode (Eco 🌿 or Power ⚡), risk, plan, dependencies, and protected terms. Eco mode for low-risk linear work (≤2 files, no logic change) — Input → Brief Plan → Execute → Diff. Power mode for refactors, public APIs, security, cross-module changes — runs the 4-step reasoning chain (Deductive → Inductive → Abductive → Analogical) before executing. When mode is uncertain, default to Power.

## Context

Loaded alongside the Constitution at the start of every task. The scratchpad
is the agent's private workspace — its chain-of-thought — where it decomposes
a task, selects the right cognitive mode, and plans before emitting any code
or output to the user.

---

## The `<scratchpad>` Block

Before generating any code, diff, or response, open a **private reasoning
block**. This block is never shown to the user unless explicitly requested.

```text
<scratchpad>
Task: [restate the user's objective in your own words]
Complexity: [low | medium | high]
Mode: [eco | power]
Risk: [what could go wrong?]
Plan:
  1. ...
  2. ...
  3. ...
Dependencies: [which skills/micro-skills will I need?]
Protected terms: [domain-specific names I must not change]
</scratchpad>
```

---

## Cognitive Mode Selection

### Eco Mode 🌿 — Linear Execution

**When:** Low-risk, bounded tasks with clear scope.

- Formatting, linting, doc generation, small fixes
- Changes that do NOT alter program logic
- Scope: 1–3 files, no cross-module impact

**Process:** Input → Brief Plan → Execute → Emit Diff

### Power Mode ⚡ — Deep Reasoning

**When:** High-risk, unbounded, or logic-altering tasks.

- Refactoring, architecture decisions, security changes
- Cross-module or public API modifications
- Any task where failure could break the build

**Process:** Input → 4-Step Reasoning → Plan → Execute → Verify → Emit Diff

---

## The 4-Step Reasoning Framework (Power Mode)

When Power Mode is selected, apply ALL four reasoning types in sequence:

### Step 1 — Deductive Reasoning (Rules → Specific)

Apply known rules and constraints to the specific case.

- "The Constitution says preview diffs first → I must show a diff."
- "DRY principle → this duplicated block should be extracted."
- "The Iron Rule → tests must pass before AND after refactoring."

### Step 2 — Inductive Reasoning (Patterns → Generalization)

Identify patterns from the codebase to form generalizations.

- "All service classes in this project use constructor injection →
  my new service should too."
- "Error responses follow `{ code, message, details }` format →
  my new endpoint should match."

### Step 3 — Abductive Reasoning (Observations → Best Explanation)

Given incomplete information, infer the most likely explanation.

- "This function is called `processData` but only handles CSV →
  likely a naming issue, not intentional polymorphism."
- "Tests are missing for this module → likely not yet written,
  not intentionally skipped."

### Step 4 — Analogical Reasoning (Similar Cases → Transfer)

Find similar solved problems and transfer the approach.

- "Module A solved N+1 queries with batch loading →
  Module B has the same pattern, apply the same fix."
- "The auth middleware in Service X uses the decorator pattern →
  Service Y should use the same approach for consistency."

---

## Mode Auto-Detection Heuristic

```text
IF task.changes_logic == false
   AND task.files <= 2
   AND task.scope == "local"
THEN mode = "eco"

ELSE IF task.involves_public_api == true
   OR task.changes_architecture == true
   OR task.security_sensitive == true
   OR task.cross_module == true
THEN mode = "power"

ELSE mode = "eco"  # default to minimal resource usage
```

**Override:** The user can always force a mode explicitly.

---

## Direction Checkpoint (Pragya)

After selecting mode and before executing, check:

- **Am I confident this is the right approach?** If not → trigger a pragya
  direction checkpoint. Present options with pros/cons, let the user steer.
- **Has the task context shifted** since the plan was made? If yes → reassess
  mode, plan, and dependencies.
- **Am I assuming or deciding?** If any part of the plan rests on an assumption
  rather than confirmed information, flag it.

Reference: `pragya` skill for the full direction-seeking protocol.

---

## Guardrails

- The scratchpad block is PRIVATE. Never leak reasoning to the user unless
  they ask "show me your reasoning."
- Every Power Mode task MUST include all 4 reasoning steps.
- If mode auto-detection is uncertain, default to Power Mode (safer).
- Scratchpad must be opened BEFORE any file reads or edits.

## Ask-When-Ambiguous

- Task complexity unclear → ask: "This could be a quick fix or a deeper
  refactor. Should I go Eco (fast, surface-level) or Power (thorough)?"
- Multiple valid approaches → show options with trade-offs in scratchpad,
  then ask the user to pick.

## Success Criteria

- Every response begins with private reasoning (even if brief in Eco mode).
- Mode selection is explicit and logged.
- Power Mode responses include all 4 reasoning steps.

## Failure Modes

- Skipping the scratchpad → leads to hallucinations and missed edge cases.
  **Recovery:** Always open scratchpad first, even retroactively.
- Choosing Eco for a high-risk task → may miss breaking changes.
  **Recovery:** If unexpected complexity is found mid-task, escalate to Power.

## Audit Log

- Mode selected (eco/power) and why.
- Reasoning steps taken (for Power mode).
- Any mode escalation events.
