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
