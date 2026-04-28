---
name: reuse-first
description: >
  Before authoring any new utility, helper, wrapper, or abstraction, scan
  the project's existing source and declared dependencies for an
  equivalent. Reuse only after fit and edge-case validation; otherwise
  document why nothing fit and write fresh. Implements the
  Check-Before-Create and Validate-Before-Trust gates of Aparigraha.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, pragmatism, dependency-utility-scout"
  reasoning_mode: plan-execute
---


# Reuse-First

> _"Search before you script. Validate before you trust. Write fresh only
> when nothing existing actually fits."_

## Context

Invoked whenever the agent is about to author a new utility, helper, wrapper
function, small abstraction, or reach for "let me just write a quick helper
for this". The skill enforces the **Check-Before-Create** gate of Aparigraha:
the agent must demonstrate it has looked for an existing equivalent in the
codebase and in the project's declared dependencies before writing anything
new.

Crucially, this skill is **not** a mandate to reuse. The check is mandatory;
the reuse is conditional on a green edge-case validation. A documented
"checked, didn't fit" outcome is a perfectly valid result.

## Scope

**In scope:**

- Detecting that a new utility/helper is about to be written.
- Searching the project's source for an existing equivalent.
- Searching the project's declared dependencies for a battle-tested
  equivalent.
- Comparing candidate behaviour against the *required* behaviour, including
  edge cases.
- Producing a decision record: reuse, reuse-with-guards, or write-fresh.

**Out of scope:**

- Building the dependency inventory itself — owned by
  `dependency-utility-scout`.
- Style of the eventual code — owned by `style-conformance`.
- Diff-size discipline — owned by `minimal-diff`.
- Removing or refactoring existing code that already calls a different
  utility — owned by `chesterton-fence`.
- Security/CVE assessment of candidate libraries — owned by
  `dependency-scanning`.

---

## Micro-Skills

### 1. Trigger Detection 🌿 (Eco Mode)

**Goal:** Detect that the agent is about to write something that may
already exist.

**Trigger phrases / patterns:**

- "I'll write a helper that…"
- "Let me create a utility for…"
- "I'll add a small wrapper around…"
- The plan includes a function whose body is < 10 lines and whose name is
  generic (`normalize*`, `format*`, `parse*`, `dedupe*`, `chunk*`,
  `retry*`, `merge*`, `sanitize*`, `slugify*`, `debounce*`, `clone*`).
- The plan introduces a new file under `utils/`, `helpers/`, `lib/`,
  `common/`, or equivalent.

**Steps:**

1. Pause before writing.
2. Extract a precise behavioural description of what the helper must do
   (inputs, outputs, edge-case expectations).
3. Hand off to micro-skill 2 (codebase scan) and micro-skill 3 (dependency
   scan) in parallel.

### 2. Codebase Scan ⚡ (Power Mode)

**Goal:** Find an existing equivalent inside the project source.

**Steps:**

1. **Nano: Name-First Search** — search by likely names: the verb,
   synonyms, common framework conventions (`StringUtils`, `Strings`,
   `Stringx`, `slug`, `slugify`, `to_slug`, etc.).
2. **Nano: Behaviour-First Search** — search for the operation's
   characteristic substrings (e.g., `normalizeSpace`, `\\s+`, `replaceAll`,
   `toLowerCase(Locale.ROOT)`).
3. Inspect candidates' signatures and bodies.
4. Cross-check the candidate's existing call sites — is it actively used,
   or itself dead code?
5. Record candidates as `{path, signature, call_sites, last_modified}`.

**Tools by ecosystem:**

| Ecosystem      | Tools                                                              |
|----------------|--------------------------------------------------------------------|
| Java           | IDE structural search, `rg`, `mvn dependency:tree`                 |
| JS / TS        | `rg`, `npm ls`, `tsc --listFiles`                                  |
| Python         | `rg`, `pip list`, `python -c "import X; help(X)"`                  |
| Go             | `rg`, `go doc`, `go list -m all`                                   |
| C# / .NET      | `rg`, `dotnet list package`, IDE Find All References               |

