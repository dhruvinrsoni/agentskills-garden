---
name: dependency-scanning
description: >
  Scan project dependencies for known CVEs and license compliance
  issues. Works with npm, pip, go mod, Maven, NuGet.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# Dependency Scanning

> _"You are responsible for every line of code you ship — including the ones you didn't write."_

## Context

Invoked as part of CI or on-demand to ensure third-party dependencies
are free of known vulnerabilities and license conflicts.

---

## Micro-Skills

### 1. CVE Scan 🌿 (Eco Mode)

**Steps:**

1. Detect the package manager:
   - `package-lock.json` / `yarn.lock` → npm/yarn
   - `requirements.txt` / `poetry.lock` → pip/poetry
   - `go.sum` → Go modules
   - `pom.xml` / `build.gradle` → Maven/Gradle
   - `*.csproj` / `packages.lock.json` → NuGet
2. Run the appropriate scanner:
   - `npm audit`, `yarn audit`
   - `pip-audit`, `safety`
   - `govulncheck`
   - `mvn dependency-check:check`
   - `dotnet list package --vulnerable`
3. Parse results into a unified format.

### 2. Severity Assessment 🌿 (Eco Mode)

**Steps:**

1. Classify each finding by CVSS score:
   - **Critical (9.0-10.0):** Fix immediately.
   - **High (7.0-8.9):** Fix before next release.
   - **Medium (4.0-6.9):** Track as tech debt.
   - **Low (0.1-3.9):** Informational.
2. Check if the vulnerability is **reachable** (is the vulnerable code path
   actually used by the project?).

### 3. Remediation 🌿 (Eco Mode)

**Steps:**

1. For each finding, check if a patched version exists.
2. If yes, generate a dependency update (version bump).
3. If no patch exists:
   - Check for alternative packages.
   - Apply a workaround if documented.
   - Document the accepted risk with a timeline for resolution.
4. Run tests after every dependency update.

### 4. License Compliance 🌿 (Eco Mode)

**Steps:**

1. Extract license information for all dependencies.
2. Flag incompatible licenses (e.g., GPL in a proprietary project).
3. Generate a license compliance report (SPDX or CycloneDX SBOM).

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `vulnerabilities`| `object[]`| List of CVEs with severity               |
| `updates`       | `object[]` | Recommended version bumps                |
| `license_report`| `string`   | SBOM / license compliance report         |

---

## Scope

### In Scope

- Scanning project dependencies for known CVEs across all supported package managers (npm, pip, Go modules, Maven/Gradle, NuGet)
- Classifying vulnerability severity using CVSS scores and reachability analysis
- Generating recommended version bumps for vulnerable dependencies
- License compliance scanning and SBOM generation (SPDX, CycloneDX)
- Identifying transitive (indirect) dependency vulnerabilities
- Producing unified vulnerability reports from heterogeneous scanner outputs
- Documenting accepted-risk decisions when no patch is available

### Out of Scope

- First-party application code vulnerability scanning (handled by `secure-coding-review`)
- Runtime dependency injection or dynamic loading analysis
- Package publishing, registry management, or private feed configuration
- CI/CD pipeline creation for automated scanning (handled by `ci-pipeline`)
- Vendor contract or legal review of license obligations
- Operating system package or base-image vulnerability scanning (handled by `docker-containerization`)

---

## Guardrails

- Never auto-upgrade a major version without confirming breaking change impact with the user.
- Always run the project’s test suite after applying any dependency update before declaring success.
- Never suppress or ignore a Critical-severity CVE without an explicit, documented risk-acceptance decision.
- Never modify source code beyond dependency manifest and lock files during remediation.
- Always verify that a recommended replacement package is actively maintained before suggesting migration.
- Preserve lock file integrity — never delete or regenerate lock files without user consent.
- Never expose vulnerability details (CVE IDs, exploit paths) in public logs or commit messages beyond what is already public.
- Always include transitive dependencies in the scan; do not limit analysis to direct dependencies only.

---

## Ask-When-Ambiguous

### Triggers

- Multiple package managers are detected in the same repository and scan scope is unclear
- A Critical CVE has no patched version and the user has not specified a risk tolerance
- A dependency update introduces a major version bump with known breaking changes
- License policy is unspecified and potentially incompatible licenses are detected (e.g., GPL in a proprietary project)
- The scanner produces conflicting severity ratings from different data sources
- A monorepo contains multiple services with independent dependency trees

