---
name: database-design
description: >
  Schema design, normalization analysis, migration planning, and
  index strategy for relational and NoSQL databases.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - domain-modeling
reasoning_mode: plan-execute
---

# Database Design

> _"Your schema is your data contract with the future."_

## Context

Invoked when designing a new database schema or modifying an existing one.
Covers relational (PostgreSQL, MySQL) and document (MongoDB, DynamoDB)
databases.

---

## Micro-Skills

### 1. Schema Design ⚡ (Power Mode)

**Steps:**

1. Map domain entities to tables/collections.
2. Define columns: name, type, nullable, default, constraints.
3. Define primary keys (prefer UUIDs or ULID for distributed systems).
4. Define foreign keys and cascade rules.
5. Apply normalization (target 3NF, denormalize only with justification).

### 2. Migration Planning ⚡ (Power Mode)

**Steps:**

1. Generate migration files (SQL or ORM-specific format).
2. Ensure migrations are **idempotent** and **reversible**.
3. Include both `up` and `down` scripts.
4. For destructive changes (column drop, type change):
   - Require explicit user approval (Ahimsa).
   - Suggest a multi-step deployment (add new → migrate data → drop old).

### 3. Index Strategy ⚡ (Power Mode)

**Steps:**

1. Analyze expected query patterns.
2. Suggest indexes: B-tree for equality/range, GIN for full-text/JSONB.
3. Warn about over-indexing (write penalty) and missing indexes (slow reads).
4. Document index rationale.

### 4. Seed Data 🌿 (Eco Mode)

**Steps:**

1. Generate seed data scripts for development and testing.
2. Include realistic but anonymized sample data.
3. Make seeds idempotent (upsert pattern).

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `schema_ddl`    | `string`   | CREATE TABLE statements                  |
| `migrations`    | `string[]` | Ordered migration files                  |
| `index_plan`    | `object`   | Index recommendations with rationale     |
| `er_diagram`    | `string`   | Mermaid ER diagram                       |

---

## Edge Cases

- Schema change on a table with millions of rows — Recommend online DDL
  tools (pt-online-schema-change, pg_repack).
- Circular foreign keys — Break with nullable FK + application-level checks.
