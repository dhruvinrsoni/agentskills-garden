````markdown
---
name: performance-review
description: >
  Identify performance bottlenecks through complexity analysis, profiling
  review, caching strategy evaluation, and resource utilization assessment.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - profiling-analysis
reasoning_mode: plan-execute
---

# Performance Review

> _"Premature optimization is the root of all evil — but ignoring O(n²) is the root of all incidents."_

## Context

Invoked when code changes may impact latency, throughput, or resource
consumption. Also triggered during capacity planning, pre-release
performance audits, or when production metrics show degradation.
Focuses on identifying bottlenecks before they reach production.

---

## Micro-Skills

### 1. Complexity Analysis ⚡ (Power Mode)

**Steps:**

1. Analyze algorithmic complexity of changed or critical functions:
   - **Time complexity:** Identify Big-O for loops, recursion, and data
     structure operations.
   - **Space complexity:** Track memory allocations, buffer growth, and
     object retention.
2. Flag common anti-patterns:
   - Nested loops over the same collection → O(n²) or worse.
   - Repeated linear search in a loop → Replace with hash map lookup.
   - Unbounded recursion → Add depth limits or convert to iteration.
   - String concatenation in a loop → Use StringBuilder/join.
3. Compare complexity against data scale:
   - O(n²) on 100 items = acceptable.
   - O(n²) on 100,000 items = critical bottleneck.
4. Recommend algorithmic improvements where complexity exceeds O(n log n)
   for large datasets.

### 2. Bottleneck Identification 🌿 (Eco Mode)

**Steps:**

1. Review code for common performance bottlenecks:
   - **N+1 queries** — Loop issuing individual DB queries instead of batch.
   - **Synchronous I/O in hot paths** — Blocking calls in request handlers.
   - **Missing pagination** — Loading unbounded result sets into memory.
   - **Excessive serialization** — Repeated JSON.parse/stringify on large objects.
   - **Unindexed queries** — DB queries filtering on non-indexed columns.
2. Trace the hot path from entry point to response:
   - Identify the critical path (longest sequential chain).
   - Flag operations that can be parallelized or deferred.
3. Estimate impact: latency contribution (ms) × request frequency.

### 3. Caching Strategy Evaluation 🌿 (Eco Mode)

**Steps:**

1. Identify cacheable operations:
   - Repeated identical DB queries within the same request.
   - Expensive computations with stable inputs.
   - External API calls with predictable responses.
2. Evaluate caching appropriateness:
   - **Cache hit ratio** — Will most requests hit the cache?
   - **Staleness tolerance** — How long can data be stale?
   - **Invalidation complexity** — Can the cache be reliably invalidated?
3. Recommend caching layer:
   - **In-process:** Request-scoped memoization, LRU caches.
   - **Distributed:** Redis, Memcached for shared state.
   - **CDN/Edge:** Static assets, API responses with long TTL.
4. Flag cache anti-patterns:
   - Caching user-specific data without proper key isolation.
   - No TTL set (stale data forever).
   - Cache stampede risk (many concurrent misses).

### 4. Profiling Review ⚡ (Power Mode)

**Steps:**

1. If profiling data is provided, analyze:
   - **CPU flame graphs** — Identify functions consuming > 5% of total CPU.
   - **Memory heap snapshots** — Find retained objects, growing collections.
   - **Trace spans** — Identify slow spans in distributed traces.
2. If no profiling data, recommend instrumentation:
   - Add timing around suspected bottlenecks.
   - Instrument DB query durations and counts per request.
   - Add memory usage logging at key checkpoints.
3. Cross-reference profiling data with code changes:
   - Did the change introduce a new hot function?
   - Did the change increase allocation rate?

---

## Inputs

| Parameter         | Type       | Required | Description                                   |
|-------------------|------------|----------|-----------------------------------------------|
| `code_diff`       | `string`   | yes      | Diff or files to review for performance       |
| `data_scale`      | `string`   | no       | Expected data volume (e.g., "100K rows")      |
| `profile_data`    | `string`   | no       | Path to profiling output (flame graph, heap)  |
| `sla_targets`     | `object`   | no       | Latency/throughput SLA (e.g., p99 < 200ms)    |

## Outputs

| Field                | Type       | Description                                  |
|----------------------|------------|----------------------------------------------|
| `complexity_findings`| `object[]` | Functions with concerning time/space complexity|
| `bottlenecks`        | `object[]` | Identified bottlenecks with impact estimates  |
| `caching_recs`       | `object[]` | Caching recommendations with layer and TTL    |
| `profiling_insights` | `object[]` | Analysis of profiling data (if provided)      |

---

## Edge Cases

- Code handles tiny datasets today but is designed for growth — Flag
  O(n²) even if current n is small; add a comment noting the scaling risk.
- Microservice with no profiling infrastructure — Recommend lightweight
  instrumentation (structured logging with durations) as a first step.
- Caching introduces consistency issues — Document the trade-off and
  require explicit staleness tolerance from the team.

---

## Scope

### In Scope

