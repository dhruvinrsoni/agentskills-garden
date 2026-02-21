```markdown
---
name: decision-records
description: >
  Create, manage, and query Architectural Decision Records (ADRs) using
  the context/decision/consequences format to capture design rationale.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - adr-management
reasoning_mode: plan-execute
---

# Decision Records

> _"Decisions are first-class artifacts — capture them or lose them."_

## Context

Invoked when a significant technical or architectural decision needs to be
recorded, when existing ADRs need to be queried for historical context, or
when decisions need to be superseded or amended. Uses the context/decision/
consequences format to ensure every decision captures why it was made, what
alternatives were considered, and what trade-offs were accepted.

---

## Micro-Skills

### 1. ADR Creation 🌿 (Eco Mode)

**Steps:**

1. Assign the next sequential ADR number (e.g., `ADR-0042`).
2. Populate the ADR template with:
   - **Title:** Short imperative statement (e.g., "Use PostgreSQL for user data").
   - **Status:** `proposed` | `accepted` | `deprecated` | `superseded`.
   - **Context:** Forces and circumstances driving the decision.
   - **Decision:** The chosen approach with rationale.
   - **Consequences:** Positive, negative, and neutral outcomes.
   - **Alternatives Considered:** Other options and why they were rejected.
3. Save to the designated ADR directory (e.g., `docs/decisions/`).
4. Update the ADR index/table of contents.

### 2. ADR Query & Search 🌿 (Eco Mode)

**Steps:**

1. Parse all existing ADRs in the decisions directory.
2. Build a searchable index by title, status, tags, and date.
3. Answer queries like "Why did we choose X?" by locating the relevant ADR.
4. Surface related ADRs that may be impacted by a new decision.

### 3. ADR Lifecycle Management ⚡ (Power Mode)

**Steps:**

1. When a decision is reversed or evolved, create a new ADR that supersedes the old one.
2. Update the superseded ADR's status to `superseded by ADR-{new_number}`.
3. Trace decision chains: original → amendments → supersessions.
4. Generate a decision timeline or dependency graph.

---

## Inputs

| Parameter        | Type     | Required | Description                                       |
|------------------|----------|----------|---------------------------------------------------|
| `title`          | `string` | yes      | Short imperative decision statement                |
| `context`        | `string` | yes      | Forces driving this decision                       |
| `decision`       | `string` | no       | The chosen approach (can be filled interactively)  |
| `alternatives`   | `string[]`| no      | Other options considered                           |
| `adr_dir`        | `string` | no       | Directory for ADR files (default: `docs/decisions`)|

## Outputs

| Field            | Type     | Description                                       |
|------------------|----------|---------------------------------------------------|
| `adr_file`       | `string` | Path to the created/updated ADR file               |
| `adr_number`     | `string` | Assigned ADR identifier                            |
| `related_adrs`   | `string[]`| ADRs related to or impacted by this decision      |
| `index_updated`  | `boolean`| Whether the ADR index was updated                  |

---

## Scope

### In Scope
- Creating new ADRs with context/decision/consequences structure
- Querying existing ADRs by keyword, status, tag, or date range
- Managing ADR lifecycle (proposed → accepted → deprecated → superseded)
- Linking related decisions and building decision chains
- Maintaining the ADR index/table of contents
- Generating decision timelines and impact graphs

### Out of Scope
- Making the actual technical decisions (this skill records decisions, not makes them)
- Writing detailed design documents or RFCs (use system-design skill)
- Project management or sprint planning decisions
- Non-technical decisions (business, legal, HR)
- Implementing the changes described in a decision

## Guardrails

- Preview diffs before applying any changes.
- Never touch generated, vendor, third_party, build, or dist folders unless explicitly allowed.
- Run formatter and linter after changes; revert if errors introduced.
- Never modify the decision or context of an accepted ADR — create a superseding ADR instead.
- Always include at least two alternatives considered (even if one is "do nothing").
- Ensure every ADR has a clear, non-ambiguous status field.
- Do not delete ADR files — deprecated or superseded ADRs remain as historical record.
- ADR numbering must be strictly sequential with no gaps in the series.

## Ask-When-Ambiguous

### Triggers
- Decision scope is unclear (team-level vs org-level vs project-level)
- No explicit alternatives have been provided by the requester
- An existing ADR appears to cover the same topic
- The decision's status lifecycle is uncertain (e.g., already partially implemented)

### Question Templates
1. "An existing ADR (`{adr_id}: {adr_title}`) covers a similar topic. Should this new decision supersede it, amend it, or stand independently?"
2. "No alternatives were provided. Can you list at least one alternative you considered before choosing `{decision}`?"
3. "What is the scope of this decision — does it apply to this project only, or across the organization?"
4. "This decision appears to already be implemented. Should the status be `accepted` with a retroactive date, or `proposed` for formal review?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| New significant technical decision | Create a new ADR with full context/decision/consequences |
| Existing ADR covers the same topic | Confirm with user whether to supersede or amend |
| Decision is being reversed | Create superseding ADR; update original status to `superseded` |
| Minor implementation detail | Do not create an ADR; suggest inline code comment instead |
| Decision has organizational impact | Include stakeholder list and approval status in the ADR |
| No alternatives provided | Prompt the user; at minimum include "Do nothing / status quo" |

## Success Criteria

- [ ] ADR contains all required sections: Title, Status, Context, Decision, Consequences
- [ ] At least two alternatives are documented with reasons for rejection
- [ ] ADR follows the project's established numbering and naming convention
- [ ] ADR index/table of contents is updated to include the new record
- [ ] Related or impacted ADRs are cross-referenced
- [ ] Status field accurately reflects the decision's current lifecycle stage

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Duplicate ADR for same decision | Two ADRs address identical concerns with conflicting conclusions | Search existing ADRs before creation; flag matches for review |
| Missing consequences section | ADR lacks trade-off analysis; team unaware of risks | Validate template completeness before saving; reject incomplete ADRs |
| Orphaned supersession chain | Superseded ADR not updated; both appear active | Automatically update the old ADR's status when creating a superseding one |
| Context too vague | Future readers cannot understand why the decision was made | Require at least 3 sentences of context explaining the forces at play |
| ADR number collision | Two ADRs assigned the same number in concurrent workflows | Read existing ADR directory and assign `max(existing) + 1` atomically |

## Audit Log

- `[{timestamp}] adr-created: Created {adr_id} — "{title}" with status {status} in {adr_dir}`
- `[{timestamp}] adr-superseded: {old_adr_id} superseded by {new_adr_id} — "{title}"`
- `[{timestamp}] adr-status-changed: {adr_id} status changed from {old_status} to {new_status}`
- `[{timestamp}] adr-index-updated: ADR index refreshed — {total_count} records ({accepted_count} accepted, {deprecated_count} deprecated)`
- `[{timestamp}] adr-query: Searched ADRs for "{query}" — {result_count} matches found`
```
