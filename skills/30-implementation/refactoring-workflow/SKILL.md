---
name: refactoring-workflow
description: >
  Master workflow for refactoring at four named depth levels — cosmetic,
  micro, meso, architectural — that compose as a ladder. Always runs
  chesterton-fence and style-conformance up front; always closes with a
  characterisation/test safety net, minimal-diff scope checks, and the
  auditor. Contains no implementation logic; orchestrates only existing
  category skills.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "0.1.0"
  dependencies: "constitution, scratchpad, pragmatism, pragya, librarian, auditor"
  reasoning_mode: plan-execute
  skill_type: master
---

# Refactoring Workflow — Master Workflow

> _"Investigate before you change. Conform before you improve. Stay surgical. Higher levels include lower levels — never skip rungs."_

## Context

Invoked when the user asks to refactor with a stated depth — "tidy up
this file" (cosmetic), "extract this method" (micro), "rationalise this
module" (meso), or "rethink this subsystem" (architectural). Freezes the
canonical refactoring shape so the agent never silently jumps from
cosmetic to architectural, and never silently changes behaviour.

**The ladder principle.** Each level **includes** all lower levels — they
are not parallel options. `meso` runs `cosmetic` + `micro` + `meso`
concretely; `architectural` runs all four. This guarantees the surface
work is always done before deeper structural changes, never after.

Named levels (`cosmetic | micro | meso | architectural`) are used instead
of numeric levels because they read clearly in audit logs.

## Scope

**In scope:**

- Sequencing the always-on backbone, the level-specific orchestration band, and the closing safety band.
- Forwarding outputs of each step into the next.
- Pausing for `pragya` checkpoints — mandatory at architectural level.

**Out of scope:**

- Formatting / dead-code mechanics (delegated to `cleanup`).
- Extract-method / guard-clause patterns (delegated to `refactoring`).
- Broader rename/inline patterns (delegated to `refactoring-suite`).
- Class hierarchies / package layout / DI wiring (delegated to `system-design`).
- *Adding* new patterns to any of those skills — this master only orchestrates what already exists; gaps are surfaced as follow-ups.

---

## Level definitions

| Level | Includes | What runs |
|-------|----------|-----------|
| `cosmetic` | itself | backbone + `cleanup` + safety band |
| `micro` (DRY/KISS) | `cosmetic` | backbone + `cleanup` + `refactoring` + safety band |
| `meso` | `micro` | backbone + `cleanup` + `refactoring` + `refactoring-suite` + safety band |
| `architectural` | `meso` | backbone + `cleanup` + `refactoring` + `refactoring-suite` + `system-design` consultation + mandatory `pragya` checkpoint + safety band |

---

## Micro-Skills (orchestration steps)

### 1. Backbone — Investigate Before Changing
**Mode:** power
**Invokes:** `chesterton-fence`
**Inputs:** `target_files`, `repo_root`
**Outputs:** `intent_memo`, `edge_case_checklist`, `proceed` (boolean)
**Steps:**
1. Load `chesterton-fence` for every file in `target_files` that contains code that looks unused, weird, or older than the rest.
2. Collect the intent memo and the edge-case checklist.
3. If any item is unconfirmed → route to `pragya` and pause until resolved.

### 2. Backbone — Detect House Style
**Mode:** eco
**Invokes:** `style-conformance`
**Inputs:** `target_files`, `repo_root`
**Outputs:** `style_profile`
**Steps:**
1. Load `style-conformance`.
2. Collect `style_profile` so every later step conforms within scope.

### 3. Cosmetic Layer — Tidy Surface
**Mode:** eco
**Invokes:** `cleanup`
**Inputs:** `target_files`, `style_profile` (from step 2)
**Outputs:** `cosmetic_diff`
**Steps:**
1. Load `cleanup`.
2. Apply formatting, whitespace, dead-code removal — preserving TODO/FIXME/HACK/NOTE markers per the cleanup skill's smart-comment policy.
3. Collect `cosmetic_diff`.

### 4. Micro Layer — Extract / Simplify (level ≥ `micro`)
**Mode:** power
**Invokes:** `refactoring`
**Inputs:** `target_files`, `style_profile`, `cosmetic_diff`, `intent_memo`
**Outputs:** `micro_diff`
**Steps:**
1. Skip this step if `level == cosmetic`.
2. Load `refactoring`.
3. Apply extract-method, simplify-conditionals, guard clauses, small DRY consolidations, and call-site dependency inversion.
4. Collect `micro_diff`.

### 5. Meso Layer — Module-Boundary Patterns (level ≥ `meso`)
**Mode:** power
**Invokes:** `refactoring-suite`
**Inputs:** `target_files`, `style_profile`, `micro_diff`, `intent_memo`
**Outputs:** `meso_diff`
**Steps:**
1. Skip this step if `level in (cosmetic, micro)`.
2. Load `refactoring-suite`.
3. Apply broader rename/inline patterns and module-boundary tightening within the scoped target.
4. Collect `meso_diff`.

