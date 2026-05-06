---
name: chesterton-fence
description: >
  Before deleting, refactoring, or "cleaning up" code that looks unused,
  redundant, or weird, investigate why it exists. Produces a
  why-it-exists memo plus an edge-case checklist that must be confirmed
  before any change to the existing code is committed. Implements the
  Chesterton's-Fence side of Validate-Before-Trust under Aparigraha.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, pragmatism, pragya"
  reasoning_mode: plan-execute
---


# Chesterton's Fence

> _"Don't tear down a fence until you know why it was put up.
> Especially in production code, where the absence of the problem the
> fence solves is the very evidence the fence is doing its job."_

## Context

Invoked whenever the agent is about to delete, refactor, modify, or
"clean up" existing code that looks unused, redundant, mysterious, or
"obviously wrong". The skill enforces an investigation protocol before
any such change is committed. It produces:

1. A **why-it-exists memo** — the best available reconstruction of the
   code's purpose, drawn from history, tests, comments, and call-graph.
2. An **edge-case checklist** — what behaviours the existing code
   guarantees today, that any change must preserve (unless explicitly
   altering them).

The skill is the "look before you remove" companion to `reuse-first`'s
"look before you write". Together they form the read-first half of
Aparigraha.

## Scope

**In scope:**

- Detecting that a delete / refactor / "cleanup" of existing code is
  about to occur.
- Reconstructing intent from git history, ticket links, comments, tests,
  ADRs, and call sites.
- Producing the why-it-exists memo and the edge-case checklist.
- Gating the change until the checklist is green or explicitly accepted
  by the user.

**Out of scope:**

- Performing the refactor itself — owned by `refactoring`.
- Removing dead code — owned by `cleanup` (which must consult this
  skill first when the candidate is non-trivial).
- Adding new utilities — owned by `reuse-first`.
- Diff-size discipline — owned by `minimal-diff`.
- Plan-vs-diff alignment — owned by `auditor`.

---

## Micro-Skills

### 1. Trigger Detection 🌿 (Eco Mode)

**Goal:** Identify candidates that require investigation before change.

**Trigger conditions** (any of):

- The change deletes a function, class, file, configuration flag,
  feature toggle, environment variable, or migration step.
- The change removes or rewrites a guard clause, defensive check,
  retry, sleep, timeout, fallback, or default value.
- The change modifies a function older than the agent's onboarding window
  (default: 90 days unchanged, or pre-existing in the repo).
- The change touches anything labelled `TODO`, `FIXME`, `HACK`, `NOTE`,
  `WARN`, `XXX`, `WORKAROUND`, or `LEGACY`.
- The change involves code with no tests covering its current behaviour.
- The agent's reasoning includes "this looks unused", "this seems
  pointless", "this is weird", "this is dead code", or "obviously
  redundant".

**Steps:**

1. When any trigger fires, pause the change.
2. Hand the candidate over to micro-skills 2–4 to build the memo.

### 2. Reconstruct Intent ⚡ (Power Mode)

**Goal:** Find the strongest evidence of why the code exists.

**Evidence sources** (use them all that apply):

