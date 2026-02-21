---
name: system-design
description: >
  High-level system architecture: component diagrams, data flow,
  scalability trade-offs, and technology selection.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - requirements-elicitation
reasoning_mode: plan-execute
---

# System Design

> _"Architect for the load you'll have, not the load you dream of."_

## Context

Invoked for greenfield projects or major re-architecture efforts. Produces
component diagrams, identifies integration points, and documents trade-offs.

---

## Micro-Skills

### 1. Component Decomposition ⚡ (Power Mode)

**Steps:**

1. Identify bounded contexts from the domain model.
2. Map each context to a service/module.
3. Define interfaces between components (sync REST, async events, shared DB).
4. Generate a Mermaid component diagram.

### 2. Data Flow Analysis ⚡ (Power Mode)

**Steps:**

1. Trace the lifecycle of key entities (create → read → update → delete).
2. Identify data ownership (which service is the source of truth).
3. Map read vs write paths (CQRS if needed).
4. Generate a Mermaid sequence or flowchart diagram.

### 3. Trade-off Analysis ⚡ (Power Mode)

**Steps:**

1. For each design decision, list at least 2 alternatives.
2. Evaluate against: complexity, latency, cost, team expertise.
3. Use a decision matrix (weighted scoring).
4. Record the decision in an ADR (invoke `adr-management`).

### 4. Scalability Planning ⚡ (Power Mode)

**Steps:**

1. Estimate load: requests/sec, data growth/month, concurrent users.
2. Identify bottlenecks: CPU-bound, I/O-bound, memory-bound.
3. Recommend scaling strategy: horizontal (stateless) or vertical.
4. Identify single points of failure and propose redundancy.

---

## Outputs

| Field              | Type     | Description                              |
|--------------------|----------|------------------------------------------|
| `component_diagram`| `string` | Mermaid diagram of system components     |
| `data_flow`        | `string` | Mermaid sequence diagram                 |
| `trade_offs`       | `object` | Decision matrix with scores              |
| `adrs`             | `string[]`| Generated ADR file paths                |

---

## Edge Cases

- "Just pick the best option" — Present the matrix anyway (Dharma: no silent
  decisions). Recommend the highest-scoring option explicitly.
- Microservices vs monolith debate — Default to modular monolith; justify
  microservices only if deployment independence is a proven requirement.

---

## Scope

### In Scope

- High-level system architecture: identifying components, services, and their boundaries.
- Component and sequence diagrams (Mermaid) showing interactions and data flow.
- Trade-off analysis with weighted decision matrices for technology and pattern choices.
- Scalability planning: load estimation, bottleneck identification, and scaling strategy.
- Identifying single points of failure and recommending redundancy.
- Recording architectural decisions via the `adr-management` skill.

### Out of Scope

- Detailed API contract design for individual endpoints (use `api-contract-design` skill).
- Database schema design, normalization, or migration planning (use `database-design` skill).
- Infrastructure provisioning, Terraform/IaC, or cloud console configuration (use `terraform-iac` skill).
- Writing application code, service implementations, or business logic (use `code-generation` skill).
- Operational concerns: monitoring dashboards, alerting rules, incident runbooks (use `monitoring-setup` skill).

---

## Guardrails

- Always produce at least one Mermaid diagram (component or sequence) per design session.
- Never make a technology or pattern choice without documenting at least 2 alternatives and their trade-offs.
- Record every significant architectural decision as an ADR via the `adr-management` skill.
- Default to a modular monolith unless the user provides concrete evidence for microservices (independent deployment, team autonomy, polyglot requirements).
- Do not over-architect: design for current known requirements plus one reasonable growth horizon, not speculative future scale.
- Clearly label assumptions about load, data volume, and team size — do not present estimates as facts.
- Ensure every component in the diagram has a defined owner (service/team) and a clear interface contract.

---

## Ask-When-Ambiguous

### Triggers

- The user has not specified expected load, data volume, or concurrent user count.
- The boundary between two components is unclear (could be one service or two).
- The user requests "microservices" without stating a concrete reason for distributed architecture.
- Communication pattern between components is unspecified (sync HTTP vs async messaging vs shared database).
- Non-functional requirements (latency SLA, uptime target, compliance) are missing.

