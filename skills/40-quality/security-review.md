````markdown
---
name: security-review
description: >
  Perform security-focused code review covering OWASP Top 10,
  vulnerability scanning, secret detection, and input validation.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - secure-coding-review
reasoning_mode: plan-execute
---

# Security Review

> _"Security is not a feature — it's a property of every line of code."_

## Context

Invoked when code changes touch authentication, authorization, data
handling, or external input processing. Also triggered during pre-release
audits, dependency updates, or after a security incident. Ensures code
does not introduce vulnerabilities from the OWASP Top 10 or expose
secrets and sensitive data.

---

## Micro-Skills

### 1. OWASP Top 10 Scan ⚡ (Power Mode)

**Steps:**

1. Review code against each OWASP Top 10 (2021) category:
   - **A01 Broken Access Control** — Verify authorization checks on every
     endpoint; confirm RBAC/ABAC enforcement.
   - **A02 Cryptographic Failures** — Check for weak algorithms (MD5, SHA1
     for hashing passwords), hardcoded keys, missing TLS.
   - **A03 Injection** — Identify SQL, NoSQL, OS command, LDAP, and XSS
     injection vectors; verify parameterized queries.
   - **A04 Insecure Design** — Look for missing rate limiting, lack of
     input validation at trust boundaries.
   - **A05 Security Misconfiguration** — Check default credentials, verbose
     error messages, unnecessary features enabled.
   - **A06 Vulnerable Components** — Flag known CVEs in dependencies.
   - **A07 Authentication Failures** — Verify password policies, session
     management, MFA support.
   - **A08 Data Integrity Failures** — Check deserialization safety,
     unsigned updates, CI/CD pipeline integrity.
   - **A09 Logging & Monitoring Failures** — Ensure security events are
     logged without leaking sensitive data.
   - **A10 SSRF** — Validate and allowlist outbound URLs; block internal
     network access from user-controlled inputs.
2. Classify each finding by severity: Critical, High, Medium, Low.

### 2. Secret Detection 🌿 (Eco Mode)

**Steps:**

1. Scan the changeset for hardcoded secrets:
   - API keys, tokens, passwords in source code.
   - Private keys, certificates, `.env` files in the repository.
   - Connection strings with embedded credentials.
2. Check `.gitignore` covers sensitive file patterns:
   - `.env`, `.env.*`, `*.pem`, `*.key`, `*.p12`.
3. Recommend secret management alternatives:
   - Environment variables, vault services (HashiCorp Vault, AWS Secrets
     Manager), CI/CD secret stores.
4. If a secret is detected in git history, recommend rotation immediately.

### 3. Input Validation Audit 🌿 (Eco Mode)

**Steps:**

1. Trace all external input entry points:
   - HTTP request parameters, headers, body.
   - File uploads, WebSocket messages.
   - Environment variables, CLI arguments.
   - Database reads (second-order injection).
2. Verify each input is validated:
   - **Type checking** — Reject unexpected types.
   - **Length limits** — Enforce max length on strings and arrays.
   - **Allowlist patterns** — Use regex or enum validation for structured inputs.
   - **Encoding** — Sanitize/escape output context (HTML, SQL, shell).
3. Flag any input that flows to a sensitive sink without validation:
   - Database queries, file system paths, shell commands, HTTP redirects.

### 4. Vulnerability Scanning Integration 🌿 (Eco Mode)

**Steps:**

1. Verify dependency scanning is configured:
   - `npm audit`, `pip-audit`, `govulncheck`, `OWASP Dependency-Check`.
2. Review scan results for:
   - **Critical/High CVEs** — Must fix before merge.
   - **Medium CVEs** — Plan fix within current sprint.
   - **Low CVEs** — Track and fix in next maintenance cycle.
3. Check for outdated dependencies with known security patches available.

---

## Inputs

| Parameter        | Type       | Required | Description                                   |
|------------------|------------|----------|-----------------------------------------------|
| `code_diff`      | `string`   | yes      | Diff or files to review for security issues   |
| `language`       | `string`   | no       | Primary language of the codebase              |
| `dep_manifest`   | `string`   | no       | Path to dependency file (package.json, etc.)  |
| `owasp_focus`    | `string[]` | no       | Specific OWASP categories to prioritize       |

## Outputs

| Field              | Type       | Description                                  |
|--------------------|------------|----------------------------------------------|
| `vulnerabilities`  | `object[]` | Findings with OWASP category and severity    |
| `secrets_found`    | `object[]` | Detected secrets with file and line location  |
| `validation_gaps`  | `object[]` | Unvalidated inputs mapped to sensitive sinks  |
| `remediation_plan` | `string`   | Prioritized list of fixes                     |

---

## Edge Cases

- Code uses an ORM that auto-parameterizes queries — Still verify raw query
  escape hatches (e.g., `raw()`, `$queryRawUnsafe()`) are not used with
  user input.
- Third-party auth provider (OAuth, SAML) — Review integration configuration,
  not the provider's internal code.
- Secret found in git history but removed from HEAD — Still flag; recommend
  secret rotation and history rewriting.

---

## Scope

### In Scope

- Reviewing code for OWASP Top 10 (2021) vulnerability categories
- Detecting hardcoded secrets, API keys, tokens, and credentials in source and config files
- Auditing input validation at all external entry points and tracing to sensitive sinks
- Reviewing dependency manifests for known CVEs (Critical/High)
- Verifying authentication and authorization enforcement on endpoints
- Checking cryptographic usage (algorithms, key management, TLS configuration)
- Validating `.gitignore` coverage for sensitive file patterns

