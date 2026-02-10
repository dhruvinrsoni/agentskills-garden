# Agent Skills Garden 🌱

> *A hierarchical, constitution-driven skill library that serves as the "brain" for AI agents.*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Skills are markdown files with YAML frontmatter that agents discover at runtime via a central registry. Every action is governed by a **Constitution** rooted in three principles:

| Pillar | Sanskrit | Meaning |
|--------|----------|---------|
| **Truth** | Satya | Deterministic, reproducible outputs. No hallucinations. |
| **Safety** | Dharma | Ask-first policy. Prefer the smallest change. |
| **Non-Destruction** | Ahimsa | Preview diffs before applying. Always reversible. |

Inspired by the [Agent Skills](https://agentskills.io/) open format.

---

## Quick Start

**Linux / macOS:**
```bash
git clone https://github.com/dhruvinrsoni/agentskills-garden.git
cd agentskills-garden
chmod +x setup_skills.sh && ./setup_skills.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/dhruvinrsoni/agentskills-garden.git
cd agentskills-garden
.\setup_skills.ps1
```

Both scripts create the full directory structure and all skill files from scratch.

---

## Repository Structure

```
agentskills-garden/
├── registry.yaml                      # Single source of truth — skill index
├── skills/
│   ├── 00-foundation/                 # Always loaded first
│   │   ├── constitution.md            # Three Pillars: Satya, Dharma, Ahimsa
│   │   ├── scratchpad.md              # Internal monologue (Eco / Power modes)
│   │   ├── auditor.md                 # Output validation & compliance
│   │   └── librarian.md              # Skill discovery (fuzzy + semantic)
│   └── 30-implementation/             # Domain-specific skills
│       └── cleanup.md                 # Remove noise, format, safe-rename
├── templates/
│   └── skill-template.md             # Boilerplate for new skills
├── setup_skills.sh                    # Portable installer (Bash)
└── setup_skills.ps1                   # Portable installer (PowerShell)
```

---

## The Skill Format (SKILL.md)

Every skill follows the [agentskills.io](https://agentskills.io/) standard:

```yaml
---
name: cleanup
description: >
  Remove noise, enforce formatting, and safely rename identifiers.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: mixed          # linear | plan-execute | tdd | mixed
---
```

The markdown body contains instructions, micro-skills, steps, inputs/outputs, and examples — progressive disclosure that agents parse at runtime.

---

## Foundation Layer (00)

| Skill | Purpose |
|-------|---------|
| **constitution** | Three Pillars + amendment mechanism |
| **scratchpad** | `<scratchpad>` block, Eco mode (linear) vs Power mode (4-step reasoning) |
| **auditor** | Plan↔Diff alignment, protected terms, constitutional compliance |
| **librarian** | Fuzzy matching (Levenshtein + prefix) and semantic search against `registry.yaml` |

These are loaded **before every task**. They are non-negotiable.

## Implementation Layer (30)

| Skill | Mode | Micro-Skills |
|-------|------|-------------|
| **cleanup** | mixed | Comment Policy (Eco), Formatting (Eco), Safe Renaming (Power) |

Add new implementation skills by copying `templates/skill-template.md` and registering them in `registry.yaml`.

---

## Eco vs Power Mode

```text
if task.changes_logic == false && task.files <= 2:
    mode = "eco"     # Simple linear plan (1-3 steps)
else:
    mode = "power"   # 4-Step Reasoning: Deductive → Inductive → Abductive → Analogical
```

When in doubt, default to **Power Mode**.

---

## Creating a New Skill

1. Copy `templates/skill-template.md` to the appropriate layer directory.
2. Fill in the YAML frontmatter (`name`, `description`, `version`, `dependencies`, `reasoning_mode`).
3. Write the markdown body (Context, Micro-Skills, Steps, Inputs, Outputs, Examples, Edge Cases).
4. Add an entry to `registry.yaml`.
5. The Librarian will auto-discover it on next invocation.

---

## License

[Apache License 2.0](LICENSE)
