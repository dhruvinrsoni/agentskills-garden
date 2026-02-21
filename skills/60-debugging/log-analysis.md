````markdown
---
name: log-analysis
description: >
  Parse, correlate, and analyze application logs to detect patterns,
  anomalies, and causal chains across distributed systems.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: plan-execute
---

# Log Analysis

> _"Logs don't lie — but they do whisper. Learn to listen."_

## Context

Invoked when diagnosing production issues, investigating user-reported bugs,
or proactively scanning logs for emerging problems. This skill provides
structured techniques for parsing log data, recognizing patterns, correlating
events across services, and detecting anomalies that signal failures.

---

## Micro-Skills

### 1. Log Parsing & Normalization 🌿 (Eco Mode)

**Steps:**

1. Identify the log format: structured JSON, syslog, CSV, or unstructured
   plain text.
2. Extract canonical fields: `timestamp`, `level`, `service`, `message`,
   `correlation_id`, `trace_id`, `error`.
3. Normalize timestamps to a single timezone (UTC preferred).
4. Filter out noise: health checks, heartbeats, debug-level entries
   (unless specifically relevant).

### 2. Pattern Recognition ⚡ (Power Mode)

**Steps:**

1. Group log entries by recurring message templates (strip variable
   parts like IDs, timestamps, paths).
2. Count occurrences of each template in the time window.
3. Identify sudden spikes — a template that jumps from baseline
   frequency to 10x+ is a signal.
4. Flag repeating error sequences: the same error chain appearing
   in a loop indicates a retry storm or crash loop.
5. Detect missing expected patterns — absence of a regular heartbeat
   or scheduled job log is itself an anomaly.

### 3. Event Correlation ⚡ (Power Mode)

**Steps:**

1. Use `correlation_id` or `trace_id` to link entries across services.
2. Build a timeline for a single request: ingress → service A → service B
   → database → response.
3. Identify gaps in the timeline: where does the request stall or fail?
4. Correlate error entries with upstream events that occurred within a
   configurable window (default: 5 seconds before).
5. Cross-reference with deployment logs, config changes, and cron
   schedules at the same timestamp.

### 4. Anomaly Detection 🌿 (Eco Mode)

**Steps:**

1. Establish a baseline for key metrics: error rate, log volume per
   minute, response time percentiles (from log data).
2. Flag entries that deviate from baseline:
   - Error rate > 2x average for the time-of-day.
   - Log volume drop > 50% (may indicate a crash or network partition).
   - New error messages never seen before in the last 7 days of logs.
3. Rank anomalies by severity: user-facing errors > internal warnings >
   informational deviations.

---

## Inputs

| Parameter         | Type       | Required | Description                                  |
|-------------------|------------|----------|----------------------------------------------|
| `log_source`      | `string`   | yes      | Path to log file(s) or log stream identifier |
| `time_range`      | `string`   | no       | Time window to analyze (e.g., "last 2h")     |
| `correlation_id`  | `string`   | no       | Specific request/trace ID to follow           |
| `filter_level`    | `string`   | no       | Minimum log level to include (default: warn)  |
| `service_filter`  | `string[]` | no       | Limit analysis to specific services            |

## Outputs

| Field              | Type       | Description                                  |
|--------------------|------------|----------------------------------------------|
| `parsed_entries`   | `number`   | Count of log entries processed               |
| `patterns`         | `object[]` | Recurring message patterns with frequencies  |
| `anomalies`        | `object[]` | Detected anomalies ranked by severity        |
| `correlation_map`  | `object`   | Request timeline across services             |
| `summary`          | `string`   | Human-readable analysis summary              |

---

## Edge Cases

- Logs are in an unrecognized or mixed format — Attempt auto-detection;
  ask the user to confirm the format if confidence is low.
- Extremely large log files (> 1 GB) — Use sampling or time-windowed
  chunking rather than loading everything into memory.
- Missing correlation IDs — Fall back to timestamp-based correlation
  with a configurable tolerance window.
- Clock skew across services — Detect and warn; adjust correlation
  windows accordingly.

## Scope

### In Scope

- Parsing structured (JSON, syslog) and semi-structured (plain text with known patterns) log files.
- Normalizing timestamps, log levels, and field names across heterogeneous log sources.
- Identifying recurring error patterns and frequency spikes in log data.
- Correlating log entries across services using trace IDs, correlation IDs, or timestamp proximity.
- Detecting anomalies by comparing current log patterns against baselines.
- Summarizing findings into actionable reports with ranked anomalies.
- Reading log files, log archives, and log stream snapshots.

### Out of Scope

