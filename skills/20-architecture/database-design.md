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

---

## Scope

### In Scope

- Designing relational schemas (PostgreSQL, MySQL, SQLite) and document schemas (MongoDB, DynamoDB).
- Normalization analysis (1NF through BCNF) and intentional denormalization with documented justification.
- Writing and reviewing DDL statements (CREATE TABLE, ALTER TABLE, CREATE INDEX).
- Generating migration files (up/down) in SQL or ORM-specific formats.
- Index strategy: selecting index types, analyzing query patterns, flagging missing or redundant indexes.
- Generating ER diagrams (Mermaid) and seed data scripts.

### Out of Scope

- Writing application-level data-access or ORM code (use `data-access` skill).
- Database server installation, configuration, or performance tuning at the infrastructure level (use `db-tuning` skill).
- Backup, replication, or disaster-recovery planning.
- API or service layer design that consumes the schema (use `api-contract-design` skill).
- Data warehouse or OLAP schema design (star/snowflake schemas).

---

## Guardrails

- Never execute destructive DDL (DROP TABLE, DROP COLUMN, type narrowing) without explicit user approval.
- All migrations must include both `up` and `down` scripts and be idempotent.
- Require justification (as a comment in the migration) for any denormalization beyond 3NF.
- Primary keys must be explicitly defined — never rely on implicit row IDs.
- Foreign keys must specify ON DELETE and ON UPDATE behavior.
- Warn when adding an index on a high-write table with more than 5 existing indexes.
- Seed data must use anonymized or synthetic values — never include real PII.
- Preview the full DDL diff before applying any schema change.

---

## Ask-When-Ambiguous

### Triggers

- Target database engine is not specified (PostgreSQL vs MySQL vs MongoDB vs DynamoDB).
- The user asks to "add a field" but the entity could belong to multiple tables.
- Normalization level is debatable (e.g., repeated groups that could be extracted to a join table).
- A destructive migration is required and rollback risk is unclear.
- The user provides entity names but no cardinality (one-to-many vs many-to-many).

### Question Templates

- "Which database engine is this schema targeting — PostgreSQL, MySQL, MongoDB, or another?"
- "The field `{field}` could belong to `{table_a}` or `{table_b}`. Which entity owns this data?"
- "Storing `{data}` inline denormalizes the schema. Should I extract it into a separate table with a foreign key, or keep it inline for read performance?"
- "This migration drops column `{column}` from `{table}`. This is irreversible in production. Should I proceed, or use a soft-deprecation approach (rename + nullable)?"
- "What is the cardinality between `{entity_a}` and `{entity_b}` — one-to-one, one-to-many, or many-to-many?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Greenfield schema with well-defined entities | Design in 3NF; generate CREATE TABLE DDL and an ER diagram |
| Read-heavy workload with complex joins | Consider targeted denormalization; document the trade-off in a migration comment and an ADR |
| Adding a column to a table with millions of rows | Recommend online DDL tool (pt-online-schema-change, pg_repack) and a phased migration |
| Multiple entities share identical fields (e.g., address) | Extract to a shared table with foreign keys unless performance benchmarks justify embedding |
| User wants to store hierarchical data (tree structures) | Evaluate adjacency list, nested set, materialized path, or closure table — recommend based on read/write ratio |
| Foreign key creates a circular dependency | Use nullable FK on one side and enforce integrity at the application level; document in an ADR |
| Query patterns are unknown or evolving | Start with minimal indexes (PK + FK); plan a review after real query data is available |

---

## Success Criteria

- [ ] Schema DDL executes without errors on the target database engine.
- [ ] All tables have explicit primary keys and appropriate foreign key constraints.
- [ ] Normalization level is at least 3NF, with documented justification for any denormalization.
- [ ] Migration files are idempotent and include reversible `down` scripts.
- [ ] Index strategy covers all expected query patterns without over-indexing.
- [ ] ER diagram accurately reflects the final schema.
- [ ] Seed data scripts run idempotently and use anonymized/synthetic values.
- [ ] No destructive DDL was applied without explicit user approval.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Migration is not idempotent | Re-running the migration fails with "already exists" errors | Use `IF NOT EXISTS` / `IF EXISTS` guards in all DDL statements |
| Missing `down` migration | Cannot roll back a failed deployment | Require both `up` and `down` scripts as part of the generation step; validate by running down then up in a test DB |
| Irreversible data loss from destructive DDL | Dropped column contained data not backed up elsewhere | Multi-step migration: rename column → deploy → verify → drop after grace period |
| Over-indexing on write-heavy tables | Insert/update latency increases significantly | Cap index count warnings at 5 per table; require performance justification for each additional index |
| Wrong cardinality assumption | Join table created for a one-to-many relationship, or FK placed incorrectly | Always confirm cardinality with the user before generating DDL when the domain model is ambiguous |
| Schema drift between environments | Dev and prod schemas diverge due to manual DDL changes | Track all schema changes exclusively through versioned migration files; never apply ad-hoc DDL |

---

## Audit Log

- `[{timestamp}] SCHEMA_DESIGNED — Tables: [{table_names}] | Engine: {db_engine} | Normalization: {level}`
- `[{timestamp}] MIGRATION_GENERATED — File: {filename} | Direction: up+down | Changes: {summary}`
- `[{timestamp}] INDEX_ADDED — Table: {table} | Columns: [{columns}] | Type: {btree|gin|hash} | Rationale: "{reason}"`
- `[{timestamp}] DESTRUCTIVE_CHANGE_APPROVED — Table: {table} | Operation: {drop_column|drop_table|type_change} | User confirmed: yes`
- `[{timestamp}] ER_DIAGRAM_GENERATED — Format: Mermaid | Entities: {count} | File: {filename}`
- `[{timestamp}] SEED_DATA_GENERATED — Tables: [{table_names}] | Rows: {count} | Idempotent: yes`
