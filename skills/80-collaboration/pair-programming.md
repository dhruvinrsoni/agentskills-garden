````markdown
---
name: pair-programming
description: >
  Facilitate effective pair and mob programming sessions including role
  rotation, session structure, and knowledge transfer practices.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: mixed
---

# Pair Programming

> _"Two minds on one problem beats two people on two problems."_

## Context

Invoked when facilitating pair programming or mob programming sessions —
defining driver/navigator roles, structuring session flow, managing rotations,
and ensuring effective knowledge transfer. Applies to both real-time
co-located sessions and remote collaboration via shared editors or screen
sharing.

---

## Micro-Skills

### 1. Session Setup 🌿 (Eco Mode)

**Steps:**

1. Define the session goal — specific task, bug, or learning objective.
2. Select pairing style:
   - **Driver/Navigator** — One types, one reviews and directs.
   - **Ping-Pong** — Alternate writing tests and implementation (TDD).
   - **Strong-Style** — Navigator dictates at the highest abstraction the driver can understand.
3. Set up shared environment:
   - VS Code Live Share, Tuple, or screen sharing with remote control.
   - Ensure both participants have access to repository, CI, and docs.
4. Agree on rotation interval (typically 15–25 minutes).
5. Set a session timebox (60–90 minutes maximum without break).

### 2. Driver/Navigator Facilitation ⚡ (Power Mode)

**Steps:**

1. **Driver** responsibilities:
   - Write code, run tests, navigate the editor.
   - Think aloud — narrate what you're doing and why.
   - Ask questions when navigator's direction is unclear.
2. **Navigator** responsibilities:
   - Focus on strategy, architecture, and upcoming steps.
   - Catch typos, logic errors, and naming issues in real time.
   - Keep a running list of TODOs and tangents to revisit later.
3. Rotate roles at the agreed interval or at natural breakpoints (test green, commit point).
4. Both participants commit under shared authorship: `Co-authored-by: Name <email>`.

### 3. Mob Programming Coordination ⚡ (Power Mode)

**Steps:**

1. Assign roles:
   - **Driver** — Types only what the navigator dictates.
   - **Navigator** — Directs the driver; rotates every round.
   - **Mob** — Contributes ideas to the navigator, not the driver directly.
2. Rotation: Navigator → Driver → Mob; new Navigator from Mob.
3. Rotation interval: 10–15 minutes for mobs of 3–5 people.
4. Use a visible timer (Mobster, Mob Timer app).
5. Designate a facilitator to manage flow, breaks, and conflicts.

### 4. Knowledge Transfer Debrief 🌿 (Eco Mode)

**Steps:**

1. At session end, spend 5–10 minutes on debrief:
   - What did we accomplish?
   - What did each person learn?
   - What surprised us or was harder than expected?
2. Capture key decisions and rationale in a commit message or doc.
3. Log any follow-up tasks or tech debt discovered during the session.
4. Rate session effectiveness (1–5) and note improvement ideas for next time.

---

## Inputs

| Parameter          | Type       | Required | Description                                      |
|--------------------|------------|----------|--------------------------------------------------|
| `task_description` | `string`   | yes      | The specific task or problem to work on          |
| `participants`     | `string[]` | yes      | Names/handles of all participants                |
| `pairing_style`    | `string`   | no       | driver-navigator, ping-pong, strong-style, mob   |
| `session_duration` | `integer`  | no       | Session length in minutes (default: 60)          |

## Outputs

| Field               | Type       | Description                                      |
|---------------------|------------|--------------------------------------------------|
| `session_summary`   | `string`   | What was accomplished during the session         |
| `learnings`         | `string[]` | Key knowledge transfers and insights             |
| `follow_ups`        | `string[]` | Tasks or issues to address after the session     |
| `commits`           | `string[]` | Commits made with co-authorship attribution      |

---

## Edge Cases

- Significant skill gap between participants — Use strong-style pairing; senior navigates at a level the junior driver can execute.
- Remote pair with high latency — Prefer asynchronous ping-pong (push commits alternately) over real-time screen sharing.
- Participant dominates the session — Facilitator enforces strict role boundaries; driver only types, navigator only directs.
- Task turns out to be trivial — Pivot to a related learning exercise or review adjacent code together.

---

## Scope

### In Scope

- Structuring pair and mob programming sessions (roles, rotations, timeboxing)
- Facilitating driver/navigator, ping-pong, and strong-style pairing workflows
- Managing remote pairing tool setup (Live Share, Tuple, screen sharing)
- Knowledge transfer practices and session debriefs
- Co-authorship attribution in commits
- Rotation scheduling and timer management for mob sessions
- Session retrospectives and effectiveness tracking
- Onboarding acceleration through guided pairing with experienced team members

### Out of Scope

