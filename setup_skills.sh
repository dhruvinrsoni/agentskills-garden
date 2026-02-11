#!/usr/bin/env bash
# ============================================================================
# Agent Skills Garden — Mega Installer (Bash)
# Run: chmod +x setup_skills.sh && ./setup_skills.sh
# ============================================================================
set -euo pipefail

echo "🌱 Creating Agent Skills Garden (Full Suite)..."

# --- Directories -----------------------------------------------------------
mkdir -p skills/00-foundation
mkdir -p skills/10-discovery
mkdir -p skills/20-architecture
mkdir -p skills/30-implementation
mkdir -p skills/40-quality
mkdir -p skills/50-performance
mkdir -p skills/60-security
mkdir -p skills/70-devops
mkdir -p skills/80-docs
mkdir -p skills/90-maintenance
mkdir -p templates

# ===========================================================================
#  00-FOUNDATION
# ===========================================================================

# --- constitution.md -------------------------------------------------------
cat << 'SKILLEOF' > skills/00-foundation/constitution.md
---
name: constitution
description: >
  The foundational constitution of the Agent Skills Garden.
  Every skill, every action, every line of code must honour these principles.
version: "1.0.0"
dependencies: []
reasoning_mode: linear
---

# Constitution — The Three Pillars

> _"Before you act, check the Constitution."_

## Principle 1 — Satya (Truth / Determinism)

Code changes **must** be truthful to the stated intent. No hallucinations.

- If a micro-skill requires high precision (refactoring, logic changes), it
  **MUST** use a **Plan → Execute → Verify** loop.
- Every output must be reproducible given the same inputs.
- Never invent facts about frameworks, APIs, or language features.

## Principle 2 — Dharma (Right Action / Safety)

**Ask-First Policy.** If certainty < 100 %, pause and query the user.

- Never assume the user's intent when the request is ambiguous.
- Always present options with trade-offs instead of choosing silently.
- Prefer the smallest change that achieves the goal (Principle of Least
  Surprise).

## Principle 3 — Ahimsa (Non-Destruction)

**Preview First.** Never overwrite without a fallback.

- Always emit a **Unified Diff** before applying changes.
- The user must confirm destructive operations (file deletion, schema
  migration, production deploy).
- Maintain reversibility: every change should be revertible within one step.

---

## Cognitive Modes

### Eco Mode 🌿

For low-risk tasks: formatting, docs, small fixes.
Linear execution, 1-3 steps, no deep reasoning required.

### Power Mode ⚡

For high-risk tasks: refactoring, logic changes, architecture decisions.
Plan-Execute-Verify loops with 4-step reasoning (Deductive, Inductive,
Abductive, Analogical).

---

## Update Mechanism — Constitutional Amendments

To amend this constitution:

1. Create a skill named `constitutional-amendment` under
   `skills/00-foundation/`.
2. The skill **must** include:
   - `rationale`: Why the amendment is necessary.
   - `impact_analysis`: Which existing skills are affected.
   - `vote`: Requires explicit user approval (no auto-merge).
3. Append the amendment to this file under a new `## Amendment N` heading.
4. Bump the `version` in the frontmatter.

---

_This constitution is loaded first. All other skills inherit these constraints._
SKILLEOF
echo "  ✔ 00-foundation/constitution.md"

# --- scratchpad.md ---------------------------------------------------------
cat << 'SKILLEOF' > skills/00-foundation/scratchpad.md
---
title: "Scratchpad"
description: "Instructions for 'Internal Monologue' (Eco vs. Power reasoning)."
---

# Scratchpad

## Internal Monologue
- Use Eco Mode for low-risk tasks.
- Use Power Mode for high-risk tasks.
EOF

cat << 'EOF' > skills/00-foundation/auditor.md
---
title: "Auditor"
description: "Validates that other skills followed the Constitution."
---

# Auditor

## Purpose
- Ensure all skills adhere to the principles of Satya, Dharma, and Ahimsa.
EOF

cat << 'EOF' > skills/00-foundation/librarian.md
---
title: "Librarian"
description: "Fuzzy search to find skills (e.g., 'fix bug' -> loads `refactoring.md` or `cleanup.md`)."
---

# Librarian

## Purpose
- Provide a search mechanism to locate relevant skills.
EOF

# Repeat similar blocks for all other SKILL.md files in the Skill Manifest

# Create the registry.yaml file
cat << 'EOF' > skills/registry.yaml
skills:
  - foundation:
      - constitution.md
      - scratchpad.md
      - auditor.md
      - librarian.md
  - discovery:
      - requirements-elicitation.md
      - domain-modeling.md
  - architecture:
      - adr-management.md
      - api-contract-design.md
      - database-design.md
      - system-design.md
  - implementation:
      - cleanup.md
      - api-implementation.md
      - data-access.md
      - refactoring-suite.md
      - error-handling.md
  - quality:
      - test-strategy.md
      - unit-testing.md
      - integration-testing.md
      - mutation-testing.md
  - performance:
      - profiling-analysis.md
      - caching-strategy.md
      - db-tuning.md
  - security:
      - threat-modeling.md
      - secure-coding-review.md
      - auth-implementation.md
      - dependency-scanning.md
  - devops:
      - ci-pipeline.md
      - docker-containerization.md
      - kubernetes-helm.md
      - terraform-iac.md
  - docs:
      - openapi-specs.md
      - readme-generation.md
      - release-notes.md
  - maintenance:
      - incident-response.md
      - legacy-upgrade.md
EOF

# Print completion message
echo "Skills directory and files have been created successfully."
SKILLEOF
echo "  ✔ 00-foundation/scratchpad.md"

# --- auditor.md ------------------------------------------------------------
cat << 'SKILLEOF' > skills/00-foundation/auditor.md
---
title: "Auditor"
description: "Validates that other skills followed the Constitution."
---

# Auditor

## Purpose
- Ensure all skills adhere to the principles of Satya, Dharma, and Ahimsa.
EOF

cat << 'EOF' > skills/00-foundation/librarian.md
---
title: "Librarian"
description: "Fuzzy search to find skills (e.g., 'fix bug' -> loads `refactoring.md` or `cleanup.md`)."
---

# Librarian

## Purpose
- Provide a search mechanism to locate relevant skills.
EOF

# Repeat similar blocks for all other SKILL.md files in the Skill Manifest

# Create the registry.yaml file
cat << 'EOF' > skills/registry.yaml
skills:
  - foundation:
      - constitution.md
      - scratchpad.md
      - auditor.md
      - librarian.md
  - discovery:
      - requirements-elicitation.md
      - domain-modeling.md
  - architecture:
      - adr-management.md
      - api-contract-design.md
      - database-design.md
      - system-design.md
  - implementation:
      - cleanup.md
      - api-implementation.md
      - data-access.md
      - refactoring-suite.md
      - error-handling.md
  - quality:
      - test-strategy.md
      - unit-testing.md
      - integration-testing.md
      - mutation-testing.md
  - performance:
      - profiling-analysis.md
      - caching-strategy.md
      - db-tuning.md
  - security:
      - threat-modeling.md
      - secure-coding-review.md
      - auth-implementation.md
      - dependency-scanning.md
  - devops:
      - ci-pipeline.md
      - docker-containerization.md
      - kubernetes-helm.md
      - terraform-iac.md
  - docs:
      - openapi-specs.md
      - readme-generation.md
      - release-notes.md
  - maintenance:
      - incident-response.md
      - legacy-upgrade.md
EOF

# Print completion message
echo "Skills directory and files have been created successfully."
SKILLEOF
echo "  ✔ 00-foundation/auditor.md"

# --- librarian.md ----------------------------------------------------------
cat << 'SKILLEOF' > skills/00-foundation/librarian.md
---
title: "Librarian"
description: "Fuzzy search to find skills (e.g., 'fix bug' -> loads `refactoring.md` or `cleanup.md`)."
---

# Librarian

## Purpose
- Provide a search mechanism to locate relevant skills.
EOF

cat << 'EOF' > skills/00-foundation/auditor.md
---
title: "Auditor"
description: "Validates that other skills followed the Constitution."
---

# Auditor

## Purpose
- Ensure all skills adhere to the principles of Satya, Dharma, and Ahimsa.
EOF

# Repeat similar blocks for all other SKILL.md files in the Skill Manifest

# Create the registry.yaml file
cat << 'EOF' > skills/registry.yaml
skills:
  - foundation:
      - constitution.md
      - scratchpad.md
      - auditor.md
      - librarian.md
  - discovery:
      - requirements-elicitation.md
      - domain-modeling.md
  - architecture:
      - adr-management.md
      - api-contract-design.md
      - database-design.md
      - system-design.md
  - implementation:
      - cleanup.md
      - api-implementation.md
      - data-access.md
      - refactoring-suite.md
      - error-handling.md
  - quality:
      - test-strategy.md
      - unit-testing.md
      - integration-testing.md
      - mutation-testing.md
  - performance:
      - profiling-analysis.md
      - caching-strategy.md
      - db-tuning.md
  - security:
      - threat-modeling.md
      - secure-coding-review.md
      - auth-implementation.md
      - dependency-scanning.md
  - devops:
      - ci-pipeline.md
      - docker-containerization.md
      - kubernetes-helm.md
      - terraform-iac.md
  - docs:
      - openapi-specs.md
      - readme-generation.md
      - release-notes.md
  - maintenance:
      - incident-response.md
      - legacy-upgrade.md
EOF

# Print completion message
echo "Skills directory and files have been created successfully."
SKILLEOF
echo "  ✔ 00-foundation/librarian.md"

# ===========================================================================
#  10-DISCOVERY
# ===========================================================================

# --- requirements-elicitation.md -------------------------------------------
cat << 'SKILLEOF' > skills/10-discovery/requirements-elicitation.md
---
name: requirements-elicitation
description: >
  Interview the user to extract goals, constraints, success metrics,
  and acceptance criteria before any code is written.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: plan-execute
---

# Requirements Elicitation

> _"Define the problem before solving it."_

## Context

Invoked at the **start** of any greenfield feature or project. Prevents
wasted effort by ensuring alignment between user expectations and the
agent's understanding.

---

## Micro-Skills

### 1. Goal Extraction ⚡ (Power Mode)

**Steps:**

1. Ask the user: "What problem are you trying to solve?"
2. Restate the goal in your own words and ask for confirmation.
3. Identify the **primary actor** (who benefits) and **scope boundary**
   (what is explicitly out of scope).

