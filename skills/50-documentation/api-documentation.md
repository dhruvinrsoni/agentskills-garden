```markdown
---
name: api-documentation
description: >
  Generate, validate, and maintain API endpoint documentation including
  OpenAPI specs, request/response examples, and versioned API references.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - openapi-specs
reasoning_mode: linear
---

# API Documentation

> _"An undocumented API is an unusable API."_

## Context

Invoked when API endpoints need comprehensive documentation — including
endpoint descriptions, parameter details, request/response examples,
authentication requirements, error codes, and versioning notes. This skill
produces consumer-facing reference docs that developers rely on to integrate.

---

## Micro-Skills

### 1. Endpoint Catalog Generation 🌿 (Eco Mode)

**Steps:**

1. Scan route definitions across the codebase.
2. Extract HTTP method, path, path parameters, query parameters, headers.
3. Identify request body schema and response schema for each endpoint.
4. Generate a structured endpoint catalog grouped by resource/domain.

### 2. Request/Response Example Generation 🌿 (Eco Mode)

**Steps:**

1. For each endpoint, generate realistic example request payloads.
2. Generate corresponding success and error response examples.
3. Include edge-case examples (empty collections, pagination, validation errors).
4. Validate examples against the declared schemas.

### 3. API Versioning Documentation ⚡ (Power Mode)

**Steps:**

1. Detect versioning strategy (URL path, header, query parameter).
2. Document version-specific behavioral differences.
3. Generate migration guides between API versions.
4. Flag deprecated endpoints with sunset dates and successor endpoints.

---

## Inputs

| Parameter         | Type     | Required | Description                                  |
|-------------------|----------|----------|----------------------------------------------|
| `source_dir`      | `string` | yes      | Root directory of API source code             |
| `spec_file`       | `string` | no       | Path to existing OpenAPI spec if available    |
| `api_version`     | `string` | no       | Target API version to document                |
| `output_format`   | `string` | no       | Output format: `markdown`, `html`, `openapi`  |

## Outputs

| Field             | Type     | Description                                  |
|-------------------|----------|----------------------------------------------|
| `docs`            | `string` | Generated API reference documentation        |
| `spec_file`       | `string` | Updated or generated OpenAPI YAML/JSON       |
| `examples`        | `object` | Request/response example collection          |
| `coverage_report` | `string` | Endpoints documented vs undocumented         |

---

## Scope

### In Scope
- Documenting REST and GraphQL API endpoints
- Generating and updating OpenAPI 3.x specifications
- Creating request/response examples with realistic data
- Documenting authentication and authorization requirements per endpoint
- Versioned API reference generation and migration guides
- Error code catalogs with descriptions and resolution hints
- Rate limiting and pagination documentation

### Out of Scope
- Internal service-to-service RPC documentation (use system-design skill)
- API implementation or code changes (use api-implementation skill)
- Load testing or performance benchmarking of endpoints
- API gateway configuration or infrastructure setup
- Client SDK generation from specs

## Guardrails

- Preview diffs before applying any changes.
- Never touch generated, vendor, third_party, build, or dist folders unless explicitly allowed.
- Run formatter and linter after changes; revert if errors introduced.
- Never expose internal implementation details (database schemas, internal IDs) in public API docs.
- Validate all example payloads against their declared schemas before publishing.
- Ensure sensitive fields (tokens, passwords, PII) use redacted placeholder values in examples.
- Preserve existing manually-written endpoint descriptions — only augment, never overwrite.
- Flag any undocumented endpoint as a documentation gap rather than silently skipping it.

## Ask-When-Ambiguous

### Triggers
- Multiple API versioning strategies detected in the codebase
- Endpoint has no clear request/response schema (e.g., dynamic or untyped)
- Authentication mechanism is unclear or inconsistent across endpoints
- Conflicting documentation exists between spec file and inline comments

### Question Templates
1. "Multiple versioning strategies detected (URL path and header). Which should be documented as the primary strategy?"
2. "Endpoint `{method} {path}` has no typed schema. Should I infer from usage or skip documenting the payload?"
3. "Auth requirements differ between `{endpoint_a}` and `{endpoint_b}` in the same resource group. Are these intentional?"
4. "The OpenAPI spec says `{field}` is required, but the code treats it as optional. Which is correct?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Endpoint has OpenAPI spec and inline docs | Prefer spec as source of truth; flag discrepancies |
| Endpoint has no documentation at all | Generate docs from code analysis and mark as "auto-generated — needs review" |
| Multiple response codes possible | Document all observed status codes with example bodies |
| Deprecated endpoint detected | Include deprecation notice with sunset date and migration path |
| Versioned and unversioned routes coexist | Document both; recommend the versioned route as primary |

## Success Criteria

- [ ] Every public endpoint has a documented description, method, path, and parameters
- [ ] All request/response examples validate against declared schemas
- [ ] Error responses are documented with status codes and error body structure
- [ ] Authentication requirements are documented per endpoint or endpoint group
- [ ] No internal implementation details leak into public documentation
- [ ] Documentation coverage report shows ≥ 95% of endpoints documented

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Schema drift between spec and code | Examples fail validation; consumers report incorrect docs | Run spec-to-code drift detection before generating docs |
| Sensitive data in examples | Tokens, real emails, or PII appear in sample payloads | Scan examples for credential/PII patterns before publishing |
| Missing error documentation | Consumers encounter undocumented 4xx/5xx responses | Cross-reference error-handling middleware to catalog all thrown status codes |
| Stale versioning info | Docs reference sunset versions still marked as active | Validate version lifecycle metadata against deployment config |
| Over-documentation of internals | Internal-only endpoints appear in public docs | Filter endpoints by route prefix or annotation (e.g., `@internal`) |

## Audit Log

- `[{timestamp}] api-docs-generated: Generated API docs for {endpoint_count} endpoints in {source_dir}`
- `[{timestamp}] examples-validated: Validated {example_count} request/response examples against schemas — {pass_count} passed, {fail_count} failed`
- `[{timestamp}] coverage-report: Documentation coverage {coverage_pct}% — {undocumented_count} endpoints missing docs`
- `[{timestamp}] drift-detected: {drift_count} spec-to-code discrepancies found and flagged`
- `[{timestamp}] version-migration: Generated migration guide from {old_version} to {new_version}`
```
