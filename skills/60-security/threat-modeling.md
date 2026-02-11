---
name: threat-modeling
description: >
  Identify threats using STRIDE methodology, assess risk,
  and prioritize mitigations for a system or component.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - system-design
reasoning_mode: plan-execute
---

# Threat Modeling

> _"Think like an attacker to build like a defender."_

## Context

Invoked at design time for new features, or periodically for existing systems.
Uses the STRIDE framework to systematically identify and categorize threats.

---

## Micro-Skills

### 1. Asset Identification ⚡ (Power Mode)

**Steps:**

1. List all data assets (PII, credentials, financial data, auth tokens).
2. List all entry points (API endpoints, message queues, file uploads).
3. List all trust boundaries (external → internal, service → service).
4. Draw a Data Flow Diagram (Mermaid) showing assets and trust boundaries.

### 2. STRIDE Analysis ⚡ (Power Mode)

**Steps:**

For each entry point, evaluate:

| Threat              | Question                                        |
|---------------------|-------------------------------------------------|
| **S**poofing        | Can an attacker impersonate a legitimate user?  |
| **T**ampering       | Can data be modified in transit or at rest?      |
| **R**epudiation     | Can an action be denied without audit trail?     |
| **I**nfo Disclosure | Can sensitive data leak via logs/errors/timing?  |
| **D**enial of Service | Can the system be overwhelmed or crashed?     |
| **E**levation       | Can a user escalate privileges?                  |

### 3. Risk Assessment ⚡ (Power Mode)

**Steps:**

1. For each identified threat, assess:
   - **Likelihood:** Low / Medium / High
   - **Impact:** Low / Medium / High / Critical
2. Calculate risk score: `Likelihood x Impact`.
3. Prioritize: Critical → High → Medium → Low.

### 4. Mitigation Planning ⚡ (Power Mode)

**Steps:**

1. For each high/critical threat, propose a mitigation:
   - Input validation, output encoding.
   - Authentication, authorization checks.
   - Rate limiting, request size limits.
   - Encryption (at rest, in transit).
   - Audit logging.
2. Map mitigations to implementation tasks.
3. Create tracking issues/tickets.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `threat_model`   | `object`   | STRIDE threat catalog                    |
| `dfd`            | `string`   | Data Flow Diagram (Mermaid)              |
| `risk_matrix`    | `object`   | Prioritized risk assessment              |
| `mitigations`    | `object[]` | Proposed mitigations per threat          |
