---
name: resilience-patterns
description: >
  Graceful degradation when external dependencies fail. Circuit breaker
  state machine, retry with backoff, bulkhead isolation, fallback chains,
  and timeout management.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, error-handling"
  reasoning_mode: linear
  skill_type: standard
---


# Resilience Patterns

> _"Plan for failure. Degrade gracefully. Recover automatically."_

## Context

Invoked when a system integrates with external dependencies — APIs, databases,
third-party services, AI models, file systems — that can fail, slow down, or
become unavailable. This skill provides patterns for surviving those failures
without cascading them to the user.

## Scope

**In scope:** Circuit breaker state machine, retry with backoff, bulkhead
isolation, fallback chains, timeout management. These are implementation
patterns applicable to any language or framework.

**Out of scope:** Error taxonomy and logging formats (see `error-handling`).
Monitoring and alerting infrastructure (see `monitoring-setup`). Specific
SDK/library recommendations.

---

## Micro-Skills

### 1. Circuit Breaker ⚡ (Power Mode)

**Goal:** Stop calling a failing dependency to prevent cascading failures.

**Steps:**

1. Track consecutive failures per dependency.
2. State machine with three states:
   - **CLOSED** (normal): Requests pass through. Count consecutive failures.
   - **OPEN** (tripped): After N consecutive failures, reject all requests
     immediately without calling the dependency. Start cooldown timer.
   - **HALF-OPEN** (probing): After cooldown expires, allow one probe request.
     If it succeeds → CLOSED. If it fails → OPEN (reset cooldown).
3. **Nano: Half-Open Probe** — the single test request sent during HALF-OPEN
   state. Must be lightweight and representative of normal traffic.
4. Configure per dependency: failure threshold (N), cooldown duration, probe
   request format.
5. When circuit is OPEN, return the fallback response (see micro-skill 4).

**State transition table:**

| Current State | Event | Next State | Action |
|--------------|-------|------------|--------|
| CLOSED | Success | CLOSED | Reset failure count |
| CLOSED | Failure (count < N) | CLOSED | Increment failure count |
| CLOSED | Failure (count = N) | OPEN | Start cooldown, reject requests |
| OPEN | Cooldown expires | HALF-OPEN | Allow one probe request |
| HALF-OPEN | Probe succeeds | CLOSED | Reset failure count, resume |
| HALF-OPEN | Probe fails | OPEN | Restart cooldown |

### 2. Retry with Backoff 🌿 (Eco Mode)

**Goal:** Retry transient failures without overwhelming the dependency.

**Steps:**

1. Classify errors: **retryable** (timeout, 503, connection reset) vs
   **non-retryable** (400, 401, 404, validation error).
2. Only retry retryable errors. Non-retryable errors fail immediately.
3. **Nano: Exponential Backoff with Jitter** — wait time =
   `min(base * 2^attempt + random(0, jitter), maxDelay)`. The jitter
   prevents thundering herd when many clients retry simultaneously.
4. Set a maximum retry count (typically 3-5). After exhausting retries,
   fall through to the fallback chain.
5. Log each retry attempt with: attempt number, wait duration, error type.

**Backoff schedule example (base=100ms, jitter=50ms, max=5s):**

| Attempt | Base delay | With jitter | Actual wait |
|---------|-----------|-------------|-------------|
| 1 | 200ms | 200-250ms | ~225ms |
| 2 | 400ms | 400-450ms | ~425ms |
| 3 | 800ms | 800-850ms | ~825ms |
| 4 | 1600ms | 1600-1650ms | ~1625ms |
| 5 | 3200ms | 3200-3250ms | ~3225ms |

### 3. Bulkhead Isolation 🌿 (Eco Mode)

**Goal:** Prevent one slow dependency from exhausting all resources.

**Steps:**

1. Assign each external dependency its own resource pool (thread pool,
   connection pool, semaphore).
2. Set a maximum concurrent requests per dependency.
3. When the pool is exhausted, new requests for that dependency are queued
   (with timeout) or rejected immediately — they do NOT consume resources
   from other dependencies' pools.
4. Monitor pool utilization — if consistently at capacity, the dependency
   may need scaling or the limit needs adjustment.
5. Name each bulkhead for observability: `bulkhead:payment-api`,
   `bulkhead:user-db`.

### 4. Fallback Chains 🌿 (Eco Mode)

**Goal:** Provide degraded but usable responses when the primary path fails.

**Steps:**

1. Define a fallback chain per critical path:
   ```
   Primary → Cache Fallback → Default Fallback → Error Response
   ```
2. **Primary:** Normal call to the dependency.
3. **Cache fallback:** Return the last known good response from cache.
   Stale data is better than no data for many use cases.
4. **Default fallback:** Return a hardcoded safe default. For feature flags:
   `false`. For settings: schema defaults. For content: placeholder.
5. **Error response:** When all fallbacks fail, return a structured error
   that the caller can handle gracefully.
6. Each fallback level is less accurate but more available. Document the
   trade-off for each level.

### 5. Timeout Management 🌿 (Eco Mode)

**Goal:** Set timeouts at every integration point.

**Steps:**

