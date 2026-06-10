# Named Principles — A Senior Engineer's Map

> *The cost of writing code dropped to zero. The cost of maintaining, testing,
> and debugging it didn't move at all. These seven principles are how a senior
> engineer keeps the codebase from drowning in AI-generated bloat.*

This page is two things at once. **Personal notes** — the named industry
principles I rely on, in one place I can scan in 90 seconds. **Public
reference** — the same notes, written tightly enough that anyone landing here
can learn the principles to a useful depth without wading through history or
op-eds.

Each principle below is paired with the skill(s) in this garden that already
operationalize it. The page is the index; the skills are the prescription.

---

## 1. 🛑 YAGNI × 100

**One-liner:** *You Aren't Gonna Need It.* Build only what the current ticket
requires.

**AI trap:** Generating 200 lines of "future-proof" abstract-factory plumbing
takes 3 seconds, so the urge to build it is enormous.

**Senior reality:** Writing code is now free; **maintaining** it costs the
same as it always did. Take the 5-line `if/else` over the AI's 200-line
"perfect" architecture. The hidden cost is paid by the next reader.

**In this garden:**
- [reuse-first](../skills/100-engineering/25-pragmatism/reuse-first/SKILL.md) — no thin wrappers, no premature generalisation.
- [minimal-diff](../skills/100-engineering/25-pragmatism/minimal-diff/SKILL.md) — diff-size caps and "while I'm here" detection.

---

## 2. ♻️ Reuse over Reinvent

**One-liner:** Before writing a utility, check `package.json` / `pom.xml` /
`requirements.txt` for one that already exists.

**AI trap:** Asked to "check if a string is empty or null", an AI will gladly
write a 10-line custom regex helper instead of using `StringUtils.isBlank`.

**Senior reality:** Every line of custom utility code is a line you legally
own. Offload the responsibility to battle-tested libraries whenever possible.

**In this garden:**
- [reuse-first](../skills/100-engineering/25-pragmatism/reuse-first/SKILL.md) — mandatory pre-search before any new helper.
- [dependency-utility-scout](../skills/100-engineering/25-pragmatism/dependency-utility-scout/SKILL.md) — mines declared deps to build a capability inventory.

---

## 3. 📐 Rule of Three (With a Twist)

**One-liner:** *Write once. Copy twice. Refactor on the third.* Don't
generalise prematurely.

**AI trap:** AIs love abstracting on the very first call site, producing
hard-to-read indirection for logic used in exactly one file.

**Senior reality:** Wait for three real call sites before extracting your own
helper. **The twist:** if a vetted library already covers the case, skip the
wait entirely — pull the library in immediately. The Rule of Three guards
against premature *local* generalisation, not against using already-imported
capability.

**In this garden:**
- [reuse-first](../skills/100-engineering/25-pragmatism/reuse-first/SKILL.md) — Rule of Three named explicitly; library-twist stated alongside it.

---

## 4. 🚧 Chesterton's Fence

**One-liner:** *Don't tear down a fence until you understand why it was put
up.*

**AI trap:** Highlight a block of "ugly" legacy code, ask the AI to "clean it
up", and you'll get a beautiful replacement that silently removes the IE11
fix written at 3 AM three years ago.

**Senior reality:** Reconstruct intent (`git blame`, original ticket, tests,
call sites) **before** deleting. Ugly code is often desperate code that fixed
something undocumented.

**In this garden:**
- [chesterton-fence](../skills/100-engineering/25-pragmatism/chesterton-fence/SKILL.md) — produces a "why-it-exists" memo and edge-case checklist before any change.

---

## 5. 🏕️ Broken Windows + Boy Scout Rule (Bounded)

**One-liner:** *Leave the campground cleaner than you found it* — but only
within the boundary of your ticket.

**AI trap:** Permission to "clean up while you're here" expands without
limit; a button-colour fix becomes a 1,200-line auth refactor.

**Senior reality:** Fix the typo in the function you're already editing.
**Don't** rewrite the auth file because "it looked messy". Giant
out-of-scope PRs are unreviewable, conflict-prone, and infuriating to QA.
Cleanups stay surgical and bounded to the ticket.

**In this garden:**
- [minimal-diff](../skills/100-engineering/25-pragmatism/minimal-diff/SKILL.md) — diff caps and "no drive-by" detection; in-scope correctness fixes are kept.
- [cleanup](../skills/100-engineering/30-implementation/cleanup/SKILL.md) — opportunistic cleanup with intent-marker preservation.
- [repo-maintenance](../skills/100-engineering/90-maintenance/repo-maintenance/SKILL.md) — value assessment before deletion.

---

## 6. 🏛️ Brownfield Mindset / "When in Rome"

**One-liner:** Conform to the existing codebase's style — even if it's
outdated, even if you'd choose differently in greenfield.

**AI trap:** AIs default to the latest fashionable style (camelCase,
async/await, strict TS) regardless of what the project already uses.

**Senior reality:** Consistency is the highest virtue of a codebase. One
slightly-outdated style is infinitely easier to read than five competing
modern ones. Check the ego at the door; if the project ships and makes
money, match its conventions.

**In this garden:**
- [style-conformance](../skills/100-engineering/25-pragmatism/style-conformance/SKILL.md) — detects idioms, conforms within scope, surfaces deviations without auto-fixing.
- [brownfield-onboarding](../skills/100-engineering/25-pragmatism/brownfield-onboarding/SKILL.md) — read the room before you redecorate.

---

## 7. 🌱 Strangler Fig + Minimal-Diff

**One-liner:** Replace legacy systems by routing traffic to a new edge piece
by piece, never in a big bang. Ship the smallest possible diff at every
step.

**AI trap:** "Modernize this whole module" produces a 2,000-line rewrite that
looks beautiful and is impossible to safely deploy or revert.

**Senior reality:** Big-bang rewrites are the graveyard of software
engineering. For bug fixes, change exactly the lines required — high signal,
low noise. For migrations, build the new beside the old, route gradually,
strangle the old until it's safe to delete.

**In this garden:**
- [minimal-diff](../skills/100-engineering/25-pragmatism/minimal-diff/SKILL.md) — surgical diffs; expand-and-contract for irreversible changes.
- [legacy-upgrade](../skills/100-engineering/90-maintenance/legacy-upgrade/SKILL.md) — names Strangler Fig directly as the strategy of choice for large upgrades.

---

## Quick-Reference Table

| # | Principle                              | Skill(s)                                              | Status  |
|---|----------------------------------------|-------------------------------------------------------|---------|
| 1 | YAGNI × 100                            | reuse-first, minimal-diff                             | covered |
| 2 | Reuse over Reinvent                    | reuse-first, dependency-utility-scout                 | covered |
| 3 | Rule of Three (with library twist)     | reuse-first                                           | covered |
| 4 | Chesterton's Fence                     | chesterton-fence                                      | covered |
| 5 | Broken Windows + Boy Scout (bounded)   | minimal-diff, cleanup, repo-maintenance               | covered |
| 6 | Brownfield / When in Rome              | style-conformance, brownfield-onboarding              | covered |
| 7 | Strangler Fig + Minimal-Diff           | minimal-diff, legacy-upgrade                          | covered |

---

## How to use this page

- **As personal notes** — scan the seven sections, remember the names.
- **As public reference** — read top-to-bottom in two minutes, click into the linked skill for the full prescription.
- **As an index into the garden** — every principle has a skill; every skill has a constitution.
