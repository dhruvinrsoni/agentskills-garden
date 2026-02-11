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
