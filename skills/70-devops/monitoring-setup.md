---
name: monitoring-setup
description: >
  Design and configure observability stacks covering metrics,
  logs, traces, alerting, SLIs/SLOs, and dashboards.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - system-design
reasoning_mode: plan-execute
---

# Monitoring & Observability Setup

> _"If you can't measure it, you can't manage it — and you certainly can't debug it at 3 AM."_

## Context

Invoked when setting up or improving observability for a system. Covers the
three pillars — metrics, logs, and traces — plus alerting, SLIs/SLOs, and
dashboards to ensure production visibility and rapid incident response.

---

## Micro-Skills

### 1. Metrics & Instrumentation ⚡ (Power Mode)

**Steps:**

1. Identify key service metrics:
   - **RED metrics** (Rate, Errors, Duration) for request-driven services.
   - **USE metrics** (Utilization, Saturation, Errors) for resources.
2. Instrument application code with a metrics library:
   - Prometheus client (`prom-client`, `prometheus_client`, `micrometer`).
   - OpenTelemetry SDK for vendor-neutral instrumentation.
3. Expose a `/metrics` endpoint (or configure OTLP exporter).
4. Configure Prometheus scrape targets or OTLP collector pipeline.

### 2. Structured Logging 🌿 (Eco Mode)

**Steps:**

1. Configure structured JSON logging (not plain text).
2. Ensure every log entry includes:
   - `timestamp`, `level`, `service`, `trace_id`, `span_id`, `message`.
3. Set log levels appropriately (ERROR for failures, WARN for degradation,
   INFO for key events, DEBUG behind a flag).
4. Ship logs to a centralized platform (ELK, Loki, CloudWatch, Datadog).
5. Add log-based alerting for error-rate spikes.

### 3. Distributed Tracing ⚡ (Power Mode)

**Steps:**

1. Integrate OpenTelemetry tracing SDK into all services.
2. Configure trace propagation headers (`traceparent`, `b3`).
3. Ensure trace context flows across HTTP, gRPC, and message queues.
4. Export traces to a backend (Jaeger, Tempo, Zipkin, X-Ray, Datadog APM).
5. Add span attributes for key business operations (user ID, order ID).
6. Set sampling strategy: 100% in dev/staging, adaptive in production.

### 4. Alerting & SLOs ⚡ (Power Mode)

**Steps:**

1. Define SLIs for each service:
   - Availability: `successful_requests / total_requests`.
   - Latency: `requests_below_threshold / total_requests` (e.g., p99 < 500ms).
   - Correctness: `correct_responses / total_responses`.
2. Set SLO targets (e.g., 99.9% availability over 30-day window).
3. Calculate error budgets and configure burn-rate alerts.
4. Create alerting rules:
   - **Page-worthy:** SLO burn rate > 14x (exhausts budget in 1 hour).
   - **Ticket-worthy:** SLO burn rate > 6x (exhausts budget in 6 hours).
5. Route alerts to appropriate channels (PagerDuty, Slack, OpsGenie).

### 5. Dashboard Design 🌿 (Eco Mode)

**Steps:**

1. Create a service-level dashboard (Grafana, Datadog, CloudWatch):
   - Row 1: Request rate, error rate, latency percentiles (p50, p95, p99).
   - Row 2: Resource utilization (CPU, memory, disk, network).
   - Row 3: Business metrics (sign-ups, orders, payments).
2. Create an infrastructure dashboard:
   - Cluster health, node status, pod restart counts.
   - Database connection pool utilization, query latency.
3. Add template variables for environment and service filtering.
4. Set time-range defaults and auto-refresh intervals.

---

## Outputs

| Field             | Type       | Description                                |
|-------------------|------------|--------------------------------------------|
| `metrics_config`  | `string`   | Metrics instrumentation configuration      |
| `logging_config`  | `string`   | Structured logging setup                   |
| `tracing_config`  | `string`   | Distributed tracing configuration          |
| `alert_rules`     | `string[]` | Alerting rules and SLO definitions         |
| `dashboards`      | `string[]` | Dashboard JSON/YAML definitions            |

---

## Scope

### In Scope

- Designing observability architectures covering metrics, logs, and distributed traces
- Instrumenting application code with OpenTelemetry, Prometheus, or vendor-specific SDKs
- Configuring log aggregation pipelines (ELK/EFK, Loki, CloudWatch Logs, Datadog)
- Setting up distributed tracing with context propagation across service boundaries
- Defining SLIs (Service Level Indicators) and SLOs (Service Level Objectives) with error budgets
- Creating alerting rules with severity tiers, routing policies, and escalation paths
- Designing Grafana/Datadog/CloudWatch dashboards for service and infrastructure visibility
- Configuring exporters, collectors, and scrape targets for the metrics pipeline

### Out of Scope

- Incident response playbook authoring (handled by `incident-response`)
- Infrastructure provisioning for monitoring backends (handled by `terraform-iac`)
- Application business logic changes unrelated to instrumentation
- Monitoring platform administration (Prometheus operator upgrades, Elasticsearch cluster tuning)
- Cost analysis of monitoring data ingestion and retention
- Load testing or performance benchmarking (handled by `profiling-analysis`)

---

## Guardrails

