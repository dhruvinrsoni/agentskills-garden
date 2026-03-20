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
| "score", "rank", "weight", "evaluate", "prioritize" | Architecture | `scorer-pipeline` |
| "config", "settings", "schema", "defaults", "feature flag" | Architecture | `schema-driven-config` |
| "pipeline context", "middleware", "pre-compute", "shared context" | Architecture | `pipeline-context` |
| "circuit breaker", "retry", "resilience", "fallback", "bulkhead" | Implementation | `resilience-patterns` |
| "two-pass", "metric gate", "threshold", "measurement vs gating" | Quality | `two-pass-analysis` |
| "progressive", "two-phase", "fast then enrich", "phase 1 phase 2" | Performance | `progressive-execution` |
| "memory pressure", "resource budget", "constraint", "degrade gracefully" | Performance | `resource-awareness` |

4. If intent matches multiple categories → present options to user.

### 2. Graduated Matching 🌿 (Eco Mode)

**Goal:** Handle typos, abbreviations, and partial names using graduated
quality tiers instead of binary match/no-match.

**Graduated Tier System:**

Each candidate skill is scored against the query. The highest-tier match wins.
If multiple skills tie at the same tier, present all to the user.

| Tier | Match Type | Weight | When it fires |
|------|-----------|--------|---------------|
| 1 | **EXACT** | 1.00 | Query exactly equals a skill name |
| 2 | **PREFIX** | 0.85 | Query is a prefix of a skill name (`"clean"` → `cleanup`) |
| 3 | **SUBSTRING** | 0.65 | Query appears anywhere in name or description (`"pipe"` → `ci-pipeline`) |
| 4 | **TAG** | 0.50 | Query matches a tag in `registry.yaml` (`"resilience"` → `resilience-patterns`) |
| 5 | **SEMANTIC** | 0.35 | **Nano: Levenshtein Distance** — edit distance ≤ 2 for names ≤ 8 chars, ≤ 3 for longer. Also: **Nano: Token Normalization** — strip hyphens, lowercase, split compound words before comparing. |
| 6 | **NONE** | 0.00 | No match → ask the user to clarify |

**Algorithm:**

1. **Nano: Token Normalization** — normalize the query: lowercase, strip
   hyphens, split compound words (`"dockercontainer"` → `["docker", "container"]`).
2. Run query against all skill names at Tier 1 (EXACT). If hit → return.
3. Run Tier 2 (PREFIX). If hit → return.
4. Run Tier 3 (SUBSTRING) against names + descriptions. Collect candidates.
5. Run Tier 4 (TAG) against registry tags. Merge with Tier 3 candidates.
6. **Nano: Levenshtein Distance** — for remaining unmatched, compute edit
   distance. Threshold: ≤ 2 for short names, ≤ 3 for long names.
7. If multiple candidates, rank by tier weight. Present top matches to user.
8. If zero candidates → NONE → ask user to clarify.

**Common Typo Map (shortcuts for Tier 5):**

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

### 4. Activation Awareness 🌿 (Eco Mode)

**Goal:** Surface skills proactively when context matches activation patterns.

**Steps:**

1. Skills declare activation patterns in their Context sections and optional
   `activation_triggers` metadata.
2. When routing, match user intent against skill descriptions AND Context
   trigger patterns — not just skill names.
3. During ongoing tasks, monitor for domain shifts (integrates with
   `orchestrator` skill for mid-task injection).
4. Surface skill suggestions proactively when context keywords match,
   presented as pragya direction checkpoints.

**Example triggers:**

| Pattern | Skill | Reason |
|---------|-------|--------|
| "cleanup", "reduce", "trim", "optimize" | `repo-maintenance` | Repo-wide cleanup intent |
| "uncertain", "not sure", "which approach" | `pragya` | Direction-seeking needed |
| "too many tokens", "budget", "expensive" | `token-efficiency` | Resource optimization |
| "deploy", "pipeline", "CI" | `ci-pipeline` | DevOps context detected |

### 5. Prompt Cleanup 🌿 (Eco Mode)

**Goal:** Clean user input without losing deliberate content.

**Rules:**

- Fix obvious typos in natural language portions of the prompt.
- **NEVER** "fix" content inside code blocks, filenames, variable names,
  or quoted strings — these may be intentional.
- If the user says "rename `wrng_speling` to `right_spelling`", preserve
  `wrng_speling` exactly (it's the search target).
- Expand common shorthand: "pls" → "please", "impl" → "implement",
  "fn" → "function" (only in natural language, not in code).

### 6. Usage-History Weighting 🌿 (Eco Mode)

**Goal:** Bias routing toward skills the user has recently loaded and found useful,
making the librarian feel like it "remembers" the user's workflow.

**Steps:**

1. After each successful skill load, record the event:
   `{ skill: "<name>", timestamp: <ISO>, session: "<id>" }`.
2. **Nano: Recency-Frequency Score** — `score = (0.6 × recency_decay) + (0.4 × frequency_ratio)`
   where `recency_decay = 1 / (1 + days_since_last_use)`,
   `frequency_ratio = skill_uses / max_skill_uses_across_all_skills`.
3. Apply as a post-tier modifier in Graduated Matching (Micro-Skill 2):
   `final_score = tier_score + (history_score × 0.10)`.
4. Present history-boosted candidates with a note:
   `"(recently used)"` appended to the skill name in option lists.

**Constraints:**

| Rule | Detail |
|------|--------|
| Boost cap | +0.10 maximum — history never overrides tier logic |
| Minimum tier | Only applies when `tier_score ≥ 0.35` (Semantic tier) — prevents ghost matches |
| Cold start | No boost until ≥ 3 skill loads recorded in session |
| Decay | Score decays to zero after 30 days of non-use |
| Scope | Session-scoped by default — no persistent storage required |

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
- History boost must never promote a sub-0.7 match into auto-load territory.
- Always respect skill dependencies — load prerequisites first.
- If multiple skills match equally, present ALL options (don't guess).
- The Librarian itself has no side effects — it only reads and routes.
- Usage data is session-scoped — no persistent storage of user behavior.

## Ask-When-Ambiguous

- Low confidence match → "I found these skills that might help:
  [list]. Which one(s) should I load?"
- Overlapping skills → "Both `cleanup` and `refactoring-suite` could
  apply here. Cleanup handles cosmetic changes; Refactoring handles
  structural changes. Which do you need?"
- No match at all → "I couldn't find a matching skill. Could you
  describe what you're trying to do in different words?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Exact name match | Load immediately (Tier 1) |
| Multiple skills tie at same tier | Present all options to user |
| Previously used skill matches ambiguous query | Apply history boost (+0.10 max), note "(recently used)" |
| Confidence < 0.7 after all tiers + history | Ask user to clarify — never auto-load |
| Query matches no skill at any tier | Show full skill index grouped by category |

## Success Criteria

- Correct skill(s) loaded for the user's intent.
- Typos handled gracefully without misrouting.
- Multi-skill execution order respects dependencies.
- User is never left without guidance.
- Frequently used skills surface faster in ambiguous queries.

## Failure Modes

- No match found → ask user to rephrase or list available categories.
  **Recovery:** Show the full skill index grouped by category.
- Wrong skill loaded → user corrects, Librarian re-routes.
  **Recovery:** "Got it. Loading [correct skill] instead."
- Registry file missing or corrupt → fall back to directory-based scanning.

## Audit Log

- User's original request (raw).
- Matched skill(s) and confidence scores.
- History boost applied (if any): skill name, history score, final adjusted score.
- Whether user was asked for clarification.
- Final skills loaded.
