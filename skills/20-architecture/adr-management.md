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