### 2. Constraint Discovery ⚡ (Power Mode)

**Steps:**

1. Ask about **technical constraints**: language, framework, deployment target.
2. Ask about **business constraints**: timeline, budget, compliance (GDPR, SOC2).
3. Ask about **non-functional requirements**: latency, throughput, uptime SLA.

### 3. Success Metrics ⚡ (Power Mode)

**Steps:**

1. Ask: "How will you know this is done?"
2. Convert answers into **measurable acceptance criteria**.
3. Format as a checklist the user can sign off on.

### 4. Assumptions Log 🌿 (Eco Mode)

**Steps:**

1. List all assumptions made during the conversation.
2. Ask the user to confirm or correct each one.
3. Record confirmed assumptions in a `assumptions.md` file.

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `goals`            | `string[]` | List of stated goals                     |
| `constraints`      | `object`   | Technical, business, non-functional      |
| `acceptance`       | `string[]` | Measurable success criteria              |
| `assumptions`      | `string[]` | Confirmed assumptions                    |
| `out_of_scope`     | `string[]` | Explicitly excluded items                |

---

## Edge Cases

- User says "just build it" — Invoke Dharma: present a minimal question set
  (3 questions max) before proceeding.
- Conflicting requirements — Flag the conflict and ask user to prioritize.
SKILLEOF
echo "  ✔ 10-discovery/requirements-elicitation.md"

# --- domain-modeling.md ----------------------------------------------------
cat << 'SKILLEOF' > skills/10-discovery/domain-modeling.md
---
name: domain-modeling
description: >
  Create and maintain a domain glossary with entities, relationships,
  and Protected Terms that must never be renamed.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - requirements-elicitation
reasoning_mode: plan-execute
---

# Domain Modeling

> _"Name things once. Name them right."_

## Context

Invoked after requirements elicitation to establish a shared vocabulary.
The domain model becomes the **single source of truth** for naming
conventions throughout the project.

---

## Micro-Skills

### 1. Entity Extraction ⚡ (Power Mode)

**Steps:**

1. Parse requirements and conversation transcripts for **nouns** (entities)
   and **verbs** (actions/events).
2. Group related nouns into **aggregates**.
3. Define each entity with: name, description, attributes, relationships.

### 2. Glossary Generation 🌿 (Eco Mode)

**Steps:**

1. Create `glossary.md` in the project root.
2. Format as a table: Term | Definition | Aliases | Protected.
3. Mark **Protected Terms** — identifiers that must never be renamed by
   any skill (especially `cleanup → safe-renaming`).

### 3. Relationship Mapping ⚡ (Power Mode)

**Steps:**

1. Identify relationships: has-one, has-many, belongs-to, many-to-many.
2. Draw a simple text-based ER diagram using Mermaid syntax.
3. Validate cardinality with the user.

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `glossary`         | `markdown` | The domain glossary file                 |
| `er_diagram`       | `string`   | Mermaid ER diagram                       |
| `protected_terms`  | `string[]` | Terms that must never be renamed         |

---

## Edge Cases

- Ambiguous terms (e.g., "order" = purchase order or sort order) — Ask user
  to disambiguate. Record both meanings with context tags.
- Domain terms that conflict with language keywords — Prefix with domain
  abbreviation (e.g., `OrderStatus` not `Status`).
SKILLEOF
echo "  ✔ 10-discovery/domain-modeling.md"

# ===========================================================================
#  20-ARCHITECTURE
# ===========================================================================

# --- adr-management.md -----------------------------------------------------
cat << 'SKILLEOF' > skills/20-architecture/adr-management.md
---
name: adr-management
description: >
  Create, index, and maintain Architecture Decision Records (ADRs)
  using the Michael Nygard template.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# ADR Management

> _"Record the why, not just the what."_

## Context

Invoked when an architectural decision is made. ADRs prevent knowledge loss
and make trade-offs explicit for future maintainers.

---

## Micro-Skills

### 1. Create ADR 🌿 (Eco Mode)

**Steps:**

1. Create `docs/adr/` directory if it does not exist.
2. Determine the next sequential number (e.g., `ADR-0005`).
3. Generate the ADR from the Nygard template:

```markdown
# ADR-NNNN: <Title>

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-XXXX

## Context
<What is the issue that we're seeing that motivates this decision?>

## Decision
<What is the change that we're proposing and/or doing?>

## Consequences
<What becomes easier or more difficult because of this change?>
```

4. Add entry to `docs/adr/index.md`.

### 2. Supersede ADR 🌿 (Eco Mode)

**Steps:**

1. Update the old ADR status to `Superseded by ADR-XXXX`.
2. In the new ADR, reference the old one in the Context section.
3. Update `docs/adr/index.md`.

### 3. Search ADRs 🌿 (Eco Mode)

**Steps:**

1. Accept a keyword or topic from the user.
2. Scan all ADR files for matches.
3. Return a ranked list of relevant ADRs.

---

## Edge Cases

- Conflicting ADRs — Flag and ask user which takes precedence.
- ADR references deleted code — Mark as `Deprecated` with a note.
SKILLEOF
echo "  ✔ 20-architecture/adr-management.md"

# --- api-contract-design.md ------------------------------------------------
cat << 'SKILLEOF' > skills/20-architecture/api-contract-design.md
---
name: api-contract-design
description: >
  Design REST or gRPC API contracts (OpenAPI/Protobuf) before any
  implementation code is written. Contract-first development.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - domain-modeling
reasoning_mode: plan-execute
---

# API Contract Design

> _"Design the contract. Then build to it."_

## Context

Invoked when a new API endpoint or service boundary is being created.
The contract is the **source of truth** — implementation must conform to it,
not the other way around.

---

## Micro-Skills

### 1. Resource Modeling ⚡ (Power Mode)

**Steps:**

1. Identify resources from the domain model (nouns become resources).
2. Define URL structure following REST conventions:
   - `GET /resources` — list
   - `GET /resources/{id}` — detail
   - `POST /resources` — create
   - `PUT /resources/{id}` — full update
   - `PATCH /resources/{id}` — partial update
   - `DELETE /resources/{id}` — remove
3. Define query parameters for filtering, pagination, sorting.

### 2. Schema Definition ⚡ (Power Mode)

**Steps:**

1. Define request/response schemas using JSON Schema or Protobuf.
2. Include all required fields, optional fields, and validation constraints.
3. Define error response schemas (RFC 7807 Problem Details).

### 3. OpenAPI Spec Generation ⚡ (Power Mode)

**Steps:**

1. Generate an `openapi.yaml` file (OpenAPI 3.1).
2. Include: info, servers, paths, components/schemas, security schemes.
3. Add examples for every endpoint.
4. Validate the spec using a linter.

### 4. Versioning Strategy 🌿 (Eco Mode)

**Steps:**

1. Ask user: URL path versioning (`/v1/`) or header versioning.
2. Document the chosen strategy in the spec and an ADR.
3. Set up deprecation headers for future use.

---

## Outputs

| Field          | Type     | Description                              |
|----------------|----------|------------------------------------------|
| `openapi_spec` | `yaml`   | Complete OpenAPI 3.1 specification       |
| `schemas`      | `object` | JSON Schema definitions                  |
| `adr`          | `string` | ADR for versioning/design decisions      |

---

## Edge Cases

- User wants GraphQL instead of REST — Switch to SDL-first design.
- Circular references in schemas — Break cycle with `$ref` and document.
SKILLEOF
echo "  ✔ 20-architecture/api-contract-design.md"

# --- database-design.md ----------------------------------------------------
cat << 'SKILLEOF' > skills/20-architecture/database-design.md
---
name: database-design
description: >
  Schema design, normalization analysis, migration planning, and
  index strategy for relational and NoSQL databases.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - domain-modeling
reasoning_mode: plan-execute
---

# Database Design

> _"Your schema is your data contract with the future."_

## Context

Invoked when designing a new database schema or modifying an existing one.
Covers relational (PostgreSQL, MySQL) and document (MongoDB, DynamoDB)
databases.

---

## Micro-Skills

### 1. Schema Design ⚡ (Power Mode)

**Steps:**

1. Map domain entities to tables/collections.
2. Define columns: name, type, nullable, default, constraints.
3. Define primary keys (prefer UUIDs or ULID for distributed systems).
4. Define foreign keys and cascade rules.
5. Apply normalization (target 3NF, denormalize only with justification).

### 2. Migration Planning ⚡ (Power Mode)

**Steps:**

1. Generate migration files (SQL or ORM-specific format).
2. Ensure migrations are **idempotent** and **reversible**.
3. Include both `up` and `down` scripts.
4. For destructive changes (column drop, type change):
   - Require explicit user approval (Ahimsa).
   - Suggest a multi-step deployment (add new → migrate data → drop old).

### 3. Index Strategy ⚡ (Power Mode)

**Steps:**

1. Analyze expected query patterns.
2. Suggest indexes: B-tree for equality/range, GIN for full-text/JSONB.
3. Warn about over-indexing (write penalty) and missing indexes (slow reads).
4. Document index rationale.

### 4. Seed Data 🌿 (Eco Mode)

**Steps:**

1. Generate seed data scripts for development and testing.
2. Include realistic but anonymized sample data.
3. Make seeds idempotent (upsert pattern).

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `schema_ddl`    | `string`   | CREATE TABLE statements                  |
| `migrations`    | `string[]` | Ordered migration files                  |
| `index_plan`    | `object`   | Index recommendations with rationale     |
| `er_diagram`    | `string`   | Mermaid ER diagram                       |

---

## Edge Cases

- Schema change on a table with millions of rows — Recommend online DDL
  tools (pt-online-schema-change, pg_repack).
- Circular foreign keys — Break with nullable FK + application-level checks.
SKILLEOF
echo "  ✔ 20-architecture/database-design.md"

# --- system-design.md ------------------------------------------------------
cat << 'SKILLEOF' > skills/20-architecture/system-design.md
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
SKILLEOF
echo "  ✔ 20-architecture/system-design.md"

# ===========================================================================
#  30-IMPLEMENTATION
# ===========================================================================

# --- cleanup.md ------------------------------------------------------------
cat << 'SKILLEOF' > skills/30-implementation/cleanup.md
---
name: cleanup
description: >
  Remove noise, enforce formatting, and safely rename identifiers.
  A mixed-mode skill: cosmetic fixes run in Eco, renaming runs in Power.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: mixed
---

# Cleanup

> _"Leave the codebase better than you found it."_

