---
name: pragmatism
description: >
  Direction-of-thought protocol for working on real, ongoing business
  projects. Implements the Aparigraha pillar — non-accumulation of code,
  utilities, and refactors beyond what the task requires. Forces the agent
  to check before creating, conform within scope, stay surgical, and
  validate edge cases before trusting any reuse or improvement of existing
  code. Always loaded alongside the Constitution.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, pragya"
  reasoning_mode: linear
---


# Pragmatism — Aparigraha (अपरिग्रह)

> _"Check first. Reuse with care. Conform within scope. Validate every edge.
> The smallest correct change that survives production wins."_

## Kernel

Aparigraha — non-accumulation. Four directional gates on every change: (1) **Check-Before-Create** — search the codebase and declared dependencies for an equivalent before authoring anything new; (2) **Conform-Before-Improve** — match house style within scope, surface deviations as suggestions instead of silently rewriting; (3) **Surgical-Before-Sweeping** — produce the minimal diff that solves the problem, every change reversible in one step; (4) **Validate-Before-Trust** — whenever reusing or modifying existing code, walk the edge-case checklist (null/empty, boundaries, type/locale, concurrency, failure paths, performance envelope, domain edges, backward compatibility). **Checking is mandatory; reusing is conditional.**

## Context

Loaded alongside `constitution`, `scratchpad`, and `pragya` at the start of
every task. Real corporate codebases are almost never greenfield. The default
greenfield instincts of a code-generating agent — *"I'll just write a tidy
helper for this"*, *"let me clean this up while I'm here"*, *"the existing
style is ugly, I'll modernise it"* — are precisely the instincts that turn
small tasks into large diffs, large diffs into review fatigue, and review
fatigue into bugs.

Pragmatism implements **Aparigraha** — the principle of *non-accumulation*.
The agent must not accumulate code, utilities, abstractions, or refactors
beyond what the current task genuinely requires. This is a **direction of
thought**, not a rigid rulebook. The goal is to *give enough thought in this
direction* on every task — open-minded yet focused.

| What Aparigraha is              | What Aparigraha is not              |
|---------------------------------|-------------------------------------|
| A bias toward checking first    | A ban on writing new code           |
| A bias toward existing style    | A ban on best practices             |
| A bias toward smaller diffs     | A ban on necessary refactoring      |
| Trust-but-verify on reuse       | Blind reuse of any near-fit utility |
| Awareness of the project's ways | Enforcement of the project's ways   |

## Scope

**In scope:**

- Pre-implementation reasoning: should this code exist at all?
- Reuse-aware decision-making: what already exists in the codebase or
  dependency graph that solves this?
- Style awareness: what conventions does the project already follow, and how
  can the change conform to them within scope?
- Diff discipline: keep changes surgical, reversible, and on-topic.
- Edge-case validation as a precondition for any reuse or improvement
  decision.
- Routing into the `25-pragmatism` category skills for concrete execution.

**Out of scope:**

- Cognitive mode selection (Eco / Power) — owned by `scratchpad`.
- Direction checkpoints with the user — owned by `pragya`.
- Plan-vs-diff alignment after the fact — owned by `auditor`.
- Skill discovery and routing — owned by `librarian`.
- The actual library inventory and code-search — delegated to the
  `25-pragmatism` category skills.

---

## The Four Directional Principles

Every Aparigraha-aligned decision passes through these four gates, in order.
Each gate is a *bias*, not a *veto*; gates can be crossed with reason, but
never silently.

### 1. Check-Before-Create

> *Before authoring anything new, look for what already exists.*

- The agent must inspect the project's existing source for an equivalent
  function, class, pattern, or template before producing a new one.
- The agent must inspect the project's declared dependencies (BOM,
  `package.json`, `requirements.txt`, `Pipfile`, `go.mod`, `Cargo.toml`,
  etc.) for a battle-tested utility that already does the job.
