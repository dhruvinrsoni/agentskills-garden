---
name: librarian
description: >
  Skill discovery and routing engine. Given a user's intent (even with
  typos or vague phrasing), finds and loads the most relevant skill(s)
  from the registry using fuzzy matching and semantic search.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: 1.0.0
  dependencies: constitution
  reasoning_mode: linear
---


# Librarian — Skill Discovery & Routing

> _"You don't need to know the skill's name. Just tell me what you want to do."_

## Context

The Librarian is invoked whenever the user's request doesn't map directly
to a known skill name. It acts as a router: understanding intent, correcting
typos, and loading the right skill(s) — even when the user's prompt is
informal, misspelled, or uses different terminology.

---

## Micro-Skills

### 1. Intent Classification 🌿 (Eco Mode)

**Goal:** Parse the user's request and classify their intent.

**Steps:**

1. Extract keywords from the user's request.
2. Normalize: lowercase, strip punctuation, expand common abbreviations
   (`impl` → `implementation`, `k8s` → `kubernetes`, `tf` → `terraform`,
    `perf` → `performance`, `sec` → `security`, `docs` → `documentation`).
3. Map intent to a category:

| Intent Signals | Category | Example Skills |
|----------------|----------|----------------|
| "clean", "format", "rename", "tidy" | Implementation | `cleanup.md` |
| "refactor", "extract", "inline", "decouple" | Implementation | `refactoring-suite.md` |
| "test", "spec", "coverage", "assert" | Quality | `unit-testing.md`, `test-strategy.md` |
| "deploy", "ci", "pipeline", "docker", "helm" | DevOps | `ci-pipeline.md`, `docker-containerization.md` |
| "secure", "auth", "vulnerability", "owasp" | Security | `secure-coding-review.md`, `auth-implementation.md` |
| "perf", "slow", "cache", "index", "optimize" | Performance | `profiling-analysis.md`, `caching-strategy.md` |
| "design", "architecture", "adr", "schema" | Architecture | `system-design.md`, `database-design.md` |
| "doc", "readme", "changelog", "api spec" | Documentation | `readme-generation.md`, `openapi-specs.md` |
| "incident", "outage", "alert", "debug prod" | Maintenance | `incident-response.md` |
| "upgrade", "migrate", "legacy", "version" | Maintenance | `legacy-upgrade.md` |
| "require", "scope", "goal", "what should" | Discovery | `requirements-elicitation.md` |

4. If intent matches multiple categories → present options to user.

### 2. Fuzzy Matching 🌿 (Eco Mode)

**Goal:** Handle typos, abbreviations, and partial names.

**Algorithm:**

1. **Exact match** — check `registry.yaml` for exact skill name.
2. **Prefix match** — `"clean"` matches `cleanup`, `"docker"` matches
   `docker-containerization`.
3. **Levenshtein distance** — if no prefix match, compute edit distance
   against all skill names. Threshold: distance ≤ 2 for names ≤ 8 chars,
   distance ≤ 3 for longer names.
4. **Tag matching** — check skill tags in `registry.yaml` metadata.
5. **Fallback** — if no match found, ask the user to clarify.

**Common Typo Map:**

```text
"clnup"       → cleanup
"refactr"     → refactoring-suite
"kubernets"   → kubernetes-helm
"teraform"    → terraform-iac
"incidnet"    → incident-response
"securty"     → secure-coding-review
"profilng"    → profiling-analysis
```

### 3. Multi-Skill Orchestration 🌿 (Eco Mode)

**Goal:** When a task requires multiple skills, determine load order.

**Steps:**

1. Identify all required skills from the intent.
2. Load each skill's `dependencies` from frontmatter.
3. Build a dependency graph (topological sort).
4. Present the execution plan to the user:
   ```text
   Your request involves these skills (in order):
   1. requirements-elicitation (gather scope)
   2. api-contract-design (define the contract)
   3. api-implementation (build the handlers)
   4. unit-testing (verify behavior)
   Proceed? [Y/n]
   ```
5. Load skills in dependency order.

### 4. Prompt Cleanup 🌿 (Eco Mode)

**Goal:** Clean user input without losing deliberate content.

**Rules:**

- Fix obvious typos in natural language portions of the prompt.
- **NEVER** "fix" content inside code blocks, filenames, variable names,
  or quoted strings — these may be intentional.
- If the user says "rename `wrng_speling` to `right_spelling`", preserve
  `wrng_speling` exactly (it's the search target).
- Expand common shorthand: "pls" → "please", "impl" → "implement",
  "fn" → "function" (only in natural language, not in code).

---

## Inputs

| Parameter      | Type     | Required | Description                       |
|----------------|----------|----------|-----------------------------------|
| `user_request` | `string` | yes      | The raw user prompt/request       |
| `registry`     | `string` | no       | Path to registry.yaml (auto-detected) |

## Outputs

| Field            | Type       | Description                         |
|------------------|------------|-------------------------------------|
| `matched_skills` | `string[]` | List of skill paths to load         |
| `confidence`     | `number`   | Match confidence (0.0 – 1.0)       |
| `execution_plan` | `string`   | Ordered plan for multi-skill tasks  |
| `clarification`  | `string`   | Question for user (if ambiguous)    |

---

## Guardrails

- Never load a skill silently if confidence < 0.7 — ask the user.
- Always respect skill dependencies — load prerequisites first.
- If multiple skills match equally, present ALL options (don't guess).
- The Librarian itself has no side effects — it only reads and routes.

## Ask-When-Ambiguous

- Low confidence match → "I found these skills that might help:
  [list]. Which one(s) should I load?"
- Overlapping skills → "Both `cleanup` and `refactoring-suite` could
  apply here. Cleanup handles cosmetic changes; Refactoring handles
  structural changes. Which do you need?"
- No match at all → "I couldn't find a matching skill. Could you
  describe what you're trying to do in different words?"

## Success Criteria

- Correct skill(s) loaded for the user's intent.
- Typos handled gracefully without misrouting.
- Multi-skill execution order respects dependencies.
- User is never left without guidance.

## Failure Modes

- No match found → ask user to rephrase or list available categories.
  **Recovery:** Show the full skill index grouped by category.
- Wrong skill loaded → user corrects, Librarian re-routes.
  **Recovery:** "Got it. Loading [correct skill] instead."
- Registry file missing or corrupt → fall back to directory-based scanning.

## Audit Log

- User's original request (raw).
- Matched skill(s) and confidence scores.
- Whether user was asked for clarification.
- Final skills loaded.