### 3. Dependency Scan ⚡ (Power Mode)

**Goal:** Find an existing equivalent inside the project's declared
dependencies.

**Steps:**

1. Identify the project's manifest(s): `pom.xml`, `build.gradle`,
   `package.json`, `requirements.txt`, `Pipfile`, `pyproject.toml`,
   `go.mod`, `Cargo.toml`, `*.csproj`.
2. If a `dependency-utility-scout` inventory exists for this session, use
   it; otherwise invoke `dependency-utility-scout` to build one.
3. Look up the candidate operation in the inventory.
4. Record candidates as `{library, function/class, signature, javadoc/url,
   version_in_use}`.

**High-leverage libraries to look for first** (per ecosystem):

| Ecosystem | Libraries                                                                  |
|-----------|----------------------------------------------------------------------------|
| Java      | Apache Commons Lang/Collections/IO/Text, Guava, Jackson, Spring's `Assert` |
| JS / TS   | Lodash, date-fns, Ramda, `query-string`, `validator.js`                    |
| Python    | `more-itertools`, `toolz`, `pydantic`, stdlib `itertools`/`functools`      |
| Go        | `golang.org/x/exp/slices`, `golang.org/x/exp/maps`, `samber/lo`            |
| .NET      | `System.Linq`, `MoreLinq`, `CommunityToolkit`                              |

### 4. Fit Comparison ⚡ (Power Mode)

**Goal:** Determine whether each candidate fits the required behaviour.

**Steps:**

1. Build the **required behaviour table**: input cases × expected outputs,
   including edge cases.
2. For each candidate, fill in the *actual* behaviour — from documentation,
   source, or a quick experiment.
3. Mark each cell `match`, `mismatch`, or `unknown`.
4. Score the candidate: `% match` over total cells.

| Bucket         | Score        | Default action                                                         |
|----------------|--------------|------------------------------------------------------------------------|
| Perfect fit    | 100% match   | Reuse directly.                                                        |
| Acceptable fit | ≥ 80% match, no mismatches on critical edges | Reuse with thin guard at the call site.                                |
| Partial fit    | ≥ 50%, with mismatches on critical edges     | Trigger Ask-When-Ambiguous; do not silently reuse.                     |
| Poor fit       | < 50% or mismatches on safety edges          | Write fresh; record what was checked.                                  |
| Unknown        | candidate behaviour can't be confirmed       | Either characterise via test, or escalate.                             |

### 5. Edge-Case Validation ⚡ (Power Mode)

**Goal:** Run the Aparigraha edge-case checklist on the chosen candidate
before reuse is committed.

This micro-skill is **mandatory** before any reuse decision is finalised.
It mirrors the checklist defined in the foundation `pragmatism` skill.

**Steps:**

1. Walk the checklist row-by-row:

| Edge case category    | Confirm by…                                                                         |
|-----------------------|-------------------------------------------------------------------------------------|
| Empty / null inputs   | Read the candidate's docs/source for `null`/empty handling, or write a probe test.  |
| Boundary values       | Min, max, zero, negative, off-by-one, overflow, underflow.                          |
| Type variance         | Unicode, locale, timezone, NaN/Infinity, signed/unsigned, large numbers.            |
| Concurrency           | Documented thread-safety, idempotence, ordering guarantees.                         |
| Failure paths         | Behaviour on exception, timeout, partial input, malformed input.                    |
| Performance envelope  | Documented complexity; behaviour on large inputs (10⁶+ elements).                   |
| Domain-specific edges | Edges the **business** cares about (e.g., zero-amount payments, leap seconds, GST). |
| Backward compatibility| Will reuse alter observable behaviour for existing callers?                         |

2. Mark each row `covered`, `N/A with reason`, or `unconfirmed`.
3. If any critical row is `unconfirmed`, do NOT silently reuse. Either:
   - Add a probe / characterisation test that turns it into `covered`, or
   - Escalate via Ask-When-Ambiguous to the user, or
   - Add a guard at the call site that handles the unconfirmed case.
4. Persist the filled checklist in the audit log under
   `[edge-case-validated]`.