## Context

Invoked when the user wants to clean up a file or module — remove dead code,
fix formatting, or rename unclear identifiers. The skill automatically selects
Eco or Power mode per micro-skill.

---

## Micro-Skills

### 1. Comment Policy 🌿 (Eco Mode)

**Goal:** Remove noise while preserving intent markers.

**Rules:**

- **Keep:** `TODO`, `FIXME`, `HACK`, `NOTE`, `WARN` — these carry intent.
- **Remove:** Commented-out code blocks (>= 2 consecutive lines of code in
  comments).
- **Preserve:** License headers, JSDoc/docstrings, and `@param`/`@returns`
  annotations.

**Steps:**

1. Scan file for comment blocks.
2. Classify each block: `intent-marker | dead-code | documentation`.
3. Remove `dead-code` blocks.
4. Emit diff for user review.

---

### 2. Formatting 🌿 (Eco Mode)

**Goal:** Apply project-specific linter/formatter.

**Steps:**

1. Detect project formatter from config files:
   - `.prettierrc`, `.eslintrc` → Prettier / ESLint
   - `pyproject.toml`, `setup.cfg` → Black / Ruff
   - `.clang-format` → clang-format
2. Run the detected formatter.
3. If no formatter config found, **ask the user** (Dharma principle).
4. Emit diff.

---

### 3. Safe Renaming ⚡ (Power Mode)

**Goal:** Rename unclear identifiers without breaking anything.

**Steps:**

1. **Identify Candidates** — single-letter vars (except `i`, `j`, `k`),
   abbreviations not in the domain glossary.
2. **Check Protected Terms** — load `domain-glossary`, skip protected.
3. **Check Visibility** — public/exported identifiers are high-risk,
   require explicit user approval.
4. **Generate Rename Map:**
   ```json
   {
     "old_name": "new_name",
     "scope": "local | module | public",
     "risk": "low | medium | high"
   }
   ```
5. **Produce Diff** — apply renames across all references, present to user.

---

## Inputs

| Parameter         | Type       | Required | Description                    |
|-------------------|------------|----------|--------------------------------|
| `file_path`       | `string`   | yes      | Path to the file to clean up   |
| `micro_skills`    | `string[]` | no       | Subset to run (default: all)   |
| `domain_glossary` | `string`   | no       | Path to domain glossary file   |

## Outputs

| Field        | Type     | Description                              |
|--------------|----------|------------------------------------------|
| `diff`       | `string` | Unified diff of all changes              |
| `rename_map` | `object` | Map of old → new names                   |
| `summary`    | `string` | Human-readable summary of changes        |
SKILLEOF
echo "  ✔ 30-implementation/cleanup.md"

# --- api-implementation.md -------------------------------------------------
cat << 'SKILLEOF' > skills/30-implementation/api-implementation.md
---
name: api-implementation
description: >
  Implement API handlers/controllers based on an existing API contract
  (OpenAPI spec). Generates route handlers, validation, and error handling.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - api-contract-design
  - error-handling
reasoning_mode: plan-execute
---

# API Implementation

> _"The contract is the blueprint. Build exactly to spec."_

## Context

Invoked after `api-contract-design` has produced an OpenAPI spec. This skill
generates the actual route handlers, request validation, response
serialization, and error handling code.

---

## Micro-Skills

### 1. Route Scaffolding ⚡ (Power Mode)

**Steps:**

1. Parse the OpenAPI spec for all paths and operations.
2. Generate one handler function per operation.
3. Wire routes to the framework's router (Express, FastAPI, Gin, etc.).
4. Add middleware: auth, rate-limiting, CORS (as specified in the contract).

### 2. Request Validation ⚡ (Power Mode)

**Steps:**

1. Extract JSON Schema from the OpenAPI `requestBody` definition.
2. Generate validation middleware using the framework's validator:
   - Node.js: `zod`, `joi`, or `ajv`
   - Python: `pydantic`
   - Go: `go-playground/validator`
3. Return 400 with RFC 7807 Problem Details on validation failure.

### 3. Response Serialization 🌿 (Eco Mode)

**Steps:**

1. Define response DTOs/models matching the OpenAPI response schemas.
2. Add serialization (exclude internal fields like `password_hash`).
3. Set correct Content-Type and HTTP status codes.

### 4. Integration Wiring ⚡ (Power Mode)

**Steps:**

1. Inject service/repository dependencies into handlers.
2. Add database transaction boundaries where needed.
3. Add structured logging for each endpoint.
4. Generate a smoke test (one passing request per endpoint).

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `handlers`      | `string[]` | Generated handler file paths             |
| `validators`    | `string[]` | Validation middleware/schema files       |
| `routes`        | `string`   | Router configuration file                |
| `smoke_tests`   | `string`   | Basic integration test file              |

---

## Edge Cases

- No OpenAPI spec exists — Invoke `api-contract-design` first.
- Spec has `x-` extensions for custom behavior — Parse and document, but
  ask user before implementing non-standard features.
SKILLEOF
echo "  ✔ 30-implementation/api-implementation.md"

# --- data-access.md --------------------------------------------------------
cat << 'SKILLEOF' > skills/30-implementation/data-access.md
---
name: data-access
description: >
  Implement data access layers using the Repository pattern.
  Prevents N+1 queries, manages transactions, and optimizes reads.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - database-design
reasoning_mode: plan-execute
---

# Data Access

> _"One query too many is one query too many."_

## Context

Invoked when implementing the persistence layer. Ensures clean separation
between business logic and database operations through the Repository pattern.

---

## Micro-Skills

### 1. Repository Scaffolding ⚡ (Power Mode)

**Steps:**

1. For each domain entity, create a repository interface:
   ```
   interface UserRepository {
     findById(id): User
     findAll(filter, pagination): Page<User>
     create(data): User
     update(id, data): User
     delete(id): void
   }
   ```
2. Implement the interface using the project's ORM/query builder.
3. Add a factory or DI registration for the repository.

### 2. N+1 Prevention ⚡ (Power Mode)

**Steps:**

1. Identify all relationships in the entity.
2. For each `findAll` query, check if related entities are accessed in loops.
3. Add eager loading / `JOIN` / `DataLoader` where N+1 is detected.
4. Add a query counter in test mode to catch regressions.

### 3. Transaction Management ⚡ (Power Mode)

**Steps:**

1. Identify operations that modify multiple entities.
2. Wrap them in a transaction boundary (Unit of Work pattern).
3. Implement retry logic for deadlock/serialization failures.
4. Ensure rollback on any exception within the boundary.

### 4. Query Optimization 🌿 (Eco Mode)

**Steps:**

1. Review generated queries for `SELECT *` — replace with explicit columns.
2. Add `LIMIT` to all paginated queries.
3. Use `EXPLAIN ANALYZE` to verify index usage on critical queries.

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `repositories`  | `string[]` | Generated repository file paths          |
| `migrations`    | `string[]` | Any new migration files                  |
| `query_report`  | `string`   | N+1 detection and optimization report    |

---

## Edge Cases

- Multi-tenant database — Add tenant_id filter to every query automatically.
- Soft deletes — Add `deleted_at` filter to all reads, expose `withTrashed`.
SKILLEOF
echo "  ✔ 30-implementation/data-access.md"

# --- refactoring-suite.md --------------------------------------------------
cat << 'SKILLEOF' > skills/30-implementation/refactoring-suite.md
---
name: refactoring-suite
description: >
  Complex refactoring operations with strict test verification.
  Every refactor follows: Test → Refactor → Test → Revert-on-Fail.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
  - unit-testing
reasoning_mode: plan-execute
---

# Refactoring Suite

> _"Change the structure, preserve the behavior."_

## Context

Invoked for structural code changes that must not alter external behavior.
Every micro-skill follows the **Red-Green-Refactor** safety net.

---

## The Iron Rule

```text
1. Run existing tests → all PASS (baseline)
2. Apply refactoring
3. Run tests again → all PASS (verification)
4. If any test FAILS → REVERT immediately, report failure
```

**No exceptions.** If no tests exist, invoke `unit-testing` first.

---

## Micro-Skills

### 1. Extract Method/Function ⚡ (Power Mode)

**Steps:**

1. Identify the code block to extract (user-selected or heuristic: >15 lines).
2. Determine parameters (variables used but defined outside the block).
3. Determine return values.
4. Create the new function with a descriptive name.
5. Replace the original block with a call to the new function.
6. Run tests.

### 2. Extract Class/Module ⚡ (Power Mode)

**Steps:**

1. Identify a class/module with >1 responsibility (SRP violation).
2. Group related methods and fields into a new class.
3. Move extracted members, update all references.
4. Add the new class as a dependency of the original.
5. Run tests.

### 3. Dependency Inversion ⚡ (Power Mode)

**Steps:**

1. Identify concrete dependencies (direct `new` calls, static method calls).
2. Extract an interface for each dependency.
3. Inject the dependency via constructor or factory.
4. Update all instantiation sites.
5. Run tests.

### 4. Rename Symbol ⚡ (Power Mode)

**Steps:**

1. Check `protected_terms` — abort if the symbol is protected.
2. Find all references across the codebase (not just the file).
3. Generate rename map with scope and risk level.
4. Apply rename, run tests, present diff.

### 5. Inline / Remove Dead Code ⚡ (Power Mode)

**Steps:**

1. Identify unused functions, variables, imports.
2. Verify "unused" by checking all call sites (including dynamic/reflection).
3. Remove dead code, run tests.
4. Present diff with a summary of what was removed and why.

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `diff`          | `string`   | Unified diff of all changes              |
| `test_results`  | `object`   | Before/after test run comparison         |
| `reverted`      | `boolean`  | Whether the refactor was reverted        |

---

## Edge Cases

- Refactoring across module boundaries — Flag as high-risk, require approval.
- Tests exist but don't cover the refactored code — Warn user, suggest adding
  tests before proceeding.
SKILLEOF
echo "  ✔ 30-implementation/refactoring-suite.md"

# --- error-handling.md -----------------------------------------------------
cat << 'SKILLEOF' > skills/30-implementation/error-handling.md
---
name: error-handling
description: >
  Standardize error types, logging formats, and error response
  structures across the project.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# Error Handling

> _"Errors are data. Treat them like first-class citizens."_

## Context

Invoked when setting up a new project's error handling strategy or when
inconsistent error patterns are detected in an existing codebase.

---

## Micro-Skills

### 1. Error Taxonomy 🌿 (Eco Mode)

