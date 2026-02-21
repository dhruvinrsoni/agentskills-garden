# Agent Skills Garden 🌱

> *A hierarchical, constitution-driven skill library that serves as the "brain" for AI agents.*
> 
> *62 skills across 15 categories — these hierarchical skills enable any model to reason as well as the best frontier models.*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Skills are markdown files with YAML frontmatter that agents discover at runtime via a central registry. Every action is governed by a **Constitution** rooted in three principles:

| Pillar | Sanskrit | Meaning |
|--------|----------|---------|
| **Truth** | Satya | Deterministic, reproducible outputs. No hallucinations. |
| **Safety** | Dharma | Ask-first policy. Prefer the smallest change. |
| **Non-Destruction** | Ahimsa | Preview diffs before applying. Always reversible. |

Inspired by the [Agent Skills](https://agentskills.io/) open format.

---

## Quick Start

**Linux / macOS:**
```bash
git clone https://github.com/dhruvinrsoni/agentskills-garden.git
cd agentskills-garden
chmod +x setup_skills.sh && ./setup_skills.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/dhruvinrsoni/agentskills-garden.git
cd agentskills-garden
.\setup_skills.ps1            # Full native installer, no WSL required
.\setup_skills.ps1 -Force     # Overwrite existing files
```

Both scripts create the full directory structure and all skill files from scratch.

---

## Repository Structure

```
agentskills-garden/
├── registry.yaml                          # Single source of truth — skill index
├── skills/
│   ├── 00-foundation/        (4 skills)   # Always loaded first
│   ├── 10-discovery/         (2 skills)   # Requirements & domain modeling
│   ├── 20-architecture/      (4 skills)   # System, API, DB, ADR design
│   ├── 20-planning/          (4 skills)   # Task decomposition, risk, estimation
│   ├── 30-implementation/    (8 skills)   # Code gen, refactoring, TDD, cleanup
│   ├── 40-quality/           (8 skills)   # Reviews, testing strategies, mutation
│   ├── 50-documentation/     (4 skills)   # API docs, ADRs, changelogs
│   ├── 50-performance/       (3 skills)   # Caching, DB tuning, profiling
│   ├── 60-debugging/         (3 skills)   # Root cause, log analysis, error handling
│   ├── 60-security/          (4 skills)   # Auth, threat modeling, secure coding
│   ├── 70-devops/            (5 skills)   # CI/CD, Docker, K8s, Terraform, monitoring
│   ├── 80-collaboration/     (4 skills)   # Git workflow, PRs, pair programming
│   ├── 80-docs/              (3 skills)   # OpenAPI, README, release notes
│   └── 90-maintenance/       (6 skills)   # Incidents, migrations, tech debt, deprecation
├── templates/
│   └── skill-template.md                  # Boilerplate for new skills
├── setup_skills.sh                        # Portable installer (Bash)
└── setup_skills.ps1                       # Portable installer (PowerShell)
```

**Total: 62 skills + 1 template + registry**

---

## Skill Format (SKILL.md)

Every skill follows the [agentskills.io](https://agentskills.io/) standard with full spec schema:

```yaml
---
name: cleanup
description: >
  Remove noise, enforce formatting, and safely rename identifiers.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: mixed          # linear | plan-execute | tdd | mixed
---
```

The markdown body uses progressive disclosure:

| Section | Purpose |
|---------|---------|
| **Context** | When and why to invoke this skill |
| **Micro-Skills** | Ordered sub-tasks with Eco 🌿 / Power ⚡ mode tags |
| **Inputs / Outputs** | Typed parameters and return artifacts |
| **Scope** | Explicit in-scope / out-of-scope boundaries |
| **Guardrails** | Hard constraints that must never be violated |
| **Ask-When-Ambiguous** | Triggers + question templates for uncertain situations |
| **Decision Criteria** | Situation → Action lookup table |
| **Success Criteria** | Verifiable checklist for "done" |
| **Failure Modes** | Known failure patterns with symptoms and mitigations |
| **Audit Log** | Structured log entry templates for traceability |
| **Examples** | Concrete before/after demonstrations |
| **Edge Cases** | Unusual inputs and how to handle them |

---

## Skill Categories

### Foundation (00) — Always Loaded First

| Skill | Purpose |
|-------|---------|
| **constitution** | Three Pillars (Satya, Dharma, Ahimsa) + amendment mechanism |
| **scratchpad** | `<scratchpad>` internal monologue, Eco vs Power mode selection, 4-step reasoning |
| **auditor** | Plan↔Diff alignment, protected terms enforcement, constitutional compliance |
| **librarian** | Fuzzy matching (Levenshtein + prefix), intent classification, multi-skill orchestration |

These are loaded **before every task**. They are non-negotiable.

### Discovery (10)

| Skill | Purpose |
|-------|---------|
| **requirements-elicitation** | Structured interviewing, functional/non-functional capture, assumption documentation |
| **domain-modeling** | Entity extraction, glossary maintenance, Protected Terms, ER diagrams |

### Architecture (20)

| Skill | Purpose |
|-------|---------|
| **system-design** | Component decomposition, scalability patterns, trade-off matrices |
| **api-contract-design** | Contract-first design, OpenAPI/SDL schemas, versioning strategy |
| **database-design** | Schema normalization, indexing, migration scripts, online DDL |
| **adr-management** | ADR lifecycle (Proposed → Accepted → Deprecated → Superseded) |

### Planning (20)

| Skill | Purpose |
|-------|---------|
| **task-decomposition** | Work breakdown, DAG ordering, T-shirt sizing, critical path |
| **risk-assessment** | Risk identification, 5×5 probability/impact matrix, mitigation strategies |
| **dependency-analysis** | Dependency graphs, circular detection, staleness/CVE audit |
| **estimation** | Three-point (PERT) estimation, relative sizing, confidence intervals |

### Implementation (30)

| Skill | Purpose |
|-------|---------|
| **code-generation** | Template expansion, language idiom enforcement, DRY deduplication |
| **refactoring** | Safe restructuring with test → refactor → test → revert protocol |
| **refactoring-suite** | Comprehensive refactoring patterns (extract, inline, rename) |
| **tdd-workflow** | Red-Green-Refactor cycle, test-first development, coverage targets |
| **cleanup** | Dead code removal, formatting, linting, import optimization |
| **api-implementation** | REST/GraphQL endpoint implementation, middleware |
| **data-access** | ORM patterns, repository pattern, query optimization |
| **error-handling** | Exception hierarchies, retry strategies, circuit breakers |

### Quality (40)

| Skill | Purpose |
|-------|---------|
| **code-review** | Review checklists, defect categories, severity classification |
| **test-strategy** | Test pyramid definition, framework selection, threshold negotiation |
| **testing-strategy** | Coverage analysis, test type selection, boundary conditions |
| **unit-testing** | AAA pattern, mock boundaries, edge-case coverage |
| **integration-testing** | Docker lifecycle, API/DB isolation, seed data versioning |
| **mutation-testing** | Mutant classification, equivalent mutant handling, score thresholds |
| **security-review** | OWASP Top 10, vulnerability scanning, secret detection |
| **performance-review** | Bottleneck identification, complexity analysis, caching strategies |

### Documentation (50)

| Skill | Purpose |
|-------|---------|
| **api-documentation** | Endpoint docs, OpenAPI specs, request/response examples |
| **inline-documentation** | JSDoc/docstrings, comment quality, self-documenting code |
| **decision-records** | ADR authoring (context → decision → consequences format) |
| **changelog-generation** | Conventional commits parsing, semantic versioning, release notes |

### Performance (50)

| Skill | Purpose |
|-------|---------|
| **profiling-analysis** | CPU/memory profiling, flame graphs, hotspot identification |
| **caching-strategy** | Cache design, TTL, invalidation, cache-aside/write-through |
| **db-tuning** | Query optimization, explain plans, index recommendations |

### Debugging (60)

| Skill | Purpose |
|-------|---------|
| **root-cause-analysis** | 5-whys, fault trees, git bisection, symptom-to-cause mapping |
| **log-analysis** | Log parsing, pattern recognition, event correlation, anomaly detection |
| **error-handling** | Exception hierarchies, retry strategies, graceful degradation |

### Security (60)

| Skill | Purpose |
|-------|---------|
| **threat-modeling** | STRIDE, attack surfaces, trust boundaries |
| **secure-coding-review** | Secure coding practices, OWASP, input validation |
| **auth-implementation** | Authentication/authorization, JWT, OAuth flows |
| **dependency-scanning** | CVE scanning, SBOM generation, supply chain security |

### DevOps (70)

| Skill | Purpose |
|-------|---------|
| **ci-pipeline** | Pipeline design, stage orchestration, deployment gates |
| **docker-containerization** | Dockerfile best practices, multi-stage builds, image optimization |
| **kubernetes-helm** | K8s manifests, Helm charts, resource limits, non-root |
| **terraform-iac** | Infrastructure as code, state management, drift detection |
| **monitoring-setup** | Observability pillars, SLIs/SLOs, alerting, distributed tracing |

### Collaboration (80)

| Skill | Purpose |
|-------|---------|
| **git-workflow** | Branching strategies, commit conventions, conflict resolution |
| **pr-management** | PR templates, review assignments, merge criteria |
| **pair-programming** | Driver/navigator roles, mob programming, knowledge transfer |
| **knowledge-sharing** | Documentation culture, wikis, runbooks, onboarding guides |

### Docs (80)

| Skill | Purpose |
|-------|---------|
| **openapi-specs** | OpenAPI spec generation and validation |
| **readme-generation** | README writing, badge generation, section management |
| **release-notes** | Release note generation from commit history |

### Maintenance (90)

| Skill | Purpose |
|-------|---------|
| **incident-response** | Incident triage, mitigation, postmortems, SLA tracking |
| **legacy-upgrade** | Legacy modernization, strangler fig pattern, codemods |
| **dependency-updates** | Automated updates, semver compatibility, lockfile management |
| **deprecation-management** | Sunset timelines, migration paths, consumer impact |
| **migration-planning** | Version upgrades, data migration, rollback strategies |
| **tech-debt-tracking** | Debt categorization, impact scoring, payoff prioritization |

---

## Eco vs Power Mode

```text
if task.changes_logic == false && task.files <= 2:
    mode = "eco"     # 🌿 Simple linear plan (1-3 steps)
else:
    mode = "power"   # ⚡ 4-Step Reasoning: Deductive → Inductive → Abductive → Analogical
```

When in doubt, default to **Power Mode**.

---

## Creating a New Skill

1. Copy `templates/skill-template.md` to the appropriate layer directory.
2. Fill in the YAML frontmatter (`name`, `description`, `version`, `dependencies`, `reasoning_mode`).
3. Write the markdown body:
   - **Context** — when to invoke
   - **Micro-Skills** — ordered steps with Eco/Power tags
   - **Inputs / Outputs** — typed parameters
   - **Scope** — explicit boundaries
   - **Guardrails** — hard constraints
   - **Ask-When-Ambiguous** — triggers + question templates
   - **Decision Criteria** — situation/action table
   - **Success Criteria** — verifiable checklist
   - **Failure Modes** — known failures with mitigations
   - **Audit Log** — structured log templates
   - **Examples** — before/after demos
   - **Edge Cases** — unusual inputs
4. Add an entry to `registry.yaml`.
5. The Librarian will auto-discover it on next invocation.

---

## License

[Apache License 2.0](LICENSE)
