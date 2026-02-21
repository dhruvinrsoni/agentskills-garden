---
name: api-contract-design
description: >
  Design REST or gRPC API contracts (OpenAPI/Protobuf) before any
  implementation code is written. Contract-first development.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - domain-modeling
reasoning_mode: plan-execute
---

# API Contract Design

> _"Design the contract. Then build to it."_

## Context

Invoked when a new API endpoint or service boundary is being created.
The contract is the **source of truth** — implementation must conform to it,
not the other way around.

---

## Micro-Skills

### 1. Resource Modeling ⚡ (Power Mode)

**Steps:**

1. Identify resources from the domain model (nouns become resources).
2. Define URL structure following REST conventions:
   - `GET /resources` — list
   - `GET /resources/{id}` — detail
   - `POST /resources` — create
   - `PUT /resources/{id}` — full update
   - `PATCH /resources/{id}` — partial update
   - `DELETE /resources/{id}` — remove
3. Define query parameters for filtering, pagination, sorting.

### 2. Schema Definition ⚡ (Power Mode)

**Steps:**

1. Define request/response schemas using JSON Schema or Protobuf.
2. Include all required fields, optional fields, and validation constraints.
3. Define error response schemas (RFC 7807 Problem Details).

### 3. OpenAPI Spec Generation ⚡ (Power Mode)

**Steps:**

1. Generate an `openapi.yaml` file (OpenAPI 3.1).
2. Include: info, servers, paths, components/schemas, security schemes.
3. Add examples for every endpoint.
4. Validate the spec using a linter.

### 4. Versioning Strategy 🌿 (Eco Mode)

**Steps:**

1. Ask user: URL path versioning (`/v1/`) or header versioning.
2. Document the chosen strategy in the spec and an ADR.
3. Set up deprecation headers for future use.

---

## Outputs

| Field          | Type     | Description                              |
|----------------|----------|------------------------------------------|
| `openapi_spec` | `yaml`   | Complete OpenAPI 3.1 specification       |
| `schemas`      | `object` | JSON Schema definitions                  |
| `adr`          | `string` | ADR for versioning/design decisions      |

---

## Edge Cases

- User wants GraphQL instead of REST — Switch to SDL-first design.
- Circular references in schemas — Break cycle with `$ref` and document.

---

## Scope

### In Scope

- Designing REST API contracts using OpenAPI 3.x specifications.
- Designing gRPC service contracts using Protocol Buffers.
- Defining request/response schemas, error formats (RFC 7807), and pagination patterns.
- Generating and validating `openapi.yaml` or `.proto` files.
- Establishing versioning strategy (URL path, header, or query parameter).
- Defining authentication/authorization schemes in the contract (OAuth2, API key, JWT).

### Out of Scope

- Implementing API handlers, controllers, or service logic (use `api-implementation` skill).
- Deploying or configuring API gateways, load balancers, or infrastructure.
- Writing integration or end-to-end tests for the API (use `integration-testing` skill).
- Database schema or data-access layer design (use `database-design` skill).
- Generating client SDKs from the spec (downstream tooling concern).

---

## Guardrails

- Always design the contract before any implementation code is written (contract-first).
- Every endpoint must include at least one request example and one response example.
- Error responses must follow RFC 7807 Problem Details format.
- Never introduce breaking changes to a published contract without incrementing the version.
- All path parameters, query parameters, and body fields must have descriptions and type constraints.
- Validate the generated OpenAPI spec with a linter (e.g., Spectral) before finalizing.
- Do not embed business logic or implementation details (e.g., database column names) in the contract.
- Require pagination for all list endpoints returning unbounded collections.

---

## Ask-When-Ambiguous

### Triggers

- The user has not specified REST vs gRPC vs GraphQL.
- Versioning strategy is not defined and the project has no prior convention.
- The user requests an endpoint that could be modeled as either a sub-resource or a top-level resource.
- Authentication scheme is unspecified for a non-public API.
- Pagination style is not indicated (cursor-based vs offset-based).

