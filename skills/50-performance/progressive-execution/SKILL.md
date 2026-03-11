---
name: progressive-execution
description: >
  Return fast approximate results immediately (Phase 1), then enhance with
  slower enriched results (Phase 2). Phase 1 is standalone. Phase 2 is
  optional enhancement. If Phase 2 fails, Phase 1 stands.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad"
  reasoning_mode: linear
  skill_type: standard
---


# Progressive Execution

> _"Fast first. Enrich later. Never block on the slow path."_

## Context

Invoked when a system has both a fast path (cheap, approximate) and a slow path
(expensive, enriched), and the user experience benefits from seeing fast results
immediately while richer results load in the background. The core contract:
Phase 1 is standalone — Phase 2 is optional enrichment, never a correction.

## Scope

**In scope:** Phase 1/Phase 2 design, independence contract, delivery
mechanisms, and failure isolation.

**Out of scope:** Specific UI frameworks for rendering progressive results.
Caching strategies (see `caching-strategy`). Network optimization.

---

## Micro-Skills

### 1. Phase 1 Design 🌿 (Eco Mode)

**Goal:** Identify the minimal useful response.

**Steps:**

1. Ask: what is the fastest result that is **usable on its own**?
2. Phase 1 must be:
   - **Complete:** The user can act on it without waiting for Phase 2.
   - **Fast:** Typically <100ms for interactive systems, <1s for batch.
   - **Cheap:** Uses only local data, cached results, or lightweight lookups.
3. **Nano: Fast-Path Identification** — strip the operation down to its
   cheapest useful form. Keyword search instead of semantic search. Cached
   response instead of live query. Placeholder content instead of generated.
4. Phase 1 sets the baseline — Phase 2 can only improve it, never degrade it.
5. Design Phase 1 as if Phase 2 doesn't exist. It must work alone.

### 2. Phase 2 Design 🌿 (Eco Mode)

**Goal:** Identify enrichments that enhance Phase 1.

**Steps:**

1. List everything Phase 1 left out: higher fidelity results, additional
   data sources, computed insights, AI-generated content.
2. Prioritize enrichments by value-to-latency ratio — what adds the most
   value for the least additional wait?
3. Phase 2 enrichments are **additive** — they add information, improve
   ranking, enhance quality. They do NOT contradict or remove Phase 1 results.
4. Set a time budget for Phase 2 (e.g., 3 seconds for interactive, 30 seconds
   for batch).
5. If Phase 2 cannot improve on Phase 1 (e.g., same results), skip it
   entirely — don't waste resources.

### 3. Independence Contract 🌿 (Eco Mode)

**Goal:** Ensure Phase 1 and Phase 2 are decoupled.

**Steps:**

1. **Rule 1:** Phase 1 never depends on Phase 2. Phase 1 code path must not
   import, reference, or wait for Phase 2 logic.
2. **Rule 2:** Phase 2 never degrades Phase 1. If Phase 2 results are worse
   (fewer items, lower confidence), discard them.
3. **Rule 3:** Phase 2 failure is invisible to the user. Phase 1 results
   remain displayed. No error state from Phase 2 reaches the user.
4. **Nano: Phase Gate** — a boolean flag or parameter (e.g., `skipEnrichment=true`)
   that lets callers explicitly opt out of Phase 2.
5. Test the independence: disable Phase 2 entirely. Does Phase 1 still
   work perfectly? If yes → contract holds.

### 4. Delivery Mechanism 🌿 (Eco Mode)

**Goal:** How Phase 2 results reach the consumer.

**Steps:**

1. Choose a delivery pattern based on the consumer:
   - **Replace:** Phase 2 results replace Phase 1 entirely (search results).
   - **Augment:** Phase 2 adds to Phase 1 (additional metadata, scores).
   - **Stream:** Results arrive incrementally (streaming API, SSE).
   - **Placeholder swap:** Phase 1 renders placeholders that Phase 2 fills
     (skeleton UI → real content).
2. Show an indicator during Phase 2 (spinner, shimmer, "enhancing..." label)
   so the user knows more is coming.
3. **Nano: Debounce Before Phase 1** — if the trigger fires rapidly (e.g.,
   keystroke search), debounce before Phase 1 to avoid redundant work.
4. Cancel in-flight Phase 2 if the user triggers a new Phase 1 (e.g., new
   search query cancels old enrichment).

### 5. Failure Isolation 🌿 (Eco Mode)

**Goal:** Phase 2 failures are gracefully absorbed.

**Steps:**

1. Wrap Phase 2 in a try/catch or equivalent. Errors are logged, not thrown.
2. If Phase 2 times out: Phase 1 results stand. Remove the "enhancing..."
   indicator. Log the timeout.
