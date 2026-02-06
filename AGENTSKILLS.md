# AgentSkills Garden 🌱

> *A composable library of AI agent skills designed to bridge the gaps AI cannot replicate.*

## Mission

AI has automated 80% of coding, but the remaining 20% requires human expertise that current models lack. This project aims to systematically address the 7 critical capability gaps where AI still falls short:

1. **Architectural reasoning** — Understanding hidden constraints and organizational context
2. **Debugging distributed systems** — Handling non-deterministic, timing-dependent failures
3. **Understanding legacy code** — Grasping why "messy" code survived for a reason
4. **Translating business needs** — Reading between the lines of stakeholder requests
5. **Strategic systems thinking** — Considering long-term maintenance and evolution
6. **Legal and ethical accountability** — Exercising professional judgment under uncertainty
7. **Human connection** — Building trust, mentoring, and managing emotional contexts

AgentSkills Garden provides a foundation of composable, model-agnostic skills that enable any AI model—from GPT-4 to Claude Opus and beyond—to perform at their highest potential when tackling these complex engineering challenges.

---

## Architecture

### Tiered Integration Model

Skills integrate with AI systems through three complementary mechanisms:

| Layer | Purpose | Integration Method |
|-------|---------|-------------------|
| **Tools** | Executable actions that interact with systems | Model Context Protocol (MCP), OpenAI Functions, Claude Tools |
| **Knowledge** | Static information, patterns, and best practices | RAG (Retrieval-Augmented Generation) |
| **Behavior** | Core identity and operational directives | System prompts and meta-prompts |

### Skill Hierarchy (Levels 0-4)

Skills are organized in a bottom-up taxonomy that enables composition from primitives to complex workflows:

| Level | Name | Description | Examples |
|-------|------|-------------|----------|
| **0** | Primitives | Atomic operations | `read`, `write`, `search`, `compare`, `transform` |
| **1** | Cognitive | Reasoning patterns | `decompose`, `synthesize`, `infer`, `verify`, `plan` |
| **2** | Task Skills | Domain-agnostic capabilities | `summarize_code`, `map_dependencies`, `clarify_requirement` |
| **3** | Domain Skills | Specialized expertise | Frontend, backend, DevOps, security, data engineering |
| **4** | Compound Skills | End-to-end workflows | Feature implementation, bug investigation, system design |

### Technical Architecture

Each skill is a **containerized microservice** with a standardized HTTP API:

```
Skill Package
├── schema.json          # JSON Schema definition (interface contract)
├── main.py             # Python implementation
├── test_main.py        # Unit tests with fixtures
├── Dockerfile          # Container definition
└── README.md           # Auto-generated documentation
```

**Standard HTTP Contract:**
- `POST /execute` — Execute the skill with provided inputs
- `GET /health` — Liveness check for orchestration
- `GET /describe` — Return the skill's JSON Schema

---

## Skill Catalog

<!-- AUTO-GENERATED: Run `python tools/generate_docs.py` to update -->

### Domain: Code Understanding (Gap #3)

| Skill ID | Level | Purpose | Status |
|----------|-------|---------|--------|
| `summarize_code` | 1 | Summarize file/function with context | 🚧 Planned |
| `analyze_history` | 2 | Explain *why* code exists via git history | 🚧 Planned |
| `map_dependencies` | 1 | Trace imports/dependencies for a module | 🚧 Planned |
| `detect_smells` | 2 | Identify patterns that "survived for a reason" | 🚧 Planned |

### Domain: Translate Business Needs (Gap #4)

| Skill ID | Level | Purpose | Status |
|----------|-------|---------|--------|
| `clarify_requirement` | 1 | Ask probing questions on vague requirements | 🚧 Planned |
| `analyze_tradeoffs` | 2 | Surface hidden tradeoffs in requests | 🚧 Planned |
| `translate_stakeholder` | 2 | Convert business-speak → technical spec | 🚧 Planned |

---

## Philosophy: Bridging the Gaps

### Gap #3: Understanding Legacy Code

**Problem:** AI sees messy code and immediately suggests refactoring. It lacks the experience to understand that "technical debt" often encodes hard-won solutions to non-obvious problems.

**Solution:** Skills that analyze:
- Git history to surface the *why* behind decisions
- Dependency graphs to reveal hidden coupling
- Code patterns that indicate survival of real-world pressures
- Change frequency to identify stable vs. volatile areas

