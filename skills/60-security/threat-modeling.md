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

---

## Scope

### In Scope

- Identifying data assets, entry points, and trust boundaries for a system or component
- Producing Data Flow Diagrams (DFDs) in Mermaid notation
- Performing STRIDE analysis against every identified entry point
- Assessing risk (likelihood × impact) for each identified threat
- Prioritizing threats into Critical / High / Medium / Low tiers
- Proposing mitigations mapped to specific implementation tasks
- Tracking threat-model decisions and rationale in ADRs (via `adr-management`)
- Re-evaluating existing threat models when architecture changes are introduced

### Out of Scope

- Implementing mitigations in code (handled by `auth-implementation`, `secure-coding-review`, etc.)
- Penetration testing or dynamic/runtime vulnerability scanning
- Compliance mapping to specific regulatory frameworks (PCI-DSS, HIPAA, SOC 2)
- Network infrastructure design (firewalls, VPNs, DNS configuration)
- Physical security or social engineering threat analysis
- Vendor or third-party risk assessment beyond dependency-level CVEs

---

## Guardrails

- Never omit a STRIDE category during analysis — all six must be evaluated for every entry point.
- Never classify a threat as Low risk without documenting the likelihood and impact justification.
- Always produce a Data Flow Diagram before beginning STRIDE analysis; do not assess threats without a visual model.
- Never propose a mitigation that introduces a new, unassessed threat (e.g., adding logging that exposes PII).
- Always re-run threat assessment when trust boundaries, entry points, or data assets change.
- Never delete or overwrite a prior threat model; version and archive superseded models.
- Preserve traceability — every mitigation must link back to the specific threat it addresses.
- Never assume internal services are trusted; evaluate east-west (service-to-service) traffic explicitly.

---

## Ask-When-Ambiguous

### Triggers

- The system boundary is unclear (which components are in scope for modeling)
- Trust boundary placement is ambiguous (e.g., is an internal microservice trusted or untrusted?)
- Data classification is unspecified (what constitutes PII, sensitive, or public data)
- The deployment environment is unknown (cloud, on-prem, hybrid) and affects threat surface
- An entry point handles both authenticated and unauthenticated traffic and the distinction is unclear
- Trade-offs exist between security mitigations and performance/usability

### Question Templates

1. "What is the system boundary for this threat model — which services and data stores are in scope?"
2. "How is `<internal-service>` accessed — is it behind a VPN/service mesh, or reachable from the public internet?"
3. "What data classification applies to `<data-asset>` — PII, financial, internal-only, or public?"
4. "Is `<entry-point>` authenticated, unauthenticated, or mixed? What trust level does the caller have?"
5. "Where is this system deployed — cloud (which provider?), on-premises, or hybrid?"
6. "For `<threat>`, the mitigation impacts performance by `<estimate>`. Is that trade-off acceptable?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| New feature adds an external-facing API endpoint | Trigger full STRIDE analysis on the new entry point |
| Architecture change moves a service across a trust boundary | Re-assess all threats involving that service |
| Threat has High likelihood and Critical impact | Classify as Critical; mitigation is a release blocker |
| Threat has Low likelihood and Low impact | Classify as Low; document and track in backlog |
| Mitigation requires significant architectural change | Escalate to system design review; document trade-offs in ADR |
| Multiple mitigations address the same threat | Prefer defense-in-depth — implement layered controls when cost permits |
| Data Flow Diagram is stale (> 1 quarter old or post-architecture change) | Regenerate DFD before re-assessing threats |
| Internal service communicates over unencrypted channel | Treat as Tampering + Information Disclosure threat; recommend mTLS |
| Third-party dependency introduces a new trust boundary | Add dependency as an entry point; assess with STRIDE |

---

## Success Criteria

- [ ] All data assets, entry points, and trust boundaries are identified and documented
- [ ] A Data Flow Diagram (Mermaid) is produced covering the full system scope
- [ ] Every entry point is evaluated against all six STRIDE categories
- [ ] Each threat has a risk score (likelihood × impact) and a priority classification
- [ ] All Critical and High threats have at least one proposed mitigation with an implementation task
- [ ] Mitigations are traceable — each links to the specific threat(s) it addresses
- [ ] The threat model is versioned and the rationale for risk-acceptance decisions is documented
- [ ] Threat model findings are actionable — mapped to tickets, ADRs, or implementation skills

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Incomplete asset inventory | Critical data or entry point missing from model; threats go unidentified | Cross-reference system-design docs, API specs, and deployment configs to ensure full coverage |
| STRIDE category skipped | One of the six categories not evaluated; blindspot in threat coverage | Use a checklist per entry point; verify all six rows are populated before finalizing |
| Stale threat model | Architecture has changed but the model reflects the old design | Tie threat model reviews to architecture change triggers; re-evaluate quarterly at minimum |
| Overly optimistic risk rating | Threat classified as Low that is subsequently exploited | Require documented justification for Low ratings; peer-review risk assessments |
| Mitigation creates new threat | Security control introduces a new attack surface (e.g., logging PII) | Assess each proposed mitigation for secondary threat introduction before implementation |
| Trust boundary misplacement | Internal service treated as trusted when it is externally reachable | Validate trust boundaries against actual network topology and deployment configuration |
| Threat model too abstract to action | Findings are vague and cannot be mapped to implementation tasks | Require each mitigation to reference a concrete implementation approach and target component |

---

## Audit Log

- `[timestamp]` model-created: Created threat model v`<version>` for `<system/component>` with `<n>` entry points and `<m>` trust boundaries
- `[timestamp]` dfd-generated: Produced Data Flow Diagram at `<file-path>` covering `<scope-description>`
- `[timestamp]` stride-completed: STRIDE analysis of `<entry-point>` — identified `<n>` threats (`<critical>`C / `<high>`H / `<medium>`M / `<low>`L)
- `[timestamp]` risk-assessed: Threat `<threat-id>` rated as `<likelihood>` likelihood × `<impact>` impact = `<priority>` priority
- `[timestamp]` mitigation-proposed: Proposed `<mitigation-summary>` for threat `<threat-id>` — mapped to task `<task-ref>`
- `[timestamp]` risk-accepted: Accepted residual risk for threat `<threat-id>` — reason: `<justification>`, reassess by `<date>`
- `[timestamp]` model-updated: Updated threat model from v`<old>` to v`<new>` due to `<trigger>` — `<n>` threats added, `<m>` re-assessed