| Source                                           | What it tells you                                       |
|--------------------------------------------------|---------------------------------------------------------|
| `git log -p -- <path>`                           | Original author, original commit message, evolution.    |
| `git blame <path>`                               | Per-line origin; identify the line that introduced the candidate. |
| Pull request / merge commit linked from blame    | Discussion, reviewers' concerns, accepted trade-offs.   |
| Linked issue / ticket (Jira, GitHub, Linear)     | Business context, user-reported symptom, fix rationale. |
| `CHANGELOG.md` / release notes                   | When and why the code shipped.                          |
| ADRs (`docs/adr/`, `architecture/decisions/`)    | Architectural rationale.                                |
| Inline comments in or near the candidate         | Author's stated intent.                                 |
| Tests that exercise the candidate                | Behavioural contract; edges the author cared about.     |
| Reverse call-graph (callers, callers' callers)   | Where the code is needed and why.                       |
| Runtime / log search                             | Whether the code path is exercised in production.       |
| Telemetry / analytics                            | How frequently the path is hit.                         |

**Steps:**

1. **Nano: Blame the introducing line** — `git blame -L <range> <file>`
   to find the commit that introduced the candidate.
2. **Nano: Read the introducing commit message and PR** — capture the
   stated reason verbatim.
3. **Nano: Find the linked ticket** — read it; extract user impact,
   reproduction case, accepted trade-off.
4. **Nano: Walk the reverse call-graph** — `rg`, IDE references, or
   language-specific "find all callers". Identify all current call sites
   and any tests pinning behaviour.
5. **Nano: Search runtime evidence** — if logs/metrics are accessible
   for this code path, sample the last N days. "Looks unused" is much
   stronger evidence when telemetry says zero hits.
6. Aggregate the findings.

### 3. Why-It-Exists Memo 🌿 (Eco Mode)

**Goal:** Produce a short, persistable record of the candidate's intent.

**Memo template:**

```markdown
# Why does <candidate> exist?

- **Candidate:** <path>:<symbol>
- **Introduced:** <commit-sha>, <date>, by <author>
- **Original intent (stated):** <one or two sentences from the commit/PR>
- **Linked ticket:** <id, title, link>
- **Behavioural contract:** <what callers depend on; bullet list>
- **Edge cases the original author cared about:** <bullet list>
- **Current call sites:** <list, or "none found in source">
- **Runtime evidence (if available):** <hits over last N days; or "no telemetry">
- **Tests pinning behaviour:** <list of tests, or "none">
- **Risk of removal/change:** <low | medium | high>, <why>
- **Confidence in the reconstruction:** <high | medium | low>, <why>
```

**Steps:**

1. Fill in each section. If a section is genuinely unknown, mark it
   `unknown` — never guess.
2. The memo is materialised in memory. If the user opts in, persist it
   under `docs/chesterton/<candidate>.md` so the next agent doesn't
   redo the work.
3. The memo accompanies the diff in any review request the agent
   produces.

### 4. Edge-Case Checklist ⚡ (Power Mode)

**Goal:** Convert the reconstructed intent into a list of behaviours the
proposed change must either preserve or explicitly alter.

This checklist mirrors the Aparigraha checklist defined in the
foundation `pragmatism` skill, extended with candidate-specific items
drawn from the memo.

| Edge case category    | Confirm by…                                                                          |
|-----------------------|--------------------------------------------------------------------------------------|
| Empty / null inputs   | Read the candidate's tests/source; check post-change behaviour matches.              |
| Boundary values       | Min, max, zero, negative, off-by-one, overflow, underflow.                           |
| Type variance         | Unicode, locale, timezone, NaN/Infinity, large numbers.                              |
| Concurrency           | Reentrancy, thread-safety, idempotence, ordering guarantees.                         |
| Failure paths         | Behaviour on exception, timeout, partial / malformed input.                          |
| Performance envelope  | Documented complexity; behaviour on large inputs.                                    |
| Backward compatibility| Will the change alter observable behaviour for existing callers / dependents?        |
| Configuration / env   | Behaviour under non-default flags / env vars / feature toggles.                      |
| Telemetry / contracts | Logs, metrics, error codes, schema commitments external systems consume.             |
| Domain-specific edges | Edges the **business** cares about (e.g., zero-amount payments, leap seconds, GST). |

**Plus, candidate-specific rows from the memo:**

- Each "edge case the original author cared about" becomes a row.
- Each linked ticket's reproduction case becomes a row.
- Each test that pins behaviour becomes a row.

**Steps:**

1. Build the checklist as `[{category, requirement, evidence,
   status}]`, where status is `preserved`, `intentionally-changed`,
   `N/A with reason`, or `unconfirmed`.
2. For each `intentionally-changed` row, the user must explicitly
   confirm — this is a behavioural change, not a transparent refactor.
3. For each `unconfirmed` row, either characterise via test, escalate
   to the user, or downgrade the change to "leave as-is, surface as
   follow-up".
4. The change does not commit until no row is `unconfirmed`.

### 5. Decision & Recording ⚡ (Power Mode)

**Goal:** Decide whether to proceed, modify, or stop.

**Decision matrix:**

| Memo confidence | Risk of removal | Default action                                          |
|-----------------|-----------------|---------------------------------------------------------|
| High            | Low             | Proceed. Document the memo + checklist alongside diff.  |
| High            | Medium          | Proceed only if checklist is fully green.               |
| High            | High            | Mandatory user approval (Pragya), even if green.        |
| Medium          | Any             | Add a characterisation test that pins current behaviour, then proceed only if green. |
| Low             | Any             | Do not change; surface candidate as a follow-up to investigate further. |

**Steps:**

1. Compute the decision from confidence × risk.
2. Emit the memo + checklist + decision to the user (or the audit log
   in autonomous mode).
3. If `Proceed`: hand the change off to `refactoring` / `cleanup` /
   `minimal-diff` for execution.
4. If the candidate is a fence guarding production behaviour, prefer a
   **deprecation path** (mark, soak, then remove) over an immediate
   removal — this preserves the fence while observing whether anyone
   "leans on it".

---

## Inputs

| Parameter                | Type       | Required | Description                                                       |
|--------------------------|------------|----------|-------------------------------------------------------------------|
| `candidate`              | `object`   | yes      | `{path, symbol, kind: function|class|file|flag|guard|...}`        |
| `proposed_change`        | `enum`     | yes      | `delete` \| `refactor` \| `modify` \| `inline` \| `replace`.      |
| `repo_root`              | `string`   | yes      | Absolute path to the repository root.                             |
| `evidence_sources`       | `string[]` | no       | Limit which sources to consult (e.g., no telemetry available).    |
| `persist_memo_to`        | `string`   | no       | Path to persist the memo. Otherwise in-memory.                    |

## Outputs

| Field                  | Type     | Description                                                              |
|------------------------|----------|--------------------------------------------------------------------------|
| `memo`                 | `object` | Structured why-it-exists memo, including confidence and risk.            |
| `checklist`            | `object[]` | Edge-case checklist with per-row status.                               |
| `decision`             | `enum`   | `proceed` \| `proceed-with-deprecation` \| `add-characterisation-test-then-proceed` \| `do-not-change-yet`. |
| `unconfirmed_rows`     | `object[]` | Any rows that block the decision.                                      |
| `recommended_followups`| `string[]` | Items the user may want to track separately.                           |

---

## Guardrails

- **No silent removals.** Every delete/refactor of pre-existing code
  must have a memo and a green checklist (or explicit user override).
- **Prefer deprecation over deletion** when the fence may be guarding
  production behaviour. Mark, soak, observe, then remove in a follow-up.
- **Telemetry is evidence; absence is not.** "I couldn't find a caller"
  is weaker than "logs show zero hits in 90 days".
- **Tests are evidence; absence is also evidence.** Code with no tests
  has no checked-in behavioural contract — treat with extra caution.
- **Aparigraha defers to Ahimsa.** If the candidate is itself a
  correctness or security fix, do not interpret "leave it alone" as the
  default. Investigate, but be willing to change.
- **The user steers (Pragya).** If the user explicitly rejects the
  decision, honour it; record the override.

## Ask-When-Ambiguous

**Triggers:**

- The introducing commit message is empty / "fix" / "wip" / similar.
- No linked ticket is found, no comments, no tests, no callers.
- The candidate is a guard / sleep / retry whose absence might surface
  intermittent problems weeks later.
- The candidate is a configuration flag with non-default values in
  production environments.
- Memo confidence is low and risk is non-trivial.

**Question Templates:**

- "I found no record of why `[candidate]` exists. Last touched
  `[N]` months ago by `[author]`, no tests, no callers in source.
  Want me to (A) leave it (default), (B) deprecate (mark, soak,
  remove later), or (C) remove now and accept the risk?"
- "`[candidate]` looks like a guard against `[symptom]`, but I can't
  find evidence of `[symptom]` happening recently. Remove the guard,
  add a regression test for `[symptom]` first, or leave it?"
- "Removing `[candidate]` would change behaviour for `[edge case]`.
  Is this intentional? If yes, this is a behavioural change, not a
  refactor."

## Decision Criteria

| Situation                                                                  | Action                                                                  |
|----------------------------------------------------------------------------|-------------------------------------------------------------------------|
| Memo confidence high, risk low, checklist all green                        | Proceed. Document the memo + checklist with the diff.                   |
| Memo confidence high, risk medium                                          | Proceed only with a green checklist.                                    |
| Memo confidence high, risk high                                            | Mandatory user approval, even with a green checklist.                   |
| Memo confidence medium                                                     | Add a characterisation test pinning current behaviour, then proceed.    |
| Memo confidence low                                                        | Do not change yet; surface as a follow-up needing investigation.        |
| Candidate is a guard against an unobserved symptom                         | Prefer deprecation (mark, soak, observe) over deletion.                 |
| Candidate has no tests and no callers                                      | Soft-remove via deprecation; do not hard-delete in one step.            |
| Telemetry shows zero hits over a long window                               | Confidence in "unused" is high; still prefer deprecation for the soak.  |
| User explicitly says "yes, remove it"                                      | Honour the override; record it in the audit log with the user's reason. |

## Success Criteria

- Every change to pre-existing code lands with an attached memo and
  green checklist (or an explicitly recorded user override).
- No edge case the original author cared about regresses silently.
- Risky candidates are deprecated, not deleted, on the first pass.
- Future readers can reconstruct *why* the change was safe without
  re-running the investigation.

## Failure Modes

- **Silent removal of a fence.** Agent deletes a guard clause whose
  absence triggers an intermittent production bug weeks later.
  **Recovery:** Restore the guard. Add the missed edge case to the
  checklist. Open an incident postmortem if the bug shipped.

- **"No callers" too quickly concluded.** Agent searched only by exact
  name; the candidate is invoked by reflection / dependency injection /
  string lookup.
  **Recovery:** Re-search by string of the symbol name, by class
  reference patterns, by config keys. Surface the indirection in the
  memo.

- **Reconstruction by hallucination.** Agent guesses an intent it
  cannot evidence.
  **Recovery:** Mark unknown sections `unknown`. Lower confidence.
  Default to deprecation rather than removal.

- **Deprecation forever.** Marked-but-never-removed code accumulates.
  **Recovery:** When deprecating, add an expiry date / ticket / soak
  duration. Track. Hard-remove on schedule, after the second
  Chesterton pass confirms no leaning.

- **Aparigraha used as an excuse to leave a real bug in place.** The
  candidate is itself a bug, not a fence.
  **Recovery:** Aparigraha does not override Satya/Ahimsa. If the
  candidate is wrong, change it; the memo just becomes the rationale.

## Audit Log

```
[chesterton-engaged]      candidate="{path:symbol}" change={delete|refactor|...}
[evidence-collected]      sources={list} blame_sha={sha} pr_link="{url}" tests={count} callers={count}
[memo-built]              confidence={high|medium|low} risk={low|medium|high} stored_at="{path|memory}"
[checklist-built]         rows={N} preserved={N} intentional_changes={N} unconfirmed={list}
[decision]                outcome={proceed|deprecate|test-first|do-not-change} reason="{summary}"
[user-override]           original_decision={x} new_decision={y} user_reason="{why}"
[deprecation-scheduled]   candidate="{path:symbol}" soak_period="{duration}" remove_after="{date|ticket}"
```

---

## Examples

### Example 1 — The mysterious sleep

**Candidate:**

```python
# in src/payments/dispatcher.py
time.sleep(0.25)  # introduced 2 years ago
```

**Investigation:**

```text
git blame      → introduced in commit "fix flaky payment test" (no PR link)
git log search → ticket PAY-1142: "Race between dispatcher and provider webhook"
tests          → tests/payments/test_dispatcher.py::test_concurrent_dispatch
callers        → only the dispatcher itself
telemetry      → zero observed races since the sleep was added
```

**Memo (excerpt):**

```text
- Original intent: prevent a race between dispatch and provider webhook.
- Risk of removal: HIGH — race condition may resurface under load.
- Confidence: HIGH (ticket + test pin the behaviour).
```

**Decision:** **Do not delete the sleep yet.**
Recommended action: replace the sleep with an explicit synchronisation
primitive (event / lock / queue) in a separate, properly-tested change
— do not just remove it because "it looks like a hack".

### Example 2 — The truly unused helper

**Candidate:**

```ts
// src/utils/legacy/buildV1Url.ts
export function buildV1Url(input: V1Input): string { ... }
```

**Investigation:**

```text
blame                      → introduced 4 years ago for the V1 API
ticket linked              → API-203: "V1 URL builder for legacy clients"
ADR docs/adr/0017-v2-api.md → "V1 retired 2024-Q3"
callers in source          → 0
runtime telemetry          → 0 calls in 12 months across all environments
tests                      → tests reference V1 only via this builder
```

**Memo:**

```text
- Confidence: HIGH
- Risk of removal: LOW (V1 is decommissioned)
```

**Decision:** **Proceed with deprecation, then deletion.**
Pass 1: rename to `_legacy_buildV1Url`, mark `@deprecated`, soak for one
release, watch for surprise calls. Pass 2: delete the function and its
tests in a follow-up commit.

### Example 3 — The mysterious guard

**Candidate:**

```java
if (request.getHeaders().containsKey("X-Legacy-Charset")) {
    request = request.copy().withCharset(StandardCharsets.ISO_8859_1).build();
}
```

**Investigation:**

```text
blame          → introduced 3 years ago, commit "fix: legacy client charset"
linked ticket  → INC-552: "POS terminals send ISO-8859-1, server assumed UTF-8"
callers        → all incoming requests
tests          → none specifically pin the charset behaviour
telemetry      → header present on ~0.4% of requests, 24/7
```

**Memo:**

```text
- Confidence: HIGH (incident ticket).
- Risk of removal: HIGH (POS terminals still send the header).
```

**Decision:** **Do not remove.**
Recommendation: write the missing characterisation test that pins this
behaviour, so the fence is documented in tests too, not only in
production code. Surface as a follow-up.

---

## Edge Cases

- **The candidate is generated code.** Generated code is governed by its
  generator; investigate the generator's input, not the generated
  artifact. Removing generated code without changing the generator
  causes the next regeneration to bring it back.

- **The candidate is in vendored / third-party code.** Do not modify
  vendored code; defer to the vendor's release process. If the vendor
  code looks broken, the change goes upstream, not into your fork.

- **The candidate is a feature flag.** Investigate the rollout state.
  Removing a feature flag while it is still 50% rolled out is a
  behavioural change, not a cleanup.

- **The candidate looks dead but uses reflection / DI / string lookup.**
  Search by symbol name as a string, by config keys, by deserialised
  class names, before concluding "no callers".

- **The candidate is a test helper used only in deleted tests.** Remove
  the helper as part of the same diff that removes the last test, not
  before. Otherwise you fragment the change.

- **The introducing commit is from before the project's git history
  began.** Treat as low confidence. Default to deprecation. Search
  doc/wiki/issue tracker for the candidate name.

- **The candidate is yours, written in this same session.** This skill
  still applies — but trust your own audit log over reconstruction. If
  you wrote it five minutes ago and now want to change it, you already
  have the memo.

- **The user says "I wrote it, just remove it."** Honour the override;
  record it. The user's word is sufficient evidence of intent.
