---
name: plan-as-agreement
description: >
  Writes the plan.md as a fit-for-purpose agreement between user and agent.
  Auto-selects one of 16 named plan formats (or a 2-3 format hybrid) based on
  task signals — top-level, file-by-file, exact-diff, pseudocode-first,
  component-tree, sequence-diagram, state-machine, trace-before-patch,
  stats-driven-cleanup, spike, api-contract, data-migration, benchmark,
  multi-pr-staged, security-patch, test-coverage. Composes task-decomposition,
  risk-assessment, estimation, root-cause-analysis when needed. Complements
  Claude Code, Cursor, and Cline plan-mode harnesses — doesn't replace them.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
domain: engineering
status: published
tags: [category, design, planning, advisory]
keywords: []
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, task-decomposition, risk-assessment, root-cause-analysis, style-conformance"
  reasoning_mode: plan-execute
  skill_type: standard
  activation_triggers: "plan, plan.md, implementation plan, plan mode, agreement, planning, plan format, exact-diff plan, file-by-file plan, trace plan, stats cleanup, spike, hypothesis plan, migration plan, benchmark plan, multi-PR plan, security patch plan, test coverage plan"
---


# Plan-as-Agreement — Fit-for-Purpose Implementation Plans

> _"The plan.md is the agreement layer. Spend tokens here. Save them everywhere else."_

## Context

Every modern agentic coding harness — Claude Code (`~/.claude/plans/`), Cursor Plan Mode (`.cursor/plans/`), Cline's "Plan → Preview → Apply" — persists a markdown plan as the gate between intent and execution. The plan.md is the highest-leverage single document in an agentic session: a tight plan reviewed in 2 minutes saves 20–60 minutes of wrong-turn execution downstream.

These harnesses do not, however, shape the plan for the task. A 23-line comment-trim PR receives the same scaffold as a new authentication subsystem. This skill closes that gap: it selects from a library of 16 named formats (and supports 2–3 format hybrids), renders one plan.md with a one-line banner explaining the choice, and accepts plain-English overrides like *"use exact-diff and stats-driven"*.

It **complements** the IDE harness — the harness owns research → clarify → approve → execute; this skill owns the *shape* of the artifact the harness writes.

## Scope

### In Scope

- Auto-selecting one or more plan formats from task signals.
- Composing existing planning skills when their data is genuinely needed.
- Rendering a single plan.md with a universal skeleton: Context · Format-Specific Body · Verification · Out-of-Scope · Lift-out.
- Showing a one-line banner naming the format(s) chosen and why.
- Accepting plain-English overrides and combinations (`use trace and exact-diff`, `add stats-driven`).
- Producing a `Lift-out` block suitable for pasting into Jira / status updates / PR descriptions.

### Out of Scope

- Owning the IDE harness's research, clarify, approve, or execute phases.
- Full living-document lifecycle (versioning, amendment logs, status transitions). Fall through to [`prd`](../../10-discovery/prd/SKILL.md) when that level is needed.
- Writing code, tests, or implementation artifacts.
- Running validation, builds, or CI — only describing how to verify in the Verification block.

---

## Micro-Skills

### 1. Signal Read ⚡ (Power Mode)

**Goal:** Convert the task description and repo state into a vector of normalized signals.

**Steps:**

1. **Nano: Archetype Keyword Scan** — Tokenize the task description and tag matches against the archetype lexicon (`fix`, `bug`, `repro`, `cleanup`, `dead`, `lint`, `trim`, `refactor`, `add`, `feature`, `migrate`, `schema`, `optimize`, `latency`, `p95`, `investigate`, `spike`, `API`, `endpoint`, `auth`, `vuln`, `STRIDE`, `test`, `coverage`). Multiple matches across categories raise the hybrid-candidate score.
2. **Nano: File-Count Estimate** — From the task scope or `git diff --name-only` if available, bucket as ≤3 / 4–15 / >15.
3. **Nano: Diff-Size Estimate** — From `git diff --shortstat` if a branch is active, else from task heuristics. Bucket as line-level / block-level / file-level.
4. **Nano: Reversibility Probe** — Flag the task as `irreversible` if it touches database migrations, public APIs, security boundaries, or paths tagged `safety-critical`.
5. **Nano: Novelty Probe** — Estimate new-file vs. modify-file ratio. Pure modifications lean to surgical formats; many new files lean to shape-first or component-tree formats.
6. **Nano: Visual-Structure Probe** — Look for UI component paths, state-machine markers (`status`, `state`, `transition`), or async-chain markers (`await`, `then`, `subscribe`, `pipe`).
7. **Nano: Explicit User Signal** — Extract user-volunteered phrases (`"surgical"`, `"exploratory"`, `"quick"`, `"production-grade"`, `"line-level"`) that hard-bias format selection.
8. Emit the signal vector for use by Format Decision Matrix.

