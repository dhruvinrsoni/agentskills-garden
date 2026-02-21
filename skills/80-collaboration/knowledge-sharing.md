````markdown
---
name: knowledge-sharing
description: >
  Establish documentation culture, wikis, runbooks, onboarding guides,
  and tribal knowledge capture to reduce bus factor and accelerate teams.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - inline-documentation
reasoning_mode: plan-execute
---

# Knowledge Sharing

> _"Knowledge hoarded is knowledge lost — write it down or it walks out the door."_

## Context

Invoked when building or improving knowledge management practices across a
team — creating runbooks, onboarding guides, internal wikis, and processes
for capturing tribal knowledge. Reduces bus factor, accelerates onboarding,
and ensures critical operational knowledge survives team changes.

---

## Micro-Skills

### 1. Runbook Authoring ⚡ (Power Mode)

**Steps:**

1. Identify operational procedures that require documentation:
   - Incident response steps, deployment rollbacks, database migrations.
   - On-call escalation paths and decision trees.
2. Structure each runbook with:
   - **Title** — Action-oriented (e.g., "Restore Production Database from Backup").
   - **When to Use** — Trigger conditions.
   - **Prerequisites** — Access, tools, permissions needed.
   - **Steps** — Numbered, copy-pasteable commands where applicable.
   - **Verification** — How to confirm the procedure succeeded.
   - **Rollback** — How to undo if something goes wrong.
3. Store runbooks in a discoverable location (repo `/docs/runbooks/`, wiki, or Notion).
4. Assign an owner responsible for keeping each runbook current.

### 2. Onboarding Guide Creation ⚡ (Power Mode)

**Steps:**

1. Define onboarding tracks:
   - **Day 1** — Environment setup, access provisioning, team introductions.
   - **Week 1** — Architecture overview, key repo walkthrough, first small task.
   - **Month 1** — Deeper domain knowledge, ownership of a small feature area.
2. Create step-by-step setup guide:
   - Clone repos, install dependencies, configure local environment.
   - Run tests, start the dev server, verify end-to-end flow.
3. List key contacts and their areas of expertise.
4. Include a "first tasks" list of good starter issues labeled `good-first-issue`.

### 3. Tribal Knowledge Capture 🌿 (Eco Mode)

**Steps:**

1. Identify knowledge held by single individuals (bus factor = 1):
   - Interview team members: "What do only you know how to do?"
   - Review on-call logs: who gets paged for specific systems?
   - Check Git blame: who is the sole contributor to critical modules?
2. Schedule knowledge transfer sessions (pair programming or walkthrough).
3. Document outcomes as wiki pages, ADRs, or inline code comments.
4. Cross-train at least one additional person on each critical knowledge area.

### 4. Wiki & Documentation Culture 🌿 (Eco Mode)

**Steps:**

1. Establish documentation standards:
   - Every new service/feature gets a README and architecture doc.
   - Every incident gets a post-mortem document.
   - Every architectural decision gets an ADR.
2. Set up a searchable wiki (Notion, Confluence, GitHub Wiki, or repo-based).
3. Implement "docs as code" — documentation lives alongside source code, reviewed in PRs.
4. Schedule quarterly documentation audits to retire stale content.

---

## Inputs

| Parameter          | Type       | Required | Description                                      |
|--------------------|------------|----------|--------------------------------------------------|
| `team_name`        | `string`   | yes      | Team or project to create knowledge artifacts for|
| `knowledge_gaps`   | `string[]` | no       | Known areas lacking documentation                |
| `doc_platform`     | `string`   | no       | Wiki platform (Notion, Confluence, GitHub Wiki)  |
| `bus_factor_areas` | `string[]` | no       | Systems/modules with single-person knowledge     |

## Outputs

| Field               | Type       | Description                                      |
|---------------------|------------|--------------------------------------------------|
| `runbooks`          | `string[]` | Generated runbook documents                      |
| `onboarding_guide`  | `string`   | Complete onboarding document                     |
| `wiki_structure`    | `object`   | Proposed wiki organization and page hierarchy    |
| `knowledge_map`     | `object`   | Map of knowledge areas to owners and backups     |

---

## Edge Cases

- Team member leaving with undocumented knowledge — Prioritize emergency knowledge transfer sessions; record video walkthroughs as a fallback.
- Documentation exists but is outdated and misleading — Worse than no documentation; schedule a doc audit sprint to update or archive stale pages.
- Remote/async team with no synchronous overlap — Use recorded video walkthroughs (Loom, recorded meetings) and written Q&A threads.
- Resistance to documentation ("I'd rather just code") — Start with lightweight formats (README sections, inline comments) and demonstrate value through faster onboarding.

---

## Scope

### In Scope

- Creating and maintaining operational runbooks for critical procedures
- Designing onboarding guides and new-hire documentation tracks
- Identifying and capturing tribal knowledge from single points of failure
- Establishing documentation culture standards and review practices
- Wiki/knowledge base organization, structure, and search optimization
- Documentation audit scheduling and stale content retirement
- "Docs as code" workflows — documentation in repos, reviewed in PRs
- Knowledge maps linking expertise areas to team members and backups

### Out of Scope

- API documentation generation (handled by `api-documentation`)
- Inline code documentation and comment standards (handled by `inline-documentation`)
- Architecture Decision Records (handled by `decision-records`)
- Release notes and changelogs (handled by `changelog-generation`)
- Meeting facilitation and agenda management
- HR onboarding processes (benefits, compliance, payroll)

