---
name: scorer-pipeline
description: >
  Decompose complex evaluation into independent, composable micro-scorers
  with shared context and explicit weights. Universal pattern for any
  multi-factor ranking or assessment system.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad"
  reasoning_mode: linear
  skill_type: standard
---


# Scorer Pipeline

> _"One scorer per signal. Combine with weights. Tune with data."_

## Context

Invoked when a task requires ranking, prioritizing, or scoring items based on
multiple independent factors. Examples: search relevance, code quality
assessment, risk scoring, candidate prioritization, feature request triage.

## Scope

**In scope:** Designing scorer decomposition, shared context objects, weight
calibration, pipeline assembly, and post-pipeline boosters.

**Out of scope:** Domain-specific scorer implementations (those belong in the
domain skill). UI rendering of scores. Storage of scored results.

---

## Micro-Skills

### 1. Scorer Decomposition 🌿 (Eco Mode)

**Goal:** Break a complex evaluation into independent micro-scorers.

**Steps:**

1. List all factors that contribute to the final score.
2. For each factor, ask: can this be evaluated independently of other factors?
3. If yes → one scorer per factor. If no → combine dependent factors into one
   scorer and document why.
4. Each scorer implements a single interface: `score(item, query, context) → number`.
5. Verify: no scorer reads another scorer's output (independence constraint).

**Decision criteria for granularity:**

| Signal count | Approach |
|-------------|----------|
| 1-2 signals | Inline scoring — no pipeline needed |
| 3-5 signals | Standard pipeline — one scorer per signal |
| 6+ signals | Grouped pipeline — cluster related signals, one scorer per cluster |

### 2. Shared Context Design 🌿 (Eco Mode)

**Goal:** Pre-compute expensive data once, pass to all scorers.

**Steps:**

1. **Nano: Context Pre-computation** — identify operations used by 2+ scorers
   (tokenization, frequency counts, embeddings, lookups). Compute once at
   pipeline entry, store in a shared context object.
2. Define the context interface: what fields exist, what types, who populates them.
3. Context is **read-only** for scorers — only the pipeline owner writes to it.
4. Lazy-compute optional fields (e.g., embeddings only computed if an
   embedding-scorer is registered).

### 3. Weight Calibration ⚡ (Power Mode)

**Goal:** Assign and tune weights per scorer.

**Steps:**

1. Start with equal weights (1.0 each) as baseline.
2. **Nano: Weight Sensitivity Analysis** — vary one weight at a time ±50%,
   observe output ranking changes. High sensitivity = high impact scorer.
3. Adjust weights based on domain priority (what matters most to users?).
4. Document the rationale for each weight — future maintainers need to know
   *why*, not just *what*.
5. Consider A/B testing weights in production if the domain supports it.

**Weight calibration table:**

| Scorer | Initial | Calibrated | Rationale |
|--------|---------|-----------|-----------|
| `<scorer-a>` | 1.0 | `<value>` | `<why>` |
| `<scorer-b>` | 1.0 | `<value>` | `<why>` |

### 4. Pipeline Assembly 🌿 (Eco Mode)

**Goal:** Compose scorers into an additive pipeline.

**Steps:**

1. Register scorers in an ordered array (order doesn't affect score, but aids
   debugging).
2. For each item: iterate scorers, compute `scorer.score(item, query, context)`.
3. **Nano: Additive Score Normalization** — multiply each scorer's output by
   its weight, sum all weighted scores. Optionally normalize to 0-1 range by
   dividing by the sum of weights.
4. Filter out items below a minimum score threshold.
5. Sort descending by composite score.

### 5. Post-Pipeline Boosters 🌿 (Eco Mode)

**Goal:** Apply orthogonal multipliers after aggregation.

**Steps:**

1. Boosters run *after* the additive pipeline — they are multiplicative, not additive.
2. Use for special cases: recency boost, freshness penalty, user preference
   multiplier, source trust factor.