### 6. Decision & Recording 🌿 (Eco Mode)

**Goal:** Produce the final decision and a durable record.

**Decision matrix:**

| Outcome                  | Action                                                                        |
|--------------------------|-------------------------------------------------------------------------------|
| Reuse                    | Inline the call. No wrapper. Delete any draft helper code from the plan.      |
| Reuse-with-guards        | Inline the call, add the explicit edge-case guards at the call site.          |
| Write-fresh              | Author the helper. Log "checked X, Y, Z; none fit because [reason]".          |
| Write-fresh + propose lib | Author the helper. File a follow-up suggestion to introduce a library.        |

**Steps:**

1. Emit the decision and the supporting evidence to the user (or to the
   audit log in autonomous mode).
2. If `Reuse` or `Reuse-with-guards`: do not author a wrapper class or
   method that simply re-exposes the library function. The Rule of Three
   says: wait for three real call sites before extracting.
3. If `Write-fresh`: keep the helper local to the call site (function-
   local or file-private) until the third use site appears.

---

## Inputs

| Parameter              | Type        | Required | Description                                                       |
|------------------------|-------------|----------|-------------------------------------------------------------------|
| `intended_helper`      | `object`    | yes      | `{name, inputs, outputs, behaviour_description}`                  |
| `target_language`      | `string`    | yes      | Primary language of the target file (`java`, `ts`, `py`, …).      |
| `dependency_inventory` | `object`    | no       | Output of `dependency-utility-scout`; built on demand if missing. |
| `domain_edges`         | `string[]`  | no       | Business-specific edge cases the user has called out.             |

## Outputs

| Field                      | Type       | Description                                                       |
|----------------------------|------------|-------------------------------------------------------------------|
| `candidates`               | `object[]` | List of in-source and in-dependency candidates considered.        |
| `chosen_candidate`         | `object`   | The selected candidate, or `null` if writing fresh.               |
| `edge_case_report`         | `object`   | Per-row status from the validation checklist.                     |
| `decision`                 | `enum`     | `reuse` \| `reuse-with-guards` \| `write-fresh`.                  |
| `audit_record`             | `string`   | Single-line summary suitable for commit / changelog references.   |

---

## Guardrails

- **Never write a new helper without running the codebase scan and
  dependency scan.** Even when "obviously nothing exists", the search
  itself is the evidence.
- **Never reuse silently when an edge-case row is unconfirmed.** Either
  cover it, guard it, or ask.
- **No thin wrappers.** Do not author `MyStringHelper.normalize(s) =>
  StringUtils.normalizeSpace(s)`. Inline the call.
- **No premature generalisation.** Do not extract a "reusable" helper
  from a single call site. Wait for three.
- **Respect Aparigraha's hierarchy.** If the candidate is in a deprecated
  or vulnerable dependency, defer to `dependency-scanning` /
  `secure-coding-review`. Reuse is not a higher value than safety.
- **Do not modify candidate code.** This skill reads, decides, and writes
  at the call site. Any change to existing helpers is a separate task
  routed through `chesterton-fence` and `minimal-diff`.

## Ask-When-Ambiguous

**Triggers:**

- Two or more candidates are tied on fit, with different trade-offs.
- A candidate is a partial fit (≥ 50% match, mismatches on critical edges).
- A candidate's behaviour on a critical edge cannot be confirmed from
  docs/source within reasonable effort.
- The required helper sits at the boundary of the project's domain (e.g.,
  payments, taxes, dates) where reuse risk is high.
- The dependency containing the best fit is on a known deprecation path.

**Question Templates:**

- "I found `[lib.fn]` that covers ~[N]% of the requirement. Edge cases
  [unconfirmed list] are unconfirmed. Want me to (A) reuse with guards,
  (B) write fresh, or (C) characterise via a probe test first?"
- "Two candidates fit: `[A]` (in `[lib1]`, already used elsewhere) and
  `[B]` (in `[lib2]`, not yet used). Prefer the existing leverage of
  `[A]`, or the cleaner API of `[B]`?"
