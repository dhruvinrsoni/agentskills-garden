---
name: caching-strategy
description: >
  Design and implement caching layers using Redis, Memcached, or
  in-memory caches with proper invalidation strategies.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - data-access
reasoning_mode: plan-execute
---

# Caching Strategy

> _"The fastest query is the one you never make."_

## Context

Invoked when read-heavy paths need optimization or when database load
must be reduced without architectural changes.

---

## Micro-Skills

### 1. Cache Identification ⚡ (Power Mode)

**Steps:**

1. Profile the application to find the top 10 most-called queries.
2. For each query, evaluate cacheability:
   - **High:** Read-heavy, rarely changes, tolerance for staleness.
   - **Medium:** Moderate writes, short TTL acceptable.
   - **Low:** Write-heavy, consistency-critical (don't cache).
3. Rank candidates by impact (frequency x latency saved).

### 2. Pattern Selection ⚡ (Power Mode)

**Steps:**

Choose the appropriate caching pattern:

| Pattern          | Use When                                      |
|------------------|-----------------------------------------------|
| **Cache-Aside**  | App reads cache first, fills on miss.         |
| **Write-Through**| App writes to cache and DB simultaneously.    |
| **Write-Behind** | App writes to cache; async flush to DB.       |
| **Read-Through** | Cache itself fetches from DB on miss.         |

Default recommendation: **Cache-Aside** (simplest, most predictable).

### 3. Implementation ⚡ (Power Mode)

**Steps:**

1. Add Redis/Memcached client to the project.
2. Implement the chosen pattern with:
   - Key naming convention: `{service}:{entity}:{id}` or `{service}:{query-hash}`.
   - TTL (start with 5 minutes, tune based on staleness tolerance).
   - Serialization format (JSON or MessagePack).
3. Add cache-hit/miss metrics.

### 4. Invalidation Strategy ⚡ (Power Mode)

**Steps:**

1. Define invalidation triggers (entity update, delete, TTL expiry).
2. Implement pattern:
   - **TTL-based:** Set expiry on every key.
   - **Event-based:** Invalidate on write (pub/sub or after-commit hook).
   - **Tag-based:** Group related keys, invalidate by tag.
3. Handle thundering herd (cache stampede): use lock/singleflight.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `cache_config`   | `string`   | Cache client configuration               |
| `implementation` | `string[]` | Modified files with caching added        |
| `key_schema`     | `string`   | Cache key naming documentation           |
| `metrics`        | `string`   | Cache-hit/miss metric implementation     |

---

## Scope

### In Scope

- Identifying cacheable read paths and selecting appropriate caching patterns.
- Configuring cache clients (Redis, Memcached, in-memory) and connection settings.
- Implementing cache-aside, write-through, write-behind, and read-through patterns.
- Designing key naming conventions, TTL policies, and serialization formats.
- Implementing invalidation strategies (TTL, event-based, tag-based).
- Adding cache-hit/miss metrics and monitoring instrumentation.
- Handling cache stampede / thundering herd with locking or singleflight.

### Out of Scope

- Provisioning or operating cache infrastructure (Redis clusters, Memcached nodes).
- Application-level business logic changes unrelated to caching.
- Database schema modifications (see `database-design` or `db-tuning`).
- CDN or edge-cache configuration (network-level caching).
- Session storage design — use dedicated session management patterns instead.

---

## Guardrails

- Never cache writes or mutation responses; only cache idempotent read paths.
- Always set a TTL on every cache key — unbounded keys cause memory exhaustion.
- Preview all code diffs before applying; revert if tests fail after changes.
- Never store secrets, tokens, or PII in cache without encryption-at-rest.
- Do not introduce caching for paths with fewer than 100 req/min unless latency is critical.
- Run existing test suites after adding caching to verify no behavioral regression.
- Never bypass existing access-control checks by serving cached responses to unauthorized users.
- Log cache invalidation events to prevent silent stale-data bugs.

---

## Ask-When-Ambiguous

### Triggers

- Staleness tolerance is not specified by the caller.
- Multiple caching patterns could apply to the same data path.
- The target environment's cache infrastructure (Redis vs. Memcached vs. in-memory) is unknown.
- Data involves user-specific content that may require per-user key segmentation.
- Write frequency is high enough that invalidation overhead may negate caching benefit.

### Question Templates

- "What staleness tolerance is acceptable for `{entity}`? (e.g., 30s, 5m, 1h)"
- "Which cache backend is available in this environment — Redis, Memcached, or in-process only?"
- "Should cached data be segmented per-user/tenant, or is it shared across all users?"
- "Are there existing pub/sub or event-bus mechanisms available for event-based invalidation?"
- "Is there a hard memory budget for the cache layer?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Read:write ratio > 10:1 and staleness tolerance ≥ 30s | Use **Cache-Aside** with TTL |
| Reads require strong consistency with DB | Use **Read-Through** with short TTL (≤ 5s) or skip caching |
| Writes are frequent but reads must reflect latest state | Use **Write-Through** to keep cache warm |
| Write latency is critical and eventual consistency is acceptable | Use **Write-Behind** with async flush |
| Multiple related keys must invalidate together | Use **Tag-based invalidation** |
| Single hot key with high concurrency on cache miss | Apply **singleflight / lock** to prevent stampede |
| Data is user-specific and varies per tenant | Segment keys with `{tenant}:{entity}:{id}` prefix |
| No external cache infra available | Use **in-memory cache** (LRU) with size cap |

---

## Success Criteria

- [ ] Cache-hit ratio for targeted paths exceeds 80% under normal load.
- [ ] p95 latency for cached endpoints drops by at least 40% compared to baseline.
- [ ] No stale data served beyond the configured TTL window.
- [ ] Cache-miss path still returns correct results (cache is not a single point of failure).
- [ ] Cache-hit/miss metrics are emitted and visible in the monitoring dashboard.
- [ ] All existing tests pass after caching is introduced.
- [ ] Key naming convention is documented and consistently applied.
- [ ] Invalidation triggers fire correctly on entity create/update/delete.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Cache stampede (thundering herd) | Spike in DB load when a popular key expires | Implement singleflight / mutex lock on cache miss; stagger TTLs with jitter |
| Stale data served after mutation | Users see outdated values after an update | Add event-based invalidation on write; verify invalidation triggers in tests |
| Memory exhaustion | Cache node OOM, evictions spike, latency increases | Set `maxmemory` policy (e.g., `allkeys-lru`); enforce TTL on all keys |
| Cache poisoning | Incorrect or corrupt data persisted in cache | Validate data before caching; add integrity checks on deserialization |
| Silent cache bypass | Cache client fails silently, all requests hit DB | Add health checks and alerting on cache connectivity; log cache errors |
| Key collision | Different data stored/retrieved under the same key | Use deterministic, namespaced key schema; include version in key prefix |
| Serialization mismatch | Deserialization errors after code deployment changes object shape | Version cache keys or add schema version suffix; flush on deploy if needed |

---

## Audit Log

Each invocation of the Caching Strategy skill records the following timestamped entries in the scratchpad:

- `[YYYY-MM-DDTHH:MM:SSZ] CACHE_SKILL_START` — Skill invoked; target paths and context noted.
- `[YYYY-MM-DDTHH:MM:SSZ] CANDIDATES_IDENTIFIED` — List of cacheable query/endpoint candidates with read frequency and latency.
- `[YYYY-MM-DDTHH:MM:SSZ] PATTERN_SELECTED` — Chosen caching pattern per candidate with rationale.
- `[YYYY-MM-DDTHH:MM:SSZ] IMPLEMENTATION_COMPLETE` — Files modified, key schema applied, TTLs configured.
- `[YYYY-MM-DDTHH:MM:SSZ] INVALIDATION_CONFIGURED` — Invalidation strategy and triggers documented.
- `[YYYY-MM-DDTHH:MM:SSZ] METRICS_ADDED` — Cache-hit/miss instrumentation added; metric names listed.
- `[YYYY-MM-DDTHH:MM:SSZ] TESTS_PASSED` — Existing test suite executed post-change; pass/fail status.
- `[YYYY-MM-DDTHH:MM:SSZ] CACHE_SKILL_END` — Skill completed; summary of cache-hit ratio improvement (if measurable).
