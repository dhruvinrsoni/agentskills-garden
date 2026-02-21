---
name: db-tuning
description: >
  Database performance tuning: index analysis, query plan optimization,
  connection pooling, and configuration tuning.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - database-design
reasoning_mode: plan-execute
---

# Database Tuning

> _"A slow query is a bug. Treat it like one."_

## Context

Invoked when database queries are identified as bottlenecks, or proactively
during performance reviews.

---

## Micro-Skills

### 1. Slow Query Identification ⚡ (Power Mode)

**Steps:**

1. Enable slow query logging (threshold: 100ms).
2. Collect the top 10 slowest queries by total time.
3. For each query, capture:
   - SQL text (parameterized).
   - Execution frequency.
   - Average and p99 duration.
   - Table sizes involved.

### 2. Query Plan Analysis ⚡ (Power Mode)

**Steps:**

1. Run `EXPLAIN ANALYZE` on each slow query.
2. Look for:
   - **Sequential scans** on large tables (missing index).
   - **Nested loops** with high row estimates (N+1 at DB level).
   - **Sort operations** without index (filesort).
   - **Hash joins** on large datasets (memory pressure).
3. Propose index additions or query rewrites.

### 3. Index Optimization ⚡ (Power Mode)

**Steps:**

1. List all existing indexes on affected tables.
2. Identify:
   - **Missing indexes** (columns in WHERE/JOIN/ORDER BY without index).
   - **Redundant indexes** (covered by a broader composite index).
   - **Unused indexes** (never hit — pure write overhead).
3. Generate `CREATE INDEX` / `DROP INDEX` migration files.

### 4. Connection Pooling 🌿 (Eco Mode)

**Steps:**

1. Review current pool settings (min, max, idle timeout).
2. Recommend settings based on:
   - Expected concurrent connections.
   - Database max_connections setting.
   - Rule of thumb: `pool_size = (2 * cpu_cores) + disk_spindles`.
3. Add connection pool health check.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `slow_queries`   | `object[]` | Top slow queries with analysis           |
| `index_changes`  | `string[]` | Migration files for index changes        |
| `pool_config`    | `object`   | Connection pool recommendations          |

---

## Scope

### In Scope

- Identifying and analyzing slow queries via logs and `EXPLAIN ANALYZE`.
- Proposing and generating index additions, removals, and modifications.
- Detecting redundant and unused indexes and recommending cleanup.
- Query rewriting for performance (eliminating N+1, reducing joins, covering indexes).
- Connection pool sizing and configuration tuning.
- Database server parameter tuning (memory buffers, work_mem, shared_buffers).
- Generating migration files for index changes.

### Out of Scope

- Schema redesign or normalization changes (see `database-design`).
- Application-level caching (see `caching-strategy`).
- Database provisioning, replication, or failover configuration.
- Data migration or ETL pipeline work (see `migration-planning`).
- Changing ORM framework or data-access layer architecture (see `data-access`).
- Production DBA operations such as vacuum, reindex on live clusters.

---

## Guardrails

- Never execute `DROP INDEX` on production without verifying the index is unused for at least 7 days.
- Always generate index changes as reversible migration files, never raw DDL against production.
- Preview all query rewrites as diffs; run the existing test suite before and after changes.
- Do not add indexes on columns with very low cardinality (e.g., boolean flags) unless part of a composite.
- Never change `max_connections` or memory parameters without documenting the rationale and rollback values.
- Avoid recommending more than 5 index changes per table in a single pass — batch to limit lock contention.
- Run `EXPLAIN ANALYZE` on non-production data or read replicas to avoid impacting live traffic.
- Log every proposed change before applying; never silently alter schema.

---

## Ask-When-Ambiguous

### Triggers

- The database engine (PostgreSQL, MySQL, SQL Server, etc.) is not specified.
- Slow query threshold is not defined by the caller.
- It is unclear whether indexes can be added during peak traffic hours.
- Table sizes are unknown, making it hard to estimate index build time.
- Multiple competing index strategies could address the same slow query.
- Connection pool settings conflict with application framework defaults.

### Question Templates