### Question Templates

1. "Multiple package managers detected (`<list>`). Should I scan all of them or focus on a specific one?"
2. "CVE `<id>` (severity: `<level>`) affects `<package>` but no patched version exists. Should I document an accepted risk, find an alternative package, or apply a workaround?"
3. "Updating `<package>` from `<old>` to `<new>` is a major version bump. Should I proceed and run tests, or hold for manual review?"
4. "License `<license>` detected on `<package>`. What is your project’s license policy — permissive-only, or are copyleft licenses acceptable?"
5. "This is a monorepo with `<n>` independent dependency trees. Should I generate a single unified report or per-service reports?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Critical CVE with patch available | Apply patch immediately; run tests; report |
| Critical CVE with no patch | Document risk; search for alternative package; set review timeline |
| High CVE with patch available | Queue update for next release; run tests |
| Medium / Low CVE | Track as tech debt in vulnerability backlog |
| Vulnerability is not reachable (unused code path) | Downgrade effective severity by one level; document reasoning |
| GPL-licensed dependency in proprietary project | Flag as license violation; recommend permissive alternative |
| Major version bump required for fix | Ask user before proceeding; assess breaking changes |
| Multiple scanners disagree on severity | Use the highest reported severity; note discrepancy in report |
| Transitive dependency is vulnerable but direct parent is unmaintained | Recommend replacing the direct parent package |

---

## Success Criteria

- [ ] All supported package managers in the repository are scanned (no manifest files missed)
- [ ] Every vulnerability is classified with CVE ID, CVSS score, severity tier, and reachability status
- [ ] All Critical and High vulnerabilities have either a remediation applied or an accepted-risk decision documented
- [ ] Dependency updates pass the full test suite with no regressions
- [ ] License compliance report is generated in SPDX or CycloneDX format
- [ ] No incompatible licenses remain unacknowledged in the report
- [ ] Lock files are regenerated consistently after updates (no phantom diffs)
- [ ] Scan results are reproducible — re-running the scan yields the same findings

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Scanner misses transitive vulnerability | Deep dependency with known CVE not reported | Use scanners that resolve full dependency trees (`npm audit --all`, `pip-audit --desc`); cross-check with OSV database |
| False positive CVE | Safe usage flagged as vulnerable, wasting remediation effort | Verify reachability; mark false positive with justification; suppress in scanner config |
| Major version bump breaks build | Tests fail after dependency update | Pin to last compatible minor/patch; create isolated branch for major migration |
| Lock file conflict after update | Merge conflicts in `package-lock.json` or `yarn.lock` | Regenerate lock file on the target branch after merge; do not manually edit lock files |
| License misidentification | Scanner reports wrong license due to missing or ambiguous `LICENSE` file in dependency | Manually verify license in the package repository; override in scanner config |
| Scanner unavailable or rate-limited | CI job fails with timeout or API error from vulnerability database | Cache scanner database locally; implement retry with backoff; fall back to alternative scanner |
| Accepted risk not re-evaluated | Documented risk-acceptance stales as new exploit information emerges | Set calendar reminder to re-assess accepted risks quarterly; track in tech-debt backlog |

---

## Audit Log

- `[timestamp]` scan-executed: Ran `<scanner>` on `<manifest-file>` — found `<n>` vulnerabilities (`<critical>`C / `<high>`H / `<medium>`M / `<low>`L)
- `[timestamp]` cve-remediated: Updated `<package>` from `<old-version>` to `<new-version>` to resolve `<CVE-ID>` (severity: `<level>`)
- `[timestamp]` risk-accepted: Accepted risk for `<CVE-ID>` in `<package>` — reason: `<justification>`, reassess by `<date>`
- `[timestamp]` license-flagged: Detected `<license>` on `<package>` — action: `<replaced|accepted|escalated>`
- `[timestamp]` sbom-generated: Produced `<format>` SBOM at `<file-path>` covering `<n>` direct and `<m>` transitive dependencies
- `[timestamp]` tests-verified: Full test suite passed after dependency updates — `<pass>`/`<total>` tests green
- `[timestamp]` false-positive-suppressed: Suppressed `<CVE-ID>` for `<package>` — reason: `<justification>`
