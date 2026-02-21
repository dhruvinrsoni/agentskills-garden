---
name: error-handling
description: >
  Standardize error types, logging formats, and error response
  structures across the project.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# Error Handling

> _"Errors are data. Treat them like first-class citizens."_

## Context

Invoked when setting up a new project's error handling strategy or when
inconsistent error patterns are detected in an existing codebase.

---

## Micro-Skills

### 1. Error Taxonomy 🌿 (Eco Mode)

**Steps:**

1. Define base error classes for the project:
   - `ValidationError` (400) — bad input from the client.
   - `AuthenticationError` (401) — identity not verified.
   - `AuthorizationError` (403) — identity verified, access denied.
   - `NotFoundError` (404) — resource does not exist.
   - `ConflictError` (409) — state conflict (optimistic locking).
   - `InternalError` (500) — unexpected server failure.
2. Each error class carries: `code`, `message`, `details`, `stack`.

### 2. Response Formatting 🌿 (Eco Mode)

**Steps:**

1. Adopt RFC 7807 Problem Details format:
   ```json
   {
     "type": "https://api.example.com/errors/validation",
     "title": "Validation Error",
     "status": 400,
     "detail": "field 'email' must be a valid email address",
     "instance": "/users/123"
   }
   ```
2. Create a global error handler middleware that converts exceptions to
   this format.
3. Never leak stack traces in production.

### 3. Structured Logging 🌿 (Eco Mode)

**Steps:**

1. Adopt JSON structured logging (not plain text).
2. Every log entry must include: `timestamp`, `level`, `message`,
   `correlation_id`, `service`, `error` (if applicable).
3. Use log levels consistently:
   - `debug`: development only.
   - `info`: business events (user created, order placed).
   - `warn`: recoverable issues (retry succeeded, cache miss).
   - `error`: unrecoverable issues requiring attention.

### 4. Retry & Circuit Breaker 🌿 (Eco Mode)

**Steps:**

1. For external service calls, add retry with exponential backoff.
2. Set max retries (default: 3).
3. Implement circuit breaker for repeated failures (open after 5 failures,
   half-open after 30s).

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `error_classes`    | `string`   | Generated error class file               |
| `error_handler`    | `string`   | Global error handler middleware           |
| `logging_config`   | `string`   | Logging configuration file               |

---

## Scope

### In Scope
- Defining a project-wide error class taxonomy (validation, auth, not-found, conflict, internal)
- Implementing a global error handler middleware that converts exceptions to RFC 7807 Problem Details
- Configuring structured JSON logging with consistent fields (timestamp, level, correlation_id, service)
- Adding retry logic with exponential backoff and circuit breakers for external service calls
- Sanitizing error responses to prevent stack trace and internal detail leakage in production
- Defining and enforcing log-level conventions across the codebase
- Generating error code catalogs for API consumers

### Out of Scope
- Implementing application-specific business validation rules (delegate to handler/service layer)
- Setting up log aggregation infrastructure (ELK, Datadog, Splunk) (delegate to `monitoring-setup`)
- Alerting and on-call configuration (delegate to `monitoring-setup`, `incident-response`)
- Writing tests for error handling paths (delegate to `unit-testing`, `integration-testing`)
- Handling frontend/client-side error display or user-facing error messages
- Database-level error handling (constraint violations, deadlocks) (delegate to `data-access`)
- Modifying CI/CD pipelines to fail on unhandled exceptions

---

## Guardrails

- Never leak stack traces, SQL statements, or internal file paths in production error responses.
- Every error class must carry a machine-readable `code` and a human-readable `message` — both are mandatory.
- Log levels must be used consistently: `error` for actionable failures, `warn` for recoverable issues, `info` for business events, `debug` for development only.
- Never swallow exceptions silently — every caught exception must be logged or re-thrown.
- Correlation IDs must be propagated across all service boundaries for distributed tracing.
- Retry logic must include a maximum retry count (default: 3) and exponential backoff — never retry infinitely.
- Circuit breakers must have explicit open/half-open/closed thresholds — never use magic numbers without configuration.
- Never log sensitive data (passwords, tokens, PII) in any log level.
- Preview all generated diffs before writing error handling code to disk.

## Ask-When-Ambiguous

