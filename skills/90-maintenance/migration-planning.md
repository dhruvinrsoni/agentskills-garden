````markdown
---
name: migration-planning
description: >
  Plan and coordinate version upgrades, data migrations, rollback
  strategies, and blue-green deployments for safe system transitions.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
  - database-design
  - risk-assessment
reasoning_mode: plan-execute
---

# Migration Planning

> _"A migration without a rollback plan is just a hope."_

## Context

Invoked when a system requires a coordinated transition — database
schema changes, data format migrations, service version upgrades, or
infrastructure cutover. Provides structured planning for safe
transitions with minimal downtime and proven rollback capability.

---

## Micro-Skills

### 1. Migration Assessment ⚡ (Power Mode)

**Steps:**

1. Identify the migration scope:
   - **Schema migration:** Table/column changes, index modifications.
   - **Data migration:** Format conversion, data backfill, ETL.
   - **Service migration:** API version upgrade, protocol change.
   - **Infrastructure migration:** Cloud provider, region, runtime.
2. Map dependencies between migrating components and downstream consumers.
3. Estimate data volume and expected migration duration.
4. Identify the acceptable downtime window (zero, minutes, hours).

### 2. Migration Strategy Selection ⚡ (Power Mode)

**Steps:**

1. Choose a deployment strategy based on constraints:
   | Strategy         | Downtime | Complexity | Risk    | Best For                |
   |------------------|----------|------------|---------|-------------------------|
   | **Big bang**     | Yes      | Low        | High    | Small, isolated systems |
   | **Rolling**      | Minimal  | Medium     | Medium  | Stateless services      |
   | **Blue-green**   | Zero     | High       | Low     | Critical production apps|
   | **Canary**       | Zero     | High       | Low     | High-traffic services   |
   | **Strangler fig**| Zero     | High       | Low     | Monolith decomposition  |
2. For data migrations, select the migration approach:
   - **Expand-contract:** Add new schema → backfill → migrate reads → drop old.
   - **Dual-write:** Write to both old and new simultaneously during transition.
   - **Snapshot-and-replay:** Take snapshot, migrate offline, replay changes.
3. Document the chosen strategy in an ADR (invoke `adr-management`).

### 3. Rollback Planning ⚡ (Power Mode)

**Steps:**

1. Define rollback triggers — specific metrics or conditions that
   initiate automatic or manual rollback:
   - Error rate exceeds baseline by > 5%.
   - Latency p99 increases by > 50%.
   - Data integrity check fails.
   - Downstream service reports increased failures.
2. Design the rollback procedure:
   - Database: backward-compatible migrations only; keep rollback scripts.
   - Services: maintain previous version artifacts and routing config.
   - Data: preserve original data until migration is verified (never delete source).
3. Test rollback in staging before production migration.
4. Define the point-of-no-return (if any) and communicate it clearly.

### 4. Execution & Verification ⚡ (Power Mode)

**Steps:**

1. Execute pre-migration checklist:
   - [ ] Backups verified and restorable.
   - [ ] Rollback procedure tested in staging.
   - [ ] Monitoring dashboards open and alerting configured.
   - [ ] Stakeholders notified of migration window.
   - [ ] Feature flags in place for traffic routing.
2. Execute migration in phases, verifying each phase before proceeding.
3. Run data integrity checks after each phase:
   - Row counts match expectations.
   - Checksums validate for critical data.
   - Referential integrity constraints pass.
4. Monitor production metrics for the soak period (minimum 24 hours).

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `migration_plan`   | `object`   | Full plan with phases, timeline, owners  |
| `rollback_plan`    | `object`   | Triggers, procedures, and point-of-no-return |
| `strategy_adr`     | `string`   | Architecture decision record             |
| `integrity_report` | `object`   | Data validation results post-migration   |
| `runbook`          | `string`   | Step-by-step execution runbook           |

---

## Scope

### In Scope

- Assessing migration scope across schema, data, services, and infrastructure
- Selecting deployment strategies (blue-green, canary, rolling, big bang, strangler fig)
- Planning data migration approaches (expand-contract, dual-write, snapshot-replay)
- Designing rollback triggers, procedures, and point-of-no-return definitions
- Creating pre-migration checklists and step-by-step runbooks
- Defining data integrity validation checks (row counts, checksums, referential integrity)
- Coordinating migration timelines with downstream consumers and stakeholders

### Out of Scope

- Writing the actual migration scripts or SQL (delegate to `database-design` or `data-access`)
- Implementing application code changes required by the migration (delegate to `code-generation`)
- Setting up monitoring dashboards or alerts (delegate to `monitoring-setup`)
- Configuring infrastructure for blue-green deployments (delegate to `terraform-iac` or `kubernetes-helm`)
- Performing incident response if migration fails catastrophically (delegate to `incident-response`)

