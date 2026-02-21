````markdown
---
name: deprecation-management
description: >
  Manage deprecation lifecycles including notices, sunset timelines,
  migration paths, and backward compatibility guarantees.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
  - api-contract-design
reasoning_mode: plan-execute
---

# Deprecation Management

> _"Sunset gracefully — give consumers a bridge before burning the old road."_

## Context

Invoked when APIs, features, libraries, or internal components need to
be deprecated and eventually removed. Ensures consumers have adequate
notice, clear migration paths, and sufficient time to transition before
the deprecated functionality is sunset.

---

## Micro-Skills

### 1. Deprecation Impact Analysis ⚡ (Power Mode)

**Steps:**

1. Identify all consumers of the item to be deprecated:
   - Internal callers (grep for imports, function calls, endpoint usage).
   - External consumers (API clients, SDKs, third-party integrations).
   - Documentation and examples referencing the deprecated item.
2. Quantify usage:
   - Request/call frequency for APIs.
   - Import count for libraries/modules.
   - Number of dependent repositories in a monorepo or org.
3. Assess migration complexity for each consumer category.

### 2. Deprecation Notice & Timeline ⚡ (Power Mode)

**Steps:**

1. Define the sunset timeline based on impact:
   | Consumer Type     | Minimum Notice Period |
   |-------------------|-----------------------|
   | Public API        | 12 months             |
   | Internal API      | 3 months              |
   | Library/module    | 2 major versions      |
   | Feature flag      | 1 sprint              |
2. Create deprecation notices:
   - Add `@deprecated` annotations or equivalent in code.
   - Emit deprecation warnings at runtime (log level: WARN).
   - Update API documentation with deprecation banner and sunset date.
   - Notify consumers via changelog, email, or migration guide.
3. Set calendar reminders for timeline milestones (50% mark, final warning, sunset).

### 3. Migration Path Design ⚡ (Power Mode)

**Steps:**

1. Design the replacement:
   - Document the new API/feature/component that replaces the deprecated one.
   - Provide a mapping: old interface → new interface.
2. Create a migration guide:
   - Step-by-step instructions for each consumer type.
   - Before/after code examples.
   - Automated migration tooling where feasible (codemods, scripts).
3. Ensure backward compatibility during the transition:
   - Deprecated item must continue to function until sunset date.
   - New and old interfaces must coexist without conflicts.

### 4. Sunset Execution 🌱 (Eco Mode)

**Steps:**

1. At sunset date, verify migration status:
   - Check usage metrics — are any consumers still using the deprecated item?
   - If active consumers remain, extend the timeline or escalate.
2. Remove the deprecated item:
   - Delete code, endpoints, or configurations.
   - Remove from documentation.
   - Update changelogs with removal notice.
3. Monitor for breakage after removal (error rates, support tickets).

---

## Outputs

| Field               | Type       | Description                              |
|---------------------|------------|------------------------------------------|
| `impact_analysis`   | `object`   | Consumer inventory and usage metrics     |
| `deprecation_plan`  | `object`   | Timeline, milestones, and notice content |
| `migration_guide`   | `string`   | Step-by-step migration documentation     |
| `sunset_report`     | `object`   | Final status: migrated consumers, removed items |

---

## Scope

### In Scope

- Identifying and inventorying all consumers of deprecated items (internal and external)
- Defining sunset timelines with minimum notice periods by consumer type
- Creating deprecation notices in code (`@deprecated`), runtime warnings, and documentation
- Designing migration paths with old-to-new interface mappings and code examples
- Maintaining backward compatibility during the transition period
- Verifying consumer migration status before sunset execution
- Removing deprecated items after sunset with monitoring for breakage

### Out of Scope

- Implementing the replacement API, feature, or component (delegate to `api-implementation` or `code-generation`)
- Migrating consumer codebases to the new interface (consumers are responsible, or delegate to `refactoring`)
- Versioning strategy for APIs beyond deprecation lifecycle (delegate to `api-contract-design`)
- Infrastructure decommissioning related to removed services (delegate to `terraform-iac`)
- Legal or contractual obligations around API retirement (escalate to product/legal)

## Guardrails

- Never remove a deprecated item before the published sunset date.
- Never deprecate without providing a documented migration path or replacement.
- Always verify that zero consumers remain before executing sunset removal.
- If any consumer still uses the deprecated item at sunset, extend the timeline — do not force-remove.
- Runtime deprecation warnings must be at WARN level, never ERROR — deprecated items must still function.
- Never deprecate and introduce the replacement in the same release — stagger by at least one version.
- All deprecation notices must include: reason, replacement, sunset date, and migration guide link.
- Preserve deprecated item behavior exactly (no behavior changes) during the deprecation period.