- "Which database engine and version is in use (e.g., PostgreSQL 15, MySQL 8)?"
- "What slow query threshold should be used — 100ms, 500ms, or a custom value?"
- "Is there a maintenance window available for adding indexes, or must changes be online?"
- "What is the approximate row count for `{table_name}`?"
- "Are there existing monitoring tools (pg_stat_statements, Performance Schema) already enabled?"
- "What is the current `max_connections` setting and peak concurrent connection count?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Sequential scan on table with > 10k rows in a frequent query | Add a B-tree index on the filtered/joined column |
| Query uses `ORDER BY` on a non-indexed column with `LIMIT` | Add an index matching the sort order to enable index-scan |
| Composite index covers a subset of an existing broader index | Drop the narrower redundant index |
| Index exists but `pg_stat_user_indexes.idx_scan = 0` for 30+ days | Recommend dropping the unused index |
| N+1 pattern detected at DB level (nested loop with high rows) | Rewrite query to use `JOIN` or batch `IN(...)` clause |
| `work_mem` too low causing disk-based sorts | Increase `work_mem` within available RAM budget |
| Pool exhaustion errors under load | Increase pool max; verify it stays below DB `max_connections` |
| Query plan changes after data growth | Add `ANALYZE` to maintenance schedule; consider partial indexes |

---

## Success Criteria

- [ ] All identified slow queries (> threshold) have been analyzed with `EXPLAIN ANALYZE`.
- [ ] Proposed index changes reduce query execution time by at least 50% for targeted queries.
- [ ] No redundant or unused indexes remain on affected tables after cleanup.
- [ ] Migration files are generated and reversible (up + down migrations).
- [ ] Connection pool settings are documented with supporting rationale.
- [ ] Existing test suite passes after query rewrites and index changes.
- [ ] No new sequential scans introduced on tables exceeding 10k rows.
- [ ] Performance improvement is validated with before/after metrics.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Index bloat from over-indexing | Write latency increases; storage grows disproportionately | Limit indexes per table; audit unused indexes quarterly |
| Lock contention during index creation | Application timeouts during migration | Use `CREATE INDEX CONCURRENTLY` (PostgreSQL) or online DDL equivalents |
| Wrong index type selected | Query plan ignores the new index; no performance gain | Verify index type matches query pattern (B-tree vs. GIN vs. hash) |
| Connection pool too large | DB runs out of memory; `max_connections` exceeded | Size pool to `(2 × CPU cores) + spindles`; monitor active vs. idle connections |
| Query rewrite changes semantics | Different result set returned after optimization | Diff query outputs before and after rewrite; run integration tests |
| Parameter tuning causes instability | OOM kills, checkpoint spikes, or replication lag | Change one parameter at a time; document rollback values; monitor for 24h |
| Missing `ANALYZE` after bulk load | Planner uses stale statistics; regression in query plans | Schedule `ANALYZE` after large data loads; automate with maintenance jobs |

---

## Audit Log

Each invocation of the Database Tuning skill records the following timestamped entries in the scratchpad:

- `[YYYY-MM-DDTHH:MM:SSZ] DB_TUNING_START` — Skill invoked; target database and tables noted.
- `[YYYY-MM-DDTHH:MM:SSZ] SLOW_QUERIES_COLLECTED` — Top N slow queries identified with frequency and duration.
- `[YYYY-MM-DDTHH:MM:SSZ] EXPLAIN_ANALYSIS` — `EXPLAIN ANALYZE` results captured for each slow query.
- `[YYYY-MM-DDTHH:MM:SSZ] INDEX_RECOMMENDATIONS` — Proposed index additions/removals with rationale.
- `[YYYY-MM-DDTHH:MM:SSZ] MIGRATIONS_GENERATED` — Migration files created; file paths listed.
- `[YYYY-MM-DDTHH:MM:SSZ] POOL_CONFIG_REVIEWED` — Connection pool settings evaluated; recommendations documented.
- `[YYYY-MM-DDTHH:MM:SSZ] TESTS_PASSED` — Test suite executed post-change; pass/fail status recorded.
- `[YYYY-MM-DDTHH:MM:SSZ] DB_TUNING_END` — Skill completed; before/after query latency comparison logged.