**Steps:**

1. Define base error classes for the project:
   - `ValidationError` (400) — bad input from the client.
   - `AuthenticationError` (401) — identity not verified.
   - `AuthorizationError` (403) — identity verified, access denied.
   - `NotFoundError` (404) — resource does not exist.
   - `ConflictError` (409) — state conflict (optimistic locking).
   - `InternalError` (500) — unexpected server failure.
2. Each error class carries: `code`, `message`, `details`, `stack`.

### 2. Response Formatting 🌿 (Eco Mode)

**Steps:**

1. Adopt RFC 7807 Problem Details format:
   ```json
   {
     "type": "https://api.example.com/errors/validation",
     "title": "Validation Error",
     "status": 400,
     "detail": "field 'email' must be a valid email address",
     "instance": "/users/123"
   }
   ```
2. Create a global error handler middleware that converts exceptions to
   this format.
3. Never leak stack traces in production.

### 3. Structured Logging 🌿 (Eco Mode)

**Steps:**

1. Adopt JSON structured logging (not plain text).
2. Every log entry must include: `timestamp`, `level`, `message`,
   `correlation_id`, `service`, `error` (if applicable).
3. Use log levels consistently:
   - `debug`: development only.
   - `info`: business events (user created, order placed).
   - `warn`: recoverable issues (retry succeeded, cache miss).
   - `error`: unrecoverable issues requiring attention.

### 4. Retry & Circuit Breaker 🌿 (Eco Mode)

**Steps:**

1. For external service calls, add retry with exponential backoff.
2. Set max retries (default: 3).
3. Implement circuit breaker for repeated failures (open after 5 failures,
   half-open after 30s).

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `error_classes`    | `string`   | Generated error class file               |
| `error_handler`    | `string`   | Global error handler middleware           |
| `logging_config`   | `string`   | Logging configuration file               |
SKILLEOF
echo "  ✔ 30-implementation/error-handling.md"

# ===========================================================================
#  40-QUALITY
# ===========================================================================

# --- test-strategy.md ------------------------------------------------------
cat << 'SKILLEOF' > skills/40-quality/test-strategy.md
---
name: test-strategy
description: >
  Define the testing pyramid for a project: unit, integration, E2E.
  Set coverage targets and testing conventions.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: plan-execute
---

# Test Strategy

> _"Tests are a specification, not an afterthought."_

## Context

Invoked at project setup or when test coverage is inadequate. Establishes
a testing pyramid and conventions that all other testing skills follow.

---

## Micro-Skills

### 1. Pyramid Definition ⚡ (Power Mode)

**Steps:**

1. Define the testing pyramid for the project:

```text
        /  E2E  \        (few, slow, expensive)
       /----------\
      / Integration \    (moderate, medium speed)
     /----------------\
    /    Unit Tests     \  (many, fast, cheap)
   /____________________\
```

2. Set targets:
   - **Unit:** >= 80% line coverage, >= 70% branch coverage.
   - **Integration:** Cover all API endpoints, all DB queries.
   - **E2E:** Cover critical user journeys (happy path + top 3 error paths).

### 2. Convention Setup 🌿 (Eco Mode)

**Steps:**

1. Define test file naming: `*.test.ts`, `*_test.go`, `test_*.py`.
2. Define test directory structure: co-located or `__tests__/` directory.
3. Configure test runner (Jest, PyTest, Go test, JUnit).
4. Add test scripts to `package.json` / `Makefile` / `pyproject.toml`.

### 3. Coverage Gate 🌿 (Eco Mode)

**Steps:**

1. Configure coverage thresholds in the test runner config.
2. Fail CI if coverage drops below the threshold.
3. Generate coverage reports in both human-readable and machine-parseable
   formats (HTML + lcov).

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `strategy_doc`     | `string`   | Test strategy document                   |
| `config_files`     | `string[]` | Test runner configuration files          |
| `coverage_config`  | `string`   | Coverage threshold configuration         |
SKILLEOF
echo "  ✔ 40-quality/test-strategy.md"

# --- unit-testing.md -------------------------------------------------------
cat << 'SKILLEOF' > skills/40-quality/unit-testing.md
---
name: unit-testing
description: >
  Generate unit tests following AAA pattern (Arrange-Act-Assert).
  Supports Jest, JUnit, Go Test, PyTest, and more.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - test-strategy
reasoning_mode: linear
---

# Unit Testing

> _"A test that doesn't assert anything is just a waste of electricity."_

## Context

Invoked when new code is written without tests, when refactoring needs a
safety net, or when coverage gaps are identified.

---

## Micro-Skills

### 1. Test Generation 🌿 (Eco Mode)

**Steps:**

1. Analyze the target function/method:
   - Input types and edge values.
   - Return type and possible exceptions.
   - Side effects (DB writes, API calls, file I/O).
2. Generate test cases using the AAA pattern:
   ```
   // Arrange — set up inputs and mocks
   // Act — call the function
   // Assert — verify the result
   ```
3. Include test cases for:
   - **Happy path** (valid inputs, expected output).
   - **Boundary values** (0, -1, MAX_INT, empty string, null).
   - **Error cases** (invalid input, missing dependencies, timeouts).

### 2. Mock Generation 🌿 (Eco Mode)

**Steps:**

1. Identify external dependencies (DB, HTTP, file system).
2. Create mocks/stubs that return controlled responses.
3. Use the project's mocking library:
   - JS/TS: `jest.mock()`, `sinon`
   - Python: `unittest.mock`, `pytest-mock`
   - Go: interfaces + test doubles
   - Java: `Mockito`

### 3. Snapshot Testing 🌿 (Eco Mode)

**Steps:**

1. For complex output (HTML, JSON, serialized objects), use snapshot tests.
2. Generate initial snapshots.
3. Document when snapshots should be updated vs investigated.

---

## Inputs

| Parameter     | Type       | Required | Description                      |
|---------------|------------|----------|----------------------------------|
| `file_path`   | `string`   | yes      | Path to the file to test         |
| `functions`   | `string[]` | no       | Specific functions (default: all)|
| `framework`   | `string`   | no       | Test framework override          |

## Outputs

| Field          | Type     | Description                              |
|----------------|----------|------------------------------------------|
| `test_file`    | `string` | Generated test file path                 |
| `test_count`   | `number` | Number of test cases generated           |
| `coverage`     | `string` | Coverage report for the tested file      |

---

## Edge Cases

- Function has no return value (void/side-effect only) — Assert on side
  effects (mock was called, DB state changed).
- Global state dependency — Refactor first (invoke `refactoring-suite`).
SKILLEOF
echo "  ✔ 40-quality/unit-testing.md"

# --- integration-testing.md ------------------------------------------------
cat << 'SKILLEOF' > skills/40-quality/integration-testing.md
---
name: integration-testing
description: >
  Test across component boundaries using real databases, HTTP clients,
  and message queues via Docker containers.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - test-strategy
  - docker-containerization
reasoning_mode: plan-execute
---

# Integration Testing

> _"Unit tests prove your code works. Integration tests prove your system works."_

## Context

Invoked when testing interactions between components: API endpoints hitting
real databases, services communicating over HTTP/gRPC, or event-driven
message flows.

---

## Micro-Skills

### 1. Test Container Setup ⚡ (Power Mode)

**Steps:**

1. Define required services (Postgres, Redis, Kafka, etc.).
2. Create a `docker-compose.test.yml` with isolated test containers.
3. Configure health checks so tests wait for readiness.
4. Set up automatic teardown after test suite completes.

### 2. API Integration Tests ⚡ (Power Mode)

**Steps:**

1. For each API endpoint, write tests that:
   - Send real HTTP requests to the running server.
   - Use a real database (seeded with known data).
   - Assert on response status, body, and headers.
2. Test error paths: 400, 401, 403, 404, 409, 500.
3. Test pagination, filtering, and sorting.

### 3. Database Integration Tests ⚡ (Power Mode)

**Steps:**

1. Use a real database instance (Docker container).
2. Run migrations before each test suite.
3. Use transactions that rollback after each test (clean slate).
4. Test: CRUD operations, constraints, cascade deletes, concurrent writes.

### 4. Contract Testing ⚡ (Power Mode)

**Steps:**

1. For service-to-service communication, write consumer-driven contracts.
2. Use Pact or similar for HTTP, Buf for Protobuf.
3. Verify both consumer expectations and provider conformance.

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `test_files`       | `string[]` | Generated integration test files         |
| `docker_compose`   | `string`   | Test Docker Compose file                 |
| `test_results`     | `object`   | Pass/fail summary                        |
SKILLEOF
echo "  ✔ 40-quality/integration-testing.md"

# --- mutation-testing.md ---------------------------------------------------
cat << 'SKILLEOF' > skills/40-quality/mutation-testing.md
---
name: mutation-testing
description: >
  Verify test suite quality by injecting faults (mutants) into
  the code and checking if tests catch them.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - unit-testing
reasoning_mode: plan-execute
---

# Mutation Testing

> _"Your tests are only as good as the bugs they catch."_

## Context

Invoked when test coverage is high but confidence in test quality is low.
Mutation testing reveals tests that pass by accident (weak assertions).

---

## Micro-Skills

### 1. Mutant Generation ⚡ (Power Mode)

**Steps:**

1. Select the target module/file.
2. Apply mutation operators:
   - **Arithmetic:** `+` → `-`, `*` → `/`
   - **Conditional:** `<` → `<=`, `==` → `!=`, `&&` → `||`
   - **Return value:** `return x` → `return null/0/true`
   - **Void method:** Remove method call
   - **Negation:** `if (cond)` → `if (!cond)`
3. Generate one mutant per operator per target expression.

### 2. Mutant Execution ⚡ (Power Mode)

**Steps:**

1. For each mutant, run the test suite.
2. Classify the result:
   - **Killed** — at least one test failed (good).
   - **Survived** — all tests passed (bad — test gap).
   - **Timeout** — tests hung (treat as killed).
   - **Equivalent** — mutation doesn't change behavior (ignore).

### 3. Gap Analysis ⚡ (Power Mode)

**Steps:**

1. For each surviving mutant, identify:
   - Which line was mutated.
   - What assertion is missing.
2. Generate a recommended test case to kill the mutant.
3. Calculate the **mutation score**: `killed / (total - equivalent)`.
4. Target: >= 80% mutation score.

---

## Tools by Language

