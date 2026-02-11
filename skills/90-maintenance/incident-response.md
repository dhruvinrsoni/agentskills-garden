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
