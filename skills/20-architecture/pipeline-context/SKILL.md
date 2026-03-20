---
name: pipeline-context
description: >
  Pre-compute expensive operations once and pass via shared context object
  to all pipeline stages. Eliminates O(n) recomputation in multi-stage
  processing.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad"
  reasoning_mode: linear
  skill_type: standard
---


# Pipeline Context

> _"Compute once, share everywhere. Context is the glue of pipelines."_

## Context

Invoked when building multi-stage processing pipelines — middleware chains,
scorer pipelines, build systems, request lifecycles, data transformation
flows. The core problem: stages independently repeat expensive operations
that could be computed once and shared.

## Scope

**In scope:** Context object design, pre-computation strategy, immutability
discipline, stage contracts, and context lifecycle management.

**Out of scope:** Specific pipeline frameworks (Express middleware, Gulp, etc.),
specific data formats, concurrent/parallel pipeline execution.

---

## Micro-Skills

### 1. Context Object Design 🌿 (Eco Mode)

**Goal:** Define what belongs in the shared context.

**Steps:**

1. Survey all pipeline stages — what does each stage compute or look up?
2. Identify data used by 2+ stages (shared) vs. data used by 1 stage (local).
3. Shared data goes into the context object. Local data stays in the stage.
4. Context contains: **pre-computed data**, **metadata** (timestamps, IDs),
   **configuration** (flags, thresholds). Context does NOT contain: mutable
   state that changes between stages, stage-specific scratch space.
5. Define the context interface/type — explicit fields, no arbitrary key-value
   bags.

**Context anatomy:**

| Field category | What goes here | Example |
|---------------|---------------|---------|
| Pre-computed | Expensive operations done once | Tokenized query, parsed AST, embeddings |
| Metadata | Immutable facts about the request | Request ID, timestamp, user locale |
| Configuration | Pipeline-level settings | Score thresholds, feature flags, mode |

### 2. Pre-computation Strategy 🌿 (Eco Mode)

**Goal:** Identify and hoist expensive operations to pipeline entry.

**Steps:**

1. **Nano: Identify-and-Hoist** — for each stage, list its computations.
   Mark any computation that appears in 2+ stages. Hoist it to the context
   initialization phase.
2. Measure cost: which pre-computations save the most time/resources?
3. Prioritize: always pre-compute O(n) operations used in O(m) loops
   (avoids O(n×m)).
4. Lazy pre-computation: for optional stages, use lazy getters that compute
   on first access. If the stage is skipped, the computation never runs.
5. Document what each pre-computed field contains and why it exists.

**Decision criteria:**

| Pattern | Action |
|---------|--------|
| Same computation in 2+ stages | Pre-compute in context |
| Computation in 1 stage only | Keep in stage — don't over-context |
| Expensive but rarely needed | Lazy getter in context |
| Cheap computation | Don't bother — overhead of context outweighs savings |

### 3. Immutability Discipline 🌿 (Eco Mode)

**Goal:** Ensure context integrity across stages.

**Steps:**

1. Context is **read-only** for all pipeline stages. Stages consume context,
   they never modify it.
2. Only the pipeline owner (the orchestrator that creates and runs the pipeline)
   may write to context.
3. If a stage needs to pass data to a later stage, use a separate **results
   accumulator**, not the context.
4. **Nano: Freeze-on-Create** — after context initialization, freeze the
   object (or use immutable data structures) to enforce read-only at runtime.
5. Violations (stage attempts to write to context) should fail loudly — throw,
   don't silently ignore.

### 4. Stage Contracts 🌿 (Eco Mode)

**Goal:** Each stage declares what it reads from context.

**Steps:**

1. Each stage declares its **reads**: which context fields it requires.
2. Each stage declares its **outputs**: what it produces (goes to results,
   not context).
3. At pipeline assembly time, verify: every stage's reads are satisfied by
   the context + prior stage outputs.
4. Missing reads = pipeline misconfiguration → fail early, don't run.
5. Stage contracts enable: static analysis, dependency graphs, dead-stage
   detection (stage whose output is never consumed).

### 5. Context Lifecycle 🌿 (Eco Mode)

**Goal:** Manage context from creation to disposal.

**Steps:**

1. **Creation:** At pipeline entry, allocate context and run all pre-computations.
2. **Propagation:** Pass context as a parameter to each stage. Never use
   globals or singletons.
3. **Scoped enrichment:** If a stage group needs additional context, create
   a scoped child context (inherits parent, adds fields). Child context
   doesn't pollute parent.
4. **Disposal:** After pipeline completes, release context references to allow
   garbage collection. Clear any large pre-computed data (embeddings, parsed
   ASTs).
