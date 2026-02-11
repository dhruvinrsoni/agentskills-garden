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