## Ask-When-Ambiguous

### Triggers

- A deprecated item has no clear replacement or successor
- Active consumers are detected at the sunset date
- The deprecation affects a public API with external consumers who cannot be directly notified
- Multiple replacement options exist with different trade-offs
- The sunset timeline conflicts with a major release or migration already in progress

### Question Templates

1. "Item `{name}` is proposed for deprecation but has no clear replacement. Should I proceed with deprecation-only and document the gap, or defer until a replacement is designed?"
2. "At the sunset date for `{name}`, `{count}` consumers are still active: `{consumer_list}`. Should I extend the timeline by `{period}`, force-remove, or escalate?"
3. "Public API `{endpoint}` has `{count}` external consumers who cannot be directly notified. What communication channels should I use: changelog only, email blast, status page banner, or all of the above?"
4. "Two replacement options exist for `{name}`: `{option_a}` (simpler, fewer features) and `{option_b}` (full parity, higher complexity). Which should the migration guide recommend?"
5. "The sunset for `{name}` falls during the `{release}` release cycle, which already includes `{migration}`. Should I defer the sunset to avoid compounding migration risk?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Item has zero consumers | Fast-track deprecation — shorten notice period to minimum, proceed to removal |
| Item has < 5 internal consumers | Standard deprecation with direct notification to owning teams |
| Item has external/public consumers | Extended deprecation timeline (minimum 12 months); multi-channel notification |
| Replacement is ready and documented | Begin deprecation immediately with migration guide |
| Replacement is not yet available | Defer deprecation until replacement ships; announce intent only |
| Consumer has not migrated at 50% timeline mark | Send targeted reminder with migration assistance offer |
| Consumer has not migrated at sunset date | Extend timeline; escalate to consumer's team lead |
| Deprecated item has a security vulnerability | Accelerate sunset if patch is impractical; provide emergency migration support |
| Deprecation would break semantic versioning | Schedule removal for next major version only |
| Multiple items deprecated simultaneously | Stagger sunset dates to avoid consumer migration overload |

## Success Criteria

- [ ] All deprecated items have documented migration paths with before/after examples
- [ ] Deprecation notices appear in code annotations, runtime warnings, and documentation
- [ ] Sunset timeline published and communicated to all known consumers
- [ ] Zero active consumers remain at sunset execution time
- [ ] Deprecated item functions correctly and without behavior changes throughout the deprecation period
- [ ] Removal is clean — no orphaned references in code, docs, or configuration
- [ ] No increase in error rates or support tickets after sunset removal
- [ ] Audit log captures every milestone in the deprecation lifecycle

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Silent deprecation — no one notices | Consumers discover removal only when it breaks their code | Enforce multi-channel notification checklist; verify delivery |
| Premature removal | Errors spike after removal; consumers not migrated | Always verify usage metrics at sunset; require zero-consumer gate |
| Migration guide is incomplete or incorrect | Consumers attempt migration but encounter undocumented edge cases | Test migration guide against real consumer codebases before publishing |
| Deprecated item behavior changes during deprecation period | Consumers experience bugs in code they haven't migrated yet | Lock deprecated code paths — no modifications except security patches |
| Sunset date repeatedly extended | Deprecation drags on indefinitely; old code never removed | Set a hard maximum extension limit (e.g., 2 extensions); escalate after |
| Replacement has lower feature parity | Consumers cannot migrate because replacement doesn't cover their use case | Conduct feature gap analysis before announcing deprecation; close gaps first |

## Audit Log

- `[{timestamp}] deprecation-proposed: {item_type} "{item_name}" — reason: {reason}`
- `[{timestamp}] impact-analyzed: {item_name} — {internal_consumers} internal, {external_consumers} external consumers identified`
- `[{timestamp}] deprecation-announced: {item_name} — sunset_date={sunset_date}, migration_guide={guide_url}`
- `[{timestamp}] notice-added: {item_name} — @deprecated annotation, runtime warning, docs updated`
- `[{timestamp}] milestone-check: {item_name} — {percent}% of timeline elapsed, {migrated}/{total} consumers migrated`
- `[{timestamp}] sunset-executed: {item_name} — removed from codebase, docs, and configuration`
- `[{timestamp}] sunset-extended: {item_name} — new_sunset_date={new_date}, reason: {reason}`
- `[{timestamp}] post-sunset-monitor: {item_name} — error_rate={rate}, support_tickets={count}`
````
