---
name: incident-response
description: >
  Structured steps to triage, mitigate, and resolve production
  incidents. Includes severity classification and postmortem template.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - auditor
reasoning_mode: plan-execute
---

# Incident Response

> _"When the pager fires, follow the playbook."_

## Context

Invoked during production incidents. Provides a structured workflow to
minimize downtime and capture learnings for prevention.

---

## Micro-Skills

### 1. Severity Classification ⚡ (Power Mode)

**Steps:**

1. Assess the incident:
   | Severity | Impact                       | Response Time |
   |----------|------------------------------|---------------|
   | **SEV1** | Full outage, data loss       | Immediate     |
   | **SEV2** | Major feature degraded       | < 30 minutes  |
   | **SEV3** | Minor feature affected       | < 4 hours     |
   | **SEV4** | Cosmetic / non-user-facing   | Next sprint   |
2. Assign an Incident Commander (IC).
3. Open a communication channel (Slack, Teams).

### 2. Triage ⚡ (Power Mode)

**Steps:**

1. **Identify:** What is broken? Which services? Which users?
2. **Correlate:** Check recent deployments, config changes, traffic spikes.
3. **Isolate:** Find the failing component using:
   - Error rates in dashboards.
   - Recent log entries (filter by `level=error`).
   - Distributed traces for failed requests.

### 3. Mitigate ⚡ (Power Mode)

**Steps:**

1. Apply the fastest safe mitigation:
   - **Rollback** the most recent deployment.
   - **Scale up** if the issue is capacity-related.
   - **Feature flag** off if a specific feature is the cause.
   - **Redirect traffic** if a region/zone is unhealthy.
2. Verify mitigation: confirm error rates are dropping.
3. Communicate status to stakeholders.

### 4. Postmortem ⚡ (Power Mode)

**Steps:**

1. After resolution, write a blameless postmortem:
   ```markdown
   ## Incident Postmortem — [Title]
   **Date:** YYYY-MM-DD
   **Duration:** Xh Ym
   **Severity:** SEV-N
   **Impact:** <who/what was affected>

   ### Timeline
   - HH:MM — Incident detected
   - HH:MM — IC assigned
   - HH:MM — Root cause identified
   - HH:MM — Mitigation applied
   - HH:MM — Resolved

   ### Root Cause
   <What actually happened>

   ### Action Items
   - [ ] <Preventive action 1>
   - [ ] <Preventive action 2>

   ### Lessons Learned
   - <What went well>
   - <What went poorly>
   ```
2. Share with the team and track action items.

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `severity`      | `string` | SEV1-SEV4 classification                 |
| `timeline`      | `object` | Incident timeline                        |
| `mitigation`    | `string` | Applied mitigation description           |
| `postmortem`    | `string` | Postmortem document                      |

---

## Scope

### In Scope

- Classifying incident severity (SEV1–SEV4) based on user impact and blast radius
- Triaging production incidents: identifying affected services, correlating recent changes, isolating the failing component
- Recommending and documenting mitigation actions (rollback, scale-up, feature-flag, traffic redirect)
- Generating blameless postmortem documents with timelines, root causes, and action items
- Coordinating communication cadence and stakeholder updates during active incidents
- Tracking postmortem action items to completion

### Out of Scope

- Performing infrastructure changes directly (Terraform applies, Kubernetes scaling) — delegate to `terraform-iac` or `kubernetes-helm`
- Long-term capacity planning or architecture redesign — delegate to `system-design`
- Writing or modifying monitoring/alerting rules — delegate to `monitoring-setup`
- Root-cause analysis of non-production bugs or test failures — delegate to `root-cause-analysis`
- Security-specific incident handling (breach containment, forensics) — delegate to `threat-modeling` and `secure-coding-review`

---

## Guardrails

- Never skip severity classification; every incident must have a SEV level before triage begins
- Always assign an Incident Commander before starting mitigation — no "everyone owns it" situations
- Prefer the fastest safe mitigation over the most thorough fix; optimise for MTTR, not perfection
- Never deploy a forward-fix during an active SEV1/SEV2 without IC approval — prefer rollback
- Do not assign blame in postmortems; use "the system allowed" language, not "person X caused"
- Require at least one preventive action item per postmortem — no postmortem closes without follow-up
- Preserve all raw logs, traces, and dashboards snapshots referenced during triage before they rotate out
- If the incident is unresolved after the expected response-time window, escalate severity by one level

