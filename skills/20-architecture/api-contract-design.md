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
