---
name: auth-implementation
description: >
  Implement authentication and authorization safely: JWT, OAuth2,
  RBAC, or API key strategies.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - api-contract-design
  - threat-modeling
reasoning_mode: plan-execute
---

# Authentication & Authorization Implementation

> _"Identity is the new perimeter."_

## Context

Invoked when adding auth to an application. Covers authentication (who are
you?) and authorization (what can you do?).

---

## Micro-Skills

### 1. Strategy Selection ⚡ (Power Mode)

**Steps:**

1. Ask the user about their auth requirements:
   - **Session-based:** Traditional web apps (server-side rendering).
   - **JWT:** SPAs, mobile apps, microservices.
   - **OAuth2/OIDC:** Third-party login (Google, GitHub, Azure AD).
   - **API Keys:** Machine-to-machine, simple integrations.
2. Document the choice in an ADR (invoke `adr-management`).

### 2. JWT Implementation ⚡ (Power Mode)

**Steps:**

1. Choose a JWT library (verify it's actively maintained, no CVEs).
2. Configure:
   - Algorithm: `RS256` (asymmetric) preferred over `HS256` (symmetric).
   - Expiry: Access token 15min, refresh token 7 days.
   - Claims: `sub`, `iss`, `exp`, `iat`, `roles`.
3. Implement:
   - Token generation endpoint (`POST /auth/token`).
   - Token validation middleware.
   - Token refresh endpoint (`POST /auth/refresh`).
   - Token revocation (blacklist or short expiry + refresh rotation).
4. **Never** store JWTs in `localStorage` — use HTTP-only cookies.

### 3. RBAC Implementation ⚡ (Power Mode)

**Steps:**

1. Define roles (e.g., `admin`, `editor`, `viewer`).
2. Define permissions per role as a matrix.
3. Implement authorization middleware that checks `user.role` against
   required permissions per endpoint.
4. Store role assignments in the database, not in the JWT (except for
   caching — always re-validate critical operations).

### 4. Security Hardening ⚡ (Power Mode)

**Steps:**

1. Password hashing: `bcrypt` (cost factor 12) or `argon2id`.
2. Rate limit auth endpoints (5 attempts per minute per IP).
3. Add CSRF protection for cookie-based auth.
4. Implement account lockout after N failed attempts.
5. Log all auth events (login, logout, failed attempts, role changes).

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `auth_middleware` | `string`  | Authentication middleware file           |
| `authz_middleware`| `string`  | Authorization middleware file            |
| `auth_routes`    | `string`   | Auth endpoint handlers                   |
| `config`         | `string`   | Auth configuration file                  |

---

## Scope

### In Scope

- Selecting and implementing authentication strategies (JWT, OAuth2/OIDC, session-based, API keys)
- Token lifecycle management: issuance, validation, refresh, and revocation
- RBAC and permission matrix design for application endpoints
- Password hashing and credential storage configuration
- Auth middleware and route guard implementation
- CSRF, CORS, and cookie security configuration for auth flows
- Rate limiting and brute-force protection on auth endpoints
- Auth event logging (login, logout, failed attempts, privilege changes)

### Out of Scope

- Identity provider (IdP) server administration (e.g., Keycloak realm setup, Azure AD tenant config)
- Network-level security (firewalls, WAF rules, TLS certificate provisioning)
- Application business logic unrelated to access control
- User registration UI/UX flows beyond the auth API surface
- Secrets management infrastructure (handled by DevOps / `terraform-iac`)
- Compliance certification audits (SOC 2, HIPAA) — this skill implements controls, not attestation

---

## Guardrails

- Never store plaintext passwords; always use `bcrypt` (cost ≥ 12) or `argon2id`.
- Never store JWTs in `localStorage` or `sessionStorage`; use HTTP-only, Secure, SameSite cookies.
- Never hard-code secrets, API keys, or signing keys in source code.
- Always validate JWT signature, `exp`, `iss`, and `aud` claims on every request.
- Never log authentication tokens, passwords, or secret keys — even at debug level.
- Always enforce HTTPS for all auth endpoints; reject plain HTTP.
- Never disable CSRF protection for cookie-based auth without documented justification.
- Always hash and compare tokens in constant time to prevent timing attacks.
- Preserve existing auth configurations when extending; never silently remove middleware or routes.

---

## Ask-When-Ambiguous

### Triggers

- The project has no existing auth and the desired strategy is unspecified
- Multiple auth strategies could apply (e.g., SPA could use JWT or OAuth2/OIDC)
- The expected token lifetime or refresh policy is not defined
- Role definitions or permission granularity is unclear
- The target IdP or user store (database, LDAP, third-party) is unspecified
- Multi-tenancy or multi-factor authentication requirements are unclear

### Question Templates

1. "Which authentication strategy should be used — JWT, OAuth2/OIDC, session-based, or API keys?"
2. "What identity provider will issue tokens — self-hosted (DB-backed), or external (Google, Azure AD, Auth0)?"
3. "What roles and permissions are required? Please list roles and their allowed operations."
4. "What should the token expiry be? (default: 15 min access / 7 day refresh)"
5. "Is multi-factor authentication (MFA) required for any user tier or sensitive operation?"
6. "Should the system support multi-tenancy with tenant-scoped roles?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Server-rendered web app with sessions | Use session-based auth with secure cookie store |
| SPA or mobile client | Use JWT with HTTP-only cookie transport or OAuth2 PKCE flow |
| Third-party login required (Google, GitHub) | Implement OAuth2/OIDC authorization code flow |
| Machine-to-machine API communication | Use API keys or OAuth2 client-credentials grant |
| Roles exceed 3 or permissions are fine-grained | Implement full RBAC with a database-backed permission matrix |
| Compliance requires MFA | Integrate TOTP or WebAuthn as a second factor |
| Token revocation is critical (e.g., admin force-logout) | Use short-lived access tokens + refresh token rotation with a revocation list |
| Password reset is needed | Implement time-limited, single-use reset tokens sent to verified email |

---

## Success Criteria

- [ ] Auth middleware rejects requests with missing, expired, or tampered tokens
- [ ] Passwords are hashed with `bcrypt` (cost ≥ 12) or `argon2id` — never stored in plaintext
- [ ] Tokens are transported via HTTP-only, Secure, SameSite cookies (not `localStorage`)
- [ ] Refresh token rotation is implemented; old refresh tokens are invalidated after use
- [ ] RBAC middleware correctly blocks users from accessing resources outside their role
- [ ] Auth endpoints are rate-limited (≤ 5 attempts per minute per IP)
- [ ] Failed login attempts are logged with timestamp, IP, and user identifier
- [ ] CSRF protection is active for all state-changing cookie-authenticated endpoints
- [ ] All auth-related tests pass (unit + integration) with ≥ 90% branch coverage on auth modules
- [ ] No secrets or tokens appear in source code, logs, or error responses

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| JWT secret leaked or committed to repo | Unauthorized token forging; all tokens compromised | Rotate signing keys immediately; use asymmetric RS256 keys stored in a vault |
| Token stored in `localStorage` | XSS attack exfiltrates tokens | Migrate to HTTP-only Secure cookies; add CSP headers |
| Missing `exp` claim validation | Expired tokens accepted indefinitely | Validate `exp` in middleware; add integration tests for expired tokens |
| Refresh token reuse not detected | Stolen refresh token grants indefinite access | Implement refresh token rotation; invalidate family on reuse detection |
| RBAC bypass via direct URL access | Unauthorized users reach admin endpoints | Enforce authorization middleware on every route; add integration tests per role |
| Timing attack on password comparison | Attacker infers valid credentials via response-time analysis | Use constant-time comparison (`crypto.timingSafeEqual` or equivalent) |
| CSRF token missing on state-changing endpoints | Cross-site request forgery exploits authenticated sessions | Add CSRF middleware; verify tokens on all POST/PUT/DELETE routes |
| Account lockout not implemented | Credential-stuffing attacks succeed via brute force | Lock account after N failed attempts; notify user and require reset |

---

## Audit Log

- `[timestamp]` strategy-selected: Chose `<auth-strategy>` for `<project-name>` based on `<rationale>`
- `[timestamp]` middleware-created: Generated auth middleware at `<file-path>` with `<algorithm>` token validation
- `[timestamp]` rbac-configured: Defined roles `<role-list>` with `<permission-count>` permissions mapped
- `[timestamp]` endpoint-secured: Applied auth guard to `<method> <route>` requiring role `<role>`
- `[timestamp]` rate-limit-applied: Configured `<max-attempts>` per `<window>` on `<endpoint>`
- `[timestamp]` hardening-applied: Enabled `<feature>` (e.g., CSRF protection, account lockout, refresh rotation)
- `[timestamp]` test-verified: Auth test suite passed — `<pass-count>`/`<total-count>` tests green