### 2. Format Decision Matrix ⚡ (Power Mode)

**Goal:** Score all 16 formats against the signal vector and pick the top format or a 2–3 format hybrid.

**Steps:**

1. **Nano: Weighted Score** — For each format, sum `signal_value × signal_weight` across the seven dimensions below. Weights sum to 1.0.

   | Signal | Weight | Source |
   |---|---|---|
   | Archetype keywords | 0.25 | Signal Read step 1 |
   | File count | 0.15 | Signal Read step 2 |
   | Diff-size estimate | 0.10 | Signal Read step 3 |
   | Reversibility | 0.15 | Signal Read step 4 |
   | Novelty | 0.10 | Signal Read step 5 |
   | Visual structure | 0.10 | Signal Read step 6 |
   | Explicit user signal | 0.15 | Signal Read step 7 |

2. **Nano: Hybrid Promotion** — If the second-highest format scores within **0.08** of the top, promote to a hybrid (top + second). If a third format scores within **0.05** of the second, allow up to a three-format hybrid (cap at three).
3. **Nano: Tie-Break Ask** — If top and second tie within **0.03**, fall through to **Ask-When-Ambiguous** with both options offered.
4. **Nano: Hard Override** — If the user named a format explicitly (`"use exact-diff"`, `"plan this as pseudocode"`), the override wins. Multiple named formats become a user-defined hybrid.
5. Emit `selected_formats`, `selection_reason` (1-line, plain English), and `score_table` for the audit log.

### 3. Composition Routing ⚡ (Power Mode)

**Goal:** Invoke upstream planning skills only when the chosen format genuinely needs their data.

**Steps:**

1. Map the selected format(s) to upstream skill needs:

   | Format | Invokes | Why |
   |---|---|---|
   | File-by-File | [`task-decomposition`](../task-decomposition/SKILL.md) | per-file subtasks |
   | Pseudocode-First (multi-file) | [`task-decomposition`](../task-decomposition/SKILL.md) | file-mapping subtasks |
   | Trace-Before-Patch | [`root-cause-analysis`](../../60-debugging/root-cause-analysis/SKILL.md) | trace + root cause |
   | API-Contract (breaking) | [`risk-assessment`](../risk-assessment/SKILL.md) | breaking-change matrix |
   | Data-Migration | [`task-decomposition`](../task-decomposition/SKILL.md), [`risk-assessment`](../risk-assessment/SKILL.md) | step ordering + rollback risk |
   | Multi-PR Staged | [`task-decomposition`](../task-decomposition/SKILL.md), [`risk-assessment`](../risk-assessment/SKILL.md) | PR DAG + merge-gate risk |
   | Security-Patch | [`risk-assessment`](../risk-assessment/SKILL.md) | threat scoring |
   | Test-Coverage | [`task-decomposition`](../task-decomposition/SKILL.md) | test-file subtasks |
   | Estimation (any format, on user ask) | [`estimation`](../estimation/SKILL.md) | sizing + confidence |
   | All formats | [`style-conformance`](../../25-pragmatism/style-conformance/SKILL.md) | banner tone + verify-block style |

2. Skip upstream invocations whose data the format does not consume.
3. Collect upstream outputs and forward to the renderer.

### 4. Banner Rendering 🌿 (Eco Mode)

**Goal:** Produce a three-line banner that explains the format choice in plain English, with override syntax.

**Steps:**