- *Checking* is mandatory. *Reusing* is conditional — see Principle 4.
- If nothing fits, the agent may write fresh, but must record *why*
  (what was checked, why it didn't fit) in the audit log.

Delegated to: `reuse-first`, `dependency-utility-scout`.

### 2. Conform-Before-Improve

> *Match the project's idioms within the scope of the change. Best
> practices are a target, not a stick.*

- The agent must detect the project's existing conventions — naming case,
  error-handling pattern, logging style, test structure, comment style,
  module layout — and adopt them inside the diff it produces.
- The agent must NOT silently refactor existing code outside the scope of
  the requested change, even when "better" patterns are obvious.
- Deviations from current style are surfaced to the user, never auto-fixed.
- If the project's style violates a hard rule (security, correctness,
  data integrity), escalate via `pragya` — do not unilaterally rewrite.

Delegated to: `style-conformance`.

### 3. Surgical-Before-Sweeping

> *The smallest correct change that solves the problem wins.*

- The agent must produce the minimal diff that satisfies the requirement.
- No "while I'm here" expansions. No drive-by formatting. No opportunistic
  rename-everything passes.
- Out-of-scope improvements are recorded as suggestions, not applied.
- Every change must remain reversible in one step (`git revert` clean).

Delegated to: `minimal-diff`.

### 4. Validate-Before-Trust (the edge-case clause)

> *Reuse and improvement are only as safe as the edge cases they cover.*

The single most common failure mode of "leverage existing code" is the
**95% fit trap**: a library function or existing helper covers the happy
path but quietly misbehaves on nulls, empties, unicode, negative numbers,
boundary timestamps, locale-sensitive text, concurrent access, large
inputs, or domain-specific edge cases.

Whenever the agent decides to:

