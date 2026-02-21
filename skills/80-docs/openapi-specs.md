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

---

## Scope

### In Scope

- Generating OpenAPI 3.0/3.1 specifications from route definitions, decorators, and type annotations.
- Validating existing specs for completeness, correctness, and style using linters (Spectral, swagger-cli).
- Detecting drift between the spec and the actual API implementation.
- Adding descriptions, examples, and `$ref` schemas to improve spec quality.
- Updating specs when new endpoints or schema changes are introduced.

### Out of Scope

- Implementing API endpoints or modifying application controller code — defer to `api-implementation`.
- Designing API contracts from scratch (resource modeling, versioning strategy) — defer to `api-contract-design`.
- Generating client SDKs or server stubs from specs — recommend `openapi-generator` but do not execute.
- Managing API gateway configuration, rate limiting, or authentication middleware.
- Writing prose-form API guides or tutorials — defer to `api-documentation`.

## Guardrails

- Never overwrite an existing `openapi.yaml` without diffing against the current version first.
- Preserve all manually-written descriptions, examples, and vendor extensions (`x-*`) already in the spec.
- Always output valid OpenAPI 3.x — validate with a linter before presenting the result.
- Use `$ref` for shared schemas; never duplicate schema definitions inline across multiple endpoints.
- Do not invent endpoints or fields not present in the source code during code-to-spec generation.
- Mark all fields lacking explicit nullability as `required` unless code evidence shows otherwise.
- Include at least one `example` value for every request body and response schema.

## Ask-When-Ambiguous

### Triggers

- The target OpenAPI version (3.0 vs 3.1) is not specified.
- Multiple API frameworks or entry points exist in the project.
- Authentication scheme is used in code but not documented in the spec.
- The user says "update the spec" but doesn't specify which endpoints changed.
- Response schemas differ between code and existing spec and the correct version is unclear.

### Question Templates

- "Should I generate the spec as OpenAPI 3.0.3 or 3.1.0? (3.1 supports JSON Schema 2020-12.)"
- "I found route definitions in both `{path_a}` and `{path_b}`. Which module should I generate the spec from?"
- "The `{endpoint}` handler returns `{code_type}` but the existing spec says `{spec_type}`. Which is correct?"
- "Should I include internal/admin endpoints in the spec or only public-facing ones?"
- "The code uses `{auth_method}`. Should I add a `securitySchemes` entry for it?"

## Decision Criteria

| Situation | Action |
|---|---|
| No existing spec in the project | Generate a complete OpenAPI 3.1 spec from code |
| Spec exists but is outdated | Run drift detection, then patch only the changed endpoints |
| Spec exists and code changed | Merge new endpoints/schemas into the existing spec |
| Multiple microservices with separate specs | Generate per-service specs; do not merge into one file |
| Spec has lint warnings but is functionally correct | Fix warnings in a separate commit; do not block generation |
| Shared schemas across endpoints | Extract to `components/schemas` and use `$ref` |
| Authentication in code but missing from spec | Add `securitySchemes` and apply `security` to relevant paths |

## Success Criteria

- [ ] Generated spec passes Spectral linting with zero errors.
- [ ] Every path has a summary, description, and at least one response example.
- [ ] All `$ref` pointers resolve to defined components.
- [ ] Drift report shows zero undocumented endpoints.
- [ ] Request/response schemas match the actual code types (verified by drift detection).
- [ ] No duplicate schema definitions exist — shared types use `$ref`.
- [ ] Spec renders correctly in Swagger UI or Redoc without errors.

## Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| Stale spec after code changes | Drift report flags missing or mismatched endpoints | Re-run code-to-spec generation; merge changes into existing spec |
| Broken `$ref` pointers | Spec linter reports unresolved references | Validate all `$ref` paths before output; use relative pointers |
| Missing response schemas | Consumers cannot generate typed clients | Extract return types from code; require at least 200 and error responses |
| Over-generated spec from internal routes | Internal admin endpoints leak into public docs | Filter routes by prefix or decorator; ask user which routes to include |
| Schema duplication | Same object defined inline in multiple endpoints | Refactor to `components/schemas` with `$ref`; deduplicate on field signature |
| Wrong OpenAPI version features used | 3.1 features (e.g., `type: ["string", "null"]`) break 3.0 tooling | Detect target version and constrain output syntax accordingly |

## Audit Log

- `[{timestamp}]` Skill invoked — mode: `{generate|validate|drift}`, framework detected: `{framework}`.
- `[{timestamp}]` Endpoints discovered: `{count}` across `{file_count}` source files.
- `[{timestamp}]` Spec generated: `{output_path}`, OpenAPI version: `{version}`, paths: `{path_count}`, schemas: `{schema_count}`.
- `[{timestamp}]` Lint result: `{error_count}` errors, `{warning_count}` warnings — rules: `{ruleset}`.
- `[{timestamp}]` Drift detected: `{added}` new, `{removed}` missing, `{changed}` mismatched endpoints.
- `[{timestamp}]` Spec updated: `{paths_added}` paths added, `{schemas_modified}` schemas modified.
