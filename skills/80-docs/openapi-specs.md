---
name: openapi-specs
description: >
  Generate or update OpenAPI (Swagger) specifications from existing
  code, or validate code against existing specs.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - api-contract-design
reasoning_mode: linear
---

# OpenAPI Spec Generation

> _"The spec is the single source of truth for your API."_

## Context

Invoked when API documentation needs to be generated from code, or when
existing specs need to be updated to reflect implementation changes.

---

## Micro-Skills

### 1. Code-to-Spec Generation 🌿 (Eco Mode)

**Steps:**

1. Detect the API framework:
   - Express/Fastify → scan route definitions.
   - FastAPI → extract from type hints + decorators.
   - Spring → extract from `@RequestMapping` annotations.
   - Go (Gin/Echo) → scan handler registrations.
2. Extract: paths, methods, parameters, request/response schemas.
3. Generate `openapi.yaml` (OpenAPI 3.1).
4. Add descriptions from JSDoc, docstrings, or comments.

### 2. Spec Validation 🌿 (Eco Mode)

**Steps:**

1. Run a spec linter (Spectral, swagger-cli).
2. Check for: missing descriptions, missing examples, unused schemas.
3. Validate all `$ref` pointers resolve correctly.
4. Report issues sorted by severity.

### 3. Spec-to-Code Drift Detection 🌿 (Eco Mode)

**Steps:**

1. Compare the spec with actual implementation.
2. Flag:
   - Endpoints in spec but not implemented.
   - Endpoints implemented but not in spec.
   - Schema mismatches (field types, required fields).
3. Generate a drift report.

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `spec_file`     | `string` | Generated/updated OpenAPI YAML           |
| `lint_report`   | `string` | Validation report                        |
| `drift_report`  | `string` | Spec vs implementation drift             |