- "Nothing existing fits. I plan to write a helper named `[name]` with
  signature `[sig]`, kept local to `[file]`. OK to proceed?"

## Decision Criteria

| Situation                                                            | Action                                                                  |
|----------------------------------------------------------------------|-------------------------------------------------------------------------|
| Candidate found, 100% match, edge cases all `covered`                | Reuse. Inline. Done.                                                    |
| Candidate found, ≥ 80% match, only non-critical mismatches           | Reuse-with-guards.                                                      |
| Candidate found, mismatch on a critical/safety edge                  | Ask-When-Ambiguous; default to write-fresh if no response.              |
| Multiple candidates tied                                             | Prefer the one already used in the project; tiebreak by API focus.      |
| Candidate is in a deprecated/vulnerable dependency                   | Escalate to `dependency-scanning`; do not reuse on autopilot.           |
| No candidate found                                                   | Write fresh. Keep local. Log the search.                                |
| Candidate's behaviour can't be confirmed for a critical edge         | Add a characterisation test or ask. Never trust silently.               |

## Success Criteria

- For every helper the agent writes, the audit log shows either a
  `[checked-and-fit]` reuse record or a `[checked-and-no-fit]` write-fresh
  record. Never a silent author event.
- No new wrapper class or wrapper function exists that simply re-exposes a
  library function.
- All `reuse` and `reuse-with-guards` decisions have a green edge-case
  report attached.
- Helpers introduced by `write-fresh` are kept local until a third call
  site emerges.

## Failure Modes

- **The 95% fit trap.** Agent reuses a candidate that handles the happy
  path but breaks on `null` / unicode / boundary / concurrency.
  **Recovery:** Re-run edge-case validation. Add guards at the call site
  or revert to write-fresh. File a regression test capturing the missed
  edge.

- **Wrapper proliferation.** Agent creates `Helper.normalize(s)` that
  delegates to `StringUtils.normalizeSpace(s)`.
  **Recovery:** Inline the wrapper away. Delete the helper. The wrapper
  hides the dependency, makes upgrades harder, and is extra maintenance.

- **Premature generalisation.** Agent extracts a helper after one call
  site, anticipating future reuse.
  **Recovery:** Inline the helper. Note the candidate. Wait for the third
  call site (Rule of Three) before extracting.

- **Lazy search.** Agent searches by exact name only and concludes
  "nothing exists".
  **Recovery:** Run the behaviour-first search (regex on characteristic
  substrings) and the dependency-utility-scout pass. Document both before
  declaring the search done.

- **Reuse despite known deprecation.** Agent reuses a function from a
  library that is on a deprecation/migration path.
  **Recovery:** Defer to the project's migration plan. Choose the
  successor library, or write fresh, or escalate.

## Audit Log

```
[reuse-first-engaged]   helper="{name}" inputs="{sig}" lang={target_language}
[search-codebase]       hits=[{path}, ...] hits_used={path|none}
[search-dependencies]   hits=[{lib.fn}, ...] hits_used={lib.fn|none}
[fit-comparison]        candidate="{name}" match_pct={N} critical_mismatches={list}
[edge-case-validated]   candidate="{name}" covered={count} na={count} unconfirmed={list}
[decision-recorded]     outcome={reuse|reuse-with-guards|write-fresh} reason="{summary}"
[wrapper-rejected]      proposed="{name}" reason="thin-wrapper-over-{lib.fn}"
```

---

## Examples

### Example 1 — Reuse: Java String Normalisation

**Intended helper:**

```java
String normaliseName(String input);  // trim, lowercase, collapse internal whitespace
```

**Reuse-First flow:**

```text
[search-codebase]    no in-project normaliser
[search-dependencies] org.apache.commons:commons-lang3 in pom.xml

Candidate: StringUtils.normalizeSpace(str) + str.toLowerCase(Locale.ROOT)

Fit comparison:
  required = trim + lowercase + collapse-internal-whitespace
  candidate behaviour matches all three; locale ROOT chosen to avoid Turkish-i bug.

Edge-case checklist:
  null               → normalizeSpace(null) = null                 covered
  empty              → normalizeSpace("") = ""                     covered
  unicode whitespace → handled per Character.isWhitespace          covered
  large strings      → O(n)                                        covered
  locale of lower    → Locale.ROOT                                 covered
  domain edge: names with apostrophes / hyphens not affected       covered

Decision: reuse, inline at call site. No new helper class.
```

