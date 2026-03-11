---
name: two-pass-analysis
description: >
  Decouple metric collection from pass/fail gating. Pass 1 gathers raw
  data. Pass 2 applies thresholds. Enables trend analysis without blocking,
  while still enforcing standards.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad"
  reasoning_mode: linear
  skill_type: standard
---


# Two-Pass Analysis

> _"Measure first. Judge second. Separate collection from gating."_

## Context

Invoked when quality analysis conflates measurement with enforcement — a common
antipattern where adding a metric to a linter also gates the build, or where
collecting data and making pass/fail decisions happen in the same step. This
skill separates the two concerns so you can collect trends without blocking,
and gate without losing historical data.

Applicable domains: linting, code review, security scanning, performance
testing, bundle size checks, dependency audits.

## Scope

**In scope:** Metric collection strategies, threshold gating, threshold
configuration, trend analysis, and the separation pattern itself.

**Out of scope:** Specific linting tools (ESLint, Pylint, etc.), specific CI
systems (GitHub Actions, Jenkins), metric storage backends.

---

## Micro-Skills

### 1. Pass 1: Metric Collection 🌿 (Eco Mode)

**Goal:** Gather raw data without judgment.

**Steps:**

1. Run the analysis tool in **data-only mode** — output structured metrics
   (JSON, CSV, or SARIF), not human-readable reports.
2. **Nano: Structured Metric Output** — every metric has: `name`, `value`,
   `unit`, `file` (optional), `line` (optional). Consistent schema across
   all analysis types.
3. Collect ALL metrics, including those below threshold — they're needed for
   trend analysis.
4. Store the raw metrics as a build artifact (persist beyond the pipeline run).
5. Pass 1 **never fails the build** — it only collects.

### 2. Pass 2: Threshold Gating 🌿 (Eco Mode)

**Goal:** Apply pass/fail decisions to collected metrics.

**Steps:**

1. Load metrics from Pass 1 output.
2. Load threshold configuration (see micro-skill 3).
3. For each metric, compare value against threshold:
   - **Pass:** value meets threshold.
   - **Warn:** value is within warning range (e.g., 90-100% of threshold).
   - **Fail:** value exceeds threshold.
4. Output human-readable report with pass/warn/fail per metric.
5. **Nano: Exit Code Convention** — exit 0 if all pass, exit 1 if any fail.
   This gates the CI pipeline.

### 3. Threshold Configuration 🌿 (Eco Mode)

**Goal:** Define thresholds separately from collection logic.

**Steps:**

1. Store thresholds in a configuration file (not hardcoded in the analysis
   tool or CI script).
2. Each threshold defines: `metric_name`, `operator` (<=, >=, ==),
   `threshold_value`, `warning_value` (optional).
3. Support per-project overrides — a monorepo may have different thresholds
   per package.
4. Thresholds are versioned with the project — changes to thresholds are
   reviewable in PRs.
5. **Nano: Ratchet Pattern** — when a metric improves beyond the current
   threshold, tighten the threshold to the new value. Prevents regression
   while allowing organic improvement.

### 4. Trend Analysis ⚡ (Power Mode)

**Goal:** Compare current metrics to historical baselines.

**Steps:**

1. Load historical metrics from previous builds/runs (stored as artifacts
   in Pass 1).
2. Compare current values to: last build, 7-day average, 30-day average.
3. Detect trends:
   - **Improving:** metric consistently getting better over time.
   - **Stable:** metric within normal variance.
   - **Regressing:** metric getting worse (even if still passing threshold).
   - **Spike:** sudden change (>2 standard deviations from mean).
4. Flag regressions and spikes even if they pass the threshold — early
   warning before they become failures.