**Principle:** *Preservation before transformation. Understand first, refactor second.*

### Gap #4: Translating Business Needs

**Problem:** When a stakeholder says "make it faster," AI starts optimizing code. It doesn't ask: "Which operations? For which users? At what cost?"

**Solution:** Skills that:
- Extract implicit requirements through structured questioning
- Surface tradeoffs between speed, cost, complexity, and maintainability
- Translate vague business language into testable technical specifications
- Identify unstated assumptions and constraints

**Principle:** *Clarify before coding. Every requirement has a hidden cost.*

---

## Contributor's Guide

### Getting Started

1. **Setup development environment:**
   ```bash
   git clone https://github.com/dhruvinrsoni/agentskills-garden.git
   cd agentskills-garden
   pip install -e ".[dev]"
   ```

2. **Explore existing skills:**
   ```bash
   ls skills/
   python tools/generate_docs.py  # Generate documentation
   ```

3. **Run tests:**
   ```bash
   pytest skills/ --cov
   ```

### Adding a New Skill

1. **Choose the appropriate level and domain** from the taxonomy above
2. **Create skill directory:**
   ```bash
   mkdir -p skills/{domain}/{skill_name}
   ```
3. **Define the interface in `schema.json`** following `schemas/skill.schema.json`
4. **Implement in `main.py`** with FastAPI endpoints
5. **Write tests in `test_main.py`** with clear fixtures
6. **Create `Dockerfile`** extending `infra/Dockerfile.base`
7. **Generate docs:** `python tools/generate_docs.py`
8. **Validate:** `pytest` and `docker build`

### Commit Conventions

We use **Conventional Commits** with skill scopes:

```
feat(summarize_code): add support for TypeScript files
fix(analyze_history): handle repositories without initial commit
docs(clarify_requirement): add examples for stakeholder translation
test(map_dependencies): add fixture for circular imports
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

**Scopes:** Use the skill's `snake_case` ID

### Pull Request Process

1. **Fork** the repository
2. **Create a feature branch:** `git checkout -b feat/your-skill-name`
3. **Sign the CLA** (see `.github/CLA.md`)
4. **Make changes** following conventions above
5. **Ensure CI passes:** All tests, linting, and schema validation
6. **Submit PR** with clear description and examples

---

## Validation & Quality

### Three-Tiered Testing Pyramid

| Layer | Method | Frequency | Purpose |
|-------|--------|-----------|---------|
| **Unit Tests** | Pytest with fixtures | Every commit (CI) | Verify code correctness |
| **LLM-as-Judge** | Model evaluations on golden dataset | Nightly | Assess output quality |
| **Human Review** | Manual evaluation with checklist | Per release | Validate real-world utility |

### Running Evaluations

```bash
# Unit tests (fast)
pytest skills/ --cov --cov-report=html

# Quality evaluations (requires LLM access)
python evals/judge.py --dataset evals/golden_dataset/

# Manual review checklist
cat evals/human_review_checklist.md
```

---

## License & Contributions

This project is licensed under **Apache License 2.0** — a business-friendly open source license with strong patent protections.

All contributors must sign the **Contributor License Agreement** (see `.github/CLA.md`) to grant the project necessary rights for stewardship and future flexibility.

---

## Project Status

**Current Phase:** Phase 0 — Repository Scaffolding ✅  
**Next Milestone:** Phase 2 — First Code Understanding Skills 🚧

**Roadmap:**
- ✅ Phase 0: Repository scaffolding
- 🚧 Phase 1: Skill contract definition
- 🚧 Phase 2: Code understanding domain (Gap #3)
- 📋 Phase 3: Translate needs domain (Gap #4)
- 📋 Phase 4: Evaluation infrastructure
- 📋 Phase 5: Integration layer (MCP, OpenAI, system prompts)

---

## Contact & Community

- **Repository:** [github.com/dhruvinrsoni/agentskills-garden](https://github.com/dhruvinrsoni/agentskills-garden)
- **Issues:** Use GitHub Issues for bug reports and feature requests
- **Discussions:** Use GitHub Discussions for questions and ideas

---

*Remember as (G)iraffe (C)an (S)ee (E)verything: **Goal → Context → Source → Expectations***
