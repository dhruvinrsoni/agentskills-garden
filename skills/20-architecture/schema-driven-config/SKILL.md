---
name: schema-driven-config
description: >
  Define configuration as a single schema that powers defaults, validation,
  storage, and optional UI generation. One entry per setting, zero duplication.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad"
  reasoning_mode: linear
  skill_type: standard
---


# Schema-Driven Configuration

> _"One schema to rule them all — defaults, validation, storage, UI."_

## Context

Invoked when a project needs configuration management — settings pages, feature
flags, environment variables, or any system where values have defaults,
constraints, and persistence. The core principle: define the schema once and
derive everything else from it.

## Scope

**In scope:** Schema definition patterns, default generation, validation
pipelines, storage mapping, and optional UI generation from schema.

**Out of scope:** Specific storage backends (Redis, Postgres, etc.), specific
UI frameworks (React, Vue, etc.), authentication/authorization for settings.

---

## Micro-Skills

### 1. Schema Definition 🌿 (Eco Mode)

**Goal:** Define the single source of truth for all configuration.

**Steps:**

1. Create one schema object where each key maps to a setting definition:
   ```
   key → { default, validate, transform, description, type }
   ```
2. **Nano: Schema Entry** — each setting is a 1-2 liner defining its type,
   default, and optional validator.
3. Every setting lives in the schema — no scattered defaults across the
   codebase. If a value has a default, it belongs here.
4. Group settings logically (e.g., by feature area) within the schema.
5. Include `description` for every entry — this drives documentation and
   UI labels.

**Schema entry anatomy:**

| Field | Required | Purpose |
|-------|----------|---------|
| `default` | yes | Fallback value when not explicitly set |
| `type` | yes | Expected type (string, number, boolean, enum, object) |
| `validate` | no | Constraint function: `(value) → boolean` |
| `transform` | no | Coercion function: `(raw) → typed` |
| `description` | yes | Human-readable explanation (used in UI and docs) |

### 2. Default Generation 🌿 (Eco Mode)

**Goal:** Derive defaults from the schema — never hardcode elsewhere.

**Steps:**

1. Write a single `getDefaults()` function that iterates the schema and
   returns an object with all default values.
2. **Nano: Single Default Source** — every code path that needs a default
   value calls `getDefaults()` or reads from the schema. Search the codebase
   for hardcoded values that duplicate schema defaults — eliminate them.
3. For nested settings, recursively generate defaults from nested schema
   definitions.
4. Defaults must be immutable — return a fresh copy each time.

### 3. Validation Pipeline 🌿 (Eco Mode)

**Goal:** Validate configuration at system boundaries.

**Steps:**

1. Validate at load time (reading from storage), save time (writing to storage),
   and API input boundaries.
2. For each setting, run its `validate` function if defined. Reject invalid
   values — fall back to the schema default.
3. **Nano: Boundary Validation** — validate at the edges, trust internally.
   Once a value passes validation at the boundary, internal code can use it
   without re-checking.
4. Collect all validation errors — don't fail on the first one. Return a
   complete error report.
5. Log validation failures with the setting key, rejected value, and constraint.

### 4. Storage Mapping 🌿 (Eco Mode)

**Goal:** Map schema to persistent storage through a single accessor.

**Steps:**

1. Create a unified settings accessor: `get(key)`, `set(key, value)`,
   `getAll()`, `reset(key)`.
2. The accessor handles: read from storage → validate → transform → return.
3. Storage backend is pluggable — file, database, environment variables,
   browser storage, cloud config. The schema doesn't care.
4. On `set()`: validate against schema → transform → persist → notify
   listeners.
5. On `get()`: read from storage → if missing, return schema default →
   transform → return.

### 5. UI Generation ⚡ (Power Mode)

**Goal:** Optionally derive a settings UI from the schema.

**Steps:**

1. Map schema types to UI components:
   - `boolean` → toggle/checkbox
   - `string` → text input
   - `number` → number input with min/max from validator
   - `enum` → dropdown/select
   - `object` → nested section/accordion
2. Use `description` as the label/tooltip.
3. Use `default` as the placeholder/initial value.
4. Wire `validate` to form-level validation (real-time feedback).
5. Group settings by schema structure — each top-level group becomes a
   tab or section.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `schema` | `object` | yes | The configuration schema definition |
| `storage_backend` | `string` | yes | Where settings are persisted |
| `current_values` | `object` | no | Existing configuration to validate/migrate |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `validated_config` | `object` | Configuration with all values validated |
| `defaults` | `object` | Generated default values from schema |
| `validation_report` | `array` | List of validation errors (if any) |

---

## Guardrails

- Schema is the single source of truth — no defaults scattered in code.
- Validation is declarative (schema-defined), not procedural (ad-hoc if/else).
- Storage backend must be pluggable — schema doesn't reference specific storage.
- Never silently coerce invalid values — log and fall back to default.
- Schema changes must be backwards-compatible or include a migration.

## Ask-When-Ambiguous

**Triggers:**

