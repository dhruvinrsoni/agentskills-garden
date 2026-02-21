````markdown
---
name: error-handling-debug
description: >
  Debug and improve error handling strategies including exception
  hierarchies, retry logic, graceful degradation, and circuit breakers.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - error-handling
reasoning_mode: plan-execute
---

# Error Handling (Debugging)

> _"A system that fails gracefully is more reliable than one that never expects failure."_

## Context

Invoked when error handling in a codebase is incomplete, inconsistent, or
causing cascading failures. This skill focuses on debugging and improving
exception hierarchies, retry strategies, graceful degradation patterns, and
circuit breaker implementations — complementing the implementation-level
`error-handling` skill with a diagnostic and corrective lens.

---

## Micro-Skills

### 1. Exception Hierarchy Audit 🌿 (Eco Mode)

**Steps:**

1. Scan the codebase for all exception/error classes and their
   inheritance tree.
2. Identify anti-patterns:
   - Catching generic `Exception` / `Error` / `Throwable` without
     re-throwing or logging.
   - Empty catch blocks that silently swallow errors.
   - Overly deep hierarchies (> 4 levels) adding complexity without
     semantic value.
   - Missing error codes or inconsistent error classification.
3. Map each exception type to its HTTP status code (if applicable)
   and verify consistency.
4. Produce a hierarchy diagram and a list of recommended changes.

### 2. Retry Strategy Analysis ⚡ (Power Mode)

**Steps:**

1. Locate all retry logic in the codebase: manual loops, library-based
   retries (Polly, tenacity, resilience4j, etc.).
2. Evaluate each retry point:
   - Is the operation idempotent? Non-idempotent retries are dangerous.
   - Is there exponential backoff with jitter?
   - Is there a max retry limit (recommended: 3–5)?
   - Are transient errors distinguished from permanent errors?
3. Flag retry storms: retries without backoff or with unlimited attempts.
4. Check for missing retries on external calls (HTTP, gRPC, database
   connections) that are known to have transient failures.

### 3. Graceful Degradation Review ⚡ (Power Mode)

**Steps:**

1. Identify service dependencies (external APIs, databases, caches,
   message queues).
2. For each dependency, determine the degradation strategy:
   - **Fallback:** Return cached/default data when the dependency is
     unavailable.
   - **Feature toggle:** Disable the feature gracefully with a user
     message.
   - **Partial response:** Return what is available, note what is
     missing.
   - **None:** The application crashes or hangs (this is the problem).
3. Flag dependencies with no degradation strategy as high-risk.
4. Recommend fallback implementations for critical paths.

### 4. Circuit Breaker Evaluation ⚡ (Power Mode)

**Steps:**

1. Identify where circuit breakers are (or should be) implemented.
2. For existing circuit breakers, verify configuration:
   - **Failure threshold:** Number of failures before opening (default: 5).
   - **Timeout:** Duration the circuit stays open before half-open
     (default: 30s).
   - **Half-open behavior:** How many trial requests are allowed.
   - **Success threshold:** Successes needed in half-open to close.
3. For missing circuit breakers, identify candidates:
   - External HTTP/gRPC calls.
   - Database connections with connection pool exhaustion risk.
   - Third-party API integrations.
4. Verify that circuit breaker state changes are logged and monitored.

---

## Inputs

| Parameter          | Type       | Required | Description                                  |
|--------------------|------------|----------|----------------------------------------------|
| `codebase_path`    | `string`   | yes      | Path to the codebase to analyze              |
| `language`         | `string`   | yes      | Primary programming language                 |
| `framework`        | `string`   | no       | Framework in use (e.g., Spring, Express)     |
| `focus_area`       | `string`   | no       | Specific area: exceptions, retries, degradation, circuit-breakers |
| `service_deps`     | `string[]` | no       | Known external service dependencies          |

## Outputs

| Field                | Type       | Description                                  |
|----------------------|------------|----------------------------------------------|
| `exception_tree`     | `string`   | Diagram of the exception hierarchy           |
| `findings`           | `object[]` | Issues found with category and severity      |
| `retry_audit`        | `object[]` | Retry points with configuration assessment   |
| `degradation_map`    | `object[]` | Dependencies and their degradation strategies|
| `circuit_breakers`   | `object[]` | Circuit breaker inventory and configuration  |
| `recommendations`    | `string[]` | Prioritized list of improvements             |

---

## Edge Cases

- Codebase uses multiple error handling paradigms (exceptions + Result types
  + error codes) — Analyze each paradigm separately, then check for
  inconsistent mixing at boundaries.
- Retry logic is embedded in a third-party library with no visible config —
  Check library documentation for default settings and flag as a review item.
- Circuit breaker is implemented with custom code instead of a library —
  Review the implementation against standard circuit breaker state machine.

## Scope

### In Scope

- Auditing exception/error class hierarchies for completeness and consistency.
- Analyzing retry logic for correctness: idempotency, backoff, jitter, max attempts.
- Reviewing graceful degradation strategies for each external dependency.
- Evaluating circuit breaker implementations and their configuration.
- Reading source code, configuration files, and dependency manifests.
- Producing findings with severity and actionable recommendations.
- Identifying silent error swallowing, missing error logging, and catch-all anti-patterns.

### Out of Scope

