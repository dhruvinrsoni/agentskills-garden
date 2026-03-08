---
name: token-efficiency
description: >
  Optimizes agent resource consumption by selecting the right model tier,
  tool, delegation strategy, and parallelization pattern for each operation.
  Integrates with Eco/Power cognitive modes to scale resource usage
  proportionally to task complexity.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad"
  reasoning_mode: linear
---

# Token Efficiency — Resource-Aware Agent Operations

> _"Spend tokens like they cost money — because they do."_

## Context

Loaded alongside `constitution` and `scratchpad` at the start of every task.
Once the scratchpad has determined the cognitive mode (Eco or Power), this
skill governs **how** the agent allocates compute resources: which model tier
to invoke, which tools to try first, whether to delegate to sub-agents, and
how to batch operations for maximum throughput.

The core principle mirrors Ahimsa (Non-Destruction) from the Constitution:
**prefer the least-resource approach that achieves the goal.** Waste is a
form of harm — to cost budgets, to latency, and to context window capacity.

## Scope

**In scope:**

- Model tier selection per task type and cognitive mode
- Tool call ordering and progressive disclosure
- Agent delegation vs direct work decisions
- Parallel vs sequential execution planning
- Resource budget awareness (context window, token cost)

**Out of scope:**

- Cognitive mode detection — owned by `scratchpad`
- Constitutional compliance checks — owned by `auditor`
- Skill routing and discovery — owned by `librarian`
- Actual tool implementations or model APIs

---

## Micro-Skills

### 1. Model Tier Selection

**Mode:** Eco

Select the lightest model tier that can handle the current operation.

**Model Tiers:**

| Tier | Profile | When to Use |
|------|---------|-------------|
| **Tier 1** (lightweight/fast) | Simple lookups, file finding, running commands, data extraction | Eco mode default; single-step operations |
| **Tier 2** (capable/balanced) | Exploration, multi-file analysis, pattern discovery, code comprehension | Power mode default; tasks needing 3+ tool calls |
| **Tier 3** (heavyweight/deep) | Major architectural decisions, security review, complex trade-off analysis | Only when Tier 2 demonstrably struggles |

**Steps:**

1. Read cognitive mode from scratchpad output (Eco or Power).
2. Classify the operation type: `lookup`, `exploration`, `modification`, `architecture`.
3. Apply the tier matrix:
   - **Eco + lookup/modification** → Tier 1
   - **Eco + exploration** → Tier 2
   - **Power + any** → Tier 2 (default), Tier 3 only on escalation
4. Record the selection and rationale in the audit log.

**Escalation rule:** Try the lower tier first. Escalate only if the output
is demonstrably insufficient (missing nuance, incomplete analysis, failed
search). Never pre-emptively jump to Tier 3.

### 2. Tool Prioritization

**Mode:** Eco

Follow the **discovery waterfall**: always start with the cheapest tool
category and escalate only when it proves insufficient.

**Waterfall Order:**

```
File Search (patterns)
    ↓ not found / need content
Symbol Navigation (definitions, references, hover)
    ↓ not available / need broader search
Content Search (regex across files)
    ↓ need deeper understanding
Targeted File Read (offset + limit)
    ↓ need multi-file comprehension
Exploration Agent (delegate broad discovery)
```

**Steps:**

1. Classify the information need:
   - **Find files** → File search (glob patterns). One call, done.
   - **Find definition** → Symbol navigation first; fall back to content search.
   - **Find usage/references** → Symbol navigation; fall back to content search.
   - **Understand structure** → Content search (paths-only mode first, then content mode).
   - **Deep comprehension** → Targeted read with offset/limit, not full file.
2. Apply progressive disclosure:
   - Content search: start with paths-only output. Switch to content mode only when you need the actual lines.
   - Use result limits (20–50 entries) when exploring broadly.
   - Add context lines only in content mode when surrounding code matters.
3. For file reads:
   - Specify `offset` and `limit` when the region of interest is known.
   - Read the full file only when comprehensive understanding is required.
   - Never speculatively read files "just in case."

### 3. Delegation Strategy

**Mode:** Power

Decide whether to work directly in the main context, delegate to a
sub-agent, or run a background task.

**Decision Matrix:**

| Condition | Strategy |
|-----------|----------|
| Code modification (edit/write) | **Always direct** — never delegate edits |
| Reading 1–2 known files | **Direct** — no overhead benefit from delegation |
| Single targeted search | **Direct** — faster than agent round-trip |
| Broad discovery (3+ search rounds likely) | **Delegate** — protect main context from result bloat |
| Isolated exploration ("find all X and summarize") | **Delegate** — let sub-agent iterate freely |
| Multiple independent queries | **Delegate in parallel** — one agent per query |
| Build/test run (>60 seconds) | **Background** — don't block the conversation |
| Sequential dependent operations | **Direct** — chain with `&&` in a single call |