The agent does **not** create `StringHelpers.normaliseName`.

### Example 2 — Reuse-with-guards: Lodash uniqBy

**Intended helper:**

```ts
function dedupeRecordsById(records: Record[]): Record[];
```

**Reuse-First flow:**

```text
[search-codebase]    no in-project dedupe utility
[search-dependencies] lodash present in package.json

Candidate: _.uniqBy(records, 'id')

Fit comparison:
  required = dedupe by id, drop records with null/undefined id, case-insensitive id match
  candidate behaviour:
    - groups null/undefined ids as one bucket → mismatch on critical edge
    - strict equality on id → mismatch (case sensitivity)

Edge-case checklist:
  empty array        → []                                covered
  null id rows       → grouped, NOT dropped              UNCONFIRMED → user wants drop
  case sensitivity   → strict                            UNCONFIRMED → ids are mixed-case

Decision: ask user. After confirmation:
  Reuse-with-guards:
    const cleaned = records.filter(r => r.id != null)
                           .map(r => ({ ...r, id: String(r.id).toLowerCase() }));
    return _.uniqBy(cleaned, 'id');
```

### Example 3 — Write-fresh: Domain-specific Tax Rounding

**Intended helper:**

```python
def round_for_invoice(amount: Decimal) -> Decimal: ...
```

**Reuse-First flow:**

```text
[search-codebase]    finance/rounding.py exists but rounds to 2dp HALF_UP
[search-dependencies] decimal stdlib, no domain rounding utility

Required: round to 2dp using HALF_EVEN (banker's rounding) per finance team rule,
          but with a domain quirk: amounts ending in .X05 are rounded UP per local
          GST rule.

Fit comparison:
  decimal.ROUND_HALF_EVEN     → matches default rule but not the .X05 quirk
  finance/rounding.py         → uses HALF_UP, contradicts the finance team rule

Edge-case checklist:
  domain edge: .X05 quirk     → no candidate covers this              critical
  negative amounts            → both candidates handle                 covered
  zero                        → both candidates handle                 covered
  very large amounts          → Decimal handles arbitrary precision    covered

Decision: write fresh. Keep local to invoice/ module. Log:
  "checked decimal stdlib and finance/rounding.py; neither fits the .X05 GST rule.
   Helper round_for_invoice kept local; revisit when a third call site appears."
```

---

## Edge Cases

- **The candidate is in a transitive dependency, not direct.** Reuse is
  acceptable but flagged: a transitive may disappear under a future
  dependency upgrade. Either pin it as a direct dependency or accept the
  risk explicitly.

- **The candidate is in the language's standard library but in a newer
  version than the project targets.** Reject; do not silently raise the
  language baseline. Surface as a follow-up.

- **The candidate's licence is incompatible.** Defer to project licence
  policy; reject the reuse if so. Surface to the user.

- **Two near-equivalent candidates: one in a focused utility lib, one in
  a "kitchen sink" lib already on the classpath.** Prefer the kitchen
  sink one if it is already a confirmed dependency, to avoid widening the
  dependency set. Surface the choice if the kitchen sink one is itself
  on a deprecation path.

- **The user explicitly says "just write it, don't search".** Honour the
  override (Pragya), record it as a documented exception, and proceed.
  Skip the search, but still apply the edge-case checklist on the new
  helper before merging.

- **The candidate exists but is buried under three levels of abstraction
  in the codebase.** Reuse is still preferred, but flag the indirection
  as a follow-up: callers should be able to find shared utilities easily.

- **The intended helper is a one-line lambda that doesn't merit a name.**
  Inline the lambda. Do not create a function at all. The smallest
  Aparigraha-aligned outcome is sometimes "no helper, no library, just
  inline expression".