1. Compose the banner exactly in this shape:

   ```
   [plan-as-agreement]
     Format: <name1>[ + <name2>[ + <name3>]] [(hybrid)]
     Why:    <≤80-char rationale citing the dominant signals>
     Override: "use <other-format>" / "drop <name>" / "add <name>"
   ```

2. Keep the rationale to one line. Cite at most three signals. Format: `keywords "<...>" + <file-count phrase> + <reversibility phrase>`.
3. Suggest the most likely override candidates in the override line — formats whose scores were close but did not win.

### 5. Plan Rendering ⚡ (Power Mode)

**Goal:** Assemble the universal skeleton with the chosen format(s) filling the body.

**Steps:**

1. Render the universal skeleton:

   ```markdown
   # {Title}

   > **Format:** {chosen}  · **Why:** {one-line reason}

   ## Context
   {why this change exists — user need, prior incident, dependency forcing it}

   ## {Format-specific body}
   {sections from the chosen format template(s); hybrids stack in priority order}

   ## Verification
   {exact commands or steps to confirm done}

   ## Out of scope
   {explicit list — guards against scope creep mid-execution}

   ## Lift-out
   {2-4 lines suitable for pasting into Jira / status / PR description}
   ```

2. For hybrids, stack format bodies in priority order (highest score first) under a single shared Context block. Avoid duplicate sections — merge by topic, not by format.
3. Always populate Out-of-Scope explicitly. An empty Out-of-Scope is a smell — flag with a TBD marker if the user gave no boundary signals.
4. Always populate Lift-out — even a 2-line summary suffices. This is the second-life hook for Jira / status / PR descriptions.
5. Length sanity check: if the plan is longer than the estimated diff, demote to a lighter format (Top-Level instead of File-by-File, File-by-File instead of Exact-Diff).

### 6. Lift-out & Audit 🌿 (Eco Mode)

**Goal:** Make the plan reusable downstream and record the format decision for posterity.

**Steps:**

1. Confirm the Lift-out block is present and self-contained — the user should be able to paste those 2–4 lines into Jira without further editing.
2. Append an audit entry capturing: signal vector, selected formats, score table, override (if any), upstream skills invoked.
3. The plan.md itself is the primary artifact; this skill does not version, branch, or amend it. If the user needs lifecycle management, route to [`prd`](../../10-discovery/prd/SKILL.md).

---

## Format Templates

> The 16 named formats. Each has a clear trigger, a required-sections list, optional sections, an anti-pattern, and a one-line skeleton.

### Format 1 — Top-Level
- **Trigger:** ≤3 files, reversible, low novelty. Hotfixes. Config flips. Single-line doc tweaks.
- **Required sections:** Context · What · Why · Verify · Out-of-Scope.
- **Anti-pattern:** any change touching more than 3 files or introducing new logic.
- **Skeleton:**
  ```markdown
  ## What
  {1–3 sentences of the change}
  ## Why
  {1–2 sentences of motivation}
  ```

### Format 2 — File-by-File
- **Trigger:** 4–15 files, reversible, default for most feature work.
- **Required sections:** Per-file (path + 2–5 bullets each).
- **Optional sections:** Mermaid module graph if interdependencies matter.
- **Anti-pattern:** when the changes are line-level rather than logical — use Exact-Diff instead.
- **Skeleton:**
  ```markdown
  ### `src/path/to/file.ts`
  - {bullet 1}
  - {bullet 2}
  ```

### Format 3 — Exact-Diff
- **Trigger:** surgical refactor, comment trim, lint fix, format-only change, review-grade precision needed.
- **Required sections:** Scope · Per-file ```diff``` blocks · Commit plan · Verification · Out-of-Scope.
- **Anti-pattern:** when introducing new logic — line-level diffs obscure shape; use Pseudocode-First or File-by-File.
- **Skeleton:**
  ```markdown
  ### Trim 1 — {what}
  ` ``diff
  - old line
  + new line
  ` ``
  ```

