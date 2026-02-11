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
