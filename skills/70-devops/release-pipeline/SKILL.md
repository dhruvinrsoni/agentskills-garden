---
name: release-pipeline
description: >
  Master workflow for cutting a release. Orchestrates test strategy
  selection, changelog generation, and CI pipeline invocation as a single
  named sequence ending in an audit. Contains no implementation logic.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "0.1.0"
  dependencies: "constitution, scratchpad, pragya, librarian, auditor"
  reasoning_mode: plan-execute
  skill_type: master
---

# Release Pipeline — Master Workflow

> _"Test what you ship. Document what changed. Pipeline what you proved. Audit what you released."_

## Context

Invoked when the user asks to cut a release, ship a version, or build the
release artefact end-to-end. Freezes the canonical release sequence so
every release follows the same shape — testable, reviewable, traceable.

This is the master skill named directly in
[`constitution/SKILL.md`](../../00-foundation/constitution/SKILL.md) (skill
hierarchy table) as the example of an orchestration workflow.

## Scope

**In scope:**

- Sequencing the three release steps and the closing audit.
- Forwarding outputs of each step into the next.
- Pausing for `pragya` checkpoints when a step requests direction.

**Out of scope:**

- Designing the test pyramid (delegated to `test-strategy`).
- Writing the changelog (delegated to `changelog-generation`).
- Executing the CI pipeline (delegated to `ci-pipeline`).
- Choosing the version bump (handled inside `changelog-generation`).
- Production deployment itself (release-pipeline ends at the artefact).

---

## Micro-Skills (orchestration steps)

### 1. Establish Test Strategy
**Mode:** power
**Invokes:** `test-strategy`
**Inputs:** `repo_root`, `release_scope` (commits since previous tag)
**Outputs:** `test_plan` (selected pyramid layers, coverage targets, must-pass suites)
**Steps:**
1. Load `test-strategy` via the librarian.
2. Pass `repo_root` and `release_scope`.
3. Collect `test_plan` and forward to step 3.

### 2. Generate Changelog
**Mode:** eco
**Invokes:** `changelog-generation`
**Inputs:** `repo_root`, `release_scope`, previous tag
**Outputs:** `changelog_entry`, `proposed_version`
**Steps:**
1. Load `changelog-generation`.
2. Pass commit range and conventional-commit prefixes.
3. Collect `changelog_entry` and `proposed_version`.

### 3. Run CI Pipeline
**Mode:** power
**Invokes:** `ci-pipeline`
**Inputs:** `repo_root`, `test_plan` (from step 1), `proposed_version` (from step 2)
**Outputs:** `pipeline_result` (artefacts, gate statuses, signed checksums)
**Steps:**
1. Load `ci-pipeline`.
2. Pass `test_plan` so the pipeline runs the agreed suites with the agreed coverage gates.
3. Pass `proposed_version` so the artefact is named correctly.
4. Collect `pipeline_result`.
5. If any gate fails → route to `pragya` with the failure as input; do not silently retry.

### 4. Audit
**Mode:** power
**Invokes:** `auditor`
**Inputs:** scratchpad plan, `test_plan`, `changelog_entry`, `pipeline_result`
**Outputs:** `compliant`, `violations`, `blocked`
**Steps:**
1. Load `auditor`.
2. Verify every named gate fired, no protected term was modified, the changelog covers every diff hunk, and the pipeline output is signed.
3. Block delivery on any violation.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_root` | `string` | yes | Path to the project being released. |
| `previous_tag` | `string` | no | Last release tag; defaults to most recent annotated tag. |
| `release_type` | `enum` | no | `patch` \| `minor` \| `major` \| `auto`. Defaults to `auto` (driven by changelog-generation). |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `test_plan` | `object` | The agreed test scope and gates. |
| `changelog_entry` | `string` | Markdown changelog block for the new version. |
| `proposed_version` | `string` | Semver string. |
| `pipeline_result` | `object` | Artefact paths, gate statuses, signatures. |
| `compliant` | `boolean` | Whether the auditor passed. |

---

## Guardrails

- All three steps must complete in order; CI cannot run without an established test plan and a versioned changelog.
- A failed pipeline step does NOT auto-retry; it routes to `pragya` for the user to choose between fix-and-retry, abort, or ship-with-known-failures.
- The auditor is mandatory; a release artefact without an audit pass is not delivered.

## Decision Criteria

| Situation | Action |
|-----------|--------|
| `release_scope` is empty | Abort — nothing to release; surface as a `pragya` notification. |
| Conventional commits absent or malformed | `changelog-generation` raises an Ask-When-Ambiguous; chain pauses. |
| Pipeline gate flapping | Route to `pragya`; do not retry silently more than once. |
| Auditor flags missing changelog hunks | Block release; require updated changelog. |

## Success Criteria

- `pipeline_result.compliant == true` and every gate listed in `test_plan` shows `pass`.
- `changelog_entry` covers every commit in `release_scope`.
- Audit log includes one entry per orchestration step.

## Audit Log

```
[release-pipeline-started] repo="{repo_root}" range="{prev}..HEAD"
[step-completed]           step={1..3} skill={invoked} outcome={summary}
[pipeline-failure]         gate="{name}" routed_to=pragya
[release-pipeline-completed] version={proposed_version} artefacts={N} compliant={bool}
```