### Format 4 — Pseudocode-First
- **Trigger:** new logic, novel control flow, parser, state-machine, ranking/scoring algorithms. The *shape* matters more than the file.
- **Required sections:** Pseudocode · File mapping · Edge cases.
- **Optional sections:** complexity analysis, data shape.
- **Anti-pattern:** when the change is purely structural — file-level abstractions hide flow.
- **Skeleton:**
  ```markdown
  ## Pseudocode
  ` ``
  function rank(items):
    for item in items:
      score = w1 * a(item) + w2 * b(item)
    return sorted(items, score)
  ` ``
  ## File mapping
  - `src/rank.ts` — implements `rank()`
  ```

### Format 5 — Component-Tree
- **Trigger:** UI feature work — React, Vue, Svelte. Components + props + state.
- **Required sections:** Hierarchy (Mermaid `graph TD`) · State location · Props contract · Files to create/modify.
- **Anti-pattern:** non-UI features — state and props don't apply.
- **Skeleton:**
  ```markdown
  ## Hierarchy
  ` ``mermaid
  graph TD
    Dashboard --> WidgetA
    Dashboard --> WidgetB
  ` ``
  ## Props contract
  | Component | Prop | Type |
  ```

### Format 6 — Sequence-Diagram
- **Trigger:** multi-actor flows, auth handshake, async pipelines, event chains.
- **Required sections:** Mermaid `sequenceDiagram` · Per-actor changes · Edge cases.
- **Anti-pattern:** single-actor flows — diagram noise without signal.
- **Skeleton:**
  ```markdown
  ## Flow
  ` ``mermaid
  sequenceDiagram
    Client->>Server: /authorize
    Server->>Client: 302 redirect
  ` ``
  ```

### Format 7 — State-Machine
- **Trigger:** finite-state features — order status, document lifecycle, workflow approval.
- **Required sections:** States + transitions (table or Mermaid `stateDiagram-v2`) · Guards · Files.
- **Anti-pattern:** features without distinct states.
- **Skeleton:**
  ```markdown
  ## States
  | From | To | Guard |
  ## Transition diagram
  ` ``mermaid
  stateDiagram-v2
    [*] --> Draft
    Draft --> Review
  ` ``
  ```

### Format 8 — Trace-Before-Patch
- **Trigger:** bug fix where existing flow must be understood first.
- **Required sections:** Repro · Trace (call chain with `file:line` refs) · Root cause · Patch points · Regression test.
- **Anti-pattern:** trivial typo fixes — overhead without value.
- **Skeleton:**
  ```markdown
  ## Repro
  1. Open Safari, click submit on /checkout.
  ## Trace
  - `checkout.tsx:42` calls `submitOrder()`
  - `submit.ts:18` awaits `validateCart()` — returns early on iOS Safari
  ## Root cause
  `navigator.userAgent` check excludes iOS Safari.
  ## Patch
  ` ``diff
  - if (isMobile && !isIOS) ...
  + if (isMobile) ...
  ` ``
  ```

### Format 9 — Stats-Driven Cleanup
- **Trigger:** dead-code removal, dependency pruning, comment trim, lint sweep.
- **Required sections:** Stats block (LOC removed, files touched, % of category cleaned) · Categories with counts · Sample diffs · Out-of-Scope.
- **Anti-pattern:** when scope is too small to need stats — fall through to Top-Level.
- **Skeleton:**
  ```markdown
  ## Stats
  | Metric | Value |
  | LOC removed | 4,127 |
  | Files touched | 38 |
  | Dead-code category coverage | 92% |
  ## Categories
  - Unused utils (`src/util/legacy/`) — 22 files
  - Unreferenced consts — 16 files
  ## Sample diff
  ` ``diff
  - export function legacyParse() { ... }
  ` ``
  ```

### Format 10 — Spike / Hypothesis-Driven
- **Trigger:** investigation, "can/should we" question, perf analysis without a known fix.
- **Required sections:** Hypothesis · Experiments · Success signals · Decision criteria · Time-box.
- **Anti-pattern:** when the answer is already known — use a concrete format.
- **Skeleton:**
  ```markdown
  ## Hypothesis
  gRPC will reduce backend p99 latency by ≥30% versus our current JSON over HTTP.
  ## Experiments
  1. Stand up a parallel gRPC handler for `/products/search`.
  2. Mirror 5% of production traffic to it.
  ## Success signals
  - p99 latency comparison
  - Error-rate delta
  ## Time-box
  4 working days.
  ```

