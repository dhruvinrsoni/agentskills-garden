---
name: legacy-upgrade
description: >
  Plan and execute upgrades of major frameworks, languages, or
  runtime versions with minimal disruption.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
  - test-strategy
reasoning_mode: plan-execute
---

# Legacy Upgrade

> _"The best time to upgrade was last quarter. The second best time is now."_

## Context

Invoked when a framework, language, or major dependency needs upgrading
(e.g., Node 16 to Node 20, Spring Boot 2 to 3, Python 2 to 3).

---

## Micro-Skills

### 1. Impact Assessment ⚡ (Power Mode)

**Steps:**

1. Read the migration guide for the target version.
2. Identify **breaking changes** that affect the codebase:
   - Removed APIs.
   - Changed default behaviors.
   - Renamed packages or modules.
3. Scan the codebase for usage of affected APIs.
4. Generate an impact report: files affected, estimated effort per file.

### 2. Upgrade Strategy ⚡ (Power Mode)

**Steps:**

1. Choose the approach:
   - **Big bang:** Upgrade everything at once (small projects).
   - **Strangler fig:** Gradually migrate module by module (large projects).
   - **Dual-run:** Run old and new versions side-by-side during transition.
2. Document the strategy in an ADR (invoke `adr-management`).
3. Estimate the timeline and break into milestones.

### 3. Automated Migration ⚡ (Power Mode)

**Steps:**

1. Use codemods where available:
   - Node.js: `jscodeshift`
   - Java: OpenRewrite
   - Python: `2to3`, `pyupgrade`
2. Apply codemods to the codebase.
3. Run tests after each codemod pass.
4. Manually fix anything the codemods couldn't handle.

### 4. Validation & Rollback ⚡ (Power Mode)

**Steps:**

1. Run the full test suite on the upgraded codebase.
2. Run integration tests with dependent services.
3. Deploy to staging and run smoke tests.
4. Define rollback criteria (what failures trigger a revert).
5. Keep the old version deployable until the new version is proven in
   production for at least one full release cycle.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `impact_report`  | `object`   | Files and APIs affected                  |
| `migration_plan` | `string`   | Step-by-step upgrade plan                |
| `adr`            | `string`   | Strategy decision record                 |
| `test_results`   | `object`   | Before/after test comparison             |
