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