### Format 11 — API-Contract
- **Trigger:** REST/gRPC change, public interface evolution.
- **Required sections:** Endpoints (path + method + before/after schema) · Breaking-change matrix · Consumer impact · Verification (contract tests).
- **Anti-pattern:** internal-only refactors — no consumers, no contract to negotiate.
- **Skeleton:**
  ```markdown
  ## Endpoint: GET /v2/products/{id}
  ### Before
  ` ``json
  { "id": "string", "name": "string" }
  ` ``
  ### After
  ` ``json
  { "id": "string", "name": "string", "currency": "ISO-4217" }
  ` ``
  ## Breaking-change matrix
  | Field | Change | Breaking? |
  ```

### Format 12 — Data-Migration
- **Trigger:** DB migration, data backfill, pipeline schema change.
- **Required sections:** Migration steps (ordered) · Rollback plan · Data integrity checks · Down-time profile.
- **Anti-pattern:** trivial column rename with no data — use Top-Level.
- **Skeleton:**
  ```markdown
  ## Migration steps
  1. Deploy reader that tolerates both shapes.
  2. Backfill `currency` column in batches of 10k.
  3. Deploy writer that requires `currency`.
  4. Mark column NOT NULL.
  ## Rollback
  - After step 2: drop column. After step 3: re-deploy reader-only.
  ```

### Format 13 — Benchmark (Before/After)
- **Trigger:** latency/throughput fix, hot-path optimization.
- **Required sections:** Baseline numbers · Bottleneck · Proposed change · Expected delta · Measurement plan.
- **Anti-pattern:** when no baseline exists — start with Spike instead.
- **Skeleton:**
  ```markdown
  ## Baseline
  - p50: 200ms, p99: 820ms (current production, last 7 days)
  ## Bottleneck
  - N+1 query on `orders.line_items` (profiled to ~60% of p99 time)
  ## Proposed change
  - Eager-load with `JOIN` in `ordersRepo.findByUser`.
  ## Expected delta
  - p99 → ≤200ms.
  ## Measurement
  - Replay last 24h of traffic on staging; compare p50/p99/error-rate.
  ```

### Format 14 — Multi-PR Staged
- **Trigger:** change too big for one PR, sequenced rollout with merge gates.
- **Required sections:** PR sequence DAG (Mermaid) · Per-PR scope · Merge gates · Rollback plan per PR.
- **Anti-pattern:** when the change fits comfortably in one PR.
- **Skeleton:**
  ```markdown
  ## Sequence
  ` ``mermaid
  graph LR
    PR1[PR1: add new column] --> PR2[PR2: dual-write]
    PR2 --> PR3[PR3: switch reads]
    PR3 --> PR4[PR4: drop old column]
  ` ``
  ## Per-PR scope
  - PR1: schema migration only, no app code changes.
  ## Merge gates
  - PR2 cannot merge until PR1 has been in prod 48h.
  ```

