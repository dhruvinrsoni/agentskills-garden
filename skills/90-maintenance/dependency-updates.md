````markdown
---
name: dependency-updates
description: >
  Automate and manage dependency updates with semver-aware compatibility
  checks, breaking change detection, and lockfile management.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
  - test-strategy
reasoning_mode: plan-execute
---

# Dependency Updates

> _"Stay current or pay compound interest on every outdated package."_

## Context

Invoked when project dependencies need updating — whether triggered by
security advisories, new feature requirements, or routine maintenance
cycles. Covers package managers across ecosystems (npm, pip, Maven,
NuGet, Go modules, Cargo, etc.).

---

## Micro-Skills

### 1. Dependency Audit 🌱 (Eco Mode)

**Steps:**

1. Run the ecosystem's audit command (`npm audit`, `pip-audit`,
   `mvn dependency:analyze`, etc.).
2. Parse output into a structured report:
   - Package name, current version, latest version.
   - Severity of known vulnerabilities (critical, high, medium, low).
   - Whether the update is patch, minor, or major (semver classification).
3. Flag transitive dependencies that are outdated or vulnerable.

### 2. Compatibility Analysis ⚡ (Power Mode)

**Steps:**

1. For each proposed update, read the package changelog / release notes.
2. Classify the update:
   - **Patch:** Bug fixes only — safe to auto-merge.
   - **Minor:** New features, backward-compatible — review briefly.
   - **Major:** Breaking changes — requires migration analysis.
3. Check for peer dependency conflicts.
4. Identify downstream packages in monorepos affected by the update.

### 3. Update Execution 🌱 (Eco Mode)

**Steps:**

1. Create a dedicated branch for the update batch.
2. Apply updates respecting grouping strategy:
   - Security patches: apply immediately, individually.
   - Minor updates: batch by category (dev deps, runtime deps).
   - Major updates: one at a time with full validation.
3. Regenerate lockfiles (`package-lock.json`, `yarn.lock`, `poetry.lock`, etc.).
4. Run `install` to verify lockfile integrity.

### 4. Validation ⚡ (Power Mode)

**Steps:**

1. Run the full test suite after each update batch.
2. Run type-checking and linting to catch API incompatibilities.
3. Build the project to detect compile-time breakage.
4. If tests fail, bisect the batch to isolate the breaking update.
5. Document any required code changes for breaking updates.

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `audit_report`     | `object`   | Vulnerability and staleness summary      |
| `update_plan`      | `object[]` | Ordered list of updates with semver type |
| `lockfile_diff`    | `string`   | Summary of lockfile changes              |
| `test_results`     | `object`   | Pass/fail results after updates          |
| `breaking_changes` | `string[]` | List of breaking changes requiring code changes |

---

## Scope

### In Scope

- Scanning and auditing direct and transitive dependencies for staleness and vulnerabilities
- Classifying updates by semver level (patch, minor, major)
- Detecting breaking changes from changelogs and release notes
- Regenerating and validating lockfiles after updates
- Running test suites to verify compatibility post-update
- Grouping and batching updates by risk level
- Managing peer dependency conflicts

### Out of Scope

- Authoring or publishing packages to registries
- Modifying application business logic to accommodate API changes (hand off to `refactoring`)
- Changing CI/CD pipeline configuration (delegate to `ci-pipeline`)
- Upgrading major frameworks or language runtimes (delegate to `legacy-upgrade`)
- License compliance auditing beyond dependency metadata

## Guardrails

- Never update a dependency without running the full test suite afterward.
- Never force-resolve peer dependency conflicts by skipping checks (`--legacy-peer-deps`, `--force`) without explicit user approval.
- Always regenerate lockfiles through the package manager — never edit lockfiles manually.
- Preserve pinned versions unless the user explicitly requests unpinning.
- Do not batch major version updates together — apply them individually.
- Roll back the entire update batch if more than 20% of tests fail.
- Never remove a dependency as part of an update operation; only update versions.
- Log every version change with before/after versions in the audit log.