### 6. Architectural Layer — Targeted System-Design Consultation (level == `architectural`)
**Mode:** power
**Invokes:** `system-design`, then `pragya`
**Inputs:** `target_files`, `intent_memo`, `meso_diff`, the proposed architectural change
**Outputs:** `architectural_proposal`, `decision` (`proceed` | `defer` | `abort`)
**Steps:**
1. Skip this step if `level != architectural`.
2. Load `system-design` to scope the change (class hierarchies, package layout, DI/bean wiring) and produce an `architectural_proposal`.
3. Load `pragya` (mandatory at this level — architectural change is rarely behaviour-preserving) and present the proposal as a checkpoint with options: proceed now, defer to a separate ticket, abort.
4. Apply the proposed change ONLY if `decision == proceed`.

### 7. Safety Band — Characterisation Tests
**Mode:** power
**Invokes:** `tdd-workflow`
**Inputs:** `target_files`, the aggregated diff so far
**Outputs:** `safety_tests`, `pre_post_behaviour_match` (boolean)
**Steps:**
1. Load `tdd-workflow` in characterisation-test mode (capture current behaviour BEFORE applying changes; verify identical behaviour AFTER).
2. Collect `safety_tests` and the pre/post behaviour comparison.
3. Block delivery if `pre_post_behaviour_match == false` and the behaviour change was not explicitly authorised at level `architectural`.

### 8. Safety Band — Minimal-Diff Cap
**Mode:** eco
**Invokes:** `minimal-diff`
**Inputs:** the aggregated diff, `level`, declared `scope_statement`
**Outputs:** `diff_compliant` (boolean), `out_of_scope_suggestions`
**Steps:**
1. Load `minimal-diff` to enforce per-level diff caps and reversibility checks.
2. If the cap is exceeded → propose a commit split before delivering; do not silently widen the cap.
3. Collect `out_of_scope_suggestions`.

### 9. Audit
**Mode:** power
**Invokes:** `auditor`
**Inputs:** scratchpad plan, all step outputs, `level`
**Outputs:** `compliant`, `violations`, `blocked`
**Steps:**
1. Load `auditor`.
2. Verify the ladder was respected (no skipped rungs), the safety tests pass pre and post, the architectural step (if present) was preceded by a pragya decision, and the diff respects the minimal-diff cap.
3. Block delivery on any violation.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `level` | `enum` | yes | `cosmetic` \| `micro` \| `meso` \| `architectural`. |
| `target_files` | `string[]` | yes | Files in the refactor scope. |
| `repo_root` | `string` | yes | Project root. |
| `scope_statement` | `string` | yes | One-sentence statement of what should and should not change. |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `cosmetic_diff` | `string` | Cosmetic step output (always present). |
| `micro_diff` | `string` | Micro step output (level ≥ micro). |
| `meso_diff` | `string` | Meso step output (level ≥ meso). |
| `architectural_proposal` | `object` | Architectural step output (level == architectural). |
| `safety_tests` | `object` | Characterisation tests with pre/post comparison. |
| `out_of_scope_suggestions` | `string[]` | Tangential improvements deferred. |
| `compliant` | `boolean` | Whether the auditor passed. |

---

## Guardrails

- **No skipped rungs.** A `meso` request must execute `cosmetic` and `micro` first; ladder integrity is checked by the auditor.
- **No silent behaviour changes below `architectural`.** Cosmetic / micro / meso must produce identical observable behaviour pre- and post-refactor; the safety band enforces this.
- **Mandatory `pragya` at architectural level.** No architectural change is applied without an explicit user decision.
- **Backbone is always-on.** `chesterton-fence` and `style-conformance` run regardless of level — investigation and conformance are not optional.
- **Out-of-scope improvements are recorded, not applied.** Surfaced as `out_of_scope_suggestions`; the user can spin them out as separate tickets or a follow-up master invocation.

## Decision Criteria

| Situation | Action |
|-----------|--------|
| `level == cosmetic` but the agent observes a clear DRY violation | Surface as `out_of_scope_suggestions`; do NOT escalate the level silently. |
| Behaviour pre/post mismatch at level ≤ `meso` | Block delivery; route to `pragya`. |
| `system-design` returns a proposal that exceeds the declared `scope_statement` | Route to `pragya` for an explicit scope-widening decision. |
| Diff cap exceeded at any level | Pause; propose commit split; resume after user agreement. |
| `chesterton-fence` cannot reconstruct intent for some target file | Default to `proceed = false` for that file; route to `pragya`. |

## Success Criteria

- Ladder respected: no rung skipped for the requested level.
- `safety_tests.pre_post_behaviour_match == true` for level ≤ `meso`; explicitly authorised behaviour change at `architectural`.
- `compliant == true` from the auditor.
- Audit log includes one entry per executed step and each level's `_diff` field is populated as expected.

## Audit Log

```
[refactoring-workflow-started] level={level} files={N} scope="{scope_statement}"
[backbone-completed]           chesterton-passed={bool} style-profile-loaded={bool}
[layer-completed]              layer={cosmetic|micro|meso|architectural} diff_files={N}
[architectural-checkpoint]     decision={proceed|defer|abort}
[safety-tests]                 pre_post_match={bool} test_count={N}
[diff-cap]                     within_cap={bool} suggestions={N}
[refactoring-workflow-completed] level={level} compliant={bool}
```