3. Each booster: `boost(item, compositeScore, context) → adjustedScore`.
4. Boosters are optional — pipeline works without them.
5. Document why each booster exists and when to disable it.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `items` | `array` | yes | The items to score |
| `query` | `string` | yes | The query or criteria to score against |
| `scorers` | `array` | yes | Registered scorer functions with weights |
| `context` | `object` | no | Pre-computed shared context |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `ranked_items` | `array` | Items sorted by composite score |
| `score_breakdown` | `object` | Per-item, per-scorer score details |
| `context_stats` | `object` | What was pre-computed and reused |

---

## Guardrails

- Each scorer must be testable in isolation.
- Weights must be documented with rationale — no magic numbers.
- Pipeline must produce deterministic output for the same inputs.
- Never let one scorer dominate by having disproportionate output range — normalize scorer outputs to a consistent range before weighting.

## Ask-When-Ambiguous

**Triggers:**

- More than 8 independent signals identified (risk of over-engineering)
- Two factors appear correlated (should they be one scorer or two?)
- No clear priority among factors (weights unclear)

**Question Templates:**

1. "I've identified {N} independent scoring signals. Should I group related ones or keep them separate?"
2. "Factors {A} and {B} seem correlated. Combine into one scorer or keep independent?"
3. "What matters most for ranking: {factor-1}, {factor-2}, or {factor-3}?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Single factor dominates | Check if weight is justified; consider capping scorer output |
| All scores cluster together | Increase weight of differentiating scorer |
| New factor discovered mid-task | Add scorer without modifying existing ones (open-closed) |
| Performance bottleneck | Profile per-scorer latency; lazy-compute expensive context fields |

## Success Criteria

- [ ] Each scorer is independently testable
- [ ] Composite score correctly reflects intended priority
- [ ] Adding a new scorer requires only: create function + register + set weight
- [ ] Score breakdown is available for debugging
- [ ] Pipeline handles edge cases (empty input, single item, all zero scores)

## Failure Modes

- **Score inflation** — one scorer returns values 10x larger than others, dominating the composite. **Recovery:** normalize all scorer outputs to 0-1 range.
- **Context bloat** — shared context grows to include rarely-used fields. **Recovery:** lazy-compute optional fields; audit context usage.
- **Weight drift** — weights tuned for one dataset don't generalize. **Recovery:** re-calibrate with diverse samples; document calibration conditions.

## Audit Log

- `[timestamp] pipeline-assembled: {N} scorers, weights: {w1, w2, ...}`
- `[timestamp] items-scored: {count} items, top-score: {value}, bottom-score: {value}`
- `[timestamp] weight-calibrated: scorer "{name}" {old} → {new}, rationale: "{why}"`

---

## Examples

### Example 1 — Search Relevance Ranking

**Scorers:** text-match (0.35), recency (0.20), popularity (0.15), domain-authority (0.15), embedding-similarity (0.15)

**Context:** `{ tokens: ["search", "query"], queryEmbedding: [...], domainCounts: Map }`

**Flow:** Pre-compute tokens + embedding → run 5 scorers → additive aggregation → recency booster (×1.2 for items < 7 days) → sort → return top 20.

### Example 2 — Code Quality Assessment

**Scorers:** complexity (0.30), test-coverage (0.25), lint-violations (0.20), documentation (0.15), dependency-freshness (0.10)

**Context:** `{ ast: parsed, coverageReport: loaded, lintResults: cached }`

**Flow:** Parse AST once → run 5 scorers → aggregate → flag files below threshold → present ranked file list with score breakdown.

---

## Edge Cases

- **Zero items:** Return empty result immediately — no scorer invocation.
- **Single item:** Still run pipeline (score may be used for threshold gating, not just ranking).
- **Scorer throws error:** Log error, exclude that scorer's contribution for the affected item, continue pipeline. Never fail the entire pipeline for one scorer.
- **All scores equal:** Return items in original order. Log warning — weights may need calibration.
