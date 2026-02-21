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

---

## Scope

### In Scope

- Assessing impact of framework, language, or runtime version upgrades by scanning for breaking-change usage
- Choosing an upgrade strategy (big bang, strangler fig, dual-run) based on project size and risk tolerance
- Applying automated codemods and migration scripts to transform deprecated API usage
- Validating upgrades through test suites, integration checks, and staged deployments
- Documenting the upgrade strategy in an Architecture Decision Record (ADR)
- Defining rollback criteria and maintaining the old version as a fallback during the transition period

### Out of Scope

- Rewriting application architecture or redesigning modules — delegate to `system-design`
- Upgrading transitive/minor dependencies without breaking changes — delegate to `dependency-updates`
- Writing new test suites from scratch — delegate to `test-strategy` or `unit-testing`
- Deploying to production or managing CI/CD pipeline changes — delegate to `ci-pipeline`
- Evaluating whether to upgrade vs. rewrite from scratch — delegate to `tech-debt-tracking` for cost-benefit analysis

---

## Guardrails

- Never start the upgrade without a passing baseline test suite on the current version; if coverage is insufficient, flag it and invoke `test-strategy` first
- Always create a dedicated branch for the upgrade — never upgrade in-place on the main branch
- Run the full test suite after every codemod pass, not just at the end; catch regressions incrementally
- Do not remove the old version's deployability until the upgraded version has been stable in production for at least one full release cycle
- Require an ADR documenting the chosen strategy before beginning migration work
- Pin the target version explicitly (e.g., `Node 20.11.0`, not `Node 20.x`) to avoid mid-upgrade drift
- If more than 30% of the codebase is affected by breaking changes, prefer strangler-fig over big-bang
- Preserve backward compatibility of public APIs during the transition unless the migration guide explicitly requires a break

---

## Ask-When-Ambiguous

### Triggers

- The migration guide lists a breaking change but the codebase uses the affected API in a non-standard way
- Multiple upgrade paths exist (e.g., skip a major version vs. step through each major version)
- A codemod only partially transforms a file, leaving manual fixups that change behavior
- The project has no integration tests and staging environment validation is unavailable
- Dual-run is desired but the old and new versions have incompatible dependency trees

### Question Templates

- "The migration guide deprecates `{api_name}`, but this codebase uses it via `{wrapper_pattern}`. Should I apply the standard codemod or write a custom transform?"
- "Two upgrade paths available: `{version_A}` → `{version_C}` directly, or `{version_A}` → `{version_B}` → `{version_C}`. Which path do you prefer?"
- "Codemod transformed `{N}` of `{M}` usages in `{file}`. The remaining `{M-N}` require manual changes that may alter behavior. Should I proceed or flag for human review?"
- "No integration tests exist. Should I create minimal smoke tests before upgrading, or proceed with unit tests only?"
- "Dual-run requires `{old_dep}` and `{new_dep}` simultaneously, but they conflict on `{shared_dep}`. Should I isolate via workspaces/monorepo or switch to strangler-fig?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Small project (< 50 files affected) with good test coverage | Use big-bang upgrade: upgrade everything in a single branch |
| Large project (> 200 files affected) or low test coverage | Use strangler-fig: migrate module by module behind feature flags |
| Public API must remain stable during migration | Use dual-run with adapter layer bridging old and new versions |
| Official codemods available for the target version | Apply codemods first, then address remaining manual fixes |
| No codemods available | Generate an impact report, prioritise files by blast radius, migrate manually |
| Skipping a major version is documented as supported | Skip intermediate version to reduce total migration effort |
| Skipping a major version is undocumented or discouraged | Step through each major version sequentially |
| Test suite fails after codemod pass | Fix failures before proceeding to the next codemod or manual migration step |
| Upgraded version stable in staging for one sprint | Promote to production; keep old version rollback-ready |
| Critical bug found in production after upgrade | Rollback to old version immediately; open incident via `incident-response` |

---

## Success Criteria

- [ ] Impact report generated listing all files and APIs affected by breaking changes
- [ ] Upgrade strategy documented in an ADR and approved by the team
- [ ] Baseline test suite passing on the current version before any migration work begins
- [ ] All available codemods applied and verified by test runs after each pass
- [ ] Manual migration fixes completed for code the codemods could not transform
- [ ] Full test suite (unit + integration) passing on the upgraded codebase
- [ ] Staging deployment completed with smoke tests passing
- [ ] Rollback criteria defined and rollback path verified as functional
- [ ] Old version remains deployable for at least one full release cycle post-upgrade
- [ ] No regressions in public API behavior unless explicitly documented as intentional breaking changes

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Upgrade started without baseline tests | Regressions introduced by the upgrade are indistinguishable from pre-existing bugs | Require a green test suite on the current version before branching; block upgrade work otherwise |
| Big-bang on a large codebase | Merge conflicts pile up; branch becomes unmergeable after weeks of parallel development | Switch to strangler-fig; migrate module by module and merge incrementally |
| Codemod applied without post-run tests | Silent behavior changes introduced by automated transforms go undetected | Run the full test suite after every codemod pass; review diffs for semantic changes |
| Target version not pinned | A patch release mid-upgrade introduces new breaking changes, invalidating prior work | Pin the exact target version in the migration plan and lock files |
| Old version decommissioned too early | Critical production bug discovered with no rollback path available | Keep old version deployable for one full release cycle; monitor error rates before decommissioning |
| Skipped intermediate major version | Undocumented incompatibilities surface late in migration, requiring rework | Verify skip-version support in the official migration guide before committing to the path |
| Dependency conflict in dual-run | Build fails or runtime errors from incompatible transitive dependencies | Isolate old and new dependency trees using workspaces, containers, or module aliasing |
| Migration stalls at 80% completion | Remaining 20% involves deeply embedded legacy patterns; team loses momentum | Break the last 20% into tracked tickets with deadlines; invoke `tech-debt-tracking` to maintain visibility |

---

## Audit Log

- `2025-02-21T00:00:00Z` — Skill created with impact assessment, upgrade strategy, automated migration, and validation micro-skills.
- `2026-02-21T00:00:00Z` — Appended Scope, Guardrails, Ask-When-Ambiguous, Decision Criteria, Success Criteria, Failure Modes, and Audit Log sections to align with spec schema.
