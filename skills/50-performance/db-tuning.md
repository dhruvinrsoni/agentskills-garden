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
