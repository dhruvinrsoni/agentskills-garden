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