- reuse a library function or existing helper, OR
- conform to an existing pattern that touches new inputs, OR
- improve, modify, or remove existing code (Chesterton's Fence territory),

it MUST first run the **edge-case validation checklist**:

| Edge case category    | Question to confirm                                                                  |
|-----------------------|--------------------------------------------------------------------------------------|
| Empty / null inputs   | What does the candidate do on `null`, `""`, `[]`, `{}`, missing fields?              |
| Boundary values       | Min, max, zero, negative, off-by-one, overflow, underflow.                           |
| Type variance         | Unicode, locale, timezone, large numbers, NaN, infinities, signed/unsigned.          |
| Concurrency           | Reentrancy, thread-safety, idempotence, ordering guarantees.                         |
| Failure paths         | What does the candidate do on exception, timeout, partial success?                   |
| Performance envelope  | Behaviour on large inputs (10⁶+ elements), deeply nested structures, slow networks.  |
| Domain-specific edges | Edges the **business** cares about (e.g., zero-amount payments, leap seconds, GST).  |
| Backward compatibility| Will the change alter observable behaviour for existing callers / callers' callers?  |

The agent confirms each row is either **covered**, **N/A with reason**, or
**flagged for the user**. Reuse/improvement proceeds only when no row is
unconfirmed. If existing tests cover an edge, that counts as confirmation;
if not, the agent either adds a check, asks the user, or records the gap in
the audit log.

Delegated to: `reuse-first`, `chesterton-fence`, and consumed by every skill
that touches existing code.

---

## Invocation Triggers

Pragmatism is always loaded, but actively *fires* — i.e., produces a visible
guardrail check — when any of the following are true:

| Trigger                                                                  | Why it fires                                                            |
|--------------------------------------------------------------------------|-------------------------------------------------------------------------|
| Task involves writing a new utility / helper / wrapper function          | Check-Before-Create gate                                                |
| Task involves modifying or deleting existing code                        | Validate-Before-Trust + Chesterton's Fence                              |
| Task involves importing a new dependency                                 | Check-Before-Create — does an existing dependency already cover this?   |
| Task spans more than 1–2 files in scope                                  | Surgical-Before-Sweeping — confirm the spread is required               |
| Codebase appears to be brownfield (existing tests, ADRs, version > 0.1)  | Conform-Before-Improve — load the house-style profile                   |
| Refactor or "cleanup" requested without a specific behaviour change      | Surgical-Before-Sweeping — narrow the scope                             |
| Reuse of a library function whose contract isn't fully visible           | Validate-Before-Trust edge-case checklist                               |
| Onboarding to an unfamiliar project                                      | Routes to `brownfield-onboarding`                                       |

---

## Decision Tree — Where to Route

```text
Task arrives
   │
   ├─ Greenfield, single file, no existing dependencies? ──► proceed normally,
   │                                                         Aparigraha is dormant.
   │
   ├─ Need a utility / helper?                            ──► reuse-first
   │     │
   │     └─ "What's already imported?"                    ──► dependency-utility-scout
   │
   ├─ Touching existing code?                             ──► style-conformance (read)
   │     │                                                    + minimal-diff (write)
   │     │
   │     └─ Removing or refactoring "weird" code?         ──► chesterton-fence
   │
   ├─ Joining a new project for the first time?           ──► brownfield-onboarding
   │
   └─ Any reuse / improvement decision                    ──► run the edge-case
                                                              validation checklist
                                                              before committing.
```

---

## Inputs

| Parameter                | Type        | Required | Description                                                |
|--------------------------|-------------|----------|------------------------------------------------------------|
| `task_intent`            | `string`    | yes      | The user's stated goal, in plain language.                 |
| `target_files`           | `string[]`  | no       | Files the task is expected to touch.                       |
| `is_brownfield`          | `boolean`   | no       | Whether the project has prior history (ADRs, tests, tags). |
| `proposed_change_type`   | `enum`      | no       | `create` \| `modify` \| `delete` \| `refactor` \| `reuse`. |
| `candidate_reuse_target` | `string`    | no       | Name/path of the library function or helper being reused.  |

## Outputs

| Field                       | Type        | Description                                                       |
|-----------------------------|-------------|-------------------------------------------------------------------|
| `gates_passed`              | `string[]`  | Which of the four gates were checked and passed.                  |
| `delegations`               | `string[]`  | Category skills the agent must invoke (e.g., `reuse-first`).      |
| `edge_case_report`          | `object`    | Per-row status of the edge-case validation checklist.             |
| `style_profile_required`    | `boolean`   | Whether `style-conformance` must be loaded for this task.         |
| `documented_exceptions`     | `string[]`  | Cases where a gate was crossed with reason — explicit and logged. |

---

## Guardrails

- **Checking is non-negotiable.** Skipping the Check-Before-Create gate for
  any new utility, wrapper, or abstraction is a constitutional violation.
- **Reusing is not non-negotiable.** The agent is not required to reuse
  every near-fit utility. A documented "checked, didn't fit" is a valid
  outcome.
- **No silent style refactors.** If the agent notices style issues outside
  the change scope, it records them as suggestions; it does not commit them.
- **Edge cases gate trust.** Any reuse/improvement decision proceeds only
  after the edge-case checklist is confirmed.
- **Reversibility is required.** Every change must `git revert` cleanly
  without cascading failures.
- **Best practices are not weapons.** "This is the right way" is never
  sufficient justification to expand scope. Correctness and the user's
  stated intent are.
- **Aparigraha never overrides Ahimsa.** If a hard correctness, security,
  or data-integrity issue is found in existing code, escalate via `pragya`
  — do not stay silent in the name of minimalism.

## Ask-When-Ambiguous

**Triggers:**

- The user requested "cleanup" or "refactor" without a specific behaviour
  change in mind.
- A near-fit reuse candidate covers ~80–95% of the requirement; the gap is
  not obviously safe to accept.
- The project's existing style conflicts with a clear best practice the
  user might still want enforced.
- The agent has identified out-of-scope improvements that look valuable but
  exceed the requested diff.
- An existing piece of code looks pointless but predates the agent's view —
  Chesterton's Fence territory.

**Question Templates:**

- "I found `[existing.utility]` in `[dependency]` that covers about [N]% of
  this. Edge cases [list] are unconfirmed. Want me to (A) reuse and add
  guards, (B) reuse and ask you about each gap, or (C) write fresh?"
- "The existing pattern in this module is `[X]`. The textbook approach is
  `[Y]`. Within the scope of this change, should I (A) conform to `[X]`,
  (B) conform but flag the deviation as a follow-up, or (C) propose a
  scoped refactor?"
- "While solving the task I noticed [N] out-of-scope improvements
  ([summary]). Want me to (A) ignore, (B) record as suggestions, or
  (C) include in this diff?"
- "This code looks unused / odd, but it predates our context. Should I
  (A) leave it, (B) investigate via `chesterton-fence` first, or
  (C) remove it now?"

## Decision Criteria

| Situation                                                                | Action                                                                  |
|--------------------------------------------------------------------------|-------------------------------------------------------------------------|
| Existing utility found, edge cases all green                             | Reuse, log decision.                                                    |
| Existing utility found, ≥ 1 edge case unconfirmed                        | Trigger Ask-When-Ambiguous; do not reuse silently.                      |
| Nothing exists; need to write fresh                                      | Write fresh; log what was checked and why nothing fit.                  |
| Existing style differs from "best practice" inside scope                 | Conform to existing style. Log the deviation as a future follow-up.     |
| Existing style violates correctness / security                           | Escalate via `pragya`; do not stay silent.                              |
| Cleanup requested without specific target                                | Ask the user to scope it. Do not make a sweeping pass on assumption.    |
| Reuse candidate looks 100% fit but contract isn't documented             | Run edge-case checklist before trusting. Add a characterisation test.   |
| Touching existing code that looks unused                                 | Route to `chesterton-fence` first.                                      |

## Success Criteria

- Every new function/helper the agent writes is preceded by a logged
  "checked, didn't fit" entry, OR was explicitly approved by the user.
- Every reuse/improvement decision has a green edge-case checklist (or
  documented gaps that the user has acknowledged).
- Diffs stay within the requested scope; out-of-scope improvements are
  surfaced as suggestions, not committed.
- Style of the change matches the surrounding code's style by default.
- The `git revert` of any single Aparigraha-aligned commit succeeds cleanly.

## Failure Modes

- **The "while I'm here" sprawl.** Agent fixes formatting / renames /
  adds comments outside the requested scope.
  **Recovery:** Reset the diff to scope-only; record the extras as a
  separate suggestion list.

- **The 95% fit trap.** Agent reuses an existing utility that handles the
  happy path but breaks on `null` / unicode / boundary / concurrency.
  **Recovery:** Re-run the edge-case checklist; either add guards in the
  caller or escalate to the user. If already merged, file a follow-up.

- **Style perfectionism.** Agent rewrites surrounding code in "the right"
  style despite the project's clear convention.
  **Recovery:** Revert style changes outside scope; raise them via the
  Ask-When-Ambiguous channel, not through silent edits.

- **Premature generalisation.** Agent extracts a "reusable" helper after
  one use site, in violation of the Rule of Three.
  **Recovery:** Inline the helper back; revisit only when there are three
  real call sites.

- **Chesterton blindness.** Agent removes "obviously unused" code without
  investigating its origin.
  **Recovery:** Restore the code; route through `chesterton-fence` and the
  edge-case checklist.

- **Minimalism as an excuse.** Agent uses Aparigraha to justify ignoring
  a real correctness or security issue in existing code.
  **Recovery:** Aparigraha never overrides Ahimsa or Satya. Escalate via
  `pragya` and address the issue or document the deferral explicitly.

## Audit Log

```
[aparigraha-engaged]      task="{intent}" gates_required={list}
[gate-passed]             gate=check-before-create checked={list_of_paths_and_deps} chosen={reuse|fresh}
[gate-passed]             gate=conform-before-improve style_profile_loaded={true|false} deviations_logged={count}
[gate-passed]             gate=surgical-before-sweeping diff_files={N} out_of_scope_suggestions={count}
[gate-passed]             gate=validate-before-trust checklist_status={covered_count}/{total} unconfirmed={list}
[exception-recorded]      gate={name} reason="{why}" approved_by={user|self_with_reason}
[delegated]               to={category_skill} input={summary}
```

---

## Examples

### Example 1 — Reuse-aware utility decision

**Scenario:** The agent is asked to add a "trim, lowercase, and remove
extra internal whitespace" normaliser to a Java service that already
imports Apache Commons Lang.

**Aparigraha-aligned flow:**

```text
[gate-1: check-before-create]
- Searched src/main/java/.../utils/ → no existing normaliser.
- Inspected pom.xml → org.apache.commons:commons-lang3 is on the classpath.
- StringUtils.normalizeSpace(str) covers trim + collapse-whitespace.
- str.toLowerCase(Locale.ROOT) covers lowercase.

[gate-4: validate-before-trust — edge cases]
- null input          → StringUtils.normalizeSpace(null) returns null.   covered.
- empty string        → returns "".                                      covered.
- unicode whitespace  → normalizeSpace handles all Unicode whitespace.   covered.
- locale of lowercase → using Locale.ROOT to avoid Turkish-i bug.        covered.
- very large strings  → O(n), acceptable.                                covered.

Decision: reuse. Inline call site, no new helper class.
Logged: "Checked Apache Commons Lang StringUtils; reused normalizeSpace."
```

The agent does **not** create a `StringHelper.normalize()` wrapper.

### Example 2 — Conform-before-improve, scoped

**Scenario:** The agent is asked to fix a bug in a service. While reading
the file, it notices the project uses `if (foo == null) { return ...; }`
guard clauses everywhere, while the textbook style would prefer
`Optional<Foo>` chaining.

**Aparigraha-aligned flow:**

```text
[gate-2: conform-before-improve]
- Existing convention in 17/19 files: explicit null guards.
- Within scope of this bug fix, conform.
- Out-of-scope suggestion logged: "Consider migrating null guards to
  Optional in a separate ticket."

Decision: write the fix using explicit null guards, matching surrounding
code. Surface the migration idea, do not perform it.
```

### Example 3 — The 95% fit trap, caught

**Scenario:** The agent is asked to dedupe a list of records in a Node.js
service that imports Lodash.

**Aparigraha-aligned flow:**

```text
[gate-1: check-before-create]
- _.uniqBy(records, 'id') covers dedupe-by-id.

[gate-4: validate-before-trust — edge cases]
- empty array         → returns [].                                      covered.
- duplicate ids       → keeps first occurrence.                          covered (matches requirement).
- id is null/undefined→ groups all null-id records into one.             UNCONFIRMED — domain may want them dropped.
- case sensitivity    → strict equality, "ABC" != "abc".                 UNCONFIRMED — the source is mixed-case.

Decision: pause and ask the user.
```

The agent triggers an Ask-When-Ambiguous prompt rather than silently
reusing `uniqBy`.

---

## Edge Cases

- **No existing dependencies at all.** Project is genuinely greenfield.
  Aparigraha goes dormant on Check-Before-Create — you cannot check what
  doesn't exist — but Conform-Before-Improve still applies as soon as the
  *second* file is written.

- **The user explicitly says "rewrite this module."** Aparigraha steps
  back; the user has set the scope. The agent still runs Validate-Before-
  Trust on every piece of behaviour the rewrite must preserve.

- **The dependency exists but is deprecated / vulnerable.** Aparigraha
  defers to `dependency-scanning` and `secure-coding-review`. Reuse is
  not a higher value than safety.

- **The existing style is internally inconsistent.** Pick the variant most
  used in the immediate vicinity (file, then package, then module). Log
  the inconsistency as a separate suggestion.

- **Two equivalent existing utilities.** Prefer the one most used in the
  project today. If usage is tied, prefer the one in the more focused
  library (e.g., Apache Commons Lang over a project-local
  `StringHelper`).

- **The "right" abstraction emerges only after this task.** Resist
  extracting it now. Note the candidate, wait for the third call site
  (Rule of Three), then propose extraction in a follow-up.

- **The user disagrees with Aparigraha for this task.** The user always
  wins on direction (Pragya). Record the override in the audit log; do
  not litigate it.
