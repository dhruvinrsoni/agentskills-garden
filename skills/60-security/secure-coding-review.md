---
name: secure-coding-review
description: >
  Review code for OWASP Top 10 vulnerabilities, common security
  anti-patterns, and language-specific pitfalls.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: plan-execute
---

# Secure Coding Review

> _"Every line of code is an attack surface."_

## Context

Invoked during code review, before merging to main, or as a periodic
security audit. Checks for the OWASP Top 10 and language-specific issues.

---

## Micro-Skills

### 1. OWASP Top 10 Scan ⚡ (Power Mode)

**Steps:**

For each file under review, check for:

| # | Vulnerability           | What to look for                         |
|---|-------------------------|------------------------------------------|
| 1 | Injection               | SQL concat, unsanitized shell exec       |
| 2 | Broken Auth             | Hardcoded secrets, weak JWT validation   |
| 3 | Sensitive Data Exposure | PII in logs, missing encryption          |
| 4 | XXE                     | XML parsing without disabling entities   |
| 5 | Broken Access Control   | Missing authZ checks on endpoints        |
| 6 | Security Misconfig      | Debug mode in prod, default credentials  |
| 7 | XSS                     | Unescaped user input in HTML/templates   |
| 8 | Insecure Deserialization| Deserializing untrusted data             |
| 9 | Known Vulnerabilities   | Outdated dependencies with CVEs          |
|10 | Insufficient Logging    | No audit trail for sensitive operations  |

### 2. Secret Detection ⚡ (Power Mode)

**Steps:**

1. Scan for patterns: API keys, AWS credentials, private keys, tokens.
2. Check `.env` files are in `.gitignore`.
3. Verify secrets come from environment variables or a vault, not code.
4. Flag any hardcoded secret as `CRITICAL`.

### 3. Language-Specific Checks ⚡ (Power Mode)

**Steps:**

- **JavaScript/TypeScript:** `eval()`, `innerHTML`, prototype pollution.
- **Python:** `pickle.loads()` on untrusted data, `os.system()`.
- **Go:** unchecked error returns, `http.ListenAndServe` without TLS.
- **Java:** XML external entity (XXE), insecure `ObjectInputStream`.
- **SQL:** String concatenation in queries instead of parameterized.

---

## Verdicts

| Severity   | Action                                              |
|------------|-----------------------------------------------------|
| `CRITICAL` | Block merge. Must fix immediately.                  |
| `HIGH`     | Block merge. Fix before release.                    |
| `MEDIUM`   | Warn. Track as tech debt.                           |
| `LOW`      | Informational. Fix at convenience.                  |

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `findings`      | `object[]` | List of vulnerabilities found            |
| `severity_summary`| `object` | Count by severity level                  |
| `remediation`   | `string[]` | Fix recommendations per finding          |

---

## Scope

### In Scope

- Reviewing application source code for OWASP Top 10 vulnerabilities
- Detecting hardcoded secrets, API keys, private keys, and tokens in source files and configuration
- Language-specific security anti-pattern detection (JavaScript, Python, Go, Java, SQL)
- Verifying that `.env` files and secret-bearing paths are excluded from version control
- Assessing input validation, output encoding, and parameterized query usage
- Evaluating deserialization safety and XML parsing configuration
- Checking audit logging adequacy for sensitive operations
- Producing severity-classified findings with actionable remediation guidance

### Out of Scope

- Third-party dependency vulnerability scanning (handled by `dependency-scanning`)
- Infrastructure and network security configuration (firewalls, TLS, WAF)
- Penetration testing or dynamic application security testing (DAST)
- Compliance framework mapping (PCI-DSS, HIPAA control attestation)
- Security architecture and threat modeling (handled by `threat-modeling`)
- Remediation implementation — this skill identifies issues and recommends fixes, not applies them

---

## Guardrails

- Never auto-fix security findings without explicit user review and approval.
- Flag every hardcoded secret as `CRITICAL` regardless of context — no exceptions.
- Never display or log the actual value of detected secrets in findings output.
- Always check the full file, not just the diff — existing vulnerabilities in unchanged code are still in scope.
- Never downgrade a severity classification without documented justification.
- Do not modify source code during review; produce findings and recommendations only.
- Always verify that flagged patterns are actual vulnerabilities, not false positives from comments, tests, or documentation.
- Preserve review objectivity — apply the same criteria to all code regardless of author.

---

## Ask-When-Ambiguous

### Triggers