5. Generate trend charts/reports for team visibility.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `analysis_tool` | `string` | yes | The tool to run in Pass 1 |
| `thresholds` | `object` | yes | Threshold configuration |
| `historical_data` | `array` | no | Previous metric snapshots for trend analysis |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `metrics` | `array` | Raw metrics from Pass 1 |
| `gate_result` | `object` | Pass/warn/fail per metric from Pass 2 |
| `trends` | `object` | Trend analysis comparing to historical |

---

## Guardrails

- Pass 1 never fails the build — collection is always safe.
- Pass 2 is the only place that gates — no hidden thresholds elsewhere.
- Thresholds live in version-controlled config, not in CI scripts.
- Raw metrics are always persisted — even when the build fails.
- Trend analysis is advisory — it informs, it doesn't gate.

## Ask-When-Ambiguous

**Triggers:**

- New metric added but no threshold defined
- Metric regressing but still within threshold
- Threshold too strict (failing builds for minor issues)

**Question Templates:**

1. "New metric '{name}' collected but has no threshold. Should I set one or keep it trend-only?"
2. "Metric '{name}' has regressed 15% over 7 days but still passes. Should I tighten the threshold?"
3. "Threshold for '{name}' is causing {N} build failures per week. Lower it or fix the root cause?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| New metric | Collect in Pass 1, set threshold after baseline established |
| Metric improving | Apply ratchet pattern — tighten threshold |
| Metric regressing but passing | Flag in trend analysis, don't gate yet |
| Metric failing | Gate in Pass 2, require fix before merge |
| Historical data unavailable | Skip trend analysis, use absolute thresholds only |

## Success Criteria

- [ ] Metrics are collected even when the build fails
- [ ] Thresholds are configurable without code changes
- [ ] Trend analysis detects regressions before they cross thresholds
- [ ] Adding a new metric requires only: add to collection + optional threshold
- [ ] Pass 1 and Pass 2 can run independently

## Failure Modes

- **Collection-gating coupling** — Pass 1 accidentally gates (exits non-zero on findings). **Recovery:** ensure Pass 1 tool runs with `--no-fail` or equivalent flag.
- **Threshold drift** — thresholds become stale as the project evolves. **Recovery:** periodic threshold review; use ratchet pattern for automatic tightening.
- **Trend noise** — normal variance triggers false regression alerts. **Recovery:** use rolling averages and standard deviation thresholds, not point comparisons.
- **Missing historical data** — first run has nothing to compare against. **Recovery:** gracefully degrade to absolute thresholds; start accumulating data.

## Audit Log

- `[timestamp] pass-1-complete: {N} metrics collected, artifact stored at {path}`
- `[timestamp] pass-2-complete: {pass} passed, {warn} warnings, {fail} failures`
- `[timestamp] threshold-ratcheted: "{metric}" {old} → {new}`
- `[timestamp] trend-detected: "{metric}" {trend-type} over {period}`

---

## Examples

### Example 1 — Linting Pipeline

**Pass 1:** `eslint --format json > metrics.json` (collects all violations, exits 0).
**Pass 2:** Load `metrics.json`, compare violation count against threshold (max 10 errors). Exit 1 if exceeded.
**Trend:** Compare to last 5 builds. Violations trending down → ratchet threshold from 10 to 7.

### Example 2 — Bundle Size Check

**Pass 1:** `webpack --json > bundle-stats.json` (collects bundle sizes per entry point).
**Pass 2:** Compare each bundle against max size threshold (main < 500KB, vendor < 300KB).
**Trend:** Track size over 30 days. Flag if any bundle grows >5% in a week.

---

## Edge Cases

- **First run ever:** No historical data. Run Pass 1, set initial baselines, skip trend analysis.
- **Threshold at zero:** Metric must have zero violations. Any finding is a failure. Common for security-critical metrics.
- **Multiple analysis tools:** Run Pass 1 for each tool independently. Merge metrics in Pass 2.
- **Flaky metrics:** Some metrics vary between runs (timing-dependent tests). Use rolling average for threshold comparison, not point-in-time value.