### Format 15 — Security-Patch
- **Trigger:** known vuln, OWASP/STRIDE category, attack vector to close.
- **Required sections:** Threat · Attack vector · Patch · STRIDE-category closure · Verification (negative test).
- **Optional sections:** Disclosure (if external).
- **Anti-pattern:** generic security hardening with no specific vuln — use Test-Coverage or Spike.
- **Skeleton:**
  ```markdown
  ## Threat
  Server-side request forgery on `/admin/import-url`.
  ## Attack vector
  Attacker submits `http://169.254.169.254/...` and reads AWS metadata.
  ## Patch
  Allow-list scheme + private IP block + DNS rebinding protection.
  ## STRIDE closure
  Information Disclosure (I) — closed.
  ## Verification
  - Negative test: malicious URLs in `tests/security/ssrf.spec.ts` must all return 400.
  ```

### Format 16 — Test-Coverage
- **Trigger:** gap-fill testing, characterization tests before a refactor.
- **Required sections:** Coverage matrix (covered / gap) · Test files to add · Test type per gap (unit/integration/contract).
- **Anti-pattern:** when the refactor itself is the goal — fold tests into the refactor plan.
- **Skeleton:**
  ```markdown
  ## Coverage matrix
  | Module | Lines covered | Branch covered | Gap |
  ## Tests to add
  - `tests/cart/discount.spec.ts` — unit — covers discount edge cases.
  ```

---

## Hybrids (first-class, not exceptional)

When the task spans archetypes, the skill emits a 2–3 format hybrid. Common patterns:

| Hybrid | When | Section order |
|---|---|---|
| Trace-Before-Patch + Exact-Diff | bug fix with clear precise patch | Trace → Patch (diff) |
| Stats-Driven Cleanup + Exact-Diff | surgical cleanup at scale | Stats → Categories → Sample diffs |
| Benchmark + Pseudocode-First | perf with new algorithm | Baseline → Pseudocode → Expected delta |
| Component-Tree + Sequence-Diagram | UI with async behavior | Hierarchy → Sequence → Files |
| Data-Migration + Multi-PR Staged | multi-phase migration | PR sequence → Per-PR migration steps |
| API-Contract + Multi-PR Staged + Test-Coverage | major API evolution | Contract → PR sequence → Coverage matrix |

Hybrids share a single Context, Verification, and Out-of-Scope. Format bodies stack in priority order (highest score first).

---

## Inputs

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_description` | `string` | yes | The user's task ask, verbatim. |
| `repo_signals` | `object` | no | `{ file_count, diff_shortstat, branch_diff_paths }` — if available from the host environment. |
| `format_override` | `string` | no | Plain-English override, e.g., `"use exact-diff"` or `"trace and stats-driven"`. Wins over auto-selection. |
| `include_estimation` | `boolean` | no | If true, invokes the `estimation` skill and includes sizing in the plan. Default: false. |

## Outputs

| Field | Type | Description |
|---|---|---|
| `plan_markdown` | `markdown` | The complete plan.md content. |
| `selected_formats` | `string[]` | One or more format names from the 16-format library. |
| `selection_reason` | `string` | One-line rationale shown in the banner. |
| `score_table` | `object` | Per-format score breakdown for the audit log. |
| `upstream_skills_invoked` | `string[]` | Names of planning skills called via Composition Routing. |
| `lift_out` | `string` | 2–4 line summary suitable for Jira / status update / PR description. |

---

## Guardrails

1. **Never produce a plan longer than the estimated diff.** If length > diff, demote to a lighter format. This is an Aparigraha (non-accumulation) constraint.
2. **Always show the banner.** The user has the right to know which format was picked and why before reading the plan.
3. **Always populate Out-of-Scope explicitly.** Empty Out-of-Scope blocks invite scope creep; mark TBD if no boundary signals exist.
4. **Always populate Lift-out.** Even a 2-line summary. The second-life hook is the difference between a one-shot plan and a status-update-ready plan.
5. **Hybrid cap is three formats.** Beyond three, the banner becomes noise and the body becomes incoherent.
6. **Explicit user override is final.** Auto-selection is a recommendation, not a mandate. Never silently override the user.
7. **Do not invoke `risk-assessment` for reversible non-safety-critical work.** Over-invoking upstream skills inflates planning cost. Stick to the routing table.
8. **Do not own lifecycle.** If the user asks for amendment logs or version history, route to [`prd`](../../10-discovery/prd/SKILL.md).
9. **Do not write code.** Pseudocode is allowed; concrete implementation is out of scope.
10. **Banner rationale ≤ 80 chars.** Long banners defeat the point of a banner.

---

## Ask-When-Ambiguous

**Triggers:**

- Top and second format scores tie within 0.03.
- Task description is too vague to extract archetype keywords (no verbs).
- Repo signals contradict task description (e.g., user says "small fix" but `git diff` shows 40 files).
- User invokes the skill outside of a planning context (no clear task ask).
- Format override names a format that conflicts with task signals (e.g., user says `"top-level"` for a 60-file change).

**Question Templates:**

- "This task scored within 0.03 between {Format A} and {Format B}. {A} fits if {reason A}; {B} fits if {reason B}. Which matches what you want?"
- "Your task description is short — could you tell me the archetype: bug fix, new feature, cleanup, migration, perf, security, or research?"
- "You said 'small fix' but the branch shows 40 changed files. Would you like the plan as File-by-File (default for this size) or stay with Top-Level (you accept the longer scan)?"
- "You overrode to {format} but the signals suggest {auto-format}. Confirm: keep your override, or take the auto pick?"