### Triggers
- The project already has partial error handling and it's unclear whether to augment or replace it
- Multiple logging libraries are present and the primary one is not obvious
- The project handles errors differently in synchronous vs. asynchronous code paths
- Custom error codes conflict with existing error codes in the codebase
- The application has both REST and GraphQL endpoints requiring different error formats
- Retry vs. fail-fast semantics are ambiguous for a specific external dependency

### Question Templates
1. "I found existing error handling in `{file}`. Should I refactor it into the new taxonomy or keep it and layer on top?"
2. "Both `{logger_a}` and `{logger_b}` are present. Which should be the primary structured logger?"
3. "For the `{service}` dependency, should I retry on failure (with backoff) or fail fast and propagate the error?"
4. "The project has both REST and GraphQL endpoints. Should error responses use RFC 7807 for both, or GraphQL-native errors for the GraphQL layer?"
5. "Error code `{code}` conflicts with an existing code in `{file}`. Should I remap it or replace the existing one?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| No error handling exists in the project | Generate full taxonomy, global handler, and structured logging from scratch |
| Partial error classes exist but are inconsistent | Extend the existing hierarchy; refactor inconsistencies with user approval |
| Plain-text logging is used throughout | Replace with structured JSON logging; migrate existing log calls |
| External service has no SLA or reliability data | Default to retry with 3 attempts + exponential backoff; add circuit breaker if >5 calls/min |
| Error response format differs between endpoints | Standardize on RFC 7807; add a response transformer for non-conforming endpoints |
| Application uses async/event-driven architecture | Add error handling for unhandled promise rejections, dead-letter queues, and event replay |
| Sensitive data appears in error `details` field | Strip PII from error details; log the full error internally at `error` level only |

## Success Criteria

- [ ] Every thrown exception maps to a defined error class with a specific HTTP status code
- [ ] Global error handler catches all unhandled exceptions and returns RFC 7807 responses
- [ ] No stack traces or internal details are exposed in production API responses
- [ ] All log entries are structured JSON with `timestamp`, `level`, `message`, `correlation_id`, and `service`
- [ ] Log levels are used consistently across the codebase (no `console.log` in production paths)
- [ ] External service calls have retry logic with exponential backoff and a circuit breaker
- [ ] Correlation IDs are propagated across all service-to-service calls
- [ ] Error code catalog is documented and available to API consumers

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Stack trace leaked in production | Sensitive internal paths visible in API response | Global error handler must sanitize all error bodies; test with a forced 500 and verify the response |
| Silent exception swallowing | Data inconsistencies with no error logs | Lint rule: every `catch` block must log or re-throw; CI fails on empty catch blocks |
| Inconsistent log levels | `error` used for non-critical issues, causing alert fatigue | Define and document log-level policy; code review enforcement |
| Missing correlation ID | Cannot trace a request across microservices | Inject correlation ID middleware at the entry point; propagate via headers on outbound calls |
| Infinite retry loop | External service outage causes cascading resource exhaustion | Enforce max retry count and circuit breaker; alert when circuit opens |
| PII in log output | Compliance violation (GDPR, HIPAA) | Scrub sensitive fields before logging; use allow-list for loggable fields |
| Error class not mapped to HTTP status | Some exceptions return 500 instead of the correct 4xx code | Unit test every error class → status code mapping; fail CI if unmapped errors exist |

## Audit Log

```
- [{{timestamp}}] error-handling:start — project={{project_name}}, existing_error_classes={{count}}, existing_logger={{logger_name}}
- [{{timestamp}}] taxonomy:generated — error_classes={{class_list}}, base_class={{base}}, status_codes={{code_map}}
- [{{timestamp}}] global-handler:installed — framework={{framework}}, format=rfc7807, stack_trace_leak_check={{bool}}
- [{{timestamp}}] structured-logging:configured — logger={{logger}}, format=json, fields={{field_list}}
- [{{timestamp}}] retry-circuit-breaker:configured — services={{service_list}}, max_retries={{count}}, circuit_threshold={{count}}
- [{{timestamp}}] error-handling:complete — error_classes_created={{count}}, handler_installed={{bool}}, logging_configured={{bool}}, all_tests_pass={{bool}}
```
