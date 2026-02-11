---
name: domain-modeling
description: >
  Create and maintain a domain glossary with entities, relationships,
  and Protected Terms that must never be renamed.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - requirements-elicitation
reasoning_mode: plan-execute
---

# Domain Modeling

> _"Name things once. Name them right."_

## Context

Invoked after requirements elicitation to establish a shared vocabulary.
The domain model becomes the **single source of truth** for naming
conventions throughout the project.

---

## Micro-Skills

### 1. Entity Extraction ⚡ (Power Mode)

**Steps:**

1. Parse requirements and conversation transcripts for **nouns** (entities)
   and **verbs** (actions/events).
2. Group related nouns into **aggregates**.
3. Define each entity with: name, description, attributes, relationships.

### 2. Glossary Generation 🌿 (Eco Mode)

**Steps:**

1. Create `glossary.md` in the project root.
2. Format as a table: Term | Definition | Aliases | Protected.
3. Mark **Protected Terms** — identifiers that must never be renamed by
   any skill (especially `cleanup → safe-renaming`).

### 3. Relationship Mapping ⚡ (Power Mode)

**Steps:**

1. Identify relationships: has-one, has-many, belongs-to, many-to-many.
2. Draw a simple text-based ER diagram using Mermaid syntax.
3. Validate cardinality with the user.

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `glossary`         | `markdown` | The domain glossary file                 |
| `er_diagram`       | `string`   | Mermaid ER diagram                       |
| `protected_terms`  | `string[]` | Terms that must never be renamed         |

---

## Edge Cases

- Ambiguous terms (e.g., "order" = purchase order or sort order) — Ask user
  to disambiguate. Record both meanings with context tags.
- Domain terms that conflict with language keywords — Prefix with domain
  abbreviation (e.g., `OrderStatus` not `Status`).
