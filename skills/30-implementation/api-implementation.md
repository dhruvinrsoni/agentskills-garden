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

---

## Scope

### In Scope
- Generating route handlers, controllers, and endpoint wiring from an OpenAPI spec
- Creating request validation middleware (body, query, path parameters, headers)
- Producing response DTOs and serialization logic matching OpenAPI response schemas
- Adding authentication and authorization middleware as defined in the contract
- Wiring dependency injection for services and repositories into handlers
- Generating smoke tests (one passing request per endpoint)
- Setting correct HTTP status codes, Content-Type headers, and CORS configuration
- Adding structured logging to each endpoint

### Out of Scope
- Creating or modifying the OpenAPI spec itself (delegate to `api-contract-design`)
- Implementing business logic inside handlers — handlers call services, not the reverse
- Writing unit or integration test suites beyond smoke tests (delegate to `unit-testing`, `integration-testing`)
- Database schema changes or migration files (delegate to `data-access`)
- Deploying the API or configuring infrastructure (delegate to `ci-pipeline`, `docker-containerization`)
- Generating client SDKs or API documentation (delegate to `api-documentation`, `openapi-specs`)
- Rate-limiting infrastructure or WAF rules beyond simple middleware registration

---

## Guardrails

- Never implement an endpoint that is not defined in the OpenAPI spec.
- All request bodies must be validated before reaching the handler — no unvalidated input passes through.
- Never expose internal error details (stack traces, SQL errors) in API responses; use RFC 7807 Problem Details.
- Handlers must be thin: delegate to service layer, do not embed business logic.
- Never hardcode secrets, API keys, or environment-specific URLs in handler code.
- Preview all generated diffs before writing to disk.
- Never overwrite existing handler files without explicit user approval.
- Run linter and formatter on generated code; revert if lint errors are introduced.
- Do not generate into `vendor/`, `node_modules/`, `dist/`, or `build/` directories.

## Ask-When-Ambiguous

### Triggers
- The OpenAPI spec defines multiple authentication schemes and the handler needs to choose one
- The spec uses `x-` extensions with non-standard semantics
- The target framework is not clear from the project (e.g., both Express and Fastify present)
- An endpoint has no `requestBody` schema but accepts a POST/PUT method
- Pagination style is not specified (cursor vs. offset)
- The spec references shared components that have conflicting or circular definitions

### Question Templates
1. "The spec defines both `{auth_a}` and `{auth_b}` auth schemes — which should this endpoint use?"
2. "I found the custom extension `{x_extension}` on `{endpoint}`. Should I implement its behavior or skip it?"
3. "Both `{framework_a}` and `{framework_b}` are present in the project. Which should I wire routes to?"
4. "Endpoint `{method} {path}` accepts a body but no schema is defined. Should I add validation or allow any payload?"
5. "Pagination isn't specified for `{endpoint}`. Should I use cursor-based or offset-based pagination?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| No OpenAPI spec exists in the project | Abort; invoke `api-contract-design` first |
| Spec defines an endpoint already implemented in the codebase | Skip generation; warn the user about the existing handler |
| Spec uses `allOf`/`oneOf`/`anyOf` composition | Resolve to concrete types; generate discriminated unions where needed |
| Endpoint requires file upload (`multipart/form-data`) | Use framework-specific multipart middleware; validate file size and type |
| Spec defines multiple response codes for a single operation | Generate branching logic in the handler for each response case |
| Auth middleware is not yet configured in the project | Generate auth middleware stubs; flag for user to implement the auth logic |
| A handler exceeds 50 lines of code | Extract sub-operations into a service method to keep the handler thin |

## Success Criteria

- [ ] Every endpoint in the OpenAPI spec has a corresponding route handler
- [ ] All request parameters (path, query, header, body) are validated before reaching the handler
- [ ] Response DTOs match the OpenAPI response schemas exactly (no extra or missing fields)
- [ ] Correct HTTP status codes are returned for success, validation error, auth error, and not-found cases
- [ ] Smoke tests pass: one successful request per endpoint returns the expected status code
- [ ] Structured logging is present on every endpoint (request received, response sent, errors)
- [ ] No secrets or environment-specific values are hardcoded in generated code
- [ ] Generated code compiles/lints without errors

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Endpoint missing from generated routes | API returns 404 for a valid spec path | Cross-check generated routes against every path+method in the OpenAPI spec |
| Validation middleware not wired | Invalid payloads reach the handler and cause 500 errors | Verify each endpoint has validation middleware registered before the handler |
| Response schema mismatch | Extra or missing fields in the API response body | Generate response DTOs directly from the OpenAPI response schema; serialize through the DTO |
| Auth middleware misconfigured | Protected endpoints return 200 without credentials | Test each secured endpoint with and without valid credentials in smoke tests |
| Framework mismatch | Code references APIs that don't exist in the project's framework | Detect the framework from `package.json`, `requirements.txt`, or `go.mod` before generating |
| OpenAPI spec has breaking changes | Regeneration overwrites custom handler logic | Never overwrite; diff against existing handlers, present changes for user review |

## Audit Log

```
- [{{timestamp}}] api-implementation:start — spec={{spec_path}}, framework={{framework}}, endpoints={{count}}
- [{{timestamp}}] route-scaffolding:complete — handlers_generated={{count}}, middleware={{list}}
- [{{timestamp}}] validation:wired — validators={{count}}, schema_source={{openapi_components}}
- [{{timestamp}}] response-serialization:complete — dtos_generated={{count}}, status_codes={{list}}
- [{{timestamp}}] integration-wiring:complete — services_injected={{count}}, transactions={{count}}
- [{{timestamp}}] smoke-tests:result — passed={{count}}, failed={{count}}, skipped={{count}}
- [{{timestamp}}] api-implementation:complete — files_created={{count}}, lines_generated={{count}}, all_smoke_pass={{bool}}
```