### Out of Scope

- Penetration testing or active exploitation of vulnerabilities
- Network-level security (firewall rules, VPN, cloud security groups)
- Infrastructure-as-code security review (delegate to `terraform-iac` or `threat-modeling`)
- Runtime application security monitoring (WAF, RASP configuration)
- Compliance auditing (SOC2, HIPAA, PCI-DSS checklist completion)
- Writing fix implementations — review is advisory; author implements fixes

---

## Guardrails

- Never disclose or log the actual value of a detected secret — reference by file and line only.
- Do not approve code that contains any unresolved Critical-severity vulnerability.
- Flag all uses of known-weak cryptographic algorithms (MD5, SHA1 for passwords, DES, RC4).
- Do not dismiss a finding because "the input is trusted" — validate at every trust boundary.
- Always recommend secret rotation when a secret has been committed, even if subsequently removed.
- Do not scan or report on test fixtures or mock data unless they contain real credentials.
- Limit scope to the changeset unless a full-codebase audit is explicitly requested.

## Ask-When-Ambiguous

### Triggers

- Code uses a custom authentication/authorization framework not recognized
- Dependency manifest is missing or incomplete
- Input validation is delegated to a middleware or framework not visible in the diff
- Secret-like strings appear in test fixtures or example configurations
- Code interacts with internal-only APIs where SSRF risk assessment differs

### Question Templates

1. "This code uses a custom auth middleware (`{{middleware_name}}`). Can you confirm it enforces {{auth_requirement}} on all routes?"
2. "I found `{{secret_pattern}}` in `{{file_path}}`. Is this a real credential or a test fixture/placeholder?"
3. "Input validation for `{{parameter}}` is not visible in this diff. Is it handled by a middleware or framework layer I should review separately?"
4. "The dependency `{{dep_name}}@{{version}}` has a known {{severity}} CVE ({{cve_id}}). Is there a planned upgrade, or should I flag this as blocking?"
5. "This endpoint (`{{endpoint}}`) accepts user input that reaches `{{sink_function}}`. Is there an allowlist or sanitization step I'm not seeing?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Hardcoded secret detected in source code | Block merge; require secret removal and rotation immediately |
| SQL query constructed with string concatenation | Flag as Critical (A03 Injection); require parameterized query |
| Dependency has a Critical CVE with a patch available | Block merge; require upgrade to patched version |
| Dependency has a Medium CVE with no patch | Log as tracked issue; allow merge with documented risk acceptance |
| User input reaches file system path without validation | Flag as High (A01/A03); require path traversal protection |
| Password stored with MD5/SHA1 | Flag as Critical (A02); require bcrypt/scrypt/argon2 |
| Authentication check missing on an internal-only endpoint | Flag as Medium (A01); assess exposure and recommend adding auth |
| Error response includes stack trace or internal details | Flag as Medium (A05); require generic error messages in production |

## Success Criteria

- [ ] All OWASP Top 10 categories have been evaluated against the changeset
- [ ] Zero hardcoded secrets remain in the codebase (or false positives are documented)
- [ ] Every external input entry point has validated type, length, and format
- [ ] No unvalidated input flows to a sensitive sink (SQL, file path, shell, redirect)
- [ ] All Critical and High dependency CVEs are resolved or have documented risk acceptance
- [ ] Cryptographic usage follows current best practices (no weak algorithms)
- [ ] Findings are classified with OWASP category and severity for traceability

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| False positive on test fixtures | Reviewer flags mock API keys as real secrets | Check file path and naming patterns; ask author to confirm if ambiguous |
| Missed second-order injection | Input stored in DB, later used unsafely in another query | Trace data flow beyond the immediate changeset; flag DB-sourced values as untrusted |
| Over-reliance on framework safety | Assume ORM prevents all injection; miss raw query usage | Explicitly search for raw query escape hatches in every ORM-based review |
| Secret detected but not rotated | Secret removed from code but still active; attacker uses leaked credential | Always mandate rotation alongside code removal; verify rotation completed |
| Incomplete input tracing | Validation exists but doesn't cover all entry points | Systematically enumerate entry points before checking validation |
| Dependency scan not run | New dependency added without CVE check | Require dependency scan as part of the review checklist before sign-off |

## Audit Log

- `[{{timestamp}}] security-review-started: files={{file_count}}, language={{language}}, owasp_focus={{categories}}`
- `[{{timestamp}}] owasp-finding: {{owasp_category}} / {{severity}} in {{file_path}}:{{line}} — {{description}}`
- `[{{timestamp}}] secret-detected: type={{secret_type}} in {{file_path}}:{{line}} — rotation_required={{yes/no}}`
- `[{{timestamp}}] validation-gap: input={{parameter}} → sink={{sink_function}} in {{file_path}}:{{line}} — unvalidated={{fields}}`
- `[{{timestamp}}] cve-flagged: {{dep_name}}@{{version}} — {{cve_id}} ({{severity}}) — patch_available={{yes/no}}`
- `[{{timestamp}}] security-review-completed: critical={{critical_count}}, high={{high_count}}, medium={{medium_count}}, low={{low_count}}, secrets={{secret_count}}`
````
