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