### Question Templates

- "Should this API use REST (OpenAPI), gRPC (Protobuf), or GraphQL (SDL)?"
- "How should the API be versioned — URL path (`/v1/`), `Accept` header, or a custom header?"
- "Should `{child}` be a sub-resource of `{parent}` (e.g., `/parents/{id}/children`) or a top-level resource (`/children?parentId={id}`)?"
- "This API appears to require authentication. Which scheme should the contract specify — OAuth2, API key, or JWT bearer?"
- "For list endpoints, do you prefer cursor-based or offset-based pagination?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| New service boundary identified in domain model | Start with Resource Modeling micro-skill to map domain nouns to REST resources |
| User provides entity relationships but no URL structure | Derive URL hierarchy from entity ownership; nested resources for strict parent-child, flat for loose associations |
| Multiple HTTP methods could serve the same operation | Follow REST semantics strictly: idempotent updates → PUT/PATCH, creation → POST, retrieval → GET |
| Schema has optional fields with complex defaults | Define explicit `default` values in JSON Schema; document nullability rules in field description |
| Contract needs to support both internal and external consumers | Define separate security schemes and tag endpoints by audience; consider a public vs internal spec split |
| Breaking change is required on a published contract | Increment the major version; keep the old version available with a deprecation sunset date |

---

## Success Criteria

- [ ] OpenAPI or Protobuf spec is syntactically valid and passes linter checks.
- [ ] Every endpoint has a summary, description, and at least one example request/response.
- [ ] All error responses use RFC 7807 Problem Details schema.
- [ ] Versioning strategy is documented in the spec and captured in an ADR.
- [ ] List endpoints include pagination parameters and response metadata.
- [ ] Security schemes are defined and applied to all non-public endpoints.
- [ ] No implementation-specific details (database fields, internal IDs) leak into the contract.
- [ ] The spec can generate a valid mock server without additional configuration.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Contract diverges from implementation | Clients receive fields or status codes not in the spec | Add contract validation tests in CI that compare live responses to the OpenAPI spec |
| Over-specified schemas block evolution | Minor additions require a version bump because `additionalProperties: false` is set everywhere | Default to `additionalProperties: true` for response schemas; restrict only request schemas |
| Inconsistent naming conventions | Mix of camelCase and snake_case across endpoints | Enforce a naming convention via linter rules (e.g., Spectral) and document it in the spec's `info.description` |
| Missing error schemas | Clients cannot programmatically handle errors | Mandate RFC 7807 error schema in Guardrails; validate with linter rule that every 4xx/5xx response has a `$ref` to the error schema |
| Pagination omitted on list endpoints | Clients retrieve unbounded result sets, causing timeouts | Require `limit`/`offset` or `cursor` parameters for every `GET` that returns an array; enforce via linter |
| Security scheme not applied | Endpoints are unprotected in the spec even though the API requires auth | Linter rule to require a `security` block on every operation unless explicitly tagged as public |

---

## Audit Log

- `[{timestamp}] CONTRACT_CREATED — Spec: {filename} | Format: {openapi|protobuf} | Endpoints: {count}`
- `[{timestamp}] RESOURCE_MODELED — Resource: {name} | Methods: [{methods}] | Path: {url_path}`
- `[{timestamp}] SCHEMA_DEFINED — Schema: {name} | Fields: {count} | Required: [{required_fields}]`
- `[{timestamp}] VERSION_STRATEGY_SET — Strategy: {url_path|header|query} | Recorded in: ADR-{number}`
- `[{timestamp}] SPEC_VALIDATED — Linter: {tool} | Errors: {count} | Warnings: {count}`
- `[{timestamp}] BREAKING_CHANGE_DETECTED — Endpoint: {path} | Change: {description} | Action: version bumped to {version}`
