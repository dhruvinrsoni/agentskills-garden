---
name: orchestrator
description: >
  Lightweight mid-task skill injection engine. Monitors task context as it
  evolves, detects domain shifts, and suggests loading relevant skills.
  Modular and non-intrusive — can be enabled or disabled independently
  without affecting core direction-seeking or routing.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, librarian, pragya"
  reasoning_mode: linear
---

# Orchestrator — Mid-Task Skill Injection

> _"The right skill at the right time — not just at the start, but as the
> task evolves."_

## Context

The `librarian` routes skills at task inception: user asks for something, the
librarian finds the matching skill. But tasks evolve. A cleanup task uncovers
an architecture problem. A testing task reveals missing error handling. A
documentation task surfaces a security concern.

The orchestrator fills this gap: it monitors the task context as it changes
and surfaces skill suggestions mid-task, presented as `pragya` direction
checkpoints. It never auto-loads — the human always decides.

**Why it's modular:** The orchestrator is a separate foundation skill, not
embedded in pragya or librarian. If it consumes too many tokens or introduces
noise, the owner can disable it. Pragya still works for direction-seeking,
librarian still works for initial routing. Only mid-task injection is lost.

## Scope

**In scope:**

- Monitoring current task context for domain keywords and patterns
- Detecting when the task has shifted into a new domain
- Suggesting relevant skills from the registry based on the shift
- Supporting owner-defined activation triggers via metadata
- Presenting injection suggestions as pragya checkpoints

**Out of scope:**

- Initial skill routing — owned by `librarian`
- Direction-seeking protocol — owned by `pragya`
- Skill content or execution — each skill owns itself
- Modifying the registry or skill files at runtime

---

## Micro-Skills

### 1. Context Monitor

**Mode:** Eco

Lightweight tracking of what the current task is about, updated as the
agent works.

**Steps:**

1. At task start, extract domain keywords from the user's request and the
   loaded skill(s). Store as `active_domains`.
2. As work progresses, track new keywords from:
   - File types being read/edited (`.yml` → devops, `.test.ts` → testing)
   - Tool usage patterns (security grep → security, database queries → data)
   - Content discovered (error handling code, CI config, auth tokens)
3. Compare new keywords against `active_domains`. If a significant cluster
   of new keywords emerges that doesn't match the active domain → flag as
   a domain shift.

**Domain keyword map (reference, not exhaustive):**

| Keywords | Domain | Suggested Skills |
|----------|--------|------------------|
| test, spec, coverage, assert, mock | Quality | `unit-testing`, `test-strategy` |
| deploy, ci, pipeline, workflow, docker | DevOps | `ci-pipeline`, `docker-containerization` |
| auth, token, jwt, rbac, oauth | Security | `auth-implementation`, `secure-coding-review` |
| schema, migration, index, query | Database | `database-design`, `db-tuning` |
| api, endpoint, contract, openapi | Architecture | `api-contract-design`, `api-implementation` |
| error, exception, retry, fallback | Implementation | `error-handling`, `resilience-patterns` |
| perf, cache, slow, bottleneck | Performance | `profiling-analysis`, `caching-strategy` |
| readme, docs, changelog, release | Documentation | `readme-generation`, `changelog-generation` |
| cleanup, dead code, unused, stale | Maintenance | `repo-maintenance`, `cleanup` |
| refactor, extract, rename, decouple | Implementation | `refactoring`, `refactoring-suite` |
| score, rank, weight, evaluate, priority | Architecture | `scorer-pipeline` |
| config, settings, defaults, feature-flag | Architecture | `schema-driven-config` |
| pipeline, context, middleware, pre-compute | Architecture | `pipeline-context` |
| circuit, breaker, bulkhead, timeout, resilience | Implementation | `resilience-patterns` |
| two-pass, metric, threshold, gate, lint | Quality | `two-pass-analysis` |
| progressive, phase, fast-first, enrich | Performance | `progressive-execution` |
| memory, pressure, budget, constraint, degrade | Performance | `resource-awareness` |

### 2. Skill Suggestion

**Mode:** Eco

When a domain shift is detected, suggest loading the relevant skill(s).

**Steps:**

1. Identify the shifted domain from the context monitor.
2. Look up matching skills in the registry by tags and description.
3. Present as a pragya-style direction checkpoint:
   ```
   This task has moved into [domain] territory. I can continue with
   general knowledge, or load the `[skill-name]` skill for domain-
   specific best practices.

   Options:
   1. Load [skill] — get specialized guidance
   2. Continue without — I'll use general knowledge
      ← Recommended: Option [N] — [rationale]
   ```
4. If user accepts → load the skill content and apply its micro-skills.
5. If user declines → proceed with caution, flag any domain-specific
   uncertainties for pragya checkpoints.

**Rules:**

- Never auto-load without user consent. Pragya principle: human steers.
- Suggest at most 2 skills per checkpoint. More than that = noise.
- If the same domain was already flagged and declined, don't suggest again
  unless the context deepens further.

### 3. Activation Triggers

**Mode:** Eco

Skills can declare activation patterns — keywords or conditions that should
surface them proactively. The orchestrator scans for these patterns.

**Steps:**

1. At startup, read all skill Context sections and any `activation_triggers`
   in metadata for trigger patterns.
2. As the task progresses, match incoming context against these patterns.
3. If a trigger fires → present as a skill suggestion (micro-skill 2).
4. Triggers are advisory — they surface suggestions, they never force-load.

**Owner control:** The repo owner can add manual triggers via metadata:
```yaml
metadata:
  activation_triggers: "when user mentions cleanup, reduce size, trim, optimize"
```

