---
name: adr-management
description: >
  Create, index, and maintain Architecture Decision Records (ADRs)
  using the Michael Nygard template.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# ADR Management

> _"Record the why, not just the what."_

## Context

Invoked when an architectural decision is made. ADRs prevent knowledge loss
and make trade-offs explicit for future maintainers.

---

## Micro-Skills

### 1. Create ADR 🌿 (Eco Mode)

**Steps:**

1. Create `docs/adr/` directory if it does not exist.
2. Determine the next sequential number (e.g., `ADR-0005`).
3. Generate the ADR from the Nygard template:

```markdown
# ADR-NNNN: <Title>

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-XXXX

## Context
<What is the issue that we're seeing that motivates this decision?>

## Decision
<What is the change that we're proposing and/or doing?>

## Consequences
<What becomes easier or more difficult because of this change?>
```

4. Add entry to `docs/adr/index.md`.

### 2. Supersede ADR 🌿 (Eco Mode)

**Steps:**

1. Update the old ADR status to `Superseded by ADR-XXXX`.
2. In the new ADR, reference the old one in the Context section.
3. Update `docs/adr/index.md`.

### 3. Search ADRs 🌿 (Eco Mode)

**Steps:**

1. Accept a keyword or topic from the user.
2. Scan all ADR files for matches.
3. Return a ranked list of relevant ADRs.

---

## Edge Cases

- Conflicting ADRs — Flag and ask user which takes precedence.
- ADR references deleted code — Mark as `Deprecated` with a note.

---

## Scope

### In Scope

- Creating, updating, and superseding ADR files in `docs/adr/`.
- Maintaining the ADR index (`docs/adr/index.md`).
- Searching and cross-referencing existing ADRs.
- Setting and transitioning ADR statuses (Proposed → Accepted → Deprecated → Superseded).
- Linking ADRs to related code, tickets, or other ADRs.

### Out of Scope

- Making the architectural decision itself — this skill records decisions, it does not choose technologies or patterns.
- Modifying source code, infrastructure configs, or CI/CD pipelines.
- Writing design documents, RFCs, or system design artifacts (use `system-design` skill).
- Enforcing ADR compliance at build/deploy time.

---

## Guardrails

- Never overwrite an existing ADR — supersede it with a new ADR instead.
- Always preserve the full history chain (Superseded by / Supersedes links).
- Require a non-empty Context and Decision section before setting status to `Accepted`.
- Validate that the ADR number is unique and sequential before writing.
- Do not auto-accept ADRs; status must remain `Proposed` until the user explicitly approves.
- Run a broken-link check on `docs/adr/index.md` after any mutation.
- Never delete an ADR file — deprecated or superseded ADRs stay in the repository for historical reference.

---

## Ask-When-Ambiguous

### Triggers

- The user describes a decision but does not specify whether it should be a new ADR or an amendment to an existing one.
- Multiple existing ADRs cover overlapping topics and it is unclear which to supersede.
- The user provides a title but no context or rationale.
- The ADR directory path differs from the default `docs/adr/`.

### Question Templates

- "Should this be recorded as a new ADR, or does it supersede an existing one (e.g., ADR-NNNN)?"
- "I found ADR-0003 and ADR-0007 both covering authentication strategy. Which one does this new decision supersede?"
- "You've provided the decision, but the Context section is empty. What problem or constraint motivated this choice?"
- "Your project stores ADRs in `{path}` instead of `docs/adr/`. Should I use that location?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| New architectural choice with no prior ADR on the topic | Create a new ADR with status `Proposed` |
| Existing ADR is no longer valid due to a new decision | Supersede the old ADR and create a new one referencing it |
| A decision is reversed without a replacement | Set the old ADR status to `Deprecated` with an explanation |
| User requests a quick lookup on past decisions | Use Search ADRs micro-skill and return ranked results |
| Two ADRs conflict on the same topic | Flag both to the user and ask which takes precedence before proceeding |
| ADR references code or components that no longer exist | Mark as `Deprecated` and add a note explaining what changed |

---

## Success Criteria

- [ ] ADR file is created in the correct directory with the correct sequential number.
- [ ] The ADR follows the Nygard template (Status, Context, Decision, Consequences).
- [ ] `docs/adr/index.md` is updated with the new or modified entry.
- [ ] Superseded ADRs have their status updated with a forward reference.
- [ ] No duplicate ADR numbers exist in the repository.
- [ ] All cross-references between ADRs resolve to valid files.
- [ ] The user has explicitly confirmed the ADR status transition (Proposed → Accepted).

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Duplicate ADR number assigned | Two files share the same `ADR-NNNN` prefix | Scan all existing ADR filenames before assigning the next number; abort and re-number if collision detected |
| Broken supersession chain | Old ADR still shows `Accepted` after being superseded | Always update the old ADR status in the same operation that creates the new one; verify both files after write |
| Index out of sync | `index.md` lists ADRs that don't exist or is missing new ones | Regenerate the index by scanning the `docs/adr/` directory after every create/supersede/deprecate operation |
| Empty Context or Decision section | ADR is accepted without meaningful rationale | Validate non-empty Context and Decision before allowing status to move beyond `Proposed` |
| ADR written for a non-architectural concern | Routine bug fixes or config changes recorded as ADRs | Check that the decision involves structural trade-offs; suggest a commit message or changelog entry instead |

---

## Audit Log

- `[{timestamp}] ADR-{number} CREATED — Title: "{title}" | Status: Proposed | File: docs/adr/{filename}`
- `[{timestamp}] ADR-{number} STATUS_CHANGED — From: {old_status} → To: {new_status} | Reason: "{reason}"`
- `[{timestamp}] ADR-{old_number} SUPERSEDED_BY ADR-{new_number} — "{old_title}" replaced by "{new_title}"`
- `[{timestamp}] ADR-{number} DEPRECATED — Reason: "{reason}"`
- `[{timestamp}] INDEX_UPDATED — Entries: {count} | File: docs/adr/index.md`
- `[{timestamp}] SEARCH_EXECUTED — Query: "{keyword}" | Results: {count} ADRs matched`