5. **Nano: Context Pooling** — for high-throughput pipelines, reuse context
   objects from a pool instead of allocating new ones each time.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pipeline_stages` | `array` | yes | Ordered list of stages to execute |
| `initial_data` | `object` | yes | Raw input data for the pipeline |
| `config` | `object` | no | Pipeline configuration and thresholds |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `result` | `object` | Accumulated outputs from all stages |
| `context_stats` | `object` | What was pre-computed, cache hits, timing |

---

## Guardrails

- Context is read-only for stages — violations must throw, not silently pass.
- Every context field must have a documented purpose — no "just in case" fields.
- Pre-compute only what saves measurable time — measure before adding.
- Context must not grow unbounded — set a field count budget.
- Pass context explicitly — never via globals, closures, or singletons.

## Ask-When-Ambiguous

**Triggers:**

- Unclear whether data belongs in context or in stage-local scope
- Two stages need different views of the same data
- Context size exceeds memory budget

**Question Templates:**

1. "Field '{name}' is used by only one stage. Keep in context for future use or keep stage-local?"
2. "Two stages need '{data}' in different formats. Pre-compute both or transform on read?"
3. "Context is growing large ({N} fields). Should I split into sub-contexts per stage group?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Data used by 1 stage | Keep stage-local |
| Data used by 2+ stages | Pre-compute in context |
| Data expensive but rarely accessed | Lazy getter |
| Context > 20 fields | Consider grouping into sub-objects |
| Stage needs to modify shared data | Use results accumulator, NOT context |

## Success Criteria

- [ ] No stage recomputes data that exists in context
- [ ] Context is immutable after initialization
- [ ] Every context field is consumed by at least one stage
- [ ] Pipeline fails fast if a stage's required context field is missing
- [ ] Context is properly disposed after pipeline completion

## Failure Modes

- **Context mutation** — a stage modifies context, corrupting data for later stages. **Recovery:** freeze context object at creation; enforce via type system or runtime check.
- **Over-contextualization** — everything is pre-computed "just in case." **Recovery:** audit context field usage; remove unused fields.
- **Context leak** — context holds large objects (ASTs, embeddings) after pipeline completes. **Recovery:** explicit disposal step; nullify references.
- **Circular dependency** — stage A's contract requires stage B's output, and vice versa. **Recovery:** stage contracts are checked at assembly time; reject cycles.

## Audit Log

- `[timestamp] context-created: {N} fields pre-computed, {M} lazy getters`
- `[timestamp] stage-executed: "{name}", reads: [{fields}], duration: {ms}`
- `[timestamp] context-disposed: {N} fields released`

---

## Examples

### Example 1 — Search Pipeline Context

**Context fields:**
```
tokens:         string[]    — query tokenized once (used by 5 scorers)
queryEmbedding: number[]    — computed once (used by embedding scorer)
domainCounts:   Map         — pre-aggregated (used by domain scorer)
```

**Without context:** Each of 5 scorers tokenizes the query independently = 5× tokenization.
**With context:** Tokenize once at pipeline entry, pass via context = 1× tokenization.

### Example 2 — Build Pipeline Context

**Context fields:**
```
sourceFiles:    string[]    — glob'd once (used by compile, lint, test stages)
tsConfig:       object      — parsed once (used by compile and type-check stages)
packageJson:    object      — read once (used by dependency-check and bundle stages)
```

**Without context:** compile stage globs 1,200 files (300ms), lint stage globs same 1,200 files (300ms), test stage globs again (300ms) = 900ms on file discovery alone.
**With context:** Glob once at pipeline entry (300ms), pass `context.sourceFiles` to all 3 stages = 300ms total. Savings: 600ms per build, ~8 seconds saved per minute in watch mode.

### Example 3 — Stage Contract Declaration

**Stage:** `lint` declares its contract:
```
reads:   ["sourceFiles", "tsConfig"]
outputs: ["lintResults"]
```

**Stage:** `type-check` declares:
```
reads:   ["sourceFiles", "tsConfig"]
outputs: ["typeErrors"]
```

**Stage:** `bundle` declares:
```
reads:   ["sourceFiles", "packageJson", "typeErrors"]
outputs: ["bundleManifest"]
```

**Assembly-time check:** Pipeline verifier walks all contracts. `bundle` reads `typeErrors` — is this satisfied? Yes, `type-check` outputs it AND `type-check` runs before `bundle` in the stage order. If `type-check` were removed, assembly would fail: `"bundle.reads 'typeErrors' but no prior stage outputs it"`. Caught before any stage runs.

### Example 4 — Scoped Child Context

**Parent context:** `{ sourceFiles, tsConfig, packageJson }` — shared by all stages.

**Test stage group** needs additional context (test fixtures, mock data) irrelevant to compile/lint:
```
testContext = context.createChild({ fixtures: loadFixtures(), mockDb: createMockPool() })
```

**Properties:**
- `testContext.sourceFiles` → inherits from parent (read-only).
- `testContext.fixtures` → only visible to test stages.
- Parent context unchanged — compile and lint never see `fixtures` or `mockDb`.
- When test stage group completes, `testContext` is disposed, releasing `mockDb` connection pool. Parent context remains alive for remaining stages.

---

## Edge Cases

- **Empty context:** Pipeline with no shared data. Skip context creation — stages are fully independent.
- **Hot-reload:** Context was created with stale data. Solution: invalidate context when source data changes, re-create for next pipeline run.
- **Partial pipeline:** Only some stages run (e.g., skip linting). Lazy context fields avoid pre-computing data for skipped stages.
- **Nested pipelines:** Inner pipeline needs parent context + its own. Use scoped child context.
