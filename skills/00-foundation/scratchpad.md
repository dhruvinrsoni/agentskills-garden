---
name: scratchpad
description: >
  Defines the agent's internal monologue and cognitive modes.
  Loaded before every task to set the thinking framework.
version: "1.0.0"
dependencies:
  - constitution
reasoning_mode: linear
---

# Scratchpad — Internal Monologue Protocol

> _"Think before you type."_

## Rule

Before generating **any** code or making **any** file change, you **must**
open a `<scratchpad>` block in your reasoning trace. This block is private
and never shown to the user unless they ask for it.

```text
<scratchpad>
  Task: ...
  Risk: low | medium | high
  Mode: eco | power
  Plan:
    1. ...
    2. ...
</scratchpad>
```

---

## Eco Mode 🌿

**When:** Low-risk tasks — typos, formatting, small fixes, doc updates.

- Use a **simple linear plan** (1-3 steps).
- No deep reasoning required.
- Execute directly after plan confirmation.

### Eco Checklist

- [ ] Change is cosmetic or additive only.
- [ ] No logic is altered.
- [ ] No public API surface changes.

---

## Power Mode ⚡

**When:** High-risk tasks — refactoring, logic changes, architecture
decisions, multi-file edits.

Engage **4-Step Reasoning**:

| Step | Mode       | Question                                      |
|------|------------|-----------------------------------------------|
| 1    | Deductive  | What do the **rules** (types, specs) require?  |
| 2    | Inductive  | What **patterns** exist in the codebase?       |
| 3    | Abductive  | What is the **best hypothesis** for the root cause? |
| 4    | Analogical | Have we seen a **similar case** before?        |

### Power Checklist

- [ ] Scratchpad includes all 4 reasoning steps.
- [ ] Plan has been reviewed against the Constitution.
- [ ] Diff has been generated before execution.
- [ ] Tests pass (or TDD loop is engaged).

---

## Mode Selection Heuristic

```text
if task.changes_logic == false && task.files <= 2:
    mode = "eco"
else:
    mode = "power"
```

_When in doubt, default to Power Mode._
