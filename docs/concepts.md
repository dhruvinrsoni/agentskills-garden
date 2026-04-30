# Concepts — A Primer

This page explains the building blocks the rest of the garden assumes you already understand: the four-level skill hierarchy, the `**Nano:**` marker, the `Eco 🌿` / `Power ⚡` mode tags, the `reasoning_mode` frontmatter, and the **always-loaded** foundation layer.

Read this once. Then `registry.yaml` and any individual `SKILL.md` will be self-explanatory.

---

## 1. The four-level hierarchy

From [`skills/00-foundation/constitution/SKILL.md`](../skills/00-foundation/constitution/SKILL.md) (the "Skill Hierarchy" section):

| Level | What it is | Where it lives | Concrete example |
|-------|------------|----------------|------------------|
| **Nano-skill** | A 1-2 line atomic technique. The smallest reusable unit. | Inline inside a micro-skill, marked `**Nano: <Name>**`. | `**Nano: Exponential Backoff with Jitter**` in [`resilience-patterns`](../skills/30-implementation/resilience-patterns/SKILL.md) |
| **Micro-skill** | A numbered `### N. Name` section that composes nano-skills into one coherent unit of work. | Inside a `SKILL.md`. | `### 2. Retry with Backoff 🌿 (Eco Mode)` in [`resilience-patterns`](../skills/30-implementation/resilience-patterns/SKILL.md) |
| **Skill** | One `SKILL.md` file. The unit the agent loads on demand for a task. | `skills/<category>/<name>/SKILL.md` | [`resilience-patterns`](../skills/30-implementation/resilience-patterns/SKILL.md) loaded when external dependencies start failing. |
| **Master skill** | A workflow that orchestrates other skills in sequence. Contains invocation steps, never implementation. Marked with `skill_type: master` in metadata. | `skills/<category>/<name>/SKILL.md` like any other skill. | `release-pipeline` (planned) — invokes `test-strategy` → `changelog-generation` → `ci-pipeline`. |

The hierarchy is **read upward**: a master skill is built from skills, a skill is built from micro-skills, a micro-skill is built from nano-skills.

---

## 2. The `**Nano:**` marker

Nano-skills are inline in prose, not separate files. The marker is the contract that makes them discoverable.

**Why this exact format:**

- **Greppable.** `rg '\*\*Nano:'` returns every nano-skill in the garden. See for yourself; today there are nano-skills inside [`resilience-patterns`](../skills/30-implementation/resilience-patterns/SKILL.md), [`pragya`](../skills/00-foundation/pragya/SKILL.md), [`prd`](../skills/10-discovery/prd/SKILL.md), [`ci-pipeline`](../skills/70-devops/ci-pipeline/SKILL.md).
- **Cross-referenceable.** `**Nano: Exponential Backoff**` defined in `resilience-patterns` can be cited from `error-handling` by name without copying the technique.
- **Right-sized signal.** A nano is an atom (1-2 sentences of mechanism). If it grows, promote it to a micro-skill instead.

**House style:** name the nano in Title Case; one nano = one technique; never bury two ideas under one marker.

---

## 3. Eco 🌿 and Power ⚡ tags on micro-skills

Each micro-skill is tagged with the cognitive mode the agent should use to execute it. Tags follow the section heading: `### 2. Retry with Backoff 🌿 (Eco Mode)` or `### 1. Circuit Breaker ⚡ (Power Mode)`.

### What each mode means

| Mode | Process | Use when |
|------|---------|----------|
| **Eco 🌿** | Input → Brief Plan → Execute → Emit Diff (linear, 1-3 steps) | Low-risk, bounded scope, no logic change. Formatting, docs, small fixes, response serialisation. |
| **Power ⚡** | Input → 4-Step Reasoning (Deductive, Inductive, Abductive, Analogical) → Plan → Execute → Verify → Emit Diff | Logic changes, refactoring, public-API/architecture/security changes, anything cross-module. |

### Why a single skill can mix modes

A skill solves a domain (resilience, refactoring, API implementation). Inside that domain, some micro-skills are routine (response shape, dead-code removal) and others are risky (circuit-breaker state machine, dependency inversion). Tagging each micro-skill independently lets the agent stay cheap on the easy parts and thorough on the dangerous parts.

[`resilience-patterns`](../skills/30-implementation/resilience-patterns/SKILL.md) is the canonical example: `1. Circuit Breaker ⚡` and `2. Retry with Backoff 🌿` live in the same file and use different reasoning depths.

### Auto-detection rule

From [`skills/00-foundation/scratchpad/SKILL.md`](../skills/00-foundation/scratchpad/SKILL.md) (the "Mode Auto-Detection Heuristic" section):

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