---

## Ask-When-Ambiguous

### Triggers

- The incident affects multiple services and the primary failing component is unclear
- A recent deployment and a traffic spike happened at the same time, making correlation uncertain
- The preferred mitigation (rollback) would also revert an unrelated critical fix
- Severity could reasonably be classified at two adjacent levels (e.g., SEV2 vs SEV3)
- The incident has been mitigated but the root cause is still unknown, and the team must decide whether to keep investigating or close

### Question Templates

- "Multiple services are degraded (`{service_list}`). Which service's restoration should be prioritised?"
- "A rollback would also revert `{unrelated_change}`. Should I proceed with rollback or attempt a targeted forward-fix?"
- "Impact is ambiguous — `{N}` users affected but only in `{region}`. Classify as SEV2 or SEV3?"
- "Root cause is still unidentified after mitigation. Should the incident remain open for investigation or close with a follow-up ticket?"
- "Communication channel preference: Slack `#incidents`, Teams, or PagerDuty war-room?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Full production outage affecting all users | Classify SEV1, page on-call immediately, open war-room |
| Single feature degraded, workaround exists | Classify SEV2/SEV3 depending on feature criticality |
| Most recent deploy correlates with error spike | Rollback the deploy as first mitigation |
| Error spike with no recent deploy | Investigate infrastructure (capacity, DNS, third-party dependency) |
| Mitigation applied, error rates still elevated | Verify mitigation target is correct; escalate severity if no improvement in 10 minutes |
| Multiple possible root causes identified | Pursue the hypothesis with the strongest log/trace evidence first |
| Rollback would revert a security patch | Attempt targeted forward-fix with IC approval; keep rollback as fallback |
| Incident resolved but root cause unknown | Close incident, open follow-up investigation ticket with 48-hour deadline |
| Postmortem reveals systemic weakness | Create action items tagged as tech-debt; invoke `tech-debt-tracking` |

---

## Success Criteria

- [ ] Incident has a severity classification assigned within 5 minutes of detection
- [ ] Incident Commander identified and acknowledged in the communication channel
- [ ] Timeline captures all key events with timestamps accurate to the minute
- [ ] Mitigation reduced error rate / restored availability to pre-incident levels
- [ ] Stakeholders received at least one status update during the incident
- [ ] Blameless postmortem document created within 48 hours of resolution
- [ ] At least one preventive action item identified and tracked in the backlog
- [ ] All raw evidence (logs, traces, dashboard snapshots) linked or archived in the postmortem
- [ ] Postmortem shared with the broader engineering team

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| No severity assigned | Team scrambles without clear urgency; responders unsure of SLA | Enforce severity classification as the mandatory first step in every incident workflow |
| Missing Incident Commander | Parallel conflicting mitigations; nobody owns communication | Auto-assign the on-call engineer as IC until explicitly handed off |
| Premature root-cause fixation | Team tunnels on one hypothesis while the real cause persists | Time-box each hypothesis to 15 minutes; if no evidence, pivot to the next |
| Rollback not available | Last known good version unclear or deployment pipeline broken | Maintain a rollback runbook and verify rollback capability during deploy readiness checks |
| Postmortem skipped | Same incident recurs because no preventive actions were taken | Gate incident closure on postmortem completion; auditor flags incidents closed without one |
| Blame-driven postmortem | Team members become defensive; future incidents go unreported | Review postmortem language for blame; replace "person X" with "the process/system allowed" |
| Stale communication | Stakeholders escalate redundantly; leadership loses trust | Set a cadence (every 30 min for SEV1, every 1 h for SEV2) and automate reminders |
| Evidence lost to log rotation | Root cause analysis blocked by missing data | Snapshot critical logs and traces within first 15 minutes; archive before retention window expires |

---

## Audit Log

- `2025-02-21T00:00:00Z` — Skill created with severity classification, triage, mitigation, and postmortem micro-skills.
- `2026-02-21T00:00:00Z` — Appended Scope, Guardrails, Ask-When-Ambiguous, Decision Criteria, Success Criteria, Failure Modes, and Audit Log sections to align with spec schema.
