---
name: resource-awareness
description: >
  Monitor memory, CPU, time, and rate-limit constraints. Adapt behavior
  gracefully — degrade, shed load, switch algorithms. Prevents runaway
  resource usage and cascading failures.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, token-efficiency"
  reasoning_mode: linear
  skill_type: standard
---


# Resource Awareness

> _"Know your limits. Adapt before you hit them. Recover when pressure drops."_

## Context

Invoked when a system operates under resource constraints — memory ceilings,
CPU quotas, time budgets, rate limits, context window sizes — and must adapt
its behavior to stay within bounds. Unlike `token-efficiency` (which is
AI-agent-specific), this skill covers general application resource management.

## Scope

**In scope:** Constraint detection, budget allocation, adaptive degradation,
pressure monitoring, and recovery protocols.

**Out of scope:** AI model tier selection (see `token-efficiency`). Infrastructure
scaling (see `monitoring-setup`). Capacity planning.

---

## Micro-Skills

### 1. Constraint Detection 🌿 (Eco Mode)

**Goal:** Identify what resources are limited and by how much.

**Steps:**

1. Survey the runtime environment for active constraints:
   - **Memory:** heap limit, container memory limit, available RAM.
   - **CPU:** core count, quota (e.g., Kubernetes CPU limits).
   - **Time:** request timeout, SLA latency target, batch job deadline.
   - **Rate limits:** API call quotas, database connection limits.
   - **Context:** AI context window size, token budget.
2. For each constraint, determine: current usage, maximum allowed, remaining
   headroom.
3. **Nano: Constraint Inventory** — a 1-2 liner per constraint documenting
   the limit and how to check it at runtime.
4. Classify constraints as **hard** (exceed = crash/rejection) vs **soft**
   (exceed = degraded performance).
5. Prioritize monitoring hard constraints — they're the cliff edges.

### 2. Budget Allocation 🌿 (Eco Mode)

**Goal:** Divide available resources across operations.

**Steps:**

1. List all operations that consume the constrained resource.
2. Assign a budget to each operation based on priority and expected cost:
   - Critical path operations get larger budgets.
   - Nice-to-have operations get smaller budgets (or zero under pressure).
3. **Nano: Headroom Reserve** — always reserve 10-20% of the total budget
   for error handling, cleanup, and unexpected spikes.
4. Budget is enforced per-operation: if an operation exceeds its budget, it
   is terminated or degraded, not allowed to steal from other operations.
5. Document budget allocations — they encode priority decisions.

### 3. Adaptive Degradation 🌿 (Eco Mode)

**Goal:** When approaching limits, reduce scope gracefully.

**Steps:**

1. Define degradation levels per operation:
   - **Full:** Normal operation, all features active.
   - **Reduced:** Disable expensive features (AI enrichment, full-text search,
     high-res rendering).
   - **Minimal:** Core function only (keyword search, cached data, placeholder
     content).
   - **Shed:** Operation skipped entirely (non-critical background tasks).
2. Map resource pressure to degradation level:
   - Green (< 60% used) → Full.
   - Yellow (60-80%) → Reduced.
   - Red (> 80%) → Minimal or Shed.
3. Degradation must be transparent — log when degradation activates and what
   was reduced.