---

## Guardrails

- Never publish runbooks containing production credentials, secrets, or PII — reference secret managers or vaults instead.
- Documentation must be stored in a searchable, version-controlled location — not in personal notes, Slack messages, or email threads.
- Every runbook must have a designated owner; ownerless runbooks are flagged for adoption or retirement.
- Do not document workarounds for known bugs as permanent solutions — file the bug and link the workaround as temporary.
- Onboarding guides must be tested by a recent new hire before being considered complete.
- Stale documentation (not updated in 6+ months) must be reviewed before being shared — add a visible staleness warning.
- Knowledge transfer sessions must produce a written artifact (doc, wiki page, or ADR) — verbal-only transfer does not count.

## Ask-When-Ambiguous

### Triggers

- Team has no existing documentation and it's unclear where to start
- Multiple documentation platforms are in use and the canonical source is undefined
- Bus factor assessment reveals many single-point-of-failure areas simultaneously
- Onboarding experience varies significantly between new hires
- Team disagrees on documentation depth (concise vs comprehensive)

### Question Templates

1. "Where does your team currently store documentation — repo, wiki, Notion, Confluence, or scattered across tools?"
2. "Which systems or processes have bus factor = 1 (only one person knows how they work)?"
3. "What does the onboarding experience look like today, and where do new hires typically get stuck?"
4. "Should documentation follow a 'docs as code' approach (in-repo, PR-reviewed) or a wiki-based approach?"
5. "How often should documentation be audited for staleness — monthly, quarterly, or on an ad-hoc basis?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Team has zero documentation | Start with onboarding guide and top-3 most-paged runbooks |
| Bus factor = 1 for a critical system | Schedule immediate knowledge transfer session; produce written artifact |
| Team member giving notice with undocumented knowledge | Prioritize video-recorded walkthrough + written runbook within their notice period |
| Multiple wiki platforms in use | Consolidate to one canonical platform; redirect or archive others |
| Documentation exists but is > 6 months stale | Run a doc audit sprint; update, archive, or flag with staleness warnings |
| New service or feature is being built | Require README and architecture doc as part of the definition of done |
| Incident occurs for an undocumented procedure | Write the runbook as part of the post-mortem action items |
| Team is fully remote/async | Prefer written documentation over synchronous walkthroughs; use recorded videos as supplement |
| Resistance to documentation from team | Start lightweight (README, inline comments); demonstrate value via reduced repeat questions |

## Success Criteria

- [ ] Every critical system has at least one operational runbook with a designated owner
- [ ] Onboarding guide exists and has been validated by a recent new hire
- [ ] Bus factor ≥ 2 for all critical knowledge areas (at least two people can perform each procedure)
- [ ] Documentation is stored in a single, searchable, version-controlled platform
- [ ] Stale documentation (> 6 months without update) is < 20% of total pages
- [ ] New services/features include a README and architecture doc at launch
- [ ] Knowledge transfer sessions produce written artifacts, not just verbal handoffs
- [ ] Quarterly documentation audit is scheduled and executed

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Documentation rot | Runbooks reference deprecated commands, old URLs, or removed services | Schedule quarterly doc audits; add "last verified" dates to all runbooks |
| Scattered knowledge | Docs spread across Slack, email, Notion, Confluence, and repo wikis | Consolidate to one canonical platform; create redirects from old locations |
| Bus factor = 1 | Only one person can perform a critical procedure; team is paralyzed when they're unavailable | Identify bus-factor-1 areas quarterly; schedule cross-training sessions |
| Onboarding friction | New hires take 2+ weeks to make their first meaningful contribution | Test onboarding guide with each new hire; update based on their feedback |
| Write-once-read-never | Team writes docs but nobody references them | Integrate docs into workflows (link from error messages, CI output, runbooks from alerts) |
| Credential leakage | Runbook accidentally includes production secrets | Use pre-commit hooks to scan for secrets; reference vault paths instead of values |
| Documentation debt | Team acknowledges docs are needed but never prioritizes writing them | Allocate fixed percentage of sprint capacity (e.g., 10%) to documentation tasks |
| Stale onboarding guide | Setup instructions fail because tooling or dependencies changed | Require onboarding guide verification with each major tooling change |

## Audit Log

- `[timestamp]` runbook-created: Created runbook `<runbook-title>` for `<system>` — owner: `<owner-name>`
- `[timestamp]` onboarding-guide-updated: Updated `<section>` of onboarding guide — verified by `<new-hire-name>`
- `[timestamp]` knowledge-transfer-completed: `<topic>` transferred from `<source-person>` to `<target-person>` — artifact: `<doc-link>`
- `[timestamp]` bus-factor-assessed: `<system>` bus factor changed from `<old>` to `<new>` after cross-training
- `[timestamp]` doc-audit-completed: Reviewed `<total-pages>` pages — updated: `<updated-count>`, archived: `<archived-count>`, flagged: `<flagged-count>`
- `[timestamp]` wiki-consolidated: Migrated `<page-count>` pages from `<old-platform>` to `<new-platform>`
- `[timestamp]` stale-doc-flagged: `<doc-title>` last updated `<days-ago>` days ago — assigned to `<owner>` for review

````