ELSE mode = "eco"   # default to minimal resource usage
```

The user can always override.

---

## 4. `reasoning_mode` in skill frontmatter

Every `SKILL.md` declares one `reasoning_mode` in its YAML frontmatter. This is the **default** mode for the skill as a whole; individual micro-skills can still tag themselves Eco or Power and override.

### Allowed values

| Value | What it triggers | When to use it | Example skill |
|-------|------------------|----------------|---------------|
| `linear` | Eco-style: short plan, one execution pass, no checkpoint loop. | Foundation skills, docs generation, advisory inventory builders, anything inherently sequential. | [`constitution`](../skills/00-foundation/constitution/SKILL.md), [`scratchpad`](../skills/00-foundation/scratchpad/SKILL.md), [`token-efficiency`](../skills/00-foundation/token-efficiency/SKILL.md), [`docker-containerization`](../skills/70-devops/docker-containerization/SKILL.md), [`release-notes`](../skills/80-docs/release-notes/SKILL.md) |
| `plan-execute` | Power-style: 4-step reasoning, explicit Plan → Execute → Verify loop, output diff before applying. | Refactors, code generation, security review, dependency updates — anything where wrong action is expensive. | [`auditor`](../skills/00-foundation/auditor/SKILL.md), [`code-review`](../skills/40-quality/code-review/SKILL.md), [`code-generation`](../skills/30-implementation/code-generation/SKILL.md), [`reuse-first`](../skills/25-pragmatism/reuse-first/SKILL.md) |
| `tdd` | Test-first cycle: write failing test → minimal code → refactor. Every micro-skill enters with a red test and exits with a green one. | TDD-strict authoring tasks where tests gate every step. | TDD workflow skills (e.g. `tdd-workflow`). |
| `mixed` | Some micro-skills are linear, others are plan-execute. The skill explicitly opts into per-section mode tagging. | Skills that span both routine and risky operations. | [`pair-programming`](../skills/80-collaboration/pair-programming/SKILL.md) |

If `reasoning_mode` is missing, the auditor flags the skill. Default to `linear` only when truly justified.

---

## 5. The "always loaded" foundation layer

### What it means

Skills live in `skills/<category>/<name>/`. Most categories (`10-discovery` through `90-maintenance`) are loaded **on demand** — only when the librarian routes a task to them.

The `00-foundation/` category is different: every skill in it is **prepended to every task's context** before the user's request is even read. They are the agent's operating system.

Today's foundation skills (see [`registry.yaml`](../registry.yaml) `foundation:` section):

| Skill | Why it is always loaded |
|-------|------------------------|
| [`constitution`](../skills/00-foundation/constitution/SKILL.md) | Defines the four pillars (Satya, Dharma, Ahimsa, Pragya). Every other skill inherits these. |
| [`scratchpad`](../skills/00-foundation/scratchpad/SKILL.md) | Forces a private reasoning pass before any output. |
| [`auditor`](../skills/00-foundation/auditor/SKILL.md) | Runs after every action; needs to see the original plan. |
| [`librarian`](../skills/00-foundation/librarian/SKILL.md) | Routes the task to the right category skill. |
| [`pragya`](../skills/00-foundation/pragya/SKILL.md) | Direction-seeking checkpoints. |
| [`orchestrator`](../skills/00-foundation/orchestrator/SKILL.md) | Mid-task skill injection on domain shift. |
| [`token-efficiency`](../skills/00-foundation/token-efficiency/SKILL.md) | Picks model tier and tool depth per mode. |
| [`pragmatism`](../skills/00-foundation/pragmatism/SKILL.md) | Aparigraha — check before create, stay surgical, validate edge cases. |

### What it costs

Always-loaded means every single agent turn pays the token cost of every foundation skill. If foundation grows unbounded, every task pays for capability nobody is using on this turn.

### What it does *not* do

- **It is not a runtime enforcement engine.** Loading the constitution does not magically prevent a violation; the [`auditor`](../skills/00-foundation/auditor/SKILL.md) (also loaded) is what flags drift.
- **It is not a substitute for category skills.** Foundation skills set rules and route; concrete patterns live in `10-` through `90-`.
- **It is not free.** A future hardening pass introduces a `KERNEL.md` aggregator so each foundation `SKILL.md` exposes only its essential `## Kernel` section in the always-loaded path; the rest loads on demand. Until then, keep new foundation skills lean.

### When to add a foundation skill

Only when **every single task** would otherwise have to re-derive what the skill encodes. Three sanity checks before promoting a category skill to foundation:

1. Is it truly cross-cutting? (Pragmatism is — it applies whether you are reviewing code, writing docs, or shipping a release.)
2. Can it be expressed in ≲150 lines of essential rules? If not, split: kernel in foundation, body in a category.
3. Would removing it break the system, or merely make it less elegant? If only the latter, keep it as a category skill.

---

## See also

- [`registry.yaml`](../registry.yaml) — the canonical index the librarian reads.
- [`templates/skill-template.md`](../templates/skill-template.md) — the SKILL.md scaffold every skill follows.
- [`docs/skills-bridge.md`](skills-bridge.md) — how the garden is consumed live by other repos.