1. Every outbound call must have an explicit timeout — never wait indefinitely.
2. **Nano: Cascading Timeout Budget** — the total time budget for a request
   is divided across all sequential calls. If the budget is 5 seconds and
   the first call takes 3 seconds, subsequent calls share the remaining
   2 seconds.
3. Set timeouts at three levels:
   - **Connection timeout:** How long to wait for a connection (short: 1-3s).
   - **Read timeout:** How long to wait for a response (medium: 5-30s).
   - **Total timeout:** End-to-end budget for the entire operation.
4. When a timeout fires, treat it as a retryable failure (feeds into
   micro-skill 2).
5. Log timeout events with: dependency name, timeout type, configured
   duration, actual duration.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dependency` | `string` | yes | Name of the external dependency |
| `operation` | `function` | yes | The call to execute with resilience |
| `config` | `object` | no | Thresholds, timeouts, retry limits |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `result` | `any` | Response from primary or fallback |
| `source` | `string` | Which level responded (primary, cache, default, error) |
| `resilience_stats` | `object` | Retry count, circuit state, timeout usage |

---

## Guardrails

- Every external call must have a timeout — zero tolerance for unbounded waits.
- Circuit breaker thresholds must be configured per dependency, not globally.
- Retries must use backoff with jitter — never retry immediately.
- Fallback responses must be clearly marked (the caller must know it got a fallback).
- Bulkhead limits must be monitored — silent exhaustion is a hidden failure.

## Ask-When-Ambiguous

**Triggers:**

- Unclear if an error is retryable or permanent
- Fallback data staleness exceeds acceptable threshold
- Multiple dependencies share failure patterns (correlated failures)

**Question Templates:**

1. "Error '{code}' from {dependency} — should this be retryable or permanent?"
2. "Cache fallback for {dependency} could be up to {duration} stale. Is that acceptable?"
3. "{Dependency-A} and {Dependency-B} are both failing. Are they correlated (shared infrastructure)?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Single transient failure | Retry with backoff |
| Repeated failures (N consecutive) | Open circuit breaker |
| One dependency slow, others fine | Bulkhead prevents contamination |
| All retries exhausted | Walk fallback chain |
| New dependency added | Configure: timeout, retry limit, circuit threshold, fallback |

## Success Criteria

- [ ] No unbounded waits — every call has a timeout
- [ ] Failing dependency doesn't cascade to unrelated features
- [ ] System recovers automatically when dependency recovers (circuit closes)
- [ ] Fallback responses are functional (degraded but usable)
- [ ] All resilience events are logged with dependency name and action taken

## Failure Modes

- **Thundering herd** — all clients retry simultaneously after a failure window. **Recovery:** jitter in backoff ensures staggered retries.
- **Circuit never closes** — half-open probe always fails because the dependency needs warm-up traffic. **Recovery:** increase probe count; allow gradual ramp-up in half-open state.
- **Fallback masks real failures** — system appears healthy but is serving stale/default data. **Recovery:** monitor fallback hit rate; alert when above threshold.
- **Timeout too aggressive** — normal slow responses trigger unnecessary retries. **Recovery:** measure p95/p99 latency, set timeout at p99 + buffer.

## Audit Log

- `[timestamp] circuit-state-change: {dependency} {old-state} → {new-state}`
- `[timestamp] retry-attempted: {dependency} attempt {N}/{max}, delay {ms}`
- `[timestamp] fallback-served: {dependency} level={cache|default|error}`
- `[timestamp] timeout-fired: {dependency} type={connection|read|total} limit={ms}`
- `[timestamp] bulkhead-rejected: {dependency} pool-size={N}, queued={M}`

---

## Examples

### Example 1 — API Integration

**Config:** timeout=5s, retries=3, circuit-threshold=5, cooldown=30s.

**Scenario:** Payment API returns 503 three times.
1. Call 1: 503 → retry after 200ms.
2. Call 2: 503 → retry after 400ms.
3. Call 3: 503 → retries exhausted → fallback: queue payment for async retry.
4. Next 2 failures: circuit opens → all payment calls immediately return "payment queued" fallback.
5. After 30s cooldown: half-open probe succeeds → circuit closes → normal flow resumes.

### Example 2 — AI Model Dependency

**Config:** timeout=10s, retries=2, circuit-threshold=3, cooldown=60s.

**Scenario:** AI model runs out of memory.
1. First request: timeout → retry after 100ms.
2. Second request: timeout → retries exhausted → fallback: return non-AI result.
3. Two more timeouts from other requests: circuit opens → skip AI for 60s.
4. Fallback chain: AI result → cached AI result → keyword-only result.

---

## Edge Cases

- **Dependency with mixed endpoints:** Different endpoints may have different failure rates. Consider per-endpoint circuit breakers if needed.
- **Cold start after circuit opens:** Dependency may need warm-up traffic. Ramp up gradually in half-open state.
- **Clock skew in distributed systems:** Timeouts may fire inconsistently across nodes. Use wall-clock + monotonic clock hybrid.
- **Correlated failures:** Multiple dependencies share infrastructure (same datacenter). One circuit opening may predict others. Consider a "global circuit" for correlated dependencies.
