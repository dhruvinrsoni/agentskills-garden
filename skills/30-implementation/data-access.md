---
name: data-access
description: >
  Implement data access layers using the Repository pattern.
  Prevents N+1 queries, manages transactions, and optimizes reads.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - database-design
reasoning_mode: plan-execute
---

# Data Access

> _"One query too many is one query too many."_

## Context

Invoked when implementing the persistence layer. Ensures clean separation
between business logic and database operations through the Repository pattern.

---

## Micro-Skills

### 1. Repository Scaffolding ⚡ (Power Mode)

**Steps:**

1. For each domain entity, create a repository interface:
   ```
   interface UserRepository {
     findById(id): User
     findAll(filter, pagination): Page<User>
     create(data): User
     update(id, data): User
     delete(id): void
   }
   ```
2. Implement the interface using the project's ORM/query builder.
3. Add a factory or DI registration for the repository.

### 2. N+1 Prevention ⚡ (Power Mode)

**Steps:**

1. Identify all relationships in the entity.
2. For each `findAll` query, check if related entities are accessed in loops.
3. Add eager loading / `JOIN` / `DataLoader` where N+1 is detected.
4. Add a query counter in test mode to catch regressions.

### 3. Transaction Management ⚡ (Power Mode)

**Steps:**

1. Identify operations that modify multiple entities.
2. Wrap them in a transaction boundary (Unit of Work pattern).
3. Implement retry logic for deadlock/serialization failures.
4. Ensure rollback on any exception within the boundary.

### 4. Query Optimization 🌿 (Eco Mode)

**Steps:**

1. Review generated queries for `SELECT *` — replace with explicit columns.
2. Add `LIMIT` to all paginated queries.
3. Use `EXPLAIN ANALYZE` to verify index usage on critical queries.

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `repositories`  | `string[]` | Generated repository file paths          |
| `migrations`    | `string[]` | Any new migration files                  |
| `query_report`  | `string`   | N+1 detection and optimization report    |

---

## Edge Cases

- Multi-tenant database — Add tenant_id filter to every query automatically.
- Soft deletes — Add `deleted_at` filter to all reads, expose `withTrashed`.

---

## Scope

### In Scope
- Creating repository interfaces and implementations for domain entities
- Detecting and preventing N+1 query patterns with eager loading or DataLoader
- Managing transaction boundaries using the Unit of Work pattern
- Optimizing queries: replacing `SELECT *`, adding `LIMIT`, verifying index usage
- Adding retry logic for deadlock and serialization failures
- Generating data access layer tests (query correctness, transaction rollback)
- Producing query performance reports using `EXPLAIN ANALYZE`
- Wiring repositories to the project's dependency injection container

### Out of Scope
- Designing the database schema or creating entity-relationship diagrams (delegate to `database-design`)
- Writing raw migration SQL or schema DDL changes (delegate to `database-design`)
- Implementing caching layers on top of repositories (delegate to `caching-strategy`)
- Tuning database server configuration (connection pools, memory, indexes at the server level) (delegate to `db-tuning`)
- Implementing business logic inside repositories — repositories return data, services apply rules
- Managing database credentials, connection strings, or secrets
- Creating API endpoints that consume repositories (delegate to `api-implementation`)

---

## Guardrails

- Every repository method must go through the ORM or query builder — no raw SQL unless explicitly justified.
- Never execute write operations outside a transaction boundary when multiple entities are modified.
- All `findAll`/list queries must be paginated — unbounded result sets are forbidden.
- Never return ORM/ActiveRecord objects directly from repositories; map to domain entities or DTOs.
- Add a query counter in test mode to catch N+1 regressions automatically.
- Never expose database-specific types (e.g., ObjectId, BigSerial) beyond the repository interface.
- Run `EXPLAIN ANALYZE` on any new query touching tables with >10k rows before merging.
- Preview all generated diffs before writing to disk.
- Never modify `vendor/`, `node_modules/`, `dist/`, or `generated/` directories.

## Ask-When-Ambiguous

