---
name: api-implementation
description: >
  Implement API handlers/controllers based on an existing API contract
  (OpenAPI spec). Generates route handlers, validation, and error handling.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - api-contract-design
  - error-handling
reasoning_mode: plan-execute
---

# API Implementation

> _"The contract is the blueprint. Build exactly to spec."_

## Context

Invoked after `api-contract-design` has produced an OpenAPI spec. This skill
generates the actual route handlers, request validation, response
serialization, and error handling code.

---

## Micro-Skills

### 1. Route Scaffolding ⚡ (Power Mode)

**Steps:**

1. Parse the OpenAPI spec for all paths and operations.
2. Generate one handler function per operation.
3. Wire routes to the framework's router (Express, FastAPI, Gin, etc.).
4. Add middleware: auth, rate-limiting, CORS (as specified in the contract).

### 2. Request Validation ⚡ (Power Mode)

**Steps:**

1. Extract JSON Schema from the OpenAPI `requestBody` definition.
2. Generate validation middleware using the framework's validator:
   - Node.js: `zod`, `joi`, or `ajv`
   - Python: `pydantic`
   - Go: `go-playground/validator`
3. Return 400 with RFC 7807 Problem Details on validation failure.

### 3. Response Serialization 🌿 (Eco Mode)

**Steps:**

1. Define response DTOs/models matching the OpenAPI response schemas.
2. Add serialization (exclude internal fields like `password_hash`).
3. Set correct Content-Type and HTTP status codes.

### 4. Integration Wiring ⚡ (Power Mode)

**Steps:**

1. Inject service/repository dependencies into handlers.
2. Add database transaction boundaries where needed.
3. Add structured logging for each endpoint.
4. Generate a smoke test (one passing request per endpoint).

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `handlers`      | `string[]` | Generated handler file paths             |
| `validators`    | `string[]` | Validation middleware/schema files       |
| `routes`        | `string`   | Router configuration file                |
| `smoke_tests`   | `string`   | Basic integration test file              |

---

## Edge Cases

- No OpenAPI spec exists — Invoke `api-contract-design` first.
- Spec has `x-` extensions for custom behavior — Parse and document, but
  ask user before implementing non-standard features.