3. If Phase 2 returns partial results: merge what's available, discard what's
   not. Partial enrichment is better than no enrichment.
4. Set a Phase 2 timeout (separate from Phase 1). Phase 2 must not block
   indefinitely.
5. Monitor Phase 2 failure rate. If consistently failing, consider disabling
   it (circuit breaker pattern — see `resilience-patterns`).

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `any` | yes | The trigger for both phases |
| `phase1_handler` | `function` | yes | Fast path handler |
| `phase2_handler` | `function` | no | Enrichment handler |
| `phase2_timeout` | `number` | no | Max time for Phase 2 (ms) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `result` | `any` | Final result (Phase 1 or Phase 1 + Phase 2 enrichment) |
| `source` | `string` | Which phases contributed (phase1_only, phase1+phase2) |
| `phase2_status` | `string` | completed, timeout, error, skipped |

---

## Guardrails

- Phase 1 must work without Phase 2 — test this explicitly.
- Phase 2 must never degrade Phase 1 results.
- Phase 2 errors are never surfaced to the user.
- Phase 2 has an explicit timeout — no unbounded waits.
- Debounce rapid triggers to prevent redundant Phase 1 executions.

## Ask-When-Ambiguous

**Triggers:**

- Unclear what constitutes "minimal useful" for Phase 1
- Phase 2 enrichment sometimes contradicts Phase 1 results
- Latency budget for Phase 2 is unclear

**Question Templates:**

1. "Is {fast-result} sufficient as a standalone result, or does the user need {enriched-data} before acting?"
2. "Phase 2 produces different ranking than Phase 1. Replace or augment?"
3. "What's the acceptable wait time for Phase 2 enrichment? {1s, 3s, 10s, no limit}?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Phase 1 is already high quality | Skip Phase 2 — no value added |
| Phase 2 latency > user patience | Reduce Phase 2 scope or increase timeout |
| Phase 2 frequently fails | Apply circuit breaker, fall back to Phase 1 only |
| Both phases needed for correctness | This pattern doesn't apply — use synchronous pipeline instead |

## Success Criteria

- [ ] Phase 1 returns within latency budget (fast path)
- [ ] Phase 2 enrichment visibly improves results
- [ ] Disabling Phase 2 doesn't break anything
- [ ] Phase 2 failure is invisible to the user
- [ ] Rapid triggers are debounced

## Failure Modes

- **Phase 2 blocks Phase 1** — Phase 1 waits for Phase 2 to start. **Recovery:** ensure Phase 1 is fire-and-forget; Phase 2 runs asynchronously.
- **Phase 2 contradicts Phase 1** — user sees results flip. **Recovery:** if Phase 2 results differ significantly, merge rather than replace.
- **Perpetual enrichment** — Phase 2 never completes. **Recovery:** strict timeout; cancel after budget exceeded.
- **Debounce too aggressive** — user waits for Phase 1 because debounce delays the trigger. **Recovery:** tune debounce window based on input cadence.

## Audit Log

- `[timestamp] phase-1-complete: duration={ms}, result-count={N}`
- `[timestamp] phase-2-started: timeout={ms}`
- `[timestamp] phase-2-complete: duration={ms}, enriched={N} items`
- `[timestamp] phase-2-skipped: reason={no-improvement|disabled|circuit-open}`
- `[timestamp] phase-2-timeout: after={ms}`

---

## Examples

### Example 1 — Search with AI Enrichment

**Phase 1 (50ms):** Keyword-only search. Returns 20 results ranked by text match.
**Phase 2 (2s):** AI semantic search. Re-ranks results by meaning similarity, adds relevance explanations.
**Delivery:** Replace — Phase 2 results replace Phase 1 ranking. "Enhancing results..." indicator shown during Phase 2.

### Example 2 — Dashboard with Analytics

**Phase 1 (200ms):** Load cached summary from last hour. Show charts with cached data.
**Phase 2 (5s):** Query live database for up-to-the-minute data. Update charts.
**Delivery:** Placeholder swap — Phase 1 fills charts, Phase 2 updates them in place.

---

## Edge Cases

- **Phase 2 faster than Phase 1:** Unusual but possible (cache hit on enrichment, cache miss on fast path). No harm — Phase 2 simply enriches immediately.
- **No Phase 2 handler:** Valid configuration. System operates as Phase 1 only. Progressive execution degrades to simple execution.
- **Phase 1 returns empty:** Still valid. Phase 2 may enrich with content. Or both empty = genuinely no results.
- **User navigates away:** Cancel in-flight Phase 2 to save resources. Use AbortController or equivalent.
