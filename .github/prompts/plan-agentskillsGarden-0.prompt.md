# Plan: AgentSkills-Garden Foundation (FINAL DRAFT)

Build a library of composable, model-agnostic AI agent skills to bridge the 7 capability gaps AI cannot replicate. Skills are JSON Schema-defined, Python-implemented (`snake_case`), containerized microservices with standardized HTTP APIs. Start with **Understanding Legacy Code** and **Translating Business Needs** domains. Tiered integration: Tools for action, RAG for knowledge, System Prompts for behavior. Apache-2.0 license with CLA. Monorepo semver with Conventional Commits.

---

## Steps

### Phase 0: Repository Scaffolding

1. Create `AGENTSKILLS.md` — "Sutra" master document:
   - **Mission**: Why this project exists (bridge the 7 gaps)
   - **Architecture**: Tiered hybrid model, skill levels 0-4
   - **Skill Catalog**: Auto-generated table of available skills
   - **Philosophy**: Problem→Solution framing for each gap
   - **Contributor's Guide**: How to add skills, commit conventions

2. Create directory structure:
   ```
   skills/
   ├── 01_code_understanding/
   │   ├── summarize_code/
   │   │   ├── schema.json
   │   │   ├── main.py
   │   │   ├── test_main.py
   │   │   └── Dockerfile
   │   └── ...
   ├── 02_translate_needs/
   │   └── ...
   schemas/
   ├── skill.schema.json       # Meta-schema for all skills
   └── http_contract.schema.json
   infra/
   ├── Dockerfile.base
   └── docker-compose.yml
   evals/
   ├── golden_dataset/
   ├── judge.py
   └── human_review_checklist.md
   tools/
   └── generate_docs.py
   .github/
   ├── workflows/
   │   ├── ci.yml
   │   └── nightly_evals.yml
   └── CLA.md
   ```

3. Create `pyproject.toml` — dependencies: `pytest`, `pydantic`, `fastapi`, `uvicorn`, `jsonschema`

4. Update `LICENSE` to Apache-2.0 (if not already)

5. Create `.github/CLA.md` — Contributor License Agreement

6. Create `.github/workflows/ci.yml`:
   - Lint Conventional Commits
   - Run pytest
   - Build container images
   - Validate schemas

### Phase 1: Skill Contract Definition

1. Create `schemas/skill.schema.json`:
   ```json
   {
     "id": "string (snake_case)",
     "name": "string (human-readable)",
     "version": "string (semver)",
     "level": "0-4",
     "domain": "string",
     "description": { "short": "...", "long": "..." },
     "interface": { "inputs": {}, "outputs": {}, "context_required": [] },
     "dependencies": ["skill_ids"],
     "validation": { "test_cases": [], "invariants": [] }
   }
   ```

2. Create `schemas/http_contract.schema.json`:
   - `POST /execute` — run the skill
   - `GET /health` — liveness check
   - `GET /describe` — return skill schema

3. Create `infra/Dockerfile.base`:
   - Python 3.11 slim base
   - FastAPI + Uvicorn
   - Standard entrypoint pattern

4. Create `tools/generate_docs.py` — reads schemas, generates Markdown

### Phase 2: Code Understanding Domain (Priority Gap #3)

| Skill ID | Level | Purpose |
|----------|-------|---------|
| `summarize_code` | 1 | Summarize file/function with context |
| `analyze_history` | 2 | Explain *why* code exists via git history |
| `map_dependencies` | 1 | Trace imports/dependencies for a module |
| `detect_smells` | 2 | Identify patterns that "survived for a reason" |

### Phase 3: Translate Needs Domain (Priority Gap #4)

| Skill ID | Level | Purpose |
|----------|-------|---------|
| `clarify_requirement` | 1 | Ask probing questions on vague requirements |
| `analyze_tradeoffs` | 2 | Surface hidden tradeoffs in requests |
| `translate_stakeholder` | 2 | Convert business-speak → technical spec |

### Phase 4: Evaluation Infrastructure

1. `evals/golden_dataset/` — curated input/expected-output pairs
2. `evals/judge.py` — LLM-as-judge evaluation harness
3. `evals/human_review_checklist.md` — manual review criteria
4. `.github/workflows/nightly_evals.yml` — scheduled runs

### Phase 5: Integration Layer

1. `integrations/mcp/` — Model Context Protocol server
2. `integrations/openai/` — Function definitions generator
3. `integrations/system_prompts/` — Composable prompt templates

---

## Verification

| Layer | Command/Check |
|-------|---------------|
| Schema validity | `python -m jsonschema --instance skill.json schemas/skill.schema.json` |
| Unit tests | `pytest skills/ --cov` |
| Container health | `curl http://localhost:8000/health` |
| Integration | MCP client test + OpenAI function call test |
| Quality (nightly) | `python evals/judge.py --dataset golden_dataset/` |

---

## Decisions Summary

| Decision | Choice |
|----------|--------|
| Skill format | JSON Schema + Python + auto-gen Markdown |
| Skill naming | `snake_case` (PEP 8 aligned) |
| Integration | Tiered hybrid: Tools / RAG / System Prompts |
| Priority gaps | #3 Legacy code, #4 Business translation |
| Container | HTTP API per skill (`/execute`, `/health`, `/describe`) |
| Versioning | Monorepo semver + Conventional Commits |
| License | Apache-2.0 with Contributor License Agreement |

---

## The 7 Gaps (Reference)

1. **Architectural reasoning**: AI suggests textbook solutions. It doesn't know your company's hidden constraints, or regulatory requirements.
2. **Debugging distributed systems**: AI was trained on static code. It has never experienced a race condition at 2am on a Friday.
3. **Understanding legacy code**: AI sees messy code and wants to refactor it. A human engineer knows that messy code has survived for a reason. ← *PRIORITY*
4. **Translating business needs**: When a stakeholder says "make it faster". AI starts coding. A human asks: "How much are you willing to pay for that speed?" ← *PRIORITY*
5. **Strategic Systems thinking**: AI optimizes for today. Engineers think about the future. Who maintains 10,000 AI-generated test cases when the schema changes?
6. **Legal and ethical accountability**: AI cannot be sued. You can. If you blindly accept AI code and it causes a data breach, you are liable.
7. **Human connection**: AI can suggest a fix during an outage. It cannot calm the room, make the call, or mentor the junior engineer who is watching.

---

## Skill Levels (Taxonomy)

| Level | Name | Description |
|-------|------|-------------|
| 0 | Primitives | Atomic operations: read, write, transform, compare, search, communicate |
| 1 | Cognitive | Reasoning patterns: decomposition, synthesis, inference, verification, planning, reflection |
| 2 | Task Skills | Domain-agnostic: code understanding, code modification, information gathering, decision support |
| 3 | Domain Skills | Specialized: frontend, backend, DevOps, data, security |
| 4 | Compound Skills | Workflows: feature implementation, bug investigation, code review, system design |

---

## Next Steps

- [ ] Approve plan or request refinements
- [ ] Begin Phase 0: Repository Scaffolding
- [ ] Create first skill: `summarize_code`