- Setting type is unclear (string vs enum?)
- Default value depends on environment (dev vs prod)
- Validation rules conflict with existing stored data

**Question Templates:**

1. "Setting '{key}' has multiple possible types. Should it be {type-a} or {type-b}?"
2. "Default for '{key}' differs between environments. Should we use a single default or environment-aware defaults?"
3. "Existing stored values for '{key}' would fail new validation. Migrate or grandfather?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| New setting needed | Add to schema — one entry with default, type, validate, description |
| Setting deprecated | Mark as deprecated in schema, keep for backwards compatibility, migrate in next major |
| Storage backend change | Swap the storage adapter — schema and accessors remain unchanged |
| Complex validation | Compose validators: `validate: (v) => isString(v) && minLength(v, 3)` |

## Success Criteria

- [ ] Every setting has exactly one definition (in the schema)
- [ ] No hardcoded defaults outside the schema
- [ ] Validation catches all invalid values at boundaries
- [ ] Adding a new setting requires only one schema entry
- [ ] Storage backend can be swapped without touching the schema

## Failure Modes

- **Scattered defaults** — defaults exist in both schema and code. **Recovery:** search for hardcoded values, consolidate into schema.
- **Silent coercion** — invalid values are silently transformed without logging. **Recovery:** always log coercion events.
- **Schema-storage mismatch** — schema expects a type that storage can't represent. **Recovery:** add transform functions to bridge the gap.

## Audit Log

- `[timestamp] schema-loaded: {N} settings defined, {M} with validators`
- `[timestamp] validation-failed: key="{key}", value="{value}", constraint="{rule}"`
- `[timestamp] setting-changed: key="{key}", old="{old}", new="{new}"`
- `[timestamp] defaults-generated: {N} settings with defaults applied`

---

## Examples

### Example 1 — Application Settings

**Schema (3 entries):**
```
theme:       { default: "light", type: "enum", values: ["light", "dark", "auto"], description: "UI color theme" }
page_size:   { default: 25, type: "number", validate: (v) => v >= 10 && v <= 100, description: "Items per page" }
auto_save:   { default: true, type: "boolean", description: "Auto-save drafts every 30 seconds" }
```

**Flow:** Schema → `getDefaults()` returns `{theme: "light", page_size: 25, auto_save: true}` → storage accessor reads/writes → UI generates toggle, dropdown, number input.

### Example 2 — Feature Flags

**Schema (3 flags):**
```
new_checkout:    { default: false, type: "boolean", description: "Enable redesigned checkout flow" }
dark_mode:       { default: false, type: "boolean", description: "Enable dark mode UI" }
ai_suggestions:  { default: false, type: "boolean", description: "Show AI-powered product suggestions" }
```

**Flow:**

1. **Defaults:** `getDefaults()` returns `{ new_checkout: false, dark_mode: false, ai_suggestions: false }` — all flags off.
2. **Storage override:** Ops team enables `new_checkout` for 10% of users via storage. `get("new_checkout")` returns `true` for those users, `false` for others.
3. **No validation needed:** Boolean is self-validating — any non-boolean input is rejected by type check, falls back to `false`.
4. **Adding a flag:** New flag `beta_search` added to schema. Zero migration — existing storage has no entry, so `get("beta_search")` returns the schema default (`false`).

### Example 3 — Validation Error Scenario

**Schema entry:** `page_size: { default: 25, type: "number", validate: (v) => v >= 10 && v <= 100, description: "Items per page" }`

**User submits:** `set("page_size", 500)`

**Flow:**

1. Accessor runs `validate(500)` → returns `false` (500 > 100).
2. Value rejected. Accessor returns validation error: `{ key: "page_size", value: 500, constraint: "v >= 10 && v <= 100", message: "Value 500 exceeds maximum 100" }`.
3. Setting retains previous value (or schema default if never set).
4. Audit log: `[2026-03-18T14:22:00Z] validation-failed: key="page_size", value="500", constraint="v >= 10 && v <= 100"`.

### Example 4 — Schema Migration

**Old schema (v1):** `{ theme: ..., page_size: ... }` — 2 settings.

**New schema (v2):** `{ theme: ..., page_size: ..., language: { default: "en", type: "enum", values: ["en", "es", "fr", "de"], description: "UI language" } }` — added `language`.

**Flow:**

1. Schema updated with new `language` entry. No storage migration needed.
2. Existing users call `get("language")` → storage has no entry → returns schema default `"en"`.
3. New users who set `language` to `"fr"` → stored in their settings.
4. Old settings untouched. Zero-downtime, backwards-compatible migration.

---

## Edge Cases

- **Unknown key requested:** Return `undefined` or throw — never invent a default for an unregistered key.
- **Schema migration:** When adding new keys to schema, existing storage won't have them. `get()` must gracefully fall back to schema default.
- **Circular transforms:** A transform that calls `get()` on another key. Prevent with a dependency-free transform contract.
- **Large schema:** 100+ settings. Group into sub-schemas, lazy-load groups.