| Language   | Tool                           |
|------------|--------------------------------|
| Java       | PIT (pitest.org)               |
| JavaScript | Stryker                        |
| Python     | mutmut, cosmic-ray             |
| Go         | gremlins, ooze                 |
| C#         | Stryker.NET                    |

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `mutation_score`| `number` | Percentage of killed mutants             |
| `survivors`     | `object[]`| Surviving mutants with locations         |
| `recommended`   | `string[]`| Suggested tests to kill survivors        |
SKILLEOF
echo "  ✔ 40-quality/mutation-testing.md"

# ===========================================================================
#  50-PERFORMANCE
# ===========================================================================

# --- profiling-analysis.md -------------------------------------------------
cat << 'SKILLEOF' > skills/50-performance/profiling-analysis.md
---
name: profiling-analysis
description: >
  Analyze application performance using profiling tools, traces,
  and logs to identify bottlenecks and hotspots.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: plan-execute
---

# Profiling & Analysis

> _"Measure first. Optimize second. Never guess."_

## Context

Invoked when the application is slower than expected, or proactively before
launch to establish performance baselines.

---

## Micro-Skills

### 1. Baseline Measurement ⚡ (Power Mode)

**Steps:**

1. Define key performance metrics:
   - **Latency:** p50, p95, p99 response times.
   - **Throughput:** requests/second under expected load.
   - **Resource usage:** CPU %, memory MB, disk I/O.
2. Run a load test (k6, wrk, locust) with realistic scenarios.
3. Record baseline metrics.

### 2. CPU Profiling ⚡ (Power Mode)

**Steps:**

1. Run the CPU profiler for the target language:
   - Node.js: `--prof`, clinic.js, 0x
   - Python: `cProfile`, py-spy, Pyroscope
   - Go: `pprof`
   - Java: async-profiler, JFR
2. Generate a flame graph.
3. Identify the top 5 hotspot functions.
4. For each hotspot, propose an optimization with expected impact.

### 3. Memory Profiling ⚡ (Power Mode)

**Steps:**

1. Take heap snapshots before and after a workload.
2. Identify memory leaks: objects that grow without bound.
3. Check for common patterns: unbounded caches, event listener leaks,
   large string concatenation in loops.
4. Propose fixes.

### 4. Trace Analysis ⚡ (Power Mode)

**Steps:**

1. Enable distributed tracing (OpenTelemetry preferred).
2. Capture traces for slow requests (p99+).
3. Identify the slowest span in the trace waterfall.
4. Correlate with logs using `trace_id`/`correlation_id`.

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `baseline`      | `object`   | Performance baseline metrics             |
| `flame_graph`   | `string`   | Path to generated flame graph            |
| `hotspots`      | `object[]` | Top bottleneck functions                 |
| `recommendations`| `string[]`| Prioritized optimization suggestions     |
SKILLEOF
echo "  ✔ 50-performance/profiling-analysis.md"

# --- caching-strategy.md --------------------------------------------------
cat << 'SKILLEOF' > skills/50-performance/caching-strategy.md
---
name: caching-strategy
description: >
  Design and implement caching layers using Redis, Memcached, or
  in-memory caches with proper invalidation strategies.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - data-access
reasoning_mode: plan-execute
---

# Caching Strategy

> _"The fastest query is the one you never make."_

## Context

Invoked when read-heavy paths need optimization or when database load
must be reduced without architectural changes.

---

## Micro-Skills

### 1. Cache Identification ⚡ (Power Mode)

**Steps:**