## Ask-When-Ambiguous

### Triggers

- A major version update has breaking changes that require code modifications
- Multiple conflicting peer dependency requirements exist
- A dependency has been deprecated with no clear successor
- The update would remove support for the project's minimum runtime version
- A security-critical update conflicts with a pinned version constraint

### Question Templates

1. "Package `{name}` has a major update from `{current}` to `{latest}` with breaking changes: {changes}. Should I proceed and apply required code modifications, or skip this update?"
2. "Peer dependency conflict detected: `{pkg_a}` requires `{dep} ^{v1}` but `{pkg_b}` requires `{dep} ^{v2}`. Should I use the newer version and risk incompatibility, or hold both packages at current versions?"
3. "Package `{name}` is deprecated. Suggested replacement is `{replacement}`. Should I migrate to the replacement or keep the current package for now?"
4. "Security patch for `{name}` conflicts with pinned version `{pinned}`. Should I override the pin to apply the security fix?"
5. "Updating `{name}` drops support for `{runtime} {version}`. Your project targets `{runtime} {min_version}`. Should I proceed?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Critical/high severity vulnerability in any dependency | Update immediately, even if it requires a major version bump |
| Patch-level update with no known issues | Auto-apply and run tests |
| Minor-level update | Batch with other minor updates for the same ecosystem, review changelog |
| Major-level update with clear migration guide | Create dedicated branch, apply one at a time with full validation |
| Major-level update with no migration guide | Flag for manual review, do not auto-apply |
| Peer dependency conflict between two direct deps | Attempt resolution with latest compatible versions; ask user if unresolvable |
| Deprecated package with known replacement | Suggest replacement; apply only with user approval |
| Lockfile out of sync with manifest | Regenerate lockfile before applying any updates |
| Transitive dependency vulnerable but direct dep is current | Check if direct dep has a newer version fixing the transitive; otherwise flag |
| Update causes test failures | Bisect batch to isolate failing update, revert it, and report |

## Success Criteria

- [ ] All dependencies at latest compatible versions or explicitly deferred with justification
- [ ] Zero critical or high severity vulnerabilities in dependency tree
- [ ] Lockfile is consistent with the dependency manifest and installs cleanly
- [ ] Full test suite passes after all updates are applied
- [ ] No peer dependency warnings or conflicts remain unresolved
- [ ] Breaking changes are documented with required code modifications
- [ ] Audit log records every version change with semver classification

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Lockfile corruption after update | Install fails with checksum or integrity errors | Delete lockfile, run fresh install, and re-apply updates one at a time |
| Silent breaking change in patch update | Tests pass but runtime behavior changes | Add integration/smoke tests for critical paths; pin the version and report upstream |
| Peer dependency deadlock | No version combination satisfies all peer constraints | Identify the constraining package, check for updates, or ask user to accept overrides |
| Transitive dependency regression | Build or tests fail on deeply nested dependency | Use resolution/overrides field to pin the transitive dep; track upstream fix |
| Update reverts a previous security fix | Vulnerability reappears after batch update | Audit each update individually; ensure security patches are applied last |
| CI flakiness masks update breakage | Tests intermittently fail, hiding real regressions | Re-run failed tests in isolation; compare failure rates before and after update |

## Audit Log

- `[{timestamp}] dependency-audit: scanned {count} dependencies — {critical} critical, {high} high, {medium} medium, {low} low vulnerabilities found`
- `[{timestamp}] update-applied: {package} {old_version} → {new_version} ({semver_level})`
- `[{timestamp}] lockfile-regenerated: {lockfile_name} — {additions} added, {removals} removed, {updates} updated`
- `[{timestamp}] test-validation: {passed}/{total} tests passed after update batch`
- `[{timestamp}] breaking-change-detected: {package} {version} — {description}`
- `[{timestamp}] rollback: reverted {package} to {old_version} — reason: {reason}`
````