- A pattern looks like a secret but may be a placeholder, test fixture, or documentation example
- Code uses `eval()` or dynamic execution but may have a legitimate, sandboxed use case
- Input validation exists but its adequacy against the specific threat is unclear
- The project’s security classification (internal tool vs. public-facing) is unknown, affecting severity assessment
- Custom serialization/deserialization is used and its trust boundary is unclear
- The codebase mixes multiple languages and the review scope is unspecified

### Question Templates

1. "Is `<detected-string>` an actual secret or a placeholder/test fixture? It matches a secret pattern."
2. "The use of `eval()` / `os.system()` at `<file:line>` — is this sandboxed or processing trusted input only?"
3. "What is the trust level of this application — internal-only, partner-facing, or public internet? This affects severity classification."
4. "Should this review cover all languages in the repo, or focus on `<language>`?"
5. "Custom deserialization is used at `<file:line>`. Does the input come from a trusted source or external users?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Hardcoded secret detected (API key, private key, password) | Classify as `CRITICAL`; recommend vault/env-var migration; check git history for exposure |
| SQL string concatenation with user input | Classify as `CRITICAL` (injection); recommend parameterized queries |
| `eval()` or `exec()` with user-influenced input | Classify as `CRITICAL`; recommend removal or strict sandboxing |
| Unescaped user input rendered in HTML/templates | Classify as `HIGH` (XSS); recommend context-aware output encoding |
| XML parsing without disabling external entities | Classify as `HIGH` (XXE); recommend disabling DTD and external entity processing |
| Deserialization of untrusted data (`pickle`, `ObjectInputStream`) | Classify as `HIGH`; recommend allow-list deserialization or JSON alternative |
| Missing authentication check on sensitive endpoint | Classify as `HIGH`; recommend auth middleware enforcement |
| PII logged at debug level | Classify as `MEDIUM`; recommend structured logging with PII redaction |
| Missing audit trail for admin operations | Classify as `MEDIUM`; recommend event logging for sensitive actions |
| Outdated cryptographic algorithm (MD5, SHA-1 for passwords) | Classify as `HIGH`; recommend bcrypt/argon2id |

---

## Success Criteria

- [ ] All source files in scope are reviewed (not just changed files, unless explicitly scoped to a diff)
- [ ] Every finding includes: file path, line number, vulnerability category, severity, and remediation guidance
- [ ] Zero `CRITICAL` findings remain unacknowledged at review completion
- [ ] No actual secret values appear in the review output or logs
- [ ] False positive rate is documented — patterns suppressed with justification
- [ ] All OWASP Top 10 categories are checked, not just injection and XSS
- [ ] Language-specific checks are applied for each language present in the review scope
- [ ] Severity summary totals are accurate and match the detailed findings list

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Secret value leaked in review output | Actual API key or password appears in findings report | Mask secret values in output; display only the pattern type and file location |
| False positive flood | Dozens of findings from test fixtures, documentation, or example code | Add context-aware filtering for test directories and doc comments; allow suppress annotations |
| Missed injection vulnerability | SQL injection or command injection ships to production | Review raw string construction near DB/OS calls explicitly; add integration tests for injection vectors |
| Severity misclassification | Critical vulnerability classified as Medium, delaying fix | Cross-reference OWASP and CWE databases for authoritative severity; require peer review for downgrades |
| Review scope too narrow (diff-only) | Existing vulnerabilities in unchanged code missed | Default to full-file review; scope to diff only when explicitly requested |
| Language-specific pattern not recognized | Go unchecked error or Python `pickle` usage missed | Maintain language-specific check profiles; update profiles when new anti-patterns emerge |
| Stale finding database | New vulnerability class not covered by review checklist | Update OWASP and language-specific checklists quarterly; subscribe to security advisory feeds |

---

## Audit Log

- `[timestamp]` review-started: Began secure coding review of `<file-list>` (`<language>`) — scope: `<full|diff>`
- `[timestamp]` finding-reported: `<severity>` — `<vulnerability-category>` at `<file>:<line>` — `<brief-description>`
- `[timestamp]` secret-detected: Hardcoded `<secret-type>` found at `<file>:<line>` — classified CRITICAL
- `[timestamp]` false-positive-suppressed: Suppressed `<pattern>` at `<file>:<line>` — reason: `<justification>`
- `[timestamp]` review-completed: `<total>` findings (`<critical>`C / `<high>`H / `<medium>`M / `<low>`L) across `<file-count>` files
- `[timestamp]` severity-override: Changed `<finding-id>` from `<original>` to `<new-severity>` — reason: `<justification>`
- `[timestamp]` remediation-recommended: Suggested `<fix-summary>` for `<finding-id>` at `<file>:<line>`