1. Profile the application to find the top 10 most-called queries.
2. For each query, evaluate cacheability:
   - **High:** Read-heavy, rarely changes, tolerance for staleness.
   - **Medium:** Moderate writes, short TTL acceptable.
   - **Low:** Write-heavy, consistency-critical (don't cache).
3. Rank candidates by impact (frequency x latency saved).

### 2. Pattern Selection ⚡ (Power Mode)

**Steps:**

Choose the appropriate caching pattern:

| Pattern          | Use When                                      |
|------------------|-----------------------------------------------|
| **Cache-Aside**  | App reads cache first, fills on miss.         |
| **Write-Through**| App writes to cache and DB simultaneously.    |
| **Write-Behind** | App writes to cache; async flush to DB.       |
| **Read-Through** | Cache itself fetches from DB on miss.         |

Default recommendation: **Cache-Aside** (simplest, most predictable).

### 3. Implementation ⚡ (Power Mode)

**Steps:**

1. Add Redis/Memcached client to the project.
2. Implement the chosen pattern with:
   - Key naming convention: `{service}:{entity}:{id}` or `{service}:{query-hash}`.
   - TTL (start with 5 minutes, tune based on staleness tolerance).
   - Serialization format (JSON or MessagePack).
3. Add cache-hit/miss metrics.

### 4. Invalidation Strategy ⚡ (Power Mode)

**Steps:**

1. Define invalidation triggers (entity update, delete, TTL expiry).
2. Implement pattern:
   - **TTL-based:** Set expiry on every key.
   - **Event-based:** Invalidate on write (pub/sub or after-commit hook).
   - **Tag-based:** Group related keys, invalidate by tag.
3. Handle thundering herd (cache stampede): use lock/singleflight.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `cache_config`   | `string`   | Cache client configuration               |
| `implementation` | `string[]` | Modified files with caching added        |
| `key_schema`     | `string`   | Cache key naming documentation           |
| `metrics`        | `string`   | Cache-hit/miss metric implementation     |
SKILLEOF
echo "  ✔ 50-performance/caching-strategy.md"

# --- db-tuning.md ----------------------------------------------------------
cat << 'SKILLEOF' > skills/50-performance/db-tuning.md
---
name: db-tuning
description: >
  Database performance tuning: index analysis, query plan optimization,
  connection pooling, and configuration tuning.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - database-design
reasoning_mode: plan-execute
---

# Database Tuning

> _"A slow query is a bug. Treat it like one."_

## Context

Invoked when database queries are identified as bottlenecks, or proactively
during performance reviews.

---

## Micro-Skills

### 1. Slow Query Identification ⚡ (Power Mode)

**Steps:**

1. Enable slow query logging (threshold: 100ms).
2. Collect the top 10 slowest queries by total time.
3. For each query, capture:
   - SQL text (parameterized).
   - Execution frequency.
   - Average and p99 duration.
   - Table sizes involved.

### 2. Query Plan Analysis ⚡ (Power Mode)

**Steps:**

1. Run `EXPLAIN ANALYZE` on each slow query.
2. Look for:
   - **Sequential scans** on large tables (missing index).
   - **Nested loops** with high row estimates (N+1 at DB level).
   - **Sort operations** without index (filesort).
   - **Hash joins** on large datasets (memory pressure).
3. Propose index additions or query rewrites.

### 3. Index Optimization ⚡ (Power Mode)

**Steps:**

1. List all existing indexes on affected tables.
2. Identify:
   - **Missing indexes** (columns in WHERE/JOIN/ORDER BY without index).
   - **Redundant indexes** (covered by a broader composite index).
   - **Unused indexes** (never hit — pure write overhead).
3. Generate `CREATE INDEX` / `DROP INDEX` migration files.

### 4. Connection Pooling 🌿 (Eco Mode)

**Steps:**

1. Review current pool settings (min, max, idle timeout).
2. Recommend settings based on:
   - Expected concurrent connections.
   - Database max_connections setting.
   - Rule of thumb: `pool_size = (2 * cpu_cores) + disk_spindles`.
3. Add connection pool health check.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `slow_queries`   | `object[]` | Top slow queries with analysis           |
| `index_changes`  | `string[]` | Migration files for index changes        |
| `pool_config`    | `object`   | Connection pool recommendations          |
SKILLEOF
echo "  ✔ 50-performance/db-tuning.md"

# ===========================================================================
#  60-SECURITY
# ===========================================================================

# --- threat-modeling.md ----------------------------------------------------
cat << 'SKILLEOF' > skills/60-security/threat-modeling.md
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
SKILLEOF
echo "  ✔ 60-security/threat-modeling.md"

# --- secure-coding-review.md -----------------------------------------------
cat << 'SKILLEOF' > skills/60-security/secure-coding-review.md
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
SKILLEOF
echo "  ✔ 60-security/secure-coding-review.md"

# --- auth-implementation.md ------------------------------------------------
cat << 'SKILLEOF' > skills/60-security/auth-implementation.md
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
SKILLEOF
echo "  ✔ 60-security/auth-implementation.md"

# --- dependency-scanning.md ------------------------------------------------
cat << 'SKILLEOF' > skills/60-security/dependency-scanning.md
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
SKILLEOF
echo "  ✔ 60-security/dependency-scanning.md"

# ===========================================================================
#  70-DEVOPS
# ===========================================================================

# --- ci-pipeline.md --------------------------------------------------------
cat << 'SKILLEOF' > skills/70-devops/ci-pipeline.md
---
name: ci-pipeline
description: >
  Generate CI/CD pipeline configurations for GitHub Actions,
  GitLab CI, or Azure Pipelines.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - test-strategy
reasoning_mode: plan-execute
---

# CI Pipeline

> _"If it's not in the pipeline, it doesn't exist."_

## Context

Invoked when setting up or improving continuous integration. The pipeline
is the **gatekeeper** — nothing merges without passing.

---

## Micro-Skills

### 1. Pipeline Generation ⚡ (Power Mode)

**Steps:**

1. Detect the CI platform:
   - `.github/` directory → GitHub Actions
   - `.gitlab-ci.yml` exists → GitLab CI
   - `azure-pipelines.yml` exists → Azure Pipelines
   - None → Ask user which platform to use.
2. Generate a pipeline with these stages:
   ```
   install → lint → test → build → security-scan → deploy
   ```

### 2. GitHub Actions Workflow ⚡ (Power Mode)

**Steps:**

1. Create `.github/workflows/ci.yml`.
2. Configure:
   - Trigger: `push` to main, `pull_request` to main.
   - Matrix: test across multiple OS/language versions if applicable.
   - Caching: cache `node_modules`, `.pip`, or Go modules.
   - Steps: checkout → setup-lang → install → lint → test → build.
3. Add branch protection rules recommendation.

### 3. Pipeline Optimization 🌿 (Eco Mode)

**Steps:**

1. Add dependency caching to reduce install time.
2. Parallelize independent jobs (lint + test simultaneously).
3. Add `paths` filter to skip jobs when only docs change.
4. Use artifacts to pass build outputs between jobs.

### 4. Deployment Stage ⚡ (Power Mode)

**Steps:**

1. Define environments: `staging`, `production`.
2. Add environment-specific secrets.
3. Implement deployment strategy:
   - **Staging:** Auto-deploy on merge to main.
   - **Production:** Manual approval gate.
4. Add rollback mechanism (revert to previous deployment).

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `pipeline_file`  | `string`   | Generated CI configuration file          |
| `branch_rules`   | `string`   | Branch protection recommendations        |
| `secrets_list`   | `string[]` | Required CI secrets                      |
SKILLEOF
echo "  ✔ 70-devops/ci-pipeline.md"

# --- docker-containerization.md --------------------------------------------
cat << 'SKILLEOF' > skills/70-devops/docker-containerization.md
---
name: docker-containerization
description: >
  Write optimized Dockerfiles with multi-stage builds,
  security best practices, and minimal image sizes.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# Docker Containerization

> _"Ship the app, not the toolchain."_

## Context

Invoked when containerizing an application. Focuses on security, image size,
build speed, and reproducibility.

---

## Micro-Skills

### 1. Dockerfile Generation 🌿 (Eco Mode)

**Steps:**

1. Detect the application type (Node.js, Python, Go, Java, .NET).
2. Generate a multi-stage Dockerfile:

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine AS runtime
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER app
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

### 2. Security Hardening 🌿 (Eco Mode)

**Steps:**

1. Use minimal base images (`-alpine`, `-slim`, `distroless`).
2. Run as non-root user (never `USER root` in final stage).
3. Add `.dockerignore` (exclude `.git`, `node_modules`, `.env`).
4. Pin image versions (no `latest` tag).
5. Scan image with `docker scout` or `trivy`.

### 3. Build Optimization 🌿 (Eco Mode)

**Steps:**

1. Order layers from least-changed to most-changed (maximize cache).
2. Separate dependency install from code copy.
3. Use BuildKit features (`--mount=type=cache` for package managers).
4. Set `.dockerignore` to exclude test files and docs from build context.

### 4. Docker Compose 🌿 (Eco Mode)

**Steps:**

1. Create `docker-compose.yml` for local development.
2. Include: app, database, cache (if applicable).
3. Use named volumes for data persistence.
4. Add health checks for all services.
5. Create `docker-compose.override.yml` for dev-specific settings
   (hot reload, debug ports).

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `dockerfile`    | `string`   | Optimized Dockerfile                     |
| `dockerignore`  | `string`   | .dockerignore file                       |
| `compose`       | `string`   | Docker Compose configuration             |
| `image_size`    | `string`   | Estimated image size                     |
SKILLEOF
echo "  ✔ 70-devops/docker-containerization.md"

# --- kubernetes-helm.md ----------------------------------------------------
cat << 'SKILLEOF' > skills/70-devops/kubernetes-helm.md
---
name: kubernetes-helm
description: >
  Generate Kubernetes manifests and Helm charts for deploying
  containerized applications to K8s clusters.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - docker-containerization
reasoning_mode: plan-execute
---

# Kubernetes & Helm

> _"Declare the desired state. Let the cluster figure out the rest."_

## Context

Invoked when deploying containerized applications to Kubernetes. Generates
production-grade manifests or Helm charts with best practices baked in.

---

## Micro-Skills

### 1. Manifest Generation ⚡ (Power Mode)

**Steps:**

1. Generate core K8s resources:
   - `Deployment` (or `StatefulSet` for stateful apps).
   - `Service` (ClusterIP, LoadBalancer, or NodePort).
   - `Ingress` (with TLS termination).
   - `ConfigMap` and `Secret` for configuration.
   - `HorizontalPodAutoscaler` (HPA).
2. Set resource requests and limits (CPU, memory).
3. Add liveness, readiness, and startup probes.
4. Set `PodDisruptionBudget` for high-availability deployments.

### 2. Helm Chart Scaffolding ⚡ (Power Mode)

**Steps:**

1. Create Helm chart structure:
   ```
   chart/
   ├── Chart.yaml
   ├── values.yaml
   ├── templates/
   │   ├── deployment.yaml
   │   ├── service.yaml
   │   ├── ingress.yaml
   │   ├── configmap.yaml
   │   ├── secret.yaml
   │   ├── hpa.yaml
   │   └── _helpers.tpl
   └── .helmignore
   ```
2. Parameterize everything in `values.yaml` (image, replicas, resources,
   env vars, ingress host).
3. Add `{{ include }}` helpers for labels and selectors.

### 3. Security Policies ⚡ (Power Mode)

**Steps:**

1. Add `NetworkPolicy` to restrict pod-to-pod traffic.
2. Set `securityContext`:
   - `runAsNonRoot: true`
   - `readOnlyRootFilesystem: true`
   - `allowPrivilegeEscalation: false`
3. Use `ServiceAccount` with minimal RBAC.
4. Scan manifests with `kubesec` or `kube-linter`.

### 4. Rollout Strategy ⚡ (Power Mode)

**Steps:**

1. Configure rolling update strategy:
   - `maxUnavailable: 0` (zero downtime).
   - `maxSurge: 25%`.
2. Add rollback command reference: `helm rollback <release> <revision>`.
3. Configure pre/post-deploy hooks if needed.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `manifests`      | `string[]` | Generated K8s YAML files                 |
| `helm_chart`     | `string`   | Helm chart directory path                |
| `values`         | `string`   | Default values.yaml                      |
SKILLEOF
echo "  ✔ 70-devops/kubernetes-helm.md"

# --- terraform-iac.md ------------------------------------------------------
cat << 'SKILLEOF' > skills/70-devops/terraform-iac.md
---
name: terraform-iac
description: >
  Generate Infrastructure as Code using Terraform (or OpenTofu).
  Modules, state management, and environment separation.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - system-design
reasoning_mode: plan-execute
---

# Terraform / Infrastructure as Code

> _"If you can't reproduce your infrastructure from code, it's not infrastructure."_

## Context

Invoked when provisioning cloud infrastructure. Generates Terraform modules
following best practices for state management, security, and reusability.

---

## Micro-Skills

### 1. Module Generation ⚡ (Power Mode)

**Steps:**

1. Identify required resources from the system design.
2. Generate Terraform module structure:
   ```
   terraform/
   ├── main.tf           # Resource definitions
   ├── variables.tf      # Input variables
   ├── outputs.tf        # Output values
   ├── providers.tf      # Provider configuration
   ├── versions.tf       # Terraform and provider version constraints
   └── terraform.tfvars  # (gitignored) Environment-specific values
   ```
3. Use data sources for existing resources (don't recreate).
4. Tag all resources consistently (team, project, environment).

### 2. State Management ⚡ (Power Mode)

**Steps:**

1. Configure remote state backend:
   - AWS: S3 + DynamoDB for locking.
   - Azure: Storage Account + Blob.
   - GCP: GCS bucket.
2. Enable state encryption.
3. Set up state locking to prevent concurrent modifications.
4. Never commit `terraform.tfstate` or `.tfvars` with secrets.

### 3. Environment Separation ⚡ (Power Mode)

**Steps:**

1. Use workspaces or directory-based separation:
   ```
   environments/
   ├── dev/
   │   ├── main.tf → ../../modules/
   │   └── terraform.tfvars
   ├── staging/
   └── production/
   ```
2. Use the same modules across environments with different variables.
3. Implement environment promotion (dev → staging → prod).

### 4. Security & Compliance ⚡ (Power Mode)

**Steps:**

1. Use `tfsec` or `checkov` to scan for misconfigurations.
2. Encrypt sensitive outputs.
3. Use IAM roles with least privilege.
4. Enable audit logging for infrastructure changes.
5. Run `terraform plan` in CI, require approval for `apply`.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `modules`        | `string[]` | Generated Terraform module files         |
| `env_configs`    | `string[]` | Environment-specific configurations      |
| `state_config`   | `string`   | Backend configuration                    |
| `scan_results`   | `string`   | Security scan output                     |
SKILLEOF
echo "  ✔ 70-devops/terraform-iac.md"

# ===========================================================================
#  80-DOCS
# ===========================================================================

# --- openapi-specs.md ------------------------------------------------------
cat << 'SKILLEOF' > skills/80-docs/openapi-specs.md
---
name: openapi-specs
description: >
  Generate or update OpenAPI (Swagger) specifications from existing
  code, or validate code against existing specs.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - api-contract-design
reasoning_mode: linear
---

# OpenAPI Spec Generation

> _"The spec is the single source of truth for your API."_

## Context

Invoked when API documentation needs to be generated from code, or when
existing specs need to be updated to reflect implementation changes.

---

## Micro-Skills

### 1. Code-to-Spec Generation 🌿 (Eco Mode)

**Steps:**

1. Detect the API framework:
   - Express/Fastify → scan route definitions.
   - FastAPI → extract from type hints + decorators.
   - Spring → extract from `@RequestMapping` annotations.
   - Go (Gin/Echo) → scan handler registrations.
2. Extract: paths, methods, parameters, request/response schemas.
3. Generate `openapi.yaml` (OpenAPI 3.1).
4. Add descriptions from JSDoc, docstrings, or comments.

### 2. Spec Validation 🌿 (Eco Mode)

**Steps:**

1. Run a spec linter (Spectral, swagger-cli).
2. Check for: missing descriptions, missing examples, unused schemas.
3. Validate all `$ref` pointers resolve correctly.
4. Report issues sorted by severity.

### 3. Spec-to-Code Drift Detection 🌿 (Eco Mode)

**Steps:**

1. Compare the spec with actual implementation.
2. Flag:
   - Endpoints in spec but not implemented.
   - Endpoints implemented but not in spec.
   - Schema mismatches (field types, required fields).
3. Generate a drift report.

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `spec_file`     | `string` | Generated/updated OpenAPI YAML           |
| `lint_report`   | `string` | Validation report                        |
| `drift_report`  | `string` | Spec vs implementation drift             |
SKILLEOF
echo "  ✔ 80-docs/openapi-specs.md"

# --- readme-generation.md --------------------------------------------------
cat << 'SKILLEOF' > skills/80-docs/readme-generation.md
---
name: readme-generation
description: >
  Create comprehensive README files with installation instructions,
  usage examples, API reference, and contribution guidelines.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# README Generation

> _"If the README doesn't explain it, it doesn't exist to newcomers."_

## Context

Invoked when a project needs a README, or when the existing README is
outdated. A good README is the most impactful documentation a project has.

---

## Micro-Skills

### 1. README Structure 🌿 (Eco Mode)

**Steps:**

1. Generate the standard README sections:
   - **Title + Badges** (build status, coverage, version, license).
   - **Description** (what, why, for whom — 2-3 sentences).
   - **Quick Start** (clone, install, run — under 5 commands).
   - **Installation** (prerequisites, step-by-step).
   - **Usage** (code examples for common use cases).
   - **API Reference** (link to OpenAPI spec or inline).
   - **Architecture** (link to system design docs or brief overview).
   - **Contributing** (how to set up dev environment, run tests, PR process).
   - **License** (SPDX identifier and link).

### 2. Badge Generation 🌿 (Eco Mode)

**Steps:**

1. Detect CI platform and add build status badge.
2. Add coverage badge (Codecov, Coveralls).
3. Add version badge (npm, PyPI, Go).
4. Add license badge.
5. Format as a single line of shields.io badges.

### 3. Example Generation 🌿 (Eco Mode)

**Steps:**

1. Identify the top 3 use cases from the codebase.
2. Write minimal code examples that are copy-paste ready.
3. Include expected output for each example.
4. Test that examples actually work (no broken code in docs).

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `readme`        | `string` | Generated README.md content              |
| `badges`        | `string` | Badge markdown                           |
SKILLEOF
echo "  ✔ 80-docs/readme-generation.md"

# --- release-notes.md ------------------------------------------------------
cat << 'SKILLEOF' > skills/80-docs/release-notes.md
---
name: release-notes
description: >
  Parse git history to generate changelogs and release notes
  following Conventional Commits and Keep a Changelog formats.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# Release Notes

> _"Users don't read code diffs. Give them a story."_

## Context

Invoked before a release to generate user-facing changelogs from the
git history, or to maintain a running CHANGELOG.md.

---

## Micro-Skills

### 1. Conventional Commit Parsing 🌿 (Eco Mode)

**Steps:**

1. Read git log since the last release tag.
2. Parse commits following the Conventional Commits spec:
   - `feat:` → Features (MINOR version bump).
   - `fix:` → Bug Fixes (PATCH version bump).
   - `BREAKING CHANGE:` → Breaking Changes (MAJOR version bump).
   - `docs:`, `chore:`, `refactor:`, `test:` → Other.
3. Group commits by type.
4. Extract scope if present: `feat(auth): add OAuth2`.

### 2. Changelog Generation 🌿 (Eco Mode)

**Steps:**

1. Generate entries following Keep a Changelog format:
   ```markdown
   ## [1.2.0] - 2025-01-15

   ### Added
   - OAuth2 authentication support (#45)

   ### Fixed
   - Connection pool exhaustion under load (#42)

   ### Changed
   - Upgraded Redis client to v5 (#43)
   ```
2. Include PR/issue references where available.
3. Prepend to `CHANGELOG.md`.

### 3. Version Bump 🌿 (Eco Mode)

**Steps:**

1. Determine the version bump type from commit analysis:
   - Any `BREAKING CHANGE` → MAJOR.
   - Any `feat` → MINOR.
   - Only `fix` → PATCH.
2. Update version in `package.json`, `pyproject.toml`, `Cargo.toml`, etc.
3. Create a git tag: `v{major}.{minor}.{patch}`.

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `changelog`     | `string` | Generated changelog entry                |
| `version`       | `string` | New version number                       |
| `tag_command`   | `string` | Git tag command to run                   |
SKILLEOF
echo "  ✔ 80-docs/release-notes.md"

# ===========================================================================
#  90-MAINTENANCE
# ===========================================================================

# --- incident-response.md --------------------------------------------------
cat << 'SKILLEOF' > skills/90-maintenance/incident-response.md
---
name: incident-response
description: >
  Structured steps to triage, mitigate, and resolve production
  incidents. Includes severity classification and postmortem template.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: plan-execute
---

# Incident Response

> _"When the pager fires, follow the playbook."_

## Context

Invoked during production incidents. Provides a structured workflow to
minimize downtime and capture learnings for prevention.

---

## Micro-Skills

### 1. Severity Classification ⚡ (Power Mode)

**Steps:**

1. Assess the incident:
   | Severity | Impact                       | Response Time |
   |----------|------------------------------|---------------|
   | **SEV1** | Full outage, data loss       | Immediate     |
   | **SEV2** | Major feature degraded       | < 30 minutes  |
   | **SEV3** | Minor feature affected       | < 4 hours     |
   | **SEV4** | Cosmetic / non-user-facing   | Next sprint   |
2. Assign an Incident Commander (IC).
3. Open a communication channel (Slack, Teams).

### 2. Triage ⚡ (Power Mode)

**Steps:**

1. **Identify:** What is broken? Which services? Which users?
2. **Correlate:** Check recent deployments, config changes, traffic spikes.
3. **Isolate:** Find the failing component using:
   - Error rates in dashboards.
   - Recent log entries (filter by `level=error`).
   - Distributed traces for failed requests.

### 3. Mitigate ⚡ (Power Mode)

**Steps:**

1. Apply the fastest safe mitigation:
   - **Rollback** the most recent deployment.
   - **Scale up** if the issue is capacity-related.
   - **Feature flag** off if a specific feature is the cause.
   - **Redirect traffic** if a region/zone is unhealthy.
2. Verify mitigation: confirm error rates are dropping.
3. Communicate status to stakeholders.

### 4. Postmortem ⚡ (Power Mode)

**Steps:**

1. After resolution, write a blameless postmortem:
   ```markdown
   ## Incident Postmortem — [Title]
   **Date:** YYYY-MM-DD
   **Duration:** Xh Ym
   **Severity:** SEV-N
   **Impact:** <who/what was affected>

   ### Timeline
   - HH:MM — Incident detected
   - HH:MM — IC assigned
   - HH:MM — Root cause identified
   - HH:MM — Mitigation applied
   - HH:MM — Resolved

   ### Root Cause
   <What actually happened>

   ### Action Items
   - [ ] <Preventive action 1>
   - [ ] <Preventive action 2>

   ### Lessons Learned
   - <What went well>
   - <What went poorly>
   ```
2. Share with the team and track action items.

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `severity`      | `string` | SEV1-SEV4 classification                 |
| `timeline`      | `object` | Incident timeline                        |
| `mitigation`    | `string` | Applied mitigation description           |
| `postmortem`    | `string` | Postmortem document                      |
SKILLEOF
echo "  ✔ 90-maintenance/incident-response.md"

# --- legacy-upgrade.md -----------------------------------------------------
cat << 'SKILLEOF' > skills/90-maintenance/legacy-upgrade.md
---
name: legacy-upgrade
description: >
  Plan and execute upgrades of major frameworks, languages, or
  runtime versions with minimal disruption.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
  - test-strategy
reasoning_mode: plan-execute
---

# Legacy Upgrade

> _"The best time to upgrade was last quarter. The second best time is now."_

## Context

Invoked when a framework, language, or major dependency needs upgrading
(e.g., Node 16 to Node 20, Spring Boot 2 to 3, Python 2 to 3).

---

## Micro-Skills

### 1. Impact Assessment ⚡ (Power Mode)

**Steps:**

1. Read the migration guide for the target version.
2. Identify **breaking changes** that affect the codebase:
   - Removed APIs.
   - Changed default behaviors.
   - Renamed packages or modules.
3. Scan the codebase for usage of affected APIs.
4. Generate an impact report: files affected, estimated effort per file.

### 2. Upgrade Strategy ⚡ (Power Mode)

**Steps:**

1. Choose the approach:
   - **Big bang:** Upgrade everything at once (small projects).
   - **Strangler fig:** Gradually migrate module by module (large projects).
   - **Dual-run:** Run old and new versions side-by-side during transition.
2. Document the strategy in an ADR (invoke `adr-management`).
3. Estimate the timeline and break into milestones.

### 3. Automated Migration ⚡ (Power Mode)

**Steps:**

1. Use codemods where available:
   - Node.js: `jscodeshift`
   - Java: OpenRewrite
   - Python: `2to3`, `pyupgrade`
2. Apply codemods to the codebase.
3. Run tests after each codemod pass.
4. Manually fix anything the codemods couldn't handle.

### 4. Validation & Rollback ⚡ (Power Mode)

**Steps:**

1. Run the full test suite on the upgraded codebase.
2. Run integration tests with dependent services.
3. Deploy to staging and run smoke tests.
4. Define rollback criteria (what failures trigger a revert).
5. Keep the old version deployable until the new version is proven in
   production for at least one full release cycle.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `impact_report`  | `object`   | Files and APIs affected                  |
| `migration_plan` | `string`   | Step-by-step upgrade plan                |
| `adr`            | `string`   | Strategy decision record                 |
| `test_results`   | `object`   | Before/after test comparison             |
SKILLEOF
echo "  ✔ 90-maintenance/legacy-upgrade.md"

# ===========================================================================
#  TEMPLATES
# ===========================================================================

cat << 'SKILLEOF' > templates/skill-template.md
---
name: <skill-name>
description: >
  <One-line description of what this skill does.>
version: "0.1.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear | plan-execute | tdd | mixed
---

# <Skill Name>

> _"<One-line philosophy or motto for this skill.>"_

## Context

<Describe when and why this skill is invoked. What problem does it solve?>

---

## Micro-Skills

### 1. <Micro-Skill A>

**Mode:** eco | power

**Steps:**

1. ...
2. ...
3. ...

### 2. <Micro-Skill B>

**Mode:** eco | power

**Steps:**

1. ...
2. ...
3. ...

---

## Inputs

| Parameter   | Type     | Required | Description            |
|-------------|----------|----------|------------------------|
| `<param>`   | `string` | yes      | <What it represents>   |

## Outputs

| Field       | Type     | Description                        |
|-------------|----------|------------------------------------|
| `<field>`   | `string` | <What the skill produces>          |

---

## Examples

### Example 1 — <Scenario>

**Input:**
```json
{
  "<param>": "<value>"
}
```

**Output:**
```json
{
  "<field>": "<value>"
}
```

---

## Edge Cases

- <Edge case 1 and how the skill handles it.>
- <Edge case 2 and how the skill handles it.>
SKILLEOF
echo "  ✔ templates/skill-template.md"

# ===========================================================================
#  REGISTRY
# ===========================================================================

cat << 'SKILLEOF' > registry.yaml
# ==========================================================================
# Agent Skills Garden — Registry (Full Suite)
# ==========================================================================
# The single source of truth for all skills in the garden.
# The Librarian uses this file for discovery and routing.
# ==========================================================================

version: "2.0.0"

# --------------------------------------------------------------------------
# Foundation Layer (00) — always loaded before every task
# --------------------------------------------------------------------------
foundation:
  - name: constitution
    path: skills/00-foundation/constitution.md
    description: Core principles — Satya, Dharma, Ahimsa. Cognitive modes.
    tags: [core, safety, principles]
    reasoning_mode: linear

  - name: scratchpad
    path: skills/00-foundation/scratchpad.md
    description: Internal monologue protocol and cognitive modes (Eco/Power).
    tags: [core, reasoning, modes]
    reasoning_mode: linear

  - name: auditor
    path: skills/00-foundation/auditor.md
    description: Output validation — ensures Constitution compliance.
    tags: [core, safety, validation]
    reasoning_mode: plan-execute

  - name: librarian
    path: skills/00-foundation/librarian.md
    description: Skill discovery via fuzzy matching and semantic search.
    tags: [core, routing, discovery]
    reasoning_mode: linear

# --------------------------------------------------------------------------
# Discovery Layer (10)
# --------------------------------------------------------------------------
discovery:
  - name: requirements-elicitation
    path: skills/10-discovery/requirements-elicitation.md
    description: Interview user for goals, constraints, and success metrics.
    tags: [discovery, requirements, planning]
    reasoning_mode: plan-execute

  - name: domain-modeling
    path: skills/10-discovery/domain-modeling.md
    description: Create domain glossary, entity relationships, Protected Terms.
    tags: [discovery, domain, glossary]
    reasoning_mode: plan-execute

# --------------------------------------------------------------------------
# Architecture Layer (20)
# --------------------------------------------------------------------------
architecture:
  - name: adr-management
    path: skills/20-architecture/adr-management.md
    description: Create and manage Architecture Decision Records.
    tags: [architecture, adr, decisions]
    reasoning_mode: linear

  - name: api-contract-design
    path: skills/20-architecture/api-contract-design.md
    description: Design REST/gRPC APIs (OpenAPI spec) before coding.
    tags: [architecture, api, contract, openapi]
    reasoning_mode: plan-execute

  - name: database-design
    path: skills/20-architecture/database-design.md
    description: Schema design, normalization, migration planning, indexing.
    tags: [architecture, database, schema, migration]
    reasoning_mode: plan-execute

  - name: system-design
    path: skills/20-architecture/system-design.md
    description: Component diagrams, data flow, trade-off analysis.
    tags: [architecture, system, design, scalability]
    reasoning_mode: plan-execute

# --------------------------------------------------------------------------
# Implementation Layer (30)
# --------------------------------------------------------------------------
implementation:
  - name: cleanup
    path: skills/30-implementation/cleanup.md
    description: Remove noise, enforce formatting, safely rename identifiers.
    tags: [code-quality, formatting, renaming]
    reasoning_mode: mixed

  - name: api-implementation
    path: skills/30-implementation/api-implementation.md
    description: Implement handlers/controllers based on API contracts.
    tags: [implementation, api, handlers, validation]
    reasoning_mode: plan-execute

  - name: data-access
    path: skills/30-implementation/data-access.md
    description: Repository pattern, query optimization, N+1 prevention.
    tags: [implementation, database, repository, queries]
    reasoning_mode: plan-execute

  - name: refactoring-suite
    path: skills/30-implementation/refactoring-suite.md
    description: Complex refactors with strict test verification.
    tags: [implementation, refactoring, extract, rename]
    reasoning_mode: plan-execute

  - name: error-handling
    path: skills/30-implementation/error-handling.md
    description: Standardize error types, logging, and response formats.
    tags: [implementation, errors, logging, resilience]
    reasoning_mode: linear

# --------------------------------------------------------------------------
# Quality Layer (40)
# --------------------------------------------------------------------------
quality:
  - name: test-strategy
    path: skills/40-quality/test-strategy.md
    description: Define the testing pyramid, coverage targets, conventions.
    tags: [quality, testing, strategy, coverage]
    reasoning_mode: plan-execute

  - name: unit-testing
    path: skills/40-quality/unit-testing.md
    description: Generate unit tests (Jest, JUnit, Go Test, PyTest).
    tags: [quality, testing, unit, tdd]
    reasoning_mode: linear

  - name: integration-testing
    path: skills/40-quality/integration-testing.md
    description: Test across component boundaries with Docker containers.
    tags: [quality, testing, integration, docker]
    reasoning_mode: plan-execute

  - name: mutation-testing
    path: skills/40-quality/mutation-testing.md
    description: Verify test quality by injecting faults (mutants).
    tags: [quality, testing, mutation, coverage]
    reasoning_mode: plan-execute

# --------------------------------------------------------------------------
# Performance Layer (50)
# --------------------------------------------------------------------------
performance:
  - name: profiling-analysis
    path: skills/50-performance/profiling-analysis.md
    description: Analyze logs/traces to find bottlenecks and hotspots.
    tags: [performance, profiling, flame-graph, optimization]
    reasoning_mode: plan-execute

  - name: caching-strategy
    path: skills/50-performance/caching-strategy.md
    description: Implement Redis/Memcached caching patterns and invalidation.
    tags: [performance, caching, redis, invalidation]
    reasoning_mode: plan-execute

  - name: db-tuning
    path: skills/50-performance/db-tuning.md
    description: Index analysis, query plan optimization, connection pooling.
    tags: [performance, database, indexing, queries]
    reasoning_mode: plan-execute

# --------------------------------------------------------------------------
# Security Layer (60)
# --------------------------------------------------------------------------
security:
  - name: threat-modeling
    path: skills/60-security/threat-modeling.md
    description: Identify STRIDE threats, assess risk, plan mitigations.
    tags: [security, threat-model, stride, risk]
    reasoning_mode: plan-execute

  - name: secure-coding-review
    path: skills/60-security/secure-coding-review.md
    description: Scan for OWASP Top 10 vulnerabilities and anti-patterns.
    tags: [security, owasp, code-review, vulnerabilities]
    reasoning_mode: plan-execute

  - name: auth-implementation
    path: skills/60-security/auth-implementation.md
    description: Implement JWT, OAuth2, or RBAC authentication safely.
    tags: [security, auth, jwt, oauth2, rbac]
    reasoning_mode: plan-execute

  - name: dependency-scanning
    path: skills/60-security/dependency-scanning.md
    description: Check dependencies for CVEs and license compliance.
    tags: [security, dependencies, cve, sbom]
    reasoning_mode: linear

# --------------------------------------------------------------------------
# DevOps Layer (70)
# --------------------------------------------------------------------------
devops:
  - name: ci-pipeline
    path: skills/70-devops/ci-pipeline.md
    description: Generate GitHub Actions/GitLab CI workflows.
    tags: [devops, ci, github-actions, pipeline]
    reasoning_mode: plan-execute

  - name: docker-containerization
    path: skills/70-devops/docker-containerization.md
    description: Write optimized Dockerfiles with multi-stage builds.
    tags: [devops, docker, containers, images]
    reasoning_mode: linear

  - name: kubernetes-helm
    path: skills/70-devops/kubernetes-helm.md
    description: Generate Helm charts and K8s manifests.
    tags: [devops, kubernetes, helm, deployment]
    reasoning_mode: plan-execute

  - name: terraform-iac
    path: skills/70-devops/terraform-iac.md
    description: Generate Infrastructure as Code modules (Terraform/OpenTofu).
    tags: [devops, terraform, iac, cloud]
    reasoning_mode: plan-execute

# --------------------------------------------------------------------------
# Documentation Layer (80)
# --------------------------------------------------------------------------
docs:
  - name: openapi-specs
    path: skills/80-docs/openapi-specs.md
    description: Generate Swagger/OpenAPI YAML from code.
    tags: [docs, openapi, swagger, api]
    reasoning_mode: linear

  - name: readme-generation
    path: skills/80-docs/readme-generation.md
    description: Create comprehensive READMEs with usage and install guides.
    tags: [docs, readme, documentation]
    reasoning_mode: linear

  - name: release-notes
    path: skills/80-docs/release-notes.md
    description: Parse git logs to generate changelogs and version bumps.
    tags: [docs, changelog, release, versioning]
    reasoning_mode: linear

# --------------------------------------------------------------------------
# Maintenance Layer (90)
# --------------------------------------------------------------------------
maintenance:
  - name: incident-response
    path: skills/90-maintenance/incident-response.md
    description: Triage, mitigate, and resolve production outages.
    tags: [maintenance, incident, outage, postmortem]
    reasoning_mode: plan-execute

  - name: legacy-upgrade
    path: skills/90-maintenance/legacy-upgrade.md
    description: Plan for upgrading major frameworks and languages.
    tags: [maintenance, upgrade, migration, legacy]
    reasoning_mode: plan-execute

# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------
templates:
  - name: skill-template
    path: templates/skill-template.md
    description: Boilerplate for creating new skills.
    tags: [meta, template]
SKILLEOF
echo "  ✔ registry.yaml"

# ===========================================================================
echo ""
echo "🌱 Agent Skills Garden created successfully! (Full Suite)"
echo ""
echo "   Structure:"
echo "   ├── registry.yaml"
echo "   ├── skills/"
echo "   │   ├── 00-foundation/    (4 skills: constitution, scratchpad, auditor, librarian)"
echo "   │   ├── 10-discovery/     (2 skills: requirements-elicitation, domain-modeling)"
echo "   │   ├── 20-architecture/  (4 skills: adr, api-contract, database, system-design)"
echo "   │   ├── 30-implementation/(5 skills: cleanup, api-impl, data-access, refactoring, error-handling)"
echo "   │   ├── 40-quality/       (4 skills: test-strategy, unit, integration, mutation)"
echo "   │   ├── 50-performance/   (3 skills: profiling, caching, db-tuning)"
echo "   │   ├── 60-security/      (4 skills: threat-model, secure-review, auth, dep-scanning)"
echo "   │   ├── 70-devops/        (4 skills: ci, docker, k8s-helm, terraform)"
echo "   │   ├── 80-docs/          (3 skills: openapi, readme, release-notes)"
echo "   │   └── 90-maintenance/   (2 skills: incident-response, legacy-upgrade)"
echo "   └── templates/"
echo "       └── skill-template.md"
echo ""
echo "   Total: 35 skills + 1 template + registry"
echo ""
echo "   Next: Read skills/00-foundation/constitution.md"
