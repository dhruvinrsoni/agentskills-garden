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

---

## Scope

### In Scope

- Extracting entities, attributes, and relationships from requirements artifacts.
- Creating and maintaining a domain glossary (`glossary.md`).
- Designating and enforcing Protected Terms that must never be renamed.
- Generating text-based ER diagrams (Mermaid syntax).
- Resolving ambiguous or overloaded domain terms with the user.

### Out of Scope

- Gathering requirements (see `requirements-elicitation`).
- Designing database schemas or choosing storage engines (see `database-design`).
- Writing data-access code or ORM mappings (see `data-access`).
- Defining API contracts or resource naming (see `api-contract-design`).
- Runtime performance analysis of domain objects.

---

## Guardrails

1. **Protected Terms are immutable** — Once a term is marked Protected, no skill may rename it without explicit user override logged in the audit trail.
2. **Single source of truth** — The glossary file is the canonical reference; do not define terms inline in other artifacts without a glossary entry.
3. **No implementation details** — Domain models describe *what* exists, not *how* it is stored or computed.
4. **User-confirmed definitions only** — Every entity and relationship must be validated by the user before being marked as confirmed.
5. **Aliases must be recorded** — If a term has synonyms in the domain, list all aliases in the glossary to prevent naming drift.
6. **Mermaid diagrams stay current** — Any change to entities or relationships must be reflected in the ER diagram within the same session.

---

## Ask-When-Ambiguous

Pause and ask the user when:

- A noun could refer to more than one concept (e.g., "account" = user account or financial account).
- The cardinality of a relationship is unclear (one-to-many vs. many-to-many).
- An entity's boundary overlaps with another aggregate (composite vs. separate entity).
- A term already exists in the glossary with a different definition.
- The user introduces a new term that conflicts with a programming language keyword or framework convention.
- It is unclear whether a concept is an entity, a value object, or an enum.

---

## Decision Criteria

| Situation | Decision | Rationale |
|-----------|----------|-----------|
| Same word, two meanings | Create two glossary entries with context tags | Prevents ambiguity in downstream skills |
| Term conflicts with language keyword | Prefix with domain abbreviation | Avoids compile/runtime errors |
| Uncertain cardinality | Default to one-to-many and flag for review | Most common relationship; easy to adjust |
| Entity vs. value object debate | If it has an identity lifecycle, it's an entity | Aligns with DDD principles |
| User introduces a synonym | Add as alias to existing term, do not create duplicate | Keeps glossary canonical |
| Glossary grows beyond 50 terms | Group terms by aggregate/bounded context | Maintains navigability |

---

## Success Criteria

- [ ] All entities mentioned in requirements are captured in the glossary.
- [ ] Each entity has a clear definition, attributes list, and relationship mapping.
- [ ] Protected Terms are explicitly marked and acknowledged by the user.
- [ ] An ER diagram in Mermaid syntax accurately reflects all entities and relationships.
- [ ] No ambiguous or overloaded terms remain unresolved.
- [ ] The glossary is stored in the agreed location (`glossary.md` at project root).
- [ ] All aliases for each term are recorded.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Unprotected critical term | A downstream skill renames a key entity causing inconsistency | Mark critical terms as Protected during initial modeling |
| Ambiguous term left unresolved | Different parts of the codebase use the same word differently | Always disambiguate before closing the session |
| Missing relationship | Entities exist in glossary but their connections are undocumented | Cross-check every entity pair for potential relationships |
| Glossary drift | Glossary diverges from actual code naming | Re-validate glossary against codebase periodically |
| Over-modeling | Too many fine-grained entities slow down development | Focus on aggregates first; decompose only when needed |
| Diagram staleness | ER diagram doesn't match current glossary | Update diagram in the same session as any glossary change |

---

## Audit Log

Every domain modeling session must produce an entry in the project's audit log:

```markdown
| Timestamp | Skill | Action | Detail | Confirmed By |
|-----------|-------|--------|--------|--------------|
| <ISO8601> | domain-modeling | session-started | Domain modeling session begun | — |
| <ISO8601> | domain-modeling | entities-extracted | N entities identified from requirements | user |
| <ISO8601> | domain-modeling | glossary-created | glossary.md created with N terms | user |
| <ISO8601> | domain-modeling | protected-terms-set | N terms marked as Protected | user |
| <ISO8601> | domain-modeling | er-diagram-generated | Mermaid ER diagram produced with N entities | user |
| <ISO8601> | domain-modeling | glossary-updated | Term X added/modified | user |
```

Log entries are append-only. Corrections are recorded as new rows, never as overwrites.