- Code review and defect classification (handled by `code-review`)
- Git workflow and branching strategy (handled by `git-workflow`)
- Task selection and sprint planning (handled by `task-decomposition`)
- IDE/editor configuration beyond collaboration plugins
- Performance evaluation of individual contributors
- Meeting scheduling and calendar management

---

## Guardrails

- Never allow a single participant to hold the driver role for more than two consecutive rotation intervals.
- Always attribute commits with `Co-authored-by` trailers for all active participants.
- Sessions must not exceed 90 minutes without a break; enforce a 10-minute break after each 60-minute block.
- The navigator must not take over the keyboard — communicate intent verbally or via chat.
- Do not use pair programming sessions for performance evaluation or comparison of participants.
- Ensure all participants have equal environment access (repo, CI, docs) before the session starts.
- Tangential discussions exceeding 5 minutes must be parked in a TODO list and revisited after the session.

## Ask-When-Ambiguous

### Triggers

- Participants have not paired before and preferred style is unknown
- Skill gap between participants is significant and unclear how to bridge
- Session goal is vague (e.g., "work on the backend")
- Remote tooling preferences are not established
- Session involves more than 2 people but mob programming was not explicitly requested

### Question Templates

1. "What specific task or problem should this pairing session focus on?"
2. "What is the experience level of each participant with this codebase or technology?"
3. "Do you prefer driver/navigator, ping-pong (TDD), or strong-style pairing?"
4. "For remote sessions, which collaboration tool should we use — VS Code Live Share, Tuple, or screen sharing?"
5. "How long should the session run, and what rotation interval works best for the group?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Two participants, similar skill level | Use ping-pong (TDD) style for balanced contribution |
| Significant skill gap (senior + junior) | Use strong-style pairing; senior navigates, junior drives |
| Onboarding a new team member | Senior drives first to demonstrate patterns, then swap to let new member practice |
| 3–5 participants available | Switch to mob programming with 10-minute rotations |
| Complex architectural decision needed | Navigator role focuses on design; driver implements spikes |
| Task is well-understood and routine | Pair may be unnecessary; suggest solo work with async review instead |
| Session exceeds 60 minutes | Enforce a 10-minute break; reassess whether to continue or schedule follow-up |
| Disagreement on approach during session | Timebox 5 minutes to discuss, then try the navigator's approach; revisit if it fails |
| Remote participant has high latency (> 200ms) | Switch to async ping-pong via commits instead of real-time shared editing |

## Success Criteria

- [ ] Session has a clearly defined goal before starting
- [ ] Roles (driver/navigator) are assigned and rotated at agreed intervals
- [ ] All participants actively contribute during the session
- [ ] Co-authorship is attributed on all commits made during the session
- [ ] Session produces at least one commit or documented decision
- [ ] Debrief captures learnings, follow-ups, and session effectiveness rating
- [ ] No single participant dominated the keyboard for the entire session
- [ ] Knowledge transfer occurred — each participant can articulate something they learned

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Driver-dominance | One person types the entire session; navigator disengages | Enforce rotation timer; facilitator calls role swaps proactively |
| Backseat driving | Navigator takes over the keyboard or dictates keystrokes | Remind navigator to communicate at the highest abstraction the driver can handle |
| Unfocused session | Pair goes down tangents; session ends with no commits | Define a concrete goal upfront; park tangents in a TODO list |
| Tool friction | 15+ minutes spent configuring Live Share or screen sharing | Pre-validate tooling before the session; have a fallback (e.g., screen share if Live Share fails) |
| Skill gap frustration | Junior feels overwhelmed; senior feels slowed down | Switch to strong-style with explicit learning objective; senior demonstrates first |
| Session fatigue | Participants lose focus after 60+ minutes without break | Enforce timeboxes; break at 60 minutes; limit sessions to 90 minutes total |
| Missing attribution | Commits lack co-authorship trailers | Use a commit template or Git hook that prompts for co-authors |
| No debrief | Session ends abruptly; learnings and decisions are lost | Schedule debrief as a fixed 10-minute block at the session end |

## Audit Log

- `[timestamp]` session-started: Pair session with `<participants>` — style: `<pairing-style>`, goal: `<task-description>`
- `[timestamp]` role-rotated: Driver switched from `<previous-driver>` to `<new-driver>` at `<interval>` minute mark
- `[timestamp]` commit-made: Committed `<sha-short>` with co-authors `<co-author-list>`
- `[timestamp]` tangent-parked: Deferred discussion on `<topic>` to follow-up task
- `[timestamp]` break-taken: 10-minute break after `<elapsed>` minutes of active pairing
- `[timestamp]` session-completed: Duration `<total-minutes>` min, commits: `<commit-count>`, effectiveness: `<rating>`/5
- `[timestamp]` debrief-logged: Learnings: `<learning-count>`, follow-ups: `<followup-count>`

````