## Guardrails

- Never execute a production migration without a tested rollback procedure.
- Never delete source data until the migration is verified and the soak period has passed.
- Always require database backups to be verified as restorable before migration begins.
- Never run destructive schema changes (DROP, TRUNCATE) as part of the forward migration — defer to the contract phase.
- All migrations must be backward-compatible during the transition period.
- Do not proceed to the next migration phase until the current phase's integrity checks pass.
- Migration windows must be communicated to all stakeholders at least 48 hours in advance.
- Rollback must be exercised in a non-production environment before every production migration.

## Ask-When-Ambiguous

### Triggers

- The acceptable downtime window is not defined by the stakeholders
- A migration has no clear rollback path (irreversible schema changes)
- Data volume is large enough that migration duration may exceed the maintenance window
- Multiple teams own components affected by the migration
- The migration requires a point-of-no-return decision

### Question Templates

1. "What is the maximum acceptable downtime for this migration? Options: zero downtime, < 5 minutes, < 1 hour, or a scheduled maintenance window of {duration}."
2. "This schema change (`{change}`) is not backward-compatible. Should I redesign as an expand-contract migration, or is a maintenance window with downtime acceptable?"
3. "Estimated migration duration for `{data_volume}` rows is `{duration}`. The maintenance window is `{window}`. Should I break the migration into batches or extend the window?"
4. "Components owned by teams `{team_a}` and `{team_b}` are both affected. Who is the migration coordinator, and has cross-team scheduling been confirmed?"
5. "After phase `{phase}`, rollback will no longer be possible without data loss. Should I proceed past this point-of-no-return, or add a manual approval gate?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Zero downtime required and system is stateless | Use rolling deployment strategy |
| Zero downtime required and system is stateful | Use blue-green or canary deployment with expand-contract data migration |
| Small dataset (< 1M rows) and off-peak window available | Big bang migration is acceptable |
| Large dataset (> 100M rows) | Batch the migration; use dual-write or snapshot-replay to avoid locking |
| Schema change is backward-compatible | Apply migration first, then deploy new code (expand phase) |
| Schema change is NOT backward-compatible | Redesign as expand-contract; if impossible, schedule downtime |
| Migration duration exceeds maintenance window | Split into incremental phases or use online migration tooling (gh-ost, pt-osc) |
| Rollback tested successfully in staging | Proceed to production migration |
| Rollback test fails in staging | Fix rollback procedure before scheduling production migration |
| Error rate exceeds rollback trigger threshold during migration | Execute rollback immediately; do not wait for manual assessment |

## Success Criteria

- [ ] Migration plan documented with phases, owners, timeline, and dependencies
- [ ] Rollback procedure defined, documented, and tested in non-production environment
- [ ] Pre-migration checklist completed with all items verified
- [ ] Data integrity checks pass after each migration phase (row counts, checksums, referential integrity)
- [ ] Production metrics remain within acceptable thresholds during and after migration
- [ ] Soak period (minimum 24 hours) completes without anomalies
- [ ] Source data preserved until migration verification is complete
- [ ] All stakeholders notified of migration status at each phase gate

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Migration exceeds time window | Migration still running at end of maintenance window | Design migration to be pausable and resumable; pre-calculate duration on staging with production-scale data |
| Data integrity loss during migration | Row count mismatch or checksum failures post-migration | Run integrity checks after each batch; halt and rollback on first failure |
| Rollback procedure fails | Rollback script errors or leaves system in inconsistent state | Always test rollback in staging with production-like data; maintain backup as last resort |
| Downstream services break after migration | Dependent APIs return errors, consumers report failures | Communicate migration timeline to all consumers; use feature flags to route traffic gradually |
| Dual-write inconsistency | Old and new data stores diverge during transition period | Implement reconciliation jobs that compare stores; alert on divergence |
| Point-of-no-return reached prematurely | Team discovers issues after irreversible changes were applied | Add explicit manual approval gates before destructive phases; never skip pre-checks |

## Audit Log

- `[{timestamp}] migration-assessed: scope={scope_type}, components={count}, estimated_duration={duration}`
- `[{timestamp}] strategy-selected: {strategy_name} — rationale: {rationale}`
- `[{timestamp}] rollback-tested: environment={env}, result={pass|fail}`
- `[{timestamp}] phase-started: phase={phase_number} "{phase_name}" — started by {operator}`
- `[{timestamp}] integrity-check: phase={phase_number}, rows_expected={expected}, rows_actual={actual}, checksum={status}`
- `[{timestamp}] phase-completed: phase={phase_number} "{phase_name}" — duration={duration}`
- `[{timestamp}] rollback-executed: trigger={trigger}, phase={phase_number}, result={success|failure}`
- `[{timestamp}] migration-completed: total_duration={duration}, soak_period_start={timestamp}`
````
