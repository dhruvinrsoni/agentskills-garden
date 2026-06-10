# Plan Formats — Cheat-Sheet

The 16 named plan formats produced by the [`plan-as-agreement`](../skills/100-engineering/20-planning/plan-as-agreement/SKILL.md) skill. One page, skim-fit. Use this to figure out which format your task wants — or to recognise a format the skill picked for you.

---

## The 16 formats at a glance

| # | Format | Trigger | Body |
|---|---|---|---|
| 1 | **Top-Level** | ≤3 files, reversible, hotfix, doc tweak | What · Why · Verify |
| 2 | **File-by-File** | 4–15 files, reversible (default for medium work) | per-file bullets |
| 3 | **Exact-Diff** | surgical refactor, comment trim, lint fix, review-grade | line-level ` ```diff ` blocks |
| 4 | **Pseudocode-First** | new logic, novel control flow, parser/state-machine | algorithm before files |
| 5 | **Component-Tree** | UI feature: components + props + state | Mermaid `graph TD` + props contract |
| 6 | **Sequence-Diagram** | multi-actor flows, auth, async pipelines | Mermaid `sequenceDiagram` |
| 7 | **State-Machine** | finite-state features, workflows, status fields | states + transitions table or `stateDiagram-v2` |
| 8 | **Trace-Before-Patch** | bug fix needing flow understanding first | repro → trace → root cause → patch points |
| 9 | **Stats-Driven Cleanup** | dead code, dep pruning, comment trim, lint sweep | LOC/file counts up front, then sample diffs |
| 10 | **Spike / Hypothesis-Driven** | research, "can-we / should-we", perf w/o known fix | hypothesis · experiments · success signals · decision · time-box |
| 11 | **API-Contract** | REST/gRPC change, public interface evolution | endpoints + before/after schema + breaking-change matrix |
| 12 | **Data-Migration** | DB migration, data backfill, pipeline schema change | ordered steps · rollback · integrity checks · down-time |
| 13 | **Benchmark (Before/After)** | latency/throughput fix, hot-path optimization | baseline · bottleneck · expected delta · measurement plan |
| 14 | **Multi-PR Staged** | change too big for one PR, sequenced merges | PR sequence DAG + per-PR scope + merge gates |
| 15 | **Security-Patch** | known vuln, OWASP/STRIDE category | threat · attack vector · patch · STRIDE closure · negative test |
| 16 | **Test-Coverage** | gap-fill testing, characterization tests | coverage matrix · test files to add · test type per gap |

---

## Decision flow

```
  task description
       │
       ▼
  Signal Read
   (archetype keywords, file count, diff size,
    reversibility, novelty, visual structure,
    explicit user signal)
       │
       ▼
  Format Decision Matrix
   (weighted score × 16 formats)
       │
       ├─── top wins by > 0.08 ──────────► single format
       ├─── second within 0.08 ──────────► hybrid (top + second)
       ├─── third within 0.05 of second ─► triple hybrid (cap)
       └─── top & second tie within 0.03 ► ask the user
       │
       ▼
  Banner + Plan render
   "[plan-as-agreement] Format: X / Why: ... / Override: ..."
```

---

## Common hybrids (first-class, not exceptional)

| Hybrid | When to use |
|---|---|
| **Trace-Before-Patch + Exact-Diff** | bug fix where you've traced AND know the precise patch |
| **Stats-Driven Cleanup + Exact-Diff** | cleanup at scale where reviewers need both stats and line-level diffs |
| **Benchmark + Pseudocode-First** | perf optimization where the new algorithm shape matters |
| **Component-Tree + Sequence-Diagram** | UI features with non-trivial async behavior |
| **Data-Migration + Multi-PR Staged** | multi-phase migration (reader → backfill → writer → drop) |
| **API-Contract + Multi-PR Staged + Test-Coverage** | major public-API evolution |

Hybrids share one Context, one Verification, one Out-of-Scope. Bodies stack in priority order (highest score first).

---

## Universal skeleton (every plan)

```markdown
# {Title}

> **Format:** {chosen}  · **Why:** {one-line reason}

## Context
{why this change exists — user need, prior incident, dependency forcing it}

## {Format-specific body}
{rendered by the chosen format(s)}

## Verification
{exact commands or steps to confirm done}

## Out of scope
{explicit list — guards against scope creep mid-execution}

## Lift-out
{2-4 lines suitable for pasting into Jira / status update / PR description}
```

The **Lift-out** block is the second-life hook — the bit you paste into Jira or a status update without re-condensing the plan by hand.

---

## Override syntax (plain English)

The skill auto-selects, but the user always wins. Plain English overrides — no flags, no syntax:

| You say | Skill does |
|---|---|
| `"use exact-diff"` | switches to Exact-Diff |
| `"use trace and exact-diff"` | hybrid of Trace-Before-Patch + Exact-Diff |
| `"add stats-driven"` | adds Stats-Driven Cleanup to the current pick |
| `"drop the exact-diff"` | removes Exact-Diff from a hybrid |
| `"swap to pseudocode-first"` | replaces top format with Pseudocode-First |

---

## Quick triggers (rule-of-thumb)

- **It's a bug** → Trace-Before-Patch (often with Exact-Diff).
- **It's a perf fix** → Benchmark (often with Pseudocode-First).
- **It's a cleanup** → Stats-Driven Cleanup (often with Exact-Diff).
- **It's a comment/lint/format sweep** → Exact-Diff.
- **It's a new feature with UI** → Component-Tree.
- **It's a multi-actor flow** → Sequence-Diagram.
- **It's a workflow with status** → State-Machine.
- **It's research / "can-we"** → Spike.
- **It's a public API change** → API-Contract.
- **It's a DB or schema change** → Data-Migration.
- **It's too big for one PR** → Multi-PR Staged.
- **It's a known vuln** → Security-Patch.
- **It's a tests-only PR** → Test-Coverage.
- **It's tiny and reversible** → Top-Level.
- **None of the above** → File-by-File.

---

## See also

- [Skill: `plan-as-agreement`](../skills/100-engineering/20-planning/plan-as-agreement/SKILL.md) — the full skill, including the Format Decision Matrix, micro-skills, examples, and audit format.
- [Concepts primer](concepts.md) — the four-level hierarchy and nano/micro/skill/master vocabulary.
- [Skill: `prd`](../skills/100-engineering/10-discovery/prd/SKILL.md) — when you need a living document with lifecycle (versioning, amendment log, approval states) rather than a single-shot plan.
