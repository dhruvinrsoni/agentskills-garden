---
name: incident-response-flow
description: >
  Master workflow for production incidents. Orchestrates incident response
  triage, root-cause analysis, log analysis, and decision-record capture
  into a single named sequence ending in an audit. Contains no
  implementation logic.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "0.1.0"
  dependencies: "constitution, scratchpad, pragya, librarian, auditor"
  reasoning_mode: plan-execute
  skill_type: master
---

# Incident Response Flow — Master Workflow

> _"Stop the bleeding. Find the cause. Read the receipts. Record the lesson. Audit the trail."_

## Context

Invoked when a production incident is declared, or when the user asks for
an end-to-end response (triage through postmortem). Freezes the canonical
incident sequence so the response shape is the same whether at 3am or
during a calm retro.

## Scope

**In scope:**

- Triaging the incident, applying mitigation, declaring severity.
- Investigating root cause once mitigation is in place.
- Mining logs for the sequence-of-events evidence.
- Capturing the durable lesson as a decision record.

**Out of scope:**

- The actual mitigation actions (delegated to `incident-response`).
- 5-whys / fault-tree mechanics (delegated to `root-cause-analysis`).
- Log parsing primitives (delegated to `log-analysis`).
- ADR formatting (delegated to `decision-records`).

---

## Micro-Skills (orchestration steps)

### 1. Triage and Mitigate
**Mode:** power
**Invokes:** `incident-response`
**Inputs:** `alert_payload`, `service_id`, declared `severity` (or `auto`)
**Outputs:** `mitigation_applied` (action description), `incident_id`, `service_state`
**Steps:**
1. Load `incident-response` via the librarian.
2. Pass alert and service context.
3. Collect `mitigation_applied`, `incident_id`, and current `service_state`.
4. If mitigation does not stabilise the service → route to `pragya` for an escalation checkpoint before proceeding.

### 2. Root-Cause Analysis
**Mode:** power
**Invokes:** `root-cause-analysis`
**Inputs:** `incident_id`, `mitigation_applied`, `service_state`, recent deploy/change list
**Outputs:** `rca_summary`, `confirmed_cause`, `contributing_factors`, `evidence_pointers`
**Steps:**
1. Load `root-cause-analysis`.
2. Pass the incident context and the change window.
3. Collect the RCA summary and the confirmed cause.

### 3. Log Evidence
**Mode:** eco
**Invokes:** `log-analysis`
**Inputs:** `evidence_pointers` (from step 2), incident time window
**Outputs:** `log_evidence` (correlated event timeline)
**Steps:**
1. Load `log-analysis`.
2. Pass the time window and the suspect components from RCA.
3. Collect `log_evidence` to either confirm or refute the candidate cause.
4. If `log_evidence` contradicts the candidate cause → loop back to step 2 with the new evidence; record the loop in the audit log.

### 4. Capture Decision Record
**Mode:** eco
**Invokes:** `decision-records`
**Inputs:** `rca_summary`, `confirmed_cause`, `mitigation_applied`, `log_evidence`
**Outputs:** `adr_path`, `adr_id`
**Steps:**
1. Load `decision-records`.
2. Build an ADR covering: context (incident), decision (mitigation kept / replaced), consequences (action items, follow-up tickets).
3. Collect the ADR path so future incidents can find it.

### 5. Audit
**Mode:** power
**Invokes:** `auditor`
**Inputs:** scratchpad plan, all step outputs
**Outputs:** `compliant`, `violations`, `blocked`
**Steps:**
1. Load `auditor`.
2. Verify each step produced its named output, the RCA loop (if any) is logged, and the ADR captures the confirmed cause.
3. Block delivery on any violation.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alert_payload` | `object` | yes | The originating alert / page payload. |
| `service_id` | `string` | yes | The affected service. |
| `severity` | `enum` | no | `sev1` \| `sev2` \| `sev3` \| `auto`. |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `mitigation_applied` | `string` | What stopped the bleeding. |
| `confirmed_cause` | `string` | Verified root cause. |
| `log_evidence` | `object` | Time-correlated event timeline. |
| `adr_path` | `string` | Where the durable lesson is recorded. |
| `compliant` | `boolean` | Whether the auditor passed. |

---

## Guardrails

- Step 1 (mitigation) runs FIRST, always. RCA does not begin while users are still impacted.
- Step 3 may loop back to step 2 at most twice; further loops require a `pragya` escalation.
- The ADR step is non-skippable — an undocumented incident is a future incident.
- The auditor MUST verify the ADR exists and references the confirmed cause.

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Alert payload incomplete | Pause; route to `pragya` to gather context. |
| Mitigation does not stabilise | Escalate via `pragya` before continuing. |
| RCA inconclusive after 2 log-evidence loops | Capture an ADR with `confirmed_cause = "UNKNOWN — see follow-ups"` and surface to the user. |
| Confirmed cause is a known previously-fixed issue | ADR references the prior ADR and flags regression. |

## Success Criteria

- `service_state` reaches `stable` after step 1.
- `confirmed_cause` is either named or explicitly marked unknown with follow-ups.
- `adr_path` exists and is committed to the repo.
- Audit log shows every step and any RCA loop.

## Audit Log

```
[incident-response-started] incident="{incident_id}" service="{service_id}" severity={sev}
[step-completed]            step={1..4} skill={invoked} outcome={summary}
[rca-loop]                  iteration={N} reason="{evidence contradicted candidate}"
[escalation]                step={N} reason="{trigger}" target=pragya
[incident-response-completed] adr={adr_path} compliant={bool}
```
