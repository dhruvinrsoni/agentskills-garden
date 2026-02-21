```markdown
---
name: dependency-analysis
description: >
  Analyse project dependencies — build dependency graphs, detect circular
  references, assess upgrade risks, and plan version migrations.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: plan-execute
---

# Dependency Analysis

> _"Every dependency is a promise someone else made — verify before you trust."_

## Context

Invoked when a project relies on external libraries, services, or internal
modules whose relationships, versions, or health need to be understood.
Produces dependency graphs, flags circular references, identifies stale or
vulnerable packages, and creates upgrade plans.

---

## Micro-Skills

### 1. Dependency Graph Construction ⚡ (Power Mode)

**Steps:**

1. Parse manifest files (package.json, requirements.txt, pom.xml, go.mod, *.csproj, etc.).
2. Resolve transitive dependencies to build the full dependency tree.
3. Generate a Mermaid graph showing direct and key transitive relationships.
4. Annotate each node with current version and latest available version.

### 2. Circular Dependency Detection ⚡ (Power Mode)

**Steps:**

1. Build an adjacency list from import/require statements or module references.
2. Run a depth-first cycle detection algorithm.
3. For each cycle found, list the participating modules and the import chain.
4. Suggest refactoring strategies to break each cycle (extract shared interface, invert dependency).

### 3. Staleness & Vulnerability Audit 🌿 (Eco Mode)

**Steps:**

1. Compare current versions against latest stable releases.
2. Flag dependencies more than 2 major versions behind as "stale".
3. Cross-reference with known vulnerability databases (CVE, GitHub Advisories).
4. Produce a summary table: package, current version, latest version, staleness, known CVEs.

### 4. Upgrade Planning ⚡ (Power Mode)

**Steps:**

1. Identify the target version for each dependency to upgrade.
2. Check for breaking changes in changelogs or migration guides.
3. Order upgrades by dependency depth (leaf dependencies first).
4. Produce a phased upgrade plan with rollback checkpoints.

---

## Outputs

| Field                | Type       | Description                                       |
|----------------------|------------|---------------------------------------------------|
| `dependency_graph`   | `string`   | Mermaid diagram of the dependency tree            |
| `circular_deps`      | `object[]` | List of detected cycles with module chains        |
| `staleness_report`   | `object[]` | Per-package version comparison and CVE flags       |
| `upgrade_plan`       | `object[]` | Phased upgrade steps with rollback checkpoints    |

---

## Edge Cases

- No manifest file found — Ask the user which package manager or module
  system is in use; fall back to scanning import statements.
- Monorepo with multiple manifests — Analyse each workspace/package
  independently, then merge into a unified graph.
- Dependency is deprecated with no replacement — Flag as critical and ask
  the user for a replacement decision.

---

## Scope

### In Scope

- Parsing package manifests and lock files to enumerate direct and transitive dependencies.
- Building and visualising dependency graphs (internal modules and external packages).
- Detecting circular dependencies among internal modules or packages.
- Comparing installed versions against latest stable releases for staleness assessment.
- Cross-referencing dependencies with known vulnerability databases (CVEs, advisories).
- Creating phased, ordered upgrade plans with rollback checkpoints.
- Suggesting refactoring strategies to break circular dependency cycles.

### Out of Scope

- Automatically upgrading or installing packages (see implementation skills).
- Deep security vulnerability analysis or exploit assessment (see `dependency-scanning`, `threat-modeling`).
- Licence compliance auditing (legal review of OSS licences).
- Runtime dependency injection or service-mesh dependency resolution.
- Performance impact analysis of dependency upgrades (see `profiling-analysis`).
- Business decisions about whether to adopt or drop a dependency.

---

## Guardrails

- Never install, upgrade, or remove a dependency — this skill only analyses and recommends.
- All dependency data must come from actual manifest/lock files, not assumptions.
- Circular dependency reports must include the exact import chain, not just module names.
- Vulnerability flags must reference a specific CVE ID or advisory URL; do not make vague claims.
- Upgrade plans must order changes leaf-first (deepest transitive dependencies upgraded before their consumers).
- Staleness thresholds (2 major versions behind) can be adjusted by the user but must be explicitly stated.
- Do not recommend "upgrade everything at once" — always produce a phased plan.
- Record all analysis artefacts in the scratchpad for traceability.

---

## Ask-When-Ambiguous

### Triggers

- Multiple manifest files exist and it is unclear which defines the primary dependency set.
- A dependency is pinned to an exact version with no explanation — it may be intentional.
- A circular dependency could be broken in more than one way (extract interface vs. merge modules).
- The user's upgrade tolerance is unknown (conservative patch-only vs. aggressive major upgrades).
- A deprecated dependency has multiple potential replacements.
- Transitive dependency conflicts exist (version A required by package X, version B by package Y).

### Question Templates

1. "I found multiple manifest files: [list]. Which is the primary one, or should I analyse all of them?"
2. "Dependency [pkg@version] is pinned exactly. Is this intentional (e.g., known incompatibility), or can it be upgraded?"
3. "Circular dependency detected: [A → B → C → A]. Should I suggest extracting a shared interface or merging modules?"
4. "What is your upgrade policy — patch/minor only, or are major version bumps acceptable?"
5. "Dependency [pkg] is deprecated. Candidates for replacement are [X, Y, Z]. Which do you prefer?"
6. "Packages [X] and [Y] require conflicting versions of [Z]. Should I align on the newer or older version?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Dependency has a known critical CVE | Flag as urgent; recommend immediate upgrade or pinning to patched version |
| Dependency is 2+ major versions behind with no CVEs | Flag as stale; include in next planned upgrade phase |
| Circular dependency among 2 modules | Suggest interface extraction as first option |
| Circular dependency among 3+ modules | Suggest creating a shared base module to break the cycle |
| Transitive version conflict between two direct dependencies | Present both resolution options (align up or align down) with trade-offs |
| Deprecated dependency with a single clear successor | Recommend the successor; include migration guide link |
| Deprecated dependency with no successor | Flag as critical risk; ask user for direction |
| Monorepo with independent workspaces | Analyse each workspace separately, then highlight cross-workspace dependency overlaps |

---

## Success Criteria

- [ ] All direct and key transitive dependencies are enumerated from manifest/lock files.
- [ ] A dependency graph (Mermaid) is generated and reviewable.
- [ ] All circular dependencies (if any) are detected and reported with exact import chains.
- [ ] A staleness report is produced comparing current vs. latest versions.
- [ ] Known CVEs are cross-referenced and flagged with advisory IDs.
- [ ] An upgrade plan is produced with phased ordering (leaf-first) and rollback checkpoints.
- [ ] The user has reviewed and acknowledged the analysis.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Missed manifest | Dependencies from a secondary manifest are not analysed | Scan the project root for all known manifest file patterns before starting |
| False circular dependency | Import used only for type-checking flagged as runtime cycle | Distinguish runtime imports from type-only imports; ask user to confirm |
| CVE false positive | Flagged vulnerability does not apply to the used API surface | Note the specific affected API in the flag; let user dismiss with rationale |
| Stale lock file | Analysis uses outdated locked versions that don't reflect actual state | Compare lock file timestamps with manifest; warn if lock file is older |
| Upgrade ordering error | Consumer upgraded before its transitive dependency | Enforce strict leaf-first topological ordering in the upgrade plan |
| Monoreporepo scope confusion | Cross-workspace dependency missed | Merge all workspace graphs into a unified view and check cross-references |

---

## Audit Log

Every dependency analysis session must produce an entry in the project's audit log:

```
- [<ISO8601>] dependency-analysis-started: Began analysis for "<project/workspace>"
- [<ISO8601>] manifests-parsed: N manifest files processed ([list])
- [<ISO8601>] graph-built: Dependency graph generated — D direct, T transitive dependencies
- [<ISO8601>] cycles-checked: Circular dependency scan complete — C cycles found
- [<ISO8601>] staleness-audited: S stale packages, V vulnerable packages flagged
- [<ISO8601>] upgrade-plan-created: Phased plan with P phases and R rollback checkpoints
- [<ISO8601>] user-review: User reviewed and acknowledged dependency analysis
- [<ISO8601>] dependency-analysis-complete: Final artefacts saved to scratchpad
```

Log entries are append-only. Re-analyses are recorded as new rows, never as overwrites.
```
