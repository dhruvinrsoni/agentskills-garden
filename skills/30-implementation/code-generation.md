---
name: code-generation
description: >
  Generate production-ready code from specifications, templates, and domain models.
  Enforces language idioms, DRY principles, and project conventions.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: plan-execute
---

# Code Generation

> _"Translate intent into idiomatic, maintainable code."_

## Context

Invoked when the user needs code generated from a specification, schema,
domain model, or natural-language description. The skill produces code that
follows project conventions, language idioms, and DRY principles — never
duplicating logic that already exists in the codebase.

---

## Micro-Skills

### 1. Spec-to-Code Translation ⚡ (Power Mode)

**Goal:** Generate implementation code from a formal or informal specification.

**Steps:**

1. Parse the specification (OpenAPI, protobuf, JSON Schema, or prose).
2. Identify entities, operations, and relationships.
3. Map to target language constructs (classes, functions, types).
4. Generate code with proper type annotations and error handling.
5. Emit diff for user review.

---

### 2. Template Expansion 🌿 (Eco Mode)

**Goal:** Expand project-specific templates (boilerplate, CRUD, etc.).

**Steps:**

1. Detect project template engine or conventions (cookiecutter, plop, yeoman, or in-repo templates).
2. Resolve template variables from user input or domain context.
3. Expand the template, filling all placeholders.
4. Validate the generated code compiles / parses correctly.
5. Emit diff.

---

### 3. DRY Deduplication 🌿 (Eco Mode)

**Goal:** Before generating new code, check for existing implementations to reuse.

**Steps:**

1. Search the codebase for functions or modules that already solve the same problem.
2. If a match is found, suggest reuse (import/call) instead of generation.
3. If partial overlap exists, extract the shared logic into a helper and reference it.
4. Only generate new code when no suitable existing implementation is found.

---

### 4. Idiom Enforcement 🌿 (Eco Mode)

**Goal:** Ensure generated code follows language-specific best practices.

**Steps:**

1. Detect the target language and version from project config.
2. Apply idiomatic patterns (e.g., list comprehensions in Python, streams in Java, async/await in JS/TS).
3. Use standard library functions over hand-rolled equivalents.
4. Validate naming conventions match project style (camelCase, snake_case, etc.).

---

## Inputs

| Parameter        | Type       | Required | Description                                      |
|------------------|------------|----------|--------------------------------------------------|
| `spec`           | `string`   | yes      | Specification or description to generate from    |
| `target_lang`    | `string`   | no       | Target language (auto-detected if omitted)       |
| `output_path`    | `string`   | no       | Where to write generated code                    |
| `template_name`  | `string`   | no       | Name of project template to expand               |
| `dry_check`      | `boolean`  | no       | Whether to check for existing code first (default: true) |

## Outputs

| Field        | Type     | Description                                |
|--------------|----------|--------------------------------------------|
| `diff`       | `string` | Unified diff of generated code             |
| `files`      | `list`   | List of files created or modified          |
| `reuse_hits` | `list`   | Existing code that was reused instead      |
| `summary`    | `string` | Human-readable summary of what was generated |

---

## Scope

### In Scope
- Generating new source files from specifications, schemas, or descriptions
- Expanding project-defined templates and scaffolds
- Detecting and reusing existing code to avoid duplication
- Enforcing language idioms, naming conventions, and type annotations
- Generating accompanying type definitions, interfaces, and constants
- Producing boilerplate (constructors, getters/setters, serializers) when warranted

### Out of Scope
- Generating or modifying test files (delegate to `unit-testing` or `tdd-workflow`)
- Modifying existing CI/CD pipelines or infrastructure code
- Creating database migrations (delegate to `data-access`)
- Generating API documentation (delegate to `openapi-specs`)
- Writing code that bypasses existing abstractions or frameworks in the project
- Generating secrets, credentials, or environment-specific configuration values

---

## Guardrails

- Always perform a DRY check before generating new code; prefer reuse over creation.
- Never generate code that duplicates logic already present in the codebase.
- Preview all generated diffs before writing to disk.
- Never overwrite existing files without explicit user approval.
- Generated code must parse and compile without errors; validate before emitting.
- Do not generate into `vendor/`, `node_modules/`, `dist/`, `build/`, or `generated/` directories unless explicitly instructed.
- Include proper imports and dependency declarations for all generated code.
- Follow the project's existing code style (indentation, quotes, semicolons) exactly.
- Never hardcode secrets, API keys, or environment-specific values in generated code.

## Ask-When-Ambiguous

### Triggers
- The target language cannot be auto-detected from project context
- The specification is ambiguous about data types or nullability
- Multiple valid architectural patterns could satisfy the spec (e.g., inheritance vs. composition)
- An existing function partially overlaps with what needs to be generated
- The spec references external dependencies not present in the project

### Question Templates
1. "The target language isn't clear from the project — should I generate in `{lang_a}` or `{lang_b}`?"
2. "The spec doesn't specify whether `{field}` can be null. Should I treat it as required or optional?"
3. "I found existing code in `{file}` that partially covers this. Should I extend it or generate a new implementation?"
4. "This could be implemented using `{pattern_a}` or `{pattern_b}` — which approach do you prefer?"
5. "The spec references `{dependency}` which isn't in the project. Should I add it or use an alternative?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Existing function fully covers the need | Reuse via import; do not generate new code |
| Existing function partially overlaps | Extract shared logic into a helper, then generate the remainder |
| No existing code matches | Generate new code following project conventions |
| Target language is ambiguous | Ask the user before generating |
| Spec has multiple valid interpretations | Choose the simplest interpretation; flag alternatives in a comment |
| Generated code exceeds 200 lines in a single file | Split into multiple files or modules |
| Project has a template that matches the task | Use the template instead of generating from scratch |

## Success Criteria

- [ ] Generated code compiles/parses without errors
- [ ] No logic duplication with existing codebase (DRY check passed)
- [ ] Language idioms and project naming conventions are followed
- [ ] All necessary imports and dependencies are declared
- [ ] Type annotations are present where the language supports them
- [ ] Generated code includes basic error handling for failure paths
- [ ] User reviewed and approved the diff before it was written to disk

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Generated code doesn't compile | Syntax errors or missing imports in output | Run parser/compiler validation before emitting; fix errors automatically |
| Logic duplication introduced | Same function exists elsewhere in codebase | Always run DRY deduplication micro-skill first; search before generating |
| Wrong language idioms used | Code works but looks foreign to the project | Detect language version and lint config; apply idiomatic transforms |
| Overwrote existing file | User's code was replaced without consent | Never overwrite without explicit approval; always preview diffs first |
| Spec misinterpreted | Generated code doesn't match user intent | Ask clarifying questions when spec is ambiguous; show spec-to-code mapping |
| Stale template expanded | Template is outdated or incompatible with current project | Validate template against project version; warn if template hasn't been updated recently |

## Audit Log

```
- [{{timestamp}}] code-generation:start — spec_type={{spec_type}}, target_lang={{lang}}, output_path={{path}}
- [{{timestamp}}] dry-check:result — duplicates_found={{count}}, reuse_suggestions={{list}}
- [{{timestamp}}] template:expanded — template_name={{name}}, variables={{vars}}
- [{{timestamp}}] idiom-check:applied — patterns={{patterns}}, conventions={{conventions}}
- [{{timestamp}}] validation:result — compiles={{bool}}, lint_pass={{bool}}, errors={{errors}}
- [{{timestamp}}] code-generation:complete — files_created={{count}}, lines_generated={{count}}, reused={{count}}
```