**Steps:**

1. Evaluate independence: can this operation run without the current conversation context?
2. Evaluate scope: how many tool calls will it likely need? (1–2 = direct, 3+ = consider delegation)
3. Select model tier for the sub-agent:
   - File finding, builds, simple searches → Tier 1 agent
   - Architecture exploration, pattern analysis → Tier 2 agent
   - Complex edge-case analysis → Tier 3 agent (rare)
4. For long-running operations (builds, large test suites), mark as background.
5. Record the delegation decision and rationale.

### 4. Parallelization

**Mode:** Eco

Maximize throughput by batching independent operations and properly
sequencing dependent ones.

**Steps:**

1. List all pending operations for the current step.
2. Analyze dependencies between them:
   - **Independent** (no shared inputs/outputs) → group into a parallel batch.
   - **Dependent** (output of A feeds input of B) → chain sequentially.
3. Execute parallel batches as a single message with multiple tool calls.
4. For sequential chains in shell commands, use `&&` to chain in one call rather than separate round-trips.
5. For mixed graphs (some parallel, some sequential), execute parallel batches first, then sequential chains that depend on their results.

**Heuristic:** If you have 3+ independent file reads, grep calls, or agent
launches — batch them. The overhead of separate round-trips exceeds the cost
of a slightly larger single message.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cognitive_mode` | `string` | yes | Current mode from scratchpad: `eco` or `power` |
| `task_type` | `string` | yes | Classification: `lookup`, `exploration`, `modification`, `architecture` |
| `operation_count` | `number` | no | Estimated number of operations needed (default: 1) |
| `has_dependencies` | `boolean` | no | Whether operations depend on each other (default: false) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `model_tier` | `string` | Selected tier: `tier-1`, `tier-2`, or `tier-3` |
| `tool_priority` | `string[]` | Ordered list of tool categories to attempt |
| `delegation` | `string` | Strategy: `direct`, `delegate`, or `background` |
| `execution_plan` | `string` | Execution shape: `single`, `parallel-batch-N`, or `sequential-chain` |

---

## Guardrails

- **Cheapest first.** Never skip lower tiers in the tool waterfall unless you
  know they cannot satisfy the need.
- **No pre-emptive Tier 3.** Eco mode must default to Tier 1. Power mode
  defaults to Tier 2. Tier 3 requires demonstrated need (prior attempt at a
  lower tier that was insufficient).
- **Code edits are always direct.** Never delegate file modifications to
  sub-agents — the main context must own all writes.
- **No speculative reads.** Do not read entire files "just in case." Use
  targeted offsets or search first to identify the relevant region.
- **Never parallelize dependent operations.** If operation B needs the output
  of operation A, they must run sequentially — no exceptions.
- **Escalation requires a log entry.** Every tier escalation must be recorded
  with the reason the lower tier was insufficient.

## Ask-When-Ambiguous

**Triggers:**

- Task complexity is borderline between Eco and Power mode
- Multiple tool categories could satisfy the need equally well
- Delegation scope is unclear (broad enough to justify an agent?)
- Context window is under pressure and trade-offs are needed

**Question Templates:**

- "This task could use Tier 1 for speed or Tier 2 for thoroughness. Which
  matters more here?"
- "I can search narrowly (direct grep) or explore broadly (delegate to
  agent). The broad search may surface more context but costs more. Prefer
  speed or coverage?"
- "Context window is getting tight. Should I delegate exploration to a
  sub-agent to protect the main context, or keep working directly?"

## Decision Criteria

| Need | Preferred Approach | Eco Mode | Power Mode |
|------|--------------------|----------|------------|
| Find files by name/pattern | File search tool | Direct, single call | Direct, single call |
| Find symbol definition | Symbol navigation | Direct, fallback to content search | Direct, fallback to content search |
| Find content across files | Content search | Paths-only, head-limited | Content mode with context lines |
| Read known files (1–2) | File read | Direct, offset+limit | Direct, full file if needed |
| Read many files (3+) | File read | Parallel batch | Parallel batch |
| Understand "how X works" | Exploration agent | Tier 1 agent, quick | Tier 2 agent, thorough |
| Code modification | Direct edit/write | Always direct | Always direct |
| Run build/tests | Shell command | Tier 1 agent or background | Background if slow |
| Multiple independent queries | Parallel tool calls | Always parallel | Always parallel |
| Sequential dependent ops | Chain with `&&` | Single shell call | Single shell call |
| Broad discovery (uncertain scope) | Delegate to agent | Tier 1–2 agent | Tier 2 agent |
| Architectural analysis | Direct or delegate | Tier 2 direct | Tier 2, escalate to Tier 3 if needed |

## Success Criteria

- Model tier matches task complexity — no Tier 3 for simple lookups, no Tier 1 for architectural analysis.
- Tool calls follow the discovery waterfall — cheapest category tried first.
- All independent operations within a step are parallelized.
- All dependent operations are properly sequenced.
- Sub-agent delegation uses the lightest sufficient tier.
- Zero speculative file reads — every read is justified by a prior search or known path.
- Tier escalations are logged with rationale.

## Failure Modes

- **Over-spending** (Tier 3 for trivial tasks)
  **Recovery:** Audit log flags tier mismatch. Recalibrate by defaulting to lower tier and only escalating on demonstrated need.

- **Under-spending** (Tier 1 for complex analysis)
  **Recovery:** Output quality is poor or incomplete. Escalate tier, retry the operation, and log the escalation reason.

- **Serial execution of independent operations**
  **Recovery:** Retrospective identifies operations that could have been batched. Restructure future steps to group independent calls.

- **Premature delegation**
  **Recovery:** Sub-agent lacks context and produces wrong or shallow results. Pull the task back to direct work with the necessary context.

- **Wrong tool category**
  **Recovery:** Multiple failed searches before finding the result. Review the discovery waterfall and adjust the classification of the need.

- **Parallelizing dependent operations**
  **Recovery:** Results are inconsistent or use stale values. Re-run in correct sequential order. Add explicit dependency annotations to the execution plan.

## Audit Log

```
[tier-selected]   tier={tier-1|tier-2|tier-3} task_type={type} mode={eco|power} reason={reason}
[tool-priority]   waterfall=[{ordered categories}] need={need} mode={eco|power}
[delegation]      strategy={direct|delegate|background} scope={description} tier={tier}
[parallel-batch]  ops={N} independent={true|false}
[sequential-chain] ops={N} chain_reason={dependency description}
[tier-escalation] from={old_tier} to={new_tier} reason={why lower tier was insufficient}
```

---

## Examples

### Example 1 — Eco Mode: Find Controller Files

**Scenario:** User asks "find all controller files in the project."

**Input:**
```json
{
  "cognitive_mode": "eco",
  "task_type": "lookup",
  "operation_count": 1,
  "has_dependencies": false
}
```

**Output:**
```json
{
  "model_tier": "tier-1",
  "tool_priority": ["file-search"],
  "delegation": "direct",
  "execution_plan": "single"
}
```

**Claude Code mapping:** Use `Glob` with pattern `**/*Controller.{java,ts,py}`. Direct call, no agent needed. Haiku-tier if delegating.

### Example 2 — Power Mode: Understand Auth System

**Scenario:** User asks "how does the authentication system work across modules?"

**Input:**
```json
{
  "cognitive_mode": "power",
  "task_type": "architecture",
  "operation_count": 8,
  "has_dependencies": false
}
```

**Output:**
```json
{
  "model_tier": "tier-2",
  "tool_priority": ["symbol-navigation", "content-search", "file-read"],
  "delegation": "delegate",
  "execution_plan": "parallel-batch-2"
}
```

**Claude Code mapping:** Launch an `Explore` agent (Sonnet-tier) with thorough mode. Alternatively, launch 2 parallel agents: one searching auth middleware, one searching token/session handling. Direct Opus only if Sonnet agent returns insufficient analysis.

### Example 3 — Eco Mode: Read and Edit 5 Config Files

**Scenario:** User asks to update a setting across 5 configuration files.

**Input:**
```json
{
  "cognitive_mode": "eco",
  "task_type": "modification",
  "operation_count": 10,
  "has_dependencies": true
}
```

**Output:**
```json
{
  "model_tier": "tier-1",
  "tool_priority": ["file-read", "file-edit"],
  "delegation": "direct",
  "execution_plan": "sequential-chain"
}
```

**Claude Code mapping:** Parallel `Read` of all 5 files (independent reads), then sequential `Edit` calls (each edit depends on reading the file). All edits in main context — never delegate modifications. Haiku not needed; main context handles directly.

---

## Edge Cases

- **Mode escalation mid-task.** If scratchpad escalates from Eco to Power
  during an operation, recalculate tier and delegation strategy without
  discarding work already completed at the lower tier.

- **Single-model environments.** When only one model tier is available,
  token-efficiency focuses solely on tool prioritization, parallelization,
  and delegation (without tier selection).

- **No sub-agent capability.** Some agent environments lack delegation.
  Fall back to aggressive parallelization of direct tool calls and careful
  sequential chaining.

- **Context window pressure.** When approaching context limits, prefer
  delegating exploration to sub-agents to offload result volume from the
  main context. Trade latency for capacity.

- **Conflicting signals.** Task is Eco-mode but requires 10+ tool calls.
  Do not escalate model tier — instead, escalate execution strategy:
  parallelize aggressively and consider delegation to keep the main context
  lean.

- **Ambiguous task classification.** When a task spans multiple types
  (e.g., lookup + modification), apply the highest-tier requirement but
  the cheapest tool for each sub-step independently.