---

## Decision Criteria

| Situation | Action | Rationale |
|---|---|---|
| Single keyword match dominates (e.g., "trim", "lint sweep") | Pick the matching format | High-signal keywords are reliable |
| Two formats within 0.08 | Promote to hybrid | Real tasks span archetypes |
| Three formats within 0.05 of each other | Three-format hybrid (cap) | Reflect genuine multi-archetype spread |
| User overrides | Honor override; log delta | User steers, no silent overrides |
| Task is exploratory ("can we", "should we") | Force Spike | Investigation deserves Spike, not implementation plan |
| Task says "production-grade" or "review-grade" | Bias to Exact-Diff or hybrids that include it | Surfaces line-level precision |
| Plan length > estimated diff | Demote to lighter format | Plans heavier than the work are noise |
| User asked for sizing | Invoke `estimation`; include in Verification block | Sizing is a separate add-on |
| Path is `safety-critical` or `irreversible` | Promote risk-assessment hybrid (Data-Migration, Security-Patch, API-Contract) | Reversibility raises the stakes |

---

## Success Criteria

- [ ] One or more formats selected with documented rationale.
- [ ] Banner present, ≤ 3 lines, with format name(s), why, and override hint.
- [ ] Plan length ≤ estimated diff length where possible (or explicit reason if not).
- [ ] All required sections of the chosen format(s) are populated.
- [ ] Out-of-Scope block is explicit, not empty.
- [ ] Lift-out block is present and self-contained.
- [ ] Upstream skills invoked only when their data is consumed.
- [ ] Audit log entry recorded with signal vector and score table.

---

## Failure Modes

| Failure | Symptom | Recovery |
|---|---|---|
| Wrong format chosen | Plan feels too heavy or too light for the task | Honor user override; refine archetype keyword list |
| Banner missing | User sees a plan with no format explanation | Re-render with banner; treat as audit violation |
| Hybrid noise | Three formats stacked but the body is incoherent | Demote to top-1 format; record the demotion |
| Plan > diff | Plan longer than the work itself | Demote to a lighter format (see Decision Criteria) |
| Lift-out empty | Section header without content | Block delivery until Lift-out is populated |
| Over-invocation | risk-assessment called for a doc tweak | Tighten Composition Routing table |
| Style drift | Banner reads as marketing copy | Route through `style-conformance` |

---

## Audit Log

Every invocation must produce an audit entry:

```markdown
| Timestamp | Skill | Action | Detail | Confirmed By |
|---|---|---|---|---|
| <ISO8601> | plan-as-agreement | signals-read | file_count=N, diff_shortstat=..., archetype_keywords=[...] | — |
| <ISO8601> | plan-as-agreement | format-selected | Formats: [<...>], Top score: <s1>, Hybrid?: <yes/no>, Override?: <yes/no> | user |
| <ISO8601> | plan-as-agreement | upstream-invoked | Skills: [<...>] | — |
| <ISO8601> | plan-as-agreement | plan-rendered | Sections: [<...>], Length: N lines | — |
| <ISO8601> | plan-as-agreement | banner-rendered | Banner: "<banner>" | — |
| <ISO8601> | plan-as-agreement | lift-out-rendered | Lines: N | — |
```

Log entries are append-only.

---

## Examples

### Example 1 — Comment trim PR (Exact-Diff)

**Task:** "Trim verbose JSDoc comments across the MicroStrategy prompts PR. 23 trims, 5 files, line-level precision."

**Signals:** `archetype_keywords=[trim, JSDoc]`, `file_count=5`, `diff_size=line-level`, `reversibility=reversible`, `novelty=low`, `visual_structure=none`, `explicit_signal="line-level precision"`.

**Score:** Exact-Diff: 0.81. Stats-Driven Cleanup: 0.62. File-by-File: 0.45. Hybrid trigger met (0.81 − 0.62 = 0.19 > 0.08 → single format).

**Banner:**
```
[plan-as-agreement]
  Format: Exact-Diff
  Why:    keywords "trim, JSDoc" + 5 files + explicit "line-level"
  Override: "use stats-driven" / "use file-by-file"
```

