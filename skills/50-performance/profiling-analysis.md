---
name: profiling-analysis
description: >
  Analyze application performance using profiling tools, traces,
  and logs to identify bottlenecks and hotspots.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: plan-execute
---

# Profiling & Analysis

> _"Measure first. Optimize second. Never guess."_

## Context

Invoked when the application is slower than expected, or proactively before
launch to establish performance baselines.

---

## Micro-Skills

### 1. Baseline Measurement ⚡ (Power Mode)

**Steps:**

1. Define key performance metrics:
   - **Latency:** p50, p95, p99 response times.
   - **Throughput:** requests/second under expected load.
   - **Resource usage:** CPU %, memory MB, disk I/O.
2. Run a load test (k6, wrk, locust) with realistic scenarios.
3. Record baseline metrics.

### 2. CPU Profiling ⚡ (Power Mode)

**Steps:**

1. Run the CPU profiler for the target language:
   - Node.js: `--prof`, clinic.js, 0x
   - Python: `cProfile`, py-spy, Pyroscope
   - Go: `pprof`
   - Java: async-profiler, JFR
2. Generate a flame graph.
3. Identify the top 5 hotspot functions.
4. For each hotspot, propose an optimization with expected impact.

### 3. Memory Profiling ⚡ (Power Mode)

**Steps:**

1. Take heap snapshots before and after a workload.
2. Identify memory leaks: objects that grow without bound.
3. Check for common patterns: unbounded caches, event listener leaks,
   large string concatenation in loops.
4. Propose fixes.

### 4. Trace Analysis ⚡ (Power Mode)

**Steps:**

1. Enable distributed tracing (OpenTelemetry preferred).
2. Capture traces for slow requests (p99+).
3. Identify the slowest span in the trace waterfall.
4. Correlate with logs using `trace_id`/`correlation_id`.

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `baseline`      | `object`   | Performance baseline metrics             |
| `flame_graph`   | `string`   | Path to generated flame graph            |
| `hotspots`      | `object[]` | Top bottleneck functions                 |
| `recommendations`| `string[]`| Prioritized optimization suggestions     |