- Analyzing algorithmic time and space complexity of changed code
- Identifying common performance bottlenecks (N+1 queries, missing pagination, synchronous I/O)
- Evaluating caching strategy appropriateness (hit ratio, staleness, invalidation)
- Reviewing profiling data (flame graphs, heap snapshots, trace spans) when provided
- Estimating performance impact based on data scale and request frequency
- Recommending instrumentation when profiling data is unavailable
- Flagging complexity that exceeds acceptable thresholds for the expected data scale

### Out of Scope

- Running benchmarks or load tests (delegate to dedicated performance testing tools)
- Infrastructure sizing and scaling decisions (delegate to system design or DevOps)
- Database schema design or index creation (delegate to `database-design` / `db-tuning`)
- Network latency optimization (CDN placement, DNS, TCP tuning)
- Frontend rendering performance (paint times, bundle size, Core Web Vitals)
- Writing optimized replacement code — review is advisory; author implements changes

---

## Guardrails

- Never recommend optimization without evidence of a bottleneck or scaling concern.
- Do not flag O(n) operations on small, bounded datasets as performance issues.
- Always pair a complexity concern with the expected data scale for context.
- Recommend caching only when the cache hit ratio is expected to exceed 50%.
- Do not suggest micro-optimizations (bit shifting, manual loop unrolling) in business logic.
- Flag premature optimization attempts by the author as a design concern.
- When profiling data contradicts code analysis, trust the profiling data.

## Ask-When-Ambiguous

### Triggers

- Expected data scale is unknown or not documented
- Code path frequency (hot path vs cold path) is unclear
- Profiling data is unavailable and cannot be generated
- SLA or latency targets are not defined for the service
- Caching is already in place but it's unclear whether it covers the reviewed code path

### Question Templates

1. "What is the expected data scale for `{{collection_name}}`? The algorithm is O({{complexity}}) which matters at scale."
2. "How frequently is `{{function_name}}` called? I need request frequency to estimate the performance impact."
3. "Are there latency SLAs for this service? I want to assess whether {{bottleneck}} is within acceptable bounds."
4. "Is profiling data available for this service? I see potential bottlenecks but need data to confirm."
5. "There's an existing cache for `{{cache_key}}`. Does it cover the code path through `{{function_name}}`, or is a separate cache needed?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| O(n²) algorithm on dataset expected to exceed 10K items | Flag as Critical; require algorithmic improvement before merge |
| O(n²) algorithm on bounded dataset (< 100 items) | Log as informational; add inline comment documenting the bound |
| N+1 query pattern detected | Flag as High; recommend batch query or eager loading |
| Missing pagination on API endpoint | Flag as High if result set is unbounded; Medium if naturally bounded |
| Cacheable operation identified with > 80% expected hit ratio | Recommend caching with specific TTL and invalidation strategy |
| Cacheable operation with complex invalidation requirements | Document trade-offs; require team decision on staleness tolerance |
| Profiling shows function < 1% of total CPU | Do not flag as a bottleneck regardless of code complexity |
| Synchronous I/O in request hot path | Flag as High; recommend async/parallel execution |

## Success Criteria

- [ ] All loops and recursive functions in the changeset have documented time complexity
- [ ] Bottlenecks are identified with estimated impact (latency × frequency)
- [ ] Complexity concerns are contextualized with expected data scale
- [ ] Caching recommendations include layer, TTL, and invalidation strategy
- [ ] No premature optimization recommendations — each is evidence-based
- [ ] Profiling data is analyzed (if provided) or instrumentation is recommended (if not)
- [ ] Findings are prioritized: Critical > High > Medium > Informational

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Premature optimization | Developer spends days optimizing a cold path with no measurable impact | Always require data scale and frequency context before recommending optimization |
| Missed N+1 query | Page load time degrades linearly with data growth | Trace DB query count per request; flag any loop containing a query |
| Cache without invalidation | Users see stale data with no way to refresh | Require explicit invalidation strategy for every cache recommendation |
| Ignoring space complexity | Service OOMs under load despite acceptable latency | Analyze memory allocation alongside time complexity; check for retained references |
| Wrong data scale assumption | Algorithm flagged as fine at 1K rows; fails at 100K in production | Document the assumed scale; revisit when data growth metrics change |
| Over-caching | Cache consumes excessive memory; hit ratio is low | Validate expected hit ratio before recommending; monitor after deployment |

## Audit Log

- `[{{timestamp}}] performance-review-started: files={{file_count}}, data_scale={{scale}}, sla={{sla_target}}`
- `[{{timestamp}}] complexity-finding: {{function_name}} — O({{time_complexity}}) time, O({{space_complexity}}) space, scale={{expected_n}}`
- `[{{timestamp}}] bottleneck-identified: {{type}} in {{file_path}}:{{line}} — est_impact={{latency_ms}}ms × {{frequency}}/sec`
- `[{{timestamp}}] caching-recommendation: {{operation}} — layer={{cache_layer}}, ttl={{ttl}}, invalidation={{strategy}}`
- `[{{timestamp}}] profiling-insight: {{function_name}} — {{cpu_pct}}% CPU, {{alloc_rate}} allocs/sec`
- `[{{timestamp}}] performance-review-completed: critical={{critical_count}}, high={{high_count}}, medium={{medium_count}}, info={{info_count}}`
````