- Implementing fixes (this skill diagnoses; defer to `code-generation` or `refactoring` for changes).
- Defining the initial error taxonomy for a greenfield project (defer to `error-handling` in 30-implementation).
- Performance testing of retry/circuit breaker configurations under load (defer to `profiling-analysis`).
- Monitoring and alerting setup for circuit breaker state changes (defer to `ci-pipeline` or ops tooling).
- Business logic correctness — this skill focuses on error flow, not functional behavior.
- Modifying third-party library source code.

## Guardrails

- Never modify source code during the audit — this skill is diagnostic and advisory.
- Clearly distinguish between confirmed bugs (silent swallowing, missing retries) and style preferences (hierarchy depth, naming).
- Do not recommend retries on non-idempotent operations without explicitly flagging the idempotency risk.
- Always verify that retry recommendations include backoff with jitter — never recommend naive fixed-interval retries.
- When reviewing circuit breaker thresholds, account for the service's SLA requirements rather than applying universal defaults.
- Flag but do not auto-fix empty catch blocks — they may be intentional (rare but possible).
- Do not access or expose secrets, API keys, or credentials encountered in configuration files.

## Ask-When-Ambiguous

### Triggers

- The codebase mixes exceptions and Result/Either types, and it's unclear which is the intended pattern.
- Retry logic exists but the operation's idempotency cannot be determined from the code alone.
- A catch-all handler exists at the top level, and it's unclear if it's intentional error boundary design.
- The circuit breaker threshold seems misconfigured but may be tuned for a specific SLA.
- External dependencies are not documented, and service discovery is needed.

### Question Templates

1. "The codebase uses both exceptions and Result types. Which is the preferred pattern, or should both be supported with clear boundary rules?"
2. "The operation `{{operation_name}}` has retry logic, but I cannot determine if it's idempotent. Is this operation safe to retry?"
3. "There's a top-level catch-all in `{{file_path}}` — is this an intentional error boundary, or should specific exceptions be handled individually?"
4. "The circuit breaker for `{{service_name}}` opens after {{threshold}} failures with a {{timeout}}s reset. Does this align with the service's SLA, or should it be adjusted?"
5. "I found {{count}} external service calls without any error handling. Should I prioritize them by criticality, or audit all equally?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Empty catch block with no logging | Flag as critical — silent error swallowing is almost always a bug |
| Catching generic Exception at a service boundary | Acceptable if it logs and converts to a proper error response; flag if it swallows |
| Retry without backoff on an external API call | Flag as high severity — risk of retry storm and cascading failure |
| External dependency has no circuit breaker | Flag as medium severity; recommend adding one with sensible defaults |
| Exception hierarchy deeper than 4 levels | Flag as minor; suggest flattening unless each level adds semantic value |
| Retry on a non-idempotent POST request | Flag as critical risk; ask user to confirm idempotency before recommending |
| Graceful degradation missing for a non-critical feature | Flag as medium; recommend feature toggle or default response |
| Graceful degradation missing for a critical path | Flag as critical; recommend fallback with cached data or queue-based retry |

## Success Criteria

- [ ] All exception/error classes in the codebase are catalogued with their hierarchy.
- [ ] Every retry point has been evaluated for idempotency, backoff strategy, and max attempts.
- [ ] Each external dependency is mapped to its degradation strategy (or flagged as missing).
- [ ] Circuit breaker coverage is assessed for all external service calls.
- [ ] Findings are categorized by type (exception, retry, degradation, circuit breaker) and severity.
- [ ] No source code was modified during the analysis.
- [ ] Recommendations are actionable, specific, and prioritized.
- [ ] Silent error swallowing instances are identified with file and line references.

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| False positive on intentional catch-all | Intentional error boundary flagged as a bug | Check for logging and re-throwing within the catch; ask user if uncertain |
| Missed retry logic in third-party abstraction | Retry behavior not detected because it's inside a library | Check dependency manifests for known resilience libraries; review their default configs |
| Incorrect idempotency assessment | Non-idempotent operation marked as safe to retry | Default to "unknown" when idempotency can't be determined; require user confirmation |
| Over-recommendation of circuit breakers | Every external call gets a circuit breaker recommendation, adding unnecessary complexity | Only recommend circuit breakers for calls with observed or expected transient failure patterns |
| Stale dependency list | Degradation map misses newly added services | Cross-reference code imports and HTTP client usage with the provided dependency list |
| Analysis of dead code paths | Error handling in unreachable code flagged as an issue | Check if the code is referenced; deprioritize findings in unused paths |

## Audit Log

- `[{{timestamp}}] error-handling-debug:start — analyzing {{codebase_path}} (language: {{language}})`
- `[{{timestamp}}] error-handling-debug:hierarchy-scanned — found {{exception_count}} exception classes, max depth: {{max_depth}}`
- `[{{timestamp}}] error-handling-debug:silent-catch-found — {{count}} empty/silent catch blocks in {{file_count}} files`
- `[{{timestamp}}] error-handling-debug:retry-audit — evaluated {{retry_count}} retry points, {{unsafe_count}} flagged unsafe`
- `[{{timestamp}}] error-handling-debug:degradation-mapped — {{dep_count}} dependencies, {{missing_count}} without degradation strategy`
- `[{{timestamp}}] error-handling-debug:circuit-breakers — {{cb_count}} found, {{missing_cb_count}} recommended`
- `[{{timestamp}}] error-handling-debug:complete — {{finding_count}} findings ({{critical_count}} critical, {{major_count}} major, {{minor_count}} minor)`
````
