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

---

## Scope

### In Scope

- Establishing performance baselines (latency, throughput, resource usage).
- Running CPU and memory profilers for the target language/runtime.
- Generating and interpreting flame graphs.
- Identifying top hotspot functions and memory leak patterns.
- Configuring distributed tracing (OpenTelemetry) and analyzing trace waterfalls.
- Correlating traces with logs via `trace_id` / `correlation_id`.
- Producing prioritized optimization recommendations with expected impact.

### Out of Scope

- Implementing the optimizations themselves (see `caching-strategy`, `db-tuning`, `refactoring`).
- Load testing infrastructure provisioning (k6/locust cluster setup).
- APM tool procurement or SaaS configuration (Datadog, New Relic dashboards).
- Network-level profiling (packet captures, DNS latency).
- Frontend/browser performance profiling (Lighthouse, Core Web Vitals).
- Production deployment of profiling agents — analysis is done in staging or via snapshots.

---

## Guardrails

- Never enable CPU or memory profilers on production services without explicit approval; use staging or snapshots.
- Always capture a baseline measurement before any optimization attempt.
- Do not profile for less than 30 seconds; short samples produce misleading flame graphs.
- Heap snapshots can pause the application — warn the caller before taking them.
- Never commit profiling artifacts (flame graphs, heap dumps) to source control; store externally.
- Run profiling under realistic load; synthetic micro-benchmarks can mislead.
- Do not recommend optimizations for functions consuming less than 2% of total CPU time.
- Preserve raw profiling data until the analysis is reviewed and accepted.

---

## Ask-When-Ambiguous

### Triggers

- The target language or runtime is not specified.
- It is unclear whether profiling should focus on CPU, memory, or I/O.
- The definition of "slow" is not quantified (no latency target or SLA).
- The environment for profiling (local, staging, production replica) is not stated.
- Load test scenarios or traffic patterns are not provided.
- Distributed tracing is requested but no tracing backend is configured.

### Question Templates

- "Which language and runtime is the target service built on (e.g., Node.js 20, Python 3.12, Go 1.22)?"
- "Should profiling focus on CPU, memory, I/O, or all three?"
- "What is the latency target or SLA for the endpoints under analysis (e.g., p99 < 200ms)?"
- "Which environment should be profiled — local dev, staging, or a production replica?"
- "Are there specific endpoints or code paths to focus on, or should the full service be profiled?"
- "Is an OpenTelemetry-compatible tracing backend (Jaeger, Tempo, etc.) already deployed?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| No baseline metrics exist for the service | Run **Baseline Measurement** micro-skill first before any analysis |
| Single endpoint is slow; others are fine | Profile that endpoint's code path; use trace analysis to find the slow span |
| Overall CPU usage is high under load | Run **CPU Profiling** and generate flame graph to find hotspots |
| Memory grows continuously under sustained load | Run **Memory Profiling** with heap snapshots to detect leaks |
| Latency spikes are intermittent, not constant | Use **Trace Analysis** on p99+ requests to correlate with GC pauses or external calls |
| Hotspot function is in a third-party library | Recommend upgrading the library, replacing it, or wrapping with caching — do not modify vendor code |
| Multiple bottlenecks found across CPU, memory, and I/O | Prioritize by impact: address the bottleneck contributing the most to p99 latency first |
| Profiling a polyglot / microservice system | Enable distributed tracing across services; profile the slowest service individually |

---

## Success Criteria

- [ ] Baseline metrics (p50, p95, p99 latency; throughput; CPU/memory usage) are captured and documented.
- [ ] Flame graph is generated and the top 5 hotspot functions are identified.
- [ ] Each hotspot has a proposed optimization with estimated impact.
- [ ] Memory profiling confirms no unbounded object growth (or leaks are identified and documented).
- [ ] Trace analysis covers p99+ slow requests with root span identified.
- [ ] Recommendations are prioritized by impact (highest latency reduction first).
- [ ] Profiling artifacts are stored externally, not committed to version control.
- [ ] Before/after comparison is available if optimizations were applied.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Profiler overhead skews results | Measured latency is 2–5× higher than real; false hotspots appear | Use low-overhead sampling profilers (py-spy, async-profiler); validate with production metrics |
| Heap snapshot pauses the application | Service becomes unresponsive during memory profiling | Take snapshots during low-traffic windows; warn the caller before triggering |
| Flame graph is too noisy to interpret | Thousands of thin frames; no clear hotspot stands out | Increase sampling duration; filter to application code only (exclude runtime internals) |
| Baseline captured under unrealistic load | Optimizations don't translate to production improvement | Use production traffic replay or realistic load test scenarios for baseline |
| Missing trace spans in distributed system | Trace waterfall has gaps; can't identify the slow service | Verify OpenTelemetry SDK is instrumented in all services; check context propagation headers |
| Profiling data lost before analysis | No artifacts available to review | Save profiling output immediately to a shared location; automate artifact export |
| Optimizing the wrong hotspot | Performance doesn't improve despite code changes | Re-profile after changes to confirm the targeted function was the actual bottleneck |

---

## Audit Log

Each invocation of the Profiling & Analysis skill records the following timestamped entries in the scratchpad:

- `[YYYY-MM-DDTHH:MM:SSZ] PROFILING_START` — Skill invoked; target service, language, and profiling focus (CPU/memory/traces) noted.
- `[YYYY-MM-DDTHH:MM:SSZ] BASELINE_CAPTURED` — Baseline metrics recorded: p50/p95/p99 latency, throughput, CPU %, memory MB.
- `[YYYY-MM-DDTHH:MM:SSZ] PROFILER_RUN` — Profiler executed; tool used, sampling duration, and environment documented.
- `[YYYY-MM-DDTHH:MM:SSZ] FLAME_GRAPH_GENERATED` — Flame graph created; storage path recorded.
- `[YYYY-MM-DDTHH:MM:SSZ] HOTSPOTS_IDENTIFIED` — Top N hotspot functions listed with CPU/memory contribution percentages.
- `[YYYY-MM-DDTHH:MM:SSZ] TRACES_ANALYZED` — Slow traces reviewed; slowest span and root cause noted.
- `[YYYY-MM-DDTHH:MM:SSZ] RECOMMENDATIONS_PRODUCED` — Prioritized optimization list generated with estimated impact.
- `[YYYY-MM-DDTHH:MM:SSZ] PROFILING_END` — Skill completed; summary of findings and next steps logged.