### Triggers
- The project uses multiple ORMs or query builders and the primary one is unclear
- A query requires joining more than 3 tables and performance trade-offs need evaluation
- Soft-delete behavior is present in some entities but not others
- Multi-tenancy is detected and the tenant isolation strategy is ambiguous (row-level vs. schema-level)
- A repository method needs to return a complex aggregate that spans multiple tables
- Pagination strategy is unspecified (cursor-based vs. offset)

### Question Templates
1. "The project has both `{orm_a}` and `{orm_b}` configured. Which should the repositories use?"
2. "The query for `{entity}` involves joins across `{table_count}` tables. Should I use eager loading or split into separate queries?"
3. "Entity `{entity}` doesn't have a `deleted_at` column. Should I add soft-delete support or use hard deletes?"
4. "Multi-tenancy is detected. Should I filter by `tenant_id` at the repository level or rely on database-level row security?"
5. "Should the `findAll` endpoint for `{entity}` use cursor-based or offset-based pagination?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Entity has no repository yet | Scaffold full CRUD repository interface + implementation |
| N+1 detected in an existing query | Add eager loading or batch query; add query counter test to prevent regression |
| Write operation spans multiple entities | Wrap in a transaction boundary with rollback on failure |
| Query uses `SELECT *` | Replace with explicit column list matching the DTO fields |
| Table has >10k rows and no index on a filtered column | Recommend index creation; log a warning in the query report |
| Repository method exceeds 30 lines | Extract query-building logic into a private helper method |
| Deadlock or serialization failure detected at runtime | Apply retry with exponential backoff (max 3 attempts) |
| Soft-delete is enabled for the entity | Auto-add `WHERE deleted_at IS NULL` to all read queries; provide `withTrashed()` escape hatch |

## Success Criteria

- [ ] Every domain entity has a repository interface and at least one implementation
- [ ] No N+1 queries exist — verified by query counter in test mode
- [ ] All multi-entity write operations are wrapped in transactions with proper rollback
- [ ] All list/findAll queries are paginated with explicit `LIMIT`
- [ ] `SELECT *` is absent from all repository queries
- [ ] Critical queries have been validated with `EXPLAIN ANALYZE` (index usage confirmed)
- [ ] Retry logic is in place for deadlock-prone operations
- [ ] Repository methods return domain entities or DTOs, not raw ORM objects

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| N+1 query regression | Response time degrades linearly with result set size | Add query counter assertions in tests; CI fails if query count exceeds threshold |
| Missing transaction boundary | Partial writes leave data in inconsistent state | Audit all multi-entity mutations; wrap in Unit of Work |
| Unbounded query returns | Out-of-memory errors or timeouts on large tables | Enforce mandatory pagination on all list methods; reject requests without `limit` |
| ORM object leaked to service layer | Lazy-loading triggers unexpected queries outside the repository | Map ORM objects to plain DTOs before returning; detach entities from session |
| Deadlock under concurrent writes | Intermittent 500 errors during high traffic | Implement retry with exponential backoff; ensure consistent lock ordering |
| Soft-delete filter missing on a query | "Deleted" records appear in user-facing results | Add global scope/filter for `deleted_at IS NULL`; test with soft-deleted fixture data |

## Audit Log

```
- [{{timestamp}}] data-access:start — entities={{entity_list}}, orm={{orm_name}}, dialect={{db_dialect}}
- [{{timestamp}}] repository-scaffolded — entity={{entity}}, methods={{method_list}}, interface={{file_path}}
- [{{timestamp}}] n+1-check:result — queries_detected={{count}}, fixed={{count}}, remaining={{count}}
- [{{timestamp}}] transaction-boundary:added — operation={{op_name}}, entities_involved={{count}}
- [{{timestamp}}] query-optimization:result — select_star_removed={{count}}, limits_added={{count}}, explain_verified={{count}}
- [{{timestamp}}] data-access:complete — repositories_created={{count}}, migrations={{count}}, n1_issues={{count}}, all_tests_pass={{bool}}
```
