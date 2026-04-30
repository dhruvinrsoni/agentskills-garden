# Agent Skills Garden 🌱

> *A hierarchical, constitution-driven skill library that serves as the "brain" for AI agents.*
> 
> *82 skills across 15 categories — these hierarchical skills enable any model to reason as well as the best frontier models.*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Skills are markdown files with YAML frontmatter that agents discover at runtime via a central registry. Every action is governed by a **Constitution** rooted in three principles:

| Pillar | Sanskrit | Meaning |
|--------|----------|---------|
| **Truth** | Satya | Deterministic, reproducible outputs. No hallucinations. |
| **Safety** | Dharma | Ask-first policy. Prefer the smallest change. |
| **Non-Destruction** | Ahimsa | Preview diffs before applying. Always reversible. |

Inspired by the [Agent Skills](https://agentskills.io/) open format.

Alongside the Constitution, the **[Pragmatism (Aparigraha)](#pragmatism-25--aparigraha-)** category gives the garden its bias for *real, ongoing business projects*: the agent *checks* before creating, *conforms* within the scope of the change, stays *surgical*, and *validates edge cases* before trusting any reuse or improvement of existing code. Direction-of-thought, not rigid rule.

---

## Quick Start

The supported install path is the **bridge-link** workflow described below — one
Windows junction (or POSIX symlink) makes the garden's `skills/` folder live-visible
inside any consumer repo, with no copy step.

> **Looking for the old `setup_skills.sh` / `setup_skills.ps1` installers?**
> They have been moved to [`legacy/`](legacy/) and are preserved for historical
> reference only. They are significantly out of sync with the current 88-skill
> hierarchical layout and will not be regenerated. See [`legacy/README.md`](legacy/README.md).

---

## Use in Other Repos (Bridge Link)

Treat this garden as a **single source of truth** for every other repo on your
machine. A single Windows junction makes the `skills/` folder live-visible at a
conventional path (`.cursor/skills`, `.claude/skills`, `.github/skills`, or
`skills`) inside any consumer repo. Edit or `git pull` here once — all
consumer repos see the change immediately. No copies, no sync step.

**First-machine setup (one time):**

```powershell
iwr https://raw.githubusercontent.com/dhruvinrsoni/agentskills-garden/main/scripts/setup-garden.ps1 | iex
```

This clones the garden to a fork-safe path (`<root>\github\<gh-user>\agentskills-garden`)
and persists settings in `~/.gitconfig` under `[agentskills]`.

**Per consumer repo (run inside the repo):**

```powershell
# Default: link the garden's skills into .cursor/skills
& "<garden>\scripts\link-skills.ps1"

# Pick a different convention
& "<garden>\scripts\link-skills.ps1" -Target claude      # .claude/skills
& "<garden>\scripts\link-skills.ps1" -Target github      # .github/skills
& "<garden>\scripts\link-skills.ps1" -Target generic     # skills
& "<garden>\scripts\link-skills.ps1" -Target custom -LinkPath ".agent/skills"

# Inspect / remove
& "<garden>\scripts\link-skills.ps1" -Status
& "<garden>\scripts\link-skills.ps1" -Unlink
```

Background, design decisions, and troubleshooting notes live in
[docs/skills-bridge.md](docs/skills-bridge.md).

> macOS/Linux support (via `ln -s`) is planned; the git-config keys and CLI
> surface will stay identical.

---

## Repository Structure

```
agentskills-garden/
├── registry.yaml                          # Single source of truth — skill index
├── skills/
│   ├── 00-foundation/        (8 skills)   # Always loaded first
│   │   └── constitution/
│   │       └── SKILL.md                   # Each skill is a directory + SKILL.md
│   ├── 10-discovery/         (3 skills)   # Requirements, domain modeling, PRD
│   ├── 20-architecture/      (4 skills)   # System, API, DB, ADR design
│   ├── 20-planning/          (4 skills)   # Task decomposition, risk, estimation
│   ├── 25-pragmatism/        (6 skills)   # Aparigraha — check, conform, stay surgical
│   ├── 30-implementation/    (9 skills)   # Code gen, refactoring, TDD, cleanup
│   ├── 40-quality/           (8 skills)   # Reviews, testing strategies, mutation
│   ├── 50-documentation/     (4 skills)   # API docs, ADRs, changelogs
│   ├── 50-performance/       (3 skills)   # Caching, DB tuning, profiling
│   ├── 60-debugging/         (3 skills)   # Root cause, log analysis, error handling
│   ├── 60-security/          (4 skills)   # Auth, threat modeling, secure coding
│   ├── 70-devops/            (5 skills)   # CI/CD, Docker, K8s, Terraform, monitoring
│   ├── 80-collaboration/     (4 skills)   # Git workflow, PRs, pair programming
│   ├── 80-docs/              (3 skills)   # OpenAPI, README, release notes
│   └── 90-maintenance/       (7 skills)   # Incidents, migrations, tech debt, deprecation
├── templates/
│   └── skill-template.md                  # Boilerplate for new skills
├── scripts/
│   ├── link-skills.ps1                    # Per-consumer bridge-link manager (Windows)
│   └── setup-garden.ps1                   # First-machine clone + git config setup
├── docs/
│   └── skills-bridge.md                   # Bridge-link design notes + troubleshooting
├── setup_skills.sh                        # Portable installer (Bash)
└── setup_skills.ps1                       # Portable installer (PowerShell)
```

**Total: 82 skills + 1 template + registry**

---

## Skill Format (SKILL.md)

Every skill follows the [agentskills.io specification](https://agentskills.io/specification). Each skill is a **directory** named after the skill, containing a `SKILL.md` file:

```
skills/<category>/<skill-name>/
└── SKILL.md
```

Frontmatter schema:

```yaml
---
name: cleanup                    # required: lowercase alphanumeric + hyphens, max 64 chars
description: >                   # required: 1-1024 chars, what it does + when to use it
  Remove noise, enforce formatting, and safely rename identifiers.
license: Apache-2.0              # optional
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:                        # optional: arbitrary key-value pairs
  version: "1.0.0"
  dependencies: "constitution, scratchpad, auditor"
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
| **pragmatism** | Aparigraha — non-accumulation. Check-before-create, conform-before-improve, surgical-before-sweeping, validate-before-trust. The driving force for working on real ongoing business projects |

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

### Pragmatism (25) — Aparigraha (अपरिग्रह)

> *Direction-of-thought, not rigid rule.* The agent *checks* before creating, *conforms* within scope, stays *surgical*, and *validates edge cases* before trusting any reuse or improvement of existing code. Built for real, ongoing business projects where the goal is *maximum output, minimum effort, zero maintenance, maximum continuity with what's already there* — not greenfield ideals. Checking is mandatory; reusing is conditional.

| Skill | Purpose |
|-------|---------|
| **reuse-first** | Before writing any new utility, scan codebase + dependencies for an equivalent. Reuse only after fit and edge-case validation; otherwise document why and write fresh |
| **dependency-utility-scout** | Mine declared dependencies (Apache Commons, Lodash, Guava, more-itertools, …) and produce a per-capability inventory other skills consult — advisory, never auto-rewrites |
| **style-conformance** | Detect existing conventions (naming, formatting, errors, logging, tests) and produce a house-style profile downstream skills consult — awareness, not enforcement |
| **minimal-diff** | Smallest correct change that solves the problem. Diff-size caps, drive-by detection, reversibility checks, and commit splitting when concerns are tangled |
| **chesterton-fence** | Before deleting or refactoring "weird" code, reconstruct intent from history, tests, comments, ADRs, and call-graph; produce a memo plus an edge-case checklist that gates the change |
| **brownfield-onboarding** | First-touch protocol — read README/AGENTS.md/ADRs, find build/test/CI commands, hot zones, entry points, and test layout; emit an onboarding cheat-sheet other Aparigraha skills consume |

The category is paired with the always-loaded foundation skill `pragmatism` (Aparigraha — non-accumulation), which codifies the four directional principles (*check-before-create*, *conform-before-improve*, *surgical-before-sweeping*, *validate-before-trust*) and the cross-cutting edge-case validation clause every reuse or improvement decision must satisfy.

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

1. Create a directory `skills/<category>/<skill-name>/` where `<skill-name>` is lowercase with hyphens.
2. Copy `templates/skill-template.md` into that directory as `SKILL.md`.
3. Fill in the YAML frontmatter — `name` must match the directory name exactly:
   ```yaml
   name: skill-name
   description: What it does and when to use it (1-1024 chars).
   license: Apache-2.0
   compatibility: Designed for Claude Code and compatible AI agent environments
   metadata:
     version: "0.1.0"
     dependencies: "constitution, scratchpad"
     reasoning_mode: linear   # linear | plan-execute | tdd | mixed
   ```
4. Write the markdown body:
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
5. Add an entry to `registry.yaml` pointing to `skills/<category>/<skill-name>/SKILL.md`.
6. The Librarian will auto-discover it on next invocation.

---

## License

[Apache License 2.0](LICENSE)