### Question Templates

- "What are the expected load characteristics — approximate requests/sec, data growth/month, and concurrent users?"
- "Should `{component_a}` and `{component_b}` be separate services with a network boundary, or modules within a single deployable unit?"
- "You've mentioned microservices. What specific requirement drives the need for independent deployment — team autonomy, scaling heterogeneity, or something else?"
- "How should `{service_a}` communicate with `{service_b}` — synchronous REST/gRPC calls, asynchronous events via a message broker, or a shared database?"
- "Are there any non-functional requirements I should factor in — latency SLAs, uptime targets (e.g., 99.9%), or regulatory/compliance constraints?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Greenfield project with a small team (≤5 engineers) | Default to modular monolith with clear module boundaries; avoid distributed complexity |
| Multiple teams need to deploy independently on different cadences | Consider microservices with well-defined API contracts between service boundaries |
| High read volume but infrequent writes | Recommend CQRS with a read-optimized view; document the trade-off in an ADR |
| Single component identified as a bottleneck | Isolate it as a separately scalable service; keep everything else monolithic |
| User cannot provide load estimates | Design for moderate scale with horizontal scaling path; document assumptions explicitly |
| Two alternatives score equally in the decision matrix | Present both to the user with a clear recommendation and rationale; do not choose silently |
| System requires high availability (≥99.9% uptime) | Identify all single points of failure; recommend redundancy, health checks, and failover mechanisms |

---

## Success Criteria

- [ ] Component diagram clearly shows all services/modules and their communication patterns.
- [ ] Data flow diagram traces at least the primary read and write paths for key entities.
- [ ] Trade-off analysis includes a decision matrix with at least 2 alternatives per significant choice.
- [ ] All architectural decisions are recorded as ADRs with status, context, and consequences.
- [ ] Scalability plan includes load estimates, identified bottlenecks, and a scaling strategy.
- [ ] Single points of failure are identified and mitigation strategies are documented.
- [ ] Assumptions about load, team size, and data volume are explicitly stated, not implicit.
- [ ] The design is validated against stated non-functional requirements (latency, uptime, compliance).

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Over-engineering for speculative scale | Complex distributed architecture for an app with 100 users | Require concrete load evidence before introducing microservices, message brokers, or CQRS |
| Missing component boundaries | Monolith with tangled dependencies that cannot be split later | Define module interfaces upfront even in a monolith; enforce boundaries via package/namespace structure |
| Silent technology choice | A framework or database is used without documented rationale | Mandate a decision matrix and ADR for every technology selection; block designs with undocumented choices |
| Data ownership ambiguity | Two services write to the same entity, causing consistency issues | Assign a single source-of-truth service per entity during Data Flow Analysis; document ownership in the component diagram |
| Diagrams not updated after design changes | Architecture diagrams diverge from the actual system | Re-generate diagrams as part of every design revision; store diagrams as code (Mermaid) next to the ADRs |
| Non-functional requirements ignored | System meets functional needs but fails latency SLA or uptime target | Explicitly ask for NFRs at the start of every design session; include them as evaluation criteria in the decision matrix |

---

## Audit Log

- `[{timestamp}] DESIGN_SESSION_STARTED — Project: {name} | Trigger: {greenfield|re-architecture|feature_addition}`
- `[{timestamp}] COMPONENT_DIAGRAM_GENERATED — Components: [{names}] | Communication: [{patterns}] | File: {filename}`
- `[{timestamp}] DATA_FLOW_TRACED — Entity: {entity} | Path: {create→read→update→delete} | Owner: {service}`
- `[{timestamp}] TRADE_OFF_ANALYZED — Decision: "{title}" | Alternatives: [{options}] | Winner: {chosen} | Score: {score}`
- `[{timestamp}] ADR_CREATED — Via adr-management | ADR-{number}: "{title}"`
- `[{timestamp}] SCALABILITY_PLAN_PRODUCED — Est. load: {rps} req/s | Bottlenecks: [{items}] | Strategy: {horizontal|vertical}`
- `[{timestamp}] SPOF_IDENTIFIED — Component: {name} | Mitigation: {redundancy_strategy}`