**Plan body:** per-file ```diff``` blocks, one logical trim per block. Commit plan: 23 atomic commits or 5 (one per file).

### Example 2 — Safari submit bug (Trace-Before-Patch + Exact-Diff hybrid)

**Task:** "Submit button does nothing on iOS Safari. Affects /checkout. Other browsers fine."

**Signals:** `archetype_keywords=[bug, Safari, submit]`, `file_count=~3 (unknown)`, `diff_size=block-level`, `reversibility=reversible`, `novelty=low`, `visual_structure=none`, `explicit_signal=none`.

**Score:** Trace-Before-Patch: 0.74. Exact-Diff: 0.69. Top-Level: 0.51. Hybrid trigger met (0.74 − 0.69 = 0.05 < 0.08 → promote).

**Banner:**
```
[plan-as-agreement]
  Format: Trace-Before-Patch + Exact-Diff  (hybrid)
  Why:    keywords "bug Safari submit" + line-level scope + ≤5 files
  Override: "use trace alone" / "use top-level"
```

**Plan body:** Repro → Trace (with `file:line`) → Root cause → Patch (```diff``` block) → Regression test.

### Example 3 — Dead-code sweep (Stats-Driven Cleanup + Exact-Diff hybrid)

**Task:** "Sweep dead utilities under `src/util/legacy/`. Expect ~4k LOC across ~40 files."

**Signals:** `archetype_keywords=[dead, sweep, cleanup]`, `file_count=40`, `diff_size=file-level`, `reversibility=reversible`, `novelty=zero`, `visual_structure=none`.

**Score:** Stats-Driven Cleanup: 0.79. Exact-Diff: 0.71. Promote to hybrid (0.08 margin).

**Plan body:** Stats block up front → Categories with counts → Sample diffs → Out-of-Scope.

### Example 4 — gRPC viability spike (Spike / Hypothesis-Driven)

**Task:** "Investigate if gRPC reduces our p99 latency."

**Signals:** `archetype_keywords=[investigate]`, `explicit_signal="investigate"`.

**Score:** Spike: 0.83. Benchmark: 0.62. Single format.

**Plan body:** Hypothesis → Experiments → Success signals → Decision criteria → Time-box.

---

## Edge Cases

- **No task description, just an open prompt** — Ask the archetype question first. Do not auto-select from zero signal.
- **User invokes during execution, not planning** — Decline. Suggest re-entering plan-mode (Claude Code) / Plan Mode (Cursor) / Plan (Cline).
- **Existing plan.md on disk** — Read it. If it follows a known format, preserve the format unless the user asks for change. If it does not, offer to re-render in the auto-selected format.
- **User pastes a plan from another tool** — Treat as input. Pick the closest matching format, render the banner, leave body content alone unless explicitly asked to reshape.
- **Hybrid scoring produces 4+ candidates within margin** — Cap at three. The 4th candidate goes in the banner's override hint.
- **The task is "plan how to plan"** — Fall through to this skill's own docs. Do not recurse.
- **The plan is for an AI agent consumer** — Maximize tables, code fences, explicit verification commands. Avoid prose paragraphs.
- **The user wants the plan in a non-English language** — Render in the requested language; preserve format names in English (they are identifiers).

---

## See Also

- [Skill: `prd`](../../10-discovery/prd/SKILL.md) — for living documents with lifecycle, versioning, and amendment logs.
- [Skill: `task-decomposition`](../task-decomposition/SKILL.md) — subtask graphs that feed File-by-File and Multi-PR Staged.
- [Skill: `risk-assessment`](../risk-assessment/SKILL.md) — risk matrix that feeds Data-Migration, API-Contract (breaking), Security-Patch, Multi-PR Staged.
- [Skill: `estimation`](../estimation/SKILL.md) — sizing add-on.
- [Skill: `root-cause-analysis`](../../60-debugging/root-cause-analysis/SKILL.md) — trace logic for Trace-Before-Patch.
- [Docs: `plan-formats.md`](../../../../docs/plan-formats.md) — 1-page cheat-sheet of all 16 formats.