4. User-facing degradation should show indicators ("Limited mode — some
   features unavailable").

### 4. Pressure Monitoring 🌿 (Eco Mode)

**Goal:** Continuously check resource pressure and trigger responses.

**Steps:**

1. Poll resource usage at regular intervals (or use push-based metrics).
2. Apply pressure thresholds: Green → Yellow → Red.
3. **Nano: Hysteresis Thresholds** — use different thresholds for escalation
   vs de-escalation to prevent oscillation. Example: escalate at 80%,
   de-escalate at 65%. This prevents rapid flip-flopping near the boundary.
4. When pressure changes level, trigger the corresponding degradation response.
5. Log pressure transitions: `[timestamp] pressure: green → yellow (memory 72%)`.

### 5. Recovery Protocol 🌿 (Eco Mode)

**Goal:** Resume full behavior when pressure drops.

**Steps:**

1. When pressure drops below the de-escalation threshold → begin recovery.
2. Recovery is **gradual**, not instant — re-enable features one at a time
   to avoid re-spiking.
3. Order of recovery: restore critical features first, nice-to-have features
   last.
4. **Nano: Recovery Backoff** — after recovering, wait a stability period
   before fully returning to normal. If pressure spikes again during the
   stability period, re-degrade immediately.
5. Monitor for oscillation: if the system degrades and recovers more than
   3 times in 5 minutes, hold at the degraded level and alert.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `constraints` | `array` | yes | List of resource constraints and their limits |
| `operations` | `array` | yes | Operations that consume resources |
| `pressure_config` | `object` | no | Threshold percentages for green/yellow/red |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `pressure_level` | `string` | Current pressure: green, yellow, red |
| `degradation_state` | `object` | Per-operation degradation level |
| `budget_usage` | `object` | Per-operation resource consumption |

---

## Guardrails

- Hard constraints must never be exceeded — degrade before hitting the limit.
- Always reserve headroom for cleanup and error handling.
- Degradation must be logged — never silently reduce functionality.
- Hysteresis thresholds prevent oscillation — escalation threshold != de-escalation threshold.
- Recovery is gradual — never jump from minimal to full in one step.

## Ask-When-Ambiguous

**Triggers:**

- Unclear which operations to degrade first
- Constraint limit is unknown or dynamic
- User experience impact of degradation is uncertain

**Question Templates:**

1. "Under memory pressure, should I degrade {operation-A} or {operation-B} first?"
2. "The memory limit isn't explicitly set. Should I assume {default} or probe at runtime?"
3. "Degrading {feature} will visibly affect users. Is that acceptable, or should I degrade {other-feature} instead?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Pressure green | Full operation |
| Pressure yellow | Disable non-critical expensive features |
| Pressure red | Core function only; shed background tasks |
| Hard constraint approaching | Emergency shed — skip everything non-essential |
| Pressure oscillating | Hold at degraded level; alert for investigation |

## Success Criteria

- [ ] No hard constraint violations (no OOM, no timeout crashes)
- [ ] Degradation activates before limits are hit (proactive, not reactive)
- [ ] Recovery restores full functionality when pressure drops
- [ ] No oscillation between pressure levels
- [ ] All degradation events are logged with reason and impact

## Failure Modes

- **Late detection** — pressure hits red before monitoring triggers. **Recovery:** increase polling frequency; use predictive thresholds (trigger at 70% if growth rate is high).
- **Over-degradation** — system stays in minimal mode when pressure is green. **Recovery:** audit hysteresis thresholds; ensure recovery protocol runs.
- **Oscillation** — rapid flip between green and yellow. **Recovery:** widen hysteresis gap (e.g., escalate at 80%, de-escalate at 60% instead of 65%).
- **Budget starvation** — critical operation doesn't get enough budget. **Recovery:** re-prioritize budget allocation; shed lower-priority operations.

## Audit Log

- `[timestamp] pressure-change: {old-level} → {new-level}, {resource}: {usage}%`
- `[timestamp] degradation-activated: operation="{name}", level={reduced|minimal|shed}`
- `[timestamp] recovery-started: operation="{name}", target-level={full|reduced}`
- `[timestamp] budget-exceeded: operation="{name}", allocated={N}, used={M}`
- `[timestamp] oscillation-detected: {count} transitions in {duration}, holding at {level}`

---

## Examples

### Example 1 — Memory Pressure in a Background Service

**Constraints:** Container memory limit = 512MB. Headroom reserve = 100MB.
**Operations:** Data processing (300MB budget), caching (80MB budget), logging (32MB budget).

**Scenario:** Cache grows unexpectedly.
1. Memory at 65% → Yellow → reduce cache TTL (evict sooner).
2. Memory at 82% → Red → disable caching entirely, process data in smaller batches.
3. Memory drops to 58% → Green → gradually restore caching with shorter TTL.

### Example 2 — API Rate Limits

**Constraints:** External API allows 100 requests/minute.
**Operations:** User-triggered searches (priority 1), background indexing (priority 2), analytics (priority 3).

**Scenario:** Traffic spike.
1. Rate at 60/min → Yellow → pause analytics API calls.
2. Rate at 85/min → Red → pause background indexing, only user searches allowed.
3. Rate drops to 40/min → Green → resume indexing, then analytics.

---

## Edge Cases

- **Unknown constraint:** Runtime doesn't expose the limit (e.g., serverless memory). Probe empirically or use conservative defaults.
- **Multiple constraints simultaneously:** Memory red + CPU green. Apply the most restrictive degradation across all constraints.
- **Constraint changes at runtime:** Cloud auto-scaling adjusts limits. Re-detect periodically.
- **Zero-budget operation:** An operation assigned no budget. It only runs when explicitly enabled (opt-in, not default).