This gives the owner fine-grained control over when specific skills are
suggested, without modifying the orchestrator itself.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `active_domains` | `string[]` | no | Currently active domain keywords |
| `registry` | `string` | no | Path to registry.yaml (auto-detected) |
| `task_context` | `string` | no | Running summary of current task state |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `domain_shift` | `boolean` | Whether a domain shift was detected |
| `shifted_to` | `string` | The new domain detected |
| `suggested_skills` | `string[]` | Skills suggested for loading |
| `trigger_fired` | `string` | Which activation trigger matched |

---

## Guardrails

- **Never auto-load.** All skill injections require user consent via a pragya
  checkpoint. The human steers, always.
- **Lightweight monitoring.** Context tracking is keyword-based, not
  semantic analysis. No heavy computation — this must not eat tokens.
- **At most 2 suggestions per checkpoint.** More than that creates noise
  and checkpoint fatigue.
- **No repeat suggestions.** If a skill was suggested and declined, don't
  suggest it again unless the context has significantly deepened.
- **Graceful degradation.** If the orchestrator is disabled, everything
  else works. Pragya still seeks direction. Librarian still routes at
  start. Only mid-task injection is lost.

## Ask-When-Ambiguous

**Triggers:**

- Domain shift is ambiguous (keywords match multiple domains equally)
- Multiple skills could serve the shifted domain
- Context monitor is uncertain whether the shift is real or incidental

**Question Templates:**

- "I'm seeing [domain] patterns emerge in this task. Should I load the
  `[skill]` skill, or is this tangential?"
- "This could be a [domain-A] or [domain-B] concern. Which feels more
  relevant to what you're doing?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Clear domain shift, one matching skill | Suggest the skill |
| Ambiguous shift, multiple matches | Present options, let user choose |
| Same domain as current task | No action — already covered |
| Shift detected but skill already loaded | No action — already available |
| Owner trigger fires | Suggest the associated skill |
| User previously declined this domain | Don't suggest again (unless context deepened) |
| Orchestrator disabled | No action — graceful degradation |

## Success Criteria

- Domain shifts detected within 2–3 tool calls of the shift occurring.
- Skill suggestions are relevant — user accepts more than declines.
- Zero auto-loading — every injection is user-approved.
- No more than 1–2 injection checkpoints per task (avoid fatigue).
- Graceful when disabled — no errors, no side effects.

## Failure Modes

- **False positive shift.** A tangential keyword triggers an unnecessary
  suggestion.
  **Recovery:** Require a cluster of keywords (3+), not a single match.
  Tune the domain keyword map based on false positives.

- **Missed shift.** Task moves into a new domain without detection.
  **Recovery:** Pragya's own skill injection request micro-skill serves as
  a backup — the agent can still manually suggest loading a skill.

- **Checkpoint fatigue.** Too many injection suggestions interrupt flow.
  **Recovery:** Batch related suggestions. Limit to 1–2 per task. Respect
  user's "just do it" mode.

- **Stale triggers.** Activation triggers in metadata become outdated as
  skills evolve.
  **Recovery:** Validate triggers during `validate_skills.py` runs. Flag
  triggers that reference non-existent keywords.

## Audit Log

```
[context-updated]     domains=[{active list}] new_keywords=[{additions}]
[domain-shift]        from="{old}" to="{new}" confidence={N} keywords=[{triggers}]
[skill-suggested]     skill={name} domain={domain} accepted={bool}
[trigger-fired]       trigger="{pattern}" skill={name} source={metadata|context}
[injection-declined]  skill={name} reason="{user reason if given}"
```

---

## Examples

### Example 1 — Testing Task Uncovers Missing Error Handling

**Context:** Agent is writing unit tests for `PaymentService.ts`.

**Domain shift detected:** Multiple `try/catch` blocks are empty. Keywords
`error`, `exception`, `fallback` emerge from the code being tested.

**Suggestion:**
```
While writing tests, I found PaymentService has no error handling for
failed API calls. This is a [quality → implementation] domain shift.

Options:
1. Load `error-handling` skill — fix the handlers, then test them
2. Continue testing as-is — note the gap for later
   ← Recommended: Option 1 — testing brittle code yields brittle tests
```

### Example 2 — Cleanup Discovers CI Configuration Issues

**Context:** Agent is cleaning up unused files in a monorepo.

**Domain shift detected:** Several stale `.github/workflows/*.yml` files
reference packages that were removed months ago.

**Suggestion:**
```
Found 3 GitHub Actions workflows referencing deleted packages. This
has shifted from [maintenance → devops].

Options:
1. Load `ci-pipeline` skill — audit and fix the workflows properly
2. Just delete the stale workflow files — quick but no validation
   ← Recommended: Option 1 — stale CI can cause silent failures
```

### Example 3 — Owner Trigger Fires

**Metadata trigger:** `activation_triggers: "when user mentions optimize, performance, slow"`

**Context:** User says "this page is loading really slowly."

**Trigger fires:**
```
Your mention of slow loading matches the performance domain. Should
I load `profiling-analysis` for bottleneck identification?
```

---

## Edge Cases

- **Rapid domain shifts.** Task bounces between domains quickly (test → CI →
  error handling → test). Buffer suggestions — only surface after the shift
  stabilizes for 2+ tool calls.

- **Already-loaded skill.** If the relevant skill is already in context,
  don't suggest loading it again. Check before presenting.

- **No matching skill.** Domain shift detected but no skill in the garden
  covers it. Log the gap. Don't suggest a tangential skill as a substitute.

- **Orchestrator disabled mid-task.** If the user disables mid-task, stop
  monitoring immediately. Don't queue up pending suggestions. Clean exit.

- **Cascading injections.** Loading skill A triggers a context change that
  suggests skill B, which triggers skill C. Cap at 2 injections per task to
  prevent chain reactions. After the cap, log but don't suggest.