- Never alert on symptoms alone; alerts must be tied to SLI degradation or error-budget burn.
- Every alert must have a linked runbook or remediation step — no "mystery" alerts in production.
- Structured JSON logging is mandatory; plain-text logs are rejected.
- All log entries must include `trace_id` and `span_id` to enable log-to-trace correlation.
- Do not set alert thresholds based on gut feeling; use historical data or SLO burn-rate math.
- Sampling rate for production traces must not drop below 1% and must be configurable without redeployment.
- Dashboard panels must use consistent units (seconds not milliseconds, bytes not megabytes) and include axis labels.
- Sensitive data (PII, tokens, passwords) must never appear in logs, metrics labels, or trace attributes.
- Retention policies must be defined for all telemetry data; default to 15 days for logs, 30 days for metrics, 7 days for traces.

---

## Ask-When-Ambiguous

### Triggers

- The monitoring backend (Prometheus, Datadog, CloudWatch, New Relic) is not specified
- The number of services requiring instrumentation is unknown or very large
- SLO targets have not been defined by the team or product owner
- The deployment environment (Kubernetes, ECS, VMs, serverless) affects collector configuration
- Alert routing destinations (PagerDuty, OpsGenie, Slack, email) are not established

### Question Templates

1. "What monitoring platform are you using or planning to use — Prometheus + Grafana, Datadog, CloudWatch, New Relic, or another?"
2. "What are the SLO targets for this service — e.g., 99.9% availability, p99 latency under 500ms?"
3. "Where should critical alerts be routed — PagerDuty, OpsGenie, Slack, or another on-call system?"
4. "How are your services deployed — Kubernetes, ECS, VMs, or serverless? This determines collector and exporter configuration."
5. "What data retention periods do you need for logs, metrics, and traces?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Vendor-neutral requirement or multi-cloud deployment | Use OpenTelemetry SDK and OTLP exporters |
| Already using Prometheus + Grafana stack | Instrument with Prometheus client libraries; configure scrape targets |
| Fully managed monitoring preferred (minimize ops overhead) | Recommend Datadog, New Relic, or CloudWatch depending on cloud provider |
| Service has no existing instrumentation | Start with RED metrics and structured logging; add tracing incrementally |
| High cardinality metric labels detected | Reduce label cardinality; use exemplars to link metrics to traces instead |
| Alert is firing too frequently (> 5 times/week) with no action taken | Tune threshold, convert to ticket-level severity, or remove if not actionable |
| Log volume exceeds retention budget | Add sampling for DEBUG/INFO; keep 100% of WARN/ERROR; drop health-check logs |
| Cross-service latency debugging needed | Ensure trace propagation headers are configured across all inter-service calls |
| Dashboard has > 20 panels | Split into focused dashboards: overview, deep-dive per service, infrastructure |

---

## Success Criteria

- [ ] All three observability pillars (metrics, logs, traces) are configured and producing data
- [ ] SLIs are defined and measurable; SLO targets are set with error-budget tracking
- [ ] Alerts fire only for actionable conditions with clear severity (page vs. ticket)
- [ ] Every alert has a linked runbook with remediation steps
- [ ] Logs are structured JSON with `trace_id` for correlation to distributed traces
- [ ] Dashboards show request rate, error rate, and latency percentiles for every instrumented service
- [ ] Trace context propagates end-to-end across all service boundaries (HTTP, gRPC, queues)
- [ ] No PII or secrets appear in any telemetry data

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Missing trace propagation | Traces terminate at service boundary; no cross-service spans | Verify propagation headers (`traceparent`) are forwarded in HTTP clients and message consumers |
| Alert fatigue | On-call team ignores alerts due to high volume of non-actionable pages | Audit alerts: remove noisy ones, raise thresholds, or downgrade to ticket severity |
| High cardinality explosion | Prometheus OOM or query timeouts; Datadog bill spike | Review metric labels; remove user-ID or request-ID labels; use exemplars for trace linking |
| Log-trace correlation broken | Cannot navigate from log entry to corresponding trace | Ensure logging framework injects `trace_id` and `span_id` from OpenTelemetry context |
| Dashboard too slow to load | Grafana panels timeout on large time ranges | Add recording rules for expensive queries; reduce default time range; use downsampled metrics |
| SLO target too aggressive | Error budget is perpetually exhausted; team cannot ship features | Re-evaluate SLO with stakeholders; relax target to match actual business requirements |
| Sampling drops important traces | Error traces are not captured due to head-based sampling | Use tail-based sampling (collect all traces, decide to keep after completion) or always sample errors |

---

## Audit Log

- `[timestamp]` metrics-instrumented: Added `<library>` metrics to `<service>` exposing `<endpoint-or-exporter>`
- `[timestamp]` logging-configured: Set up structured JSON logging for `<service>` shipping to `<backend>`
- `[timestamp]` tracing-enabled: Configured OpenTelemetry tracing for `<service>` exporting to `<backend>`
- `[timestamp]` slo-defined: Set SLO for `<service>`: `<sli-type>` target `<percentage>`% over `<window>`
- `[timestamp]` alert-created: Added `<severity>` alert `<alert-name>` routing to `<destination>`
- `[timestamp]` dashboard-created: Created `<dashboard-name>` dashboard with `<n>` panels in `<platform>`
- `[timestamp]` retention-set: Configured retention — logs: `<days>`d, metrics: `<days>`d, traces: `<days>`d