- Real-time log streaming or live tail monitoring (this skill operates on static log snapshots).
- Modifying application logging configuration or code (defer to `error-handling`).
- Infrastructure log analysis (kernel logs, network device logs) unless explicitly provided.
- Setting up or configuring log aggregation systems (ELK, Splunk, Datadog).
- Root cause determination beyond log evidence (defer to `root-cause-analysis` for deeper investigation).
- Generating alerts or modifying alerting rules in monitoring systems.

## Guardrails

- Never modify or delete original log files — all analysis is read-only.
- Redact or mask PII, secrets, tokens, and credentials encountered in log entries before including them in outputs.
- Limit memory usage: for files > 500 MB, process in time-windowed chunks rather than loading entirely.
- Do not assume log timestamps are accurate across services; flag potential clock skew.
- Always report the number of entries analyzed and any entries skipped due to parse failures.
- Preserve original line numbers and file references so findings can be traced back to source.
- Do not make causal claims based solely on temporal proximity — report correlations, not conclusions.

## Ask-When-Ambiguous

### Triggers

- Log format cannot be auto-detected with high confidence.
- Multiple log files are provided with no indication of which service each belongs to.
- The requested time range exceeds 24 hours or contains > 1 million entries.
- Correlation IDs are absent, and timestamp-based correlation may produce false positives.
- Logs contain entries in multiple languages or character encodings.

### Question Templates

1. "The log format appears to be {{detected_format}} — can you confirm, or should I try a different parser?"
2. "Multiple log files were provided without service labels. Can you map each file to its service name?"
3. "The time range contains {{entry_count}} entries. Should I analyze the full range, or focus on a narrower window around the incident?"
4. "No correlation IDs are present in these logs. Should I use timestamp proximity (±{{window}}s) for cross-service correlation?"
5. "Some log entries contain what appears to be PII (email addresses, IP addresses). Should I redact these in the output?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Structured JSON logs with correlation IDs | Use event correlation to build request timelines |
| Unstructured plain-text logs | Apply pattern recognition with regex-based template extraction |
| Single-service investigation with clear error messages | Focus on pattern recognition and frequency analysis |
| Cross-service failure with distributed traces | Prioritize event correlation using trace IDs |
| Large log volume with no specific incident time | Run anomaly detection first to identify the time window of interest |
| Intermittent error with no obvious pattern | Compare error occurrence times against deploy logs, cron schedules, and traffic patterns |

## Success Criteria

- [ ] All provided log entries have been parsed, with parse failure rate < 5%.
- [ ] Timestamps are normalized to a single timezone (UTC).
- [ ] Recurring error patterns are identified with frequency counts.
- [ ] Anomalies are detected and ranked by severity.
- [ ] Cross-service correlations are mapped (if multiple services are involved).
- [ ] PII and secrets are redacted from all output.
- [ ] A human-readable summary with actionable findings is produced.
- [ ] Original log files remain unmodified.

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Log format misidentified | Parser extracts garbage fields or skips most entries | Implement format auto-detection with confidence score; ask user to confirm when confidence < 80% |
| Clock skew corrupts correlation | Events appear out of order; timeline is nonsensical | Detect clock skew by comparing overlapping events; adjust windows and warn in output |
| PII leakage in output | Sensitive data appears in the analysis summary | Apply regex-based PII detection (emails, IPs, tokens) and mask before output |
| False anomaly due to seasonal traffic | Normal traffic spike flagged as anomaly | Use time-of-day and day-of-week baselines; allow user to provide expected traffic patterns |
| Memory exhaustion on large files | Process crashes or hangs during parsing | Enforce chunked processing for files > 500 MB; report progress incrementally |
| Over-filtering hides relevant entries | Important debug or info entries excluded by default level filter | Start with warn+ but note if error entries reference info-level context; suggest widening if needed |

## Audit Log

- `[{{timestamp}}] log-analysis:start — analyzing {{file_count}} log files, time range: {{time_range}}`
- `[{{timestamp}}] log-analysis:parse-complete — parsed {{parsed_count}}/{{total_count}} entries ({{failure_count}} parse failures)`
- `[{{timestamp}}] log-analysis:patterns-found — identified {{pattern_count}} recurring patterns, {{spike_count}} frequency spikes`
- `[{{timestamp}}] log-analysis:correlation-built — correlated {{trace_count}} request traces across {{service_count}} services`
- `[{{timestamp}}] log-analysis:anomalies-detected — {{anomaly_count}} anomalies ranked ({{critical_count}} critical)`
- `[{{timestamp}}] log-analysis:pii-redacted — redacted {{redaction_count}} PII occurrences`
- `[{{timestamp}}] log-analysis:complete — summary generated, {{finding_count}} actionable findings`
````
