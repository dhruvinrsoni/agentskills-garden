---
name: style-conformance
description: >
  Detect the project's existing coding conventions — naming, formatting,
  error handling, logging, test structure, comment style, module layout —
  and produce a "house style profile" that downstream skills consult when
  writing or modifying code. Awareness, not enforcement: the agent
  conforms within the scope of the change and surfaces deviations rather
  than auto-fixing them.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, pragmatism"
  reasoning_mode: plan-execute
---


# Style Conformance

> _"When in Rome. Match the project's idioms within scope. Surface
> deviations, don't smuggle them."_

## Context

Invoked whenever the agent is about to write or modify code in an
existing project — i.e., almost always in a brownfield context. The skill
implements the **Conform-Before-Improve** gate of Aparigraha: detect the
project's idioms, adopt them within the scope of the current change, and
surface deviations as suggestions instead of silently rewriting.

The skill is deliberately *narrow* in authority. It produces a profile.
It does not lint, format, or refactor existing code. The
`code-generation`, `refactoring`, `cleanup`, and `code-review` skills
consume the profile when they write or evaluate code.

## Scope

**In scope:**

- Sampling representative source files and inferring idioms.
- Producing a structured **house style profile** covering naming,
  formatting, error handling, logging, test layout, and comment style.
- Detecting and recording inconsistencies *within* the project for the
  user to resolve later.
- Annotating the profile with sources (which files informed each rule).

**Out of scope:**

- Running formatters/linters across the codebase — that's `cleanup`.
- Refactoring existing code to fit any style — that's `refactoring`.
- Reviewing diffs for style compliance — that's `code-review`.
- Adding/changing the project's actual lint config files — out of scope;
  defer to the user.
- Enforcing one "right" style across projects. The right style is the
  project's *current* style.

---

## Micro-Skills

### 1. Configured-First Detection ⚡ (Power Mode)

**Goal:** Honour explicit configuration before inferring.

**Steps:**

1. Look for declared style configuration. If found, it wins; inference is
   only used to fill gaps.

| Concern        | Configuration files (in order of authority)                                  |
|----------------|------------------------------------------------------------------------------|
| Formatting     | `.editorconfig`, `.prettierrc*`, `.clang-format`, `pyproject.toml [tool.black]` |
| Linting        | `.eslintrc*`, `tsconfig.json`, `pylintrc`, `ruff.toml`, `checkstyle.xml`, `detekt.yml` |
| Imports        | `eslint-plugin-import` config, `isort.cfg`, `goimports`                      |
| Tests          | `jest.config*`, `pytest.ini`, `pyproject.toml [tool.pytest]`, `surefire`     |
| Commits        | `commitlint.config.*`, `.gitmessage`, repo `CONTRIBUTING.md`                 |
| Pre-commit     | `.pre-commit-config.yaml`, `lefthook.yml`, `husky/`                          |

2. Read the declared rules verbatim into the profile.
3. If multiple configs disagree (e.g., editor vs prettier), record the
   conflict and surface it.

### 2. Inferred Idioms (sampling) ⚡ (Power Mode)

**Goal:** Where configuration is silent, infer idioms from real code.

**Sampling strategy:**

1. Take a stratified sample of files:
   - Top-N most-recently-modified files (recent style is current style).
   - Top-N most-changed files in the last 6 months (these set patterns).
   - One file per package/module to capture local norms.
   - Exclude `vendor/`, `generated/`, `proto/`, `migrations/`, fixtures.

2. For each idiom category, count and pick the dominant pattern. Below
   are the **idiom dimensions** to capture:

| Dimension                  | Examples to detect                                                                |
|----------------------------|-----------------------------------------------------------------------------------|
| Naming — types/classes     | `PascalCase`, `snake_case`, suffix conventions (`Service`, `Repo`, `Manager`)     |
| Naming — functions/methods | `camelCase`, `snake_case`, verb prefix (`get`, `fetch`, `load`, `find`)           |
| Naming — variables         | `camelCase`, `snake_case`, abbreviations the project uses (`req`, `res`, `ctx`)   |
| Naming — constants         | `SCREAMING_SNAKE_CASE`, `kPascalCase`                                             |
| Naming — files             | `kebab-case`, `snake_case`, `PascalCase.ts`                                       |
| Indentation                | spaces vs tabs, width                                                             |
| Line length                | observed median + p95                                                             |
| Brace / block style        | Allman, K&R, Stroustrup; trailing commas; semicolons                              |
| Quote style                | single vs double; template literals usage                                         |
| Imports                    | grouping, ordering, absolute vs relative, side-effect imports                     |
| Module layout              | file-per-class? feature folders? layered? colocated tests?                        |
| Error handling             | exceptions vs `Result`; bare `throw` vs typed errors; wrap-and-rethrow patterns   |
| Logging                    | logger choice (`slf4j`, `pino`, `loguru`); levels usage; structured fields        |
| Null / optional            | `Optional<T>` vs `T?`; null-guard style                                           |
| Async style                | callbacks, Promises, `async`/`await`, RxJS, Mono/Flux                             |
| Comments                   | language, density, JSDoc/JavaDoc/docstring presence and shape                     |
| Test layout                | `*.test.ts` colocated, `__tests__/`, `src/test/java/...` mirror                   |
| Test style                 | AAA blocks, `describe`/`it`, parametric data, mocking library                     |
| Public API surface         | barrel files (`index.ts`), explicit exports, default vs named                     |
| Localization / i18n        | string externalisation pattern; key naming                                        |

3. For each dimension, record:
   - `value` — the dominant pattern.
   - `confidence` — share of sampled files following it.
   - `sources` — file paths that informed the rule.
   - `outliers` — files that deviate (for the inconsistency report).

### 3. Inconsistency Report 🌿 (Eco Mode)

**Goal:** Surface places where the project disagrees with itself.

**Steps:**

1. For each idiom dimension where the dominant pattern's confidence is
   below a threshold (default 70%), mark the dimension `inconsistent`.
2. Record the competing variants with example files for each.
3. Emit the report alongside the profile. The report is informational —
   the agent does NOT auto-fix inconsistencies.

### 4. Profile Emission 🌿 (Eco Mode)

**Goal:** Produce a structured profile that downstream skills can read.

**Profile shape (JSON / YAML):**

```yaml
project: <repo_root>
detected_at: <iso-timestamp>
language_primary: <java|ts|py|go|...>
configured:
  formatter: prettier@2.x with .prettierrc.json
  linter: eslint with .eslintrc.cjs
  imports: eslint-plugin-import order rule active
inferred:
  naming:
    classes: PascalCase  (confidence 0.96, sources: [...])
    functions: camelCase (confidence 0.92, sources: [...])
    files: kebab-case    (confidence 0.88, sources: [...])
    constants: SCREAMING_SNAKE_CASE (confidence 0.81, sources: [...])
  formatting:
    indentation: { kind: spaces, width: 2, confidence: 0.99 }
    line_length: { median: 88, p95: 110, configured_max: 100 }
    quotes: single (confidence 0.94)
    semicolons: always (confidence 0.97)
  imports:
    style: absolute via tsconfig paths, relative within feature folder
    order: external > internal > relative
  errors:
    style: throw typed errors (subclasses of AppError); avoid bare throw
    propagation: wrap-and-rethrow at module boundaries
  logging:
    library: pino (singleton in src/log.ts)
    levels: trace|debug|info|warn|error|fatal
    structured: true (key 'event' on every log)
  tests:
    layout: colocated (*.test.ts next to source)
    framework: vitest
    style: describe/it blocks; one assertion per it; AAA inline
  comments:
    docstrings: tsdoc on public exports; sparse internally
inconsistencies:
  - dimension: error_handling
    variants:
      - { value: typed-error, share: 0.72, examples: [...] }
      - { value: bare-throw,  share: 0.28, examples: [...] }
    note: "28% of files still throw raw Error; recommend gradual migration."
sources:
  sampled_files: [...]
  configs_read: [.editorconfig, .prettierrc.json, .eslintrc.cjs]
```

**Steps:**

1. Materialise the profile in memory.
2. If the user requested persistence, write it to
   `.cursor/style-profile.yaml` (or whichever path the user chose). Never
   commit the profile silently.
3. Hand the profile to downstream skills as input.

### 5. Scoped Conformance Application ⚡ (Power Mode)

**Goal:** When the agent writes or modifies code, the change matches the
profile *within the scope of the change*.

**Rules:**

- Scope is the diff. New code uses the dominant patterns from the
  profile. Existing code outside the diff is **untouched** by this skill.
- If the agent's change naturally crosses an inconsistency boundary
  (e.g., it imports a function whose surrounding file uses a different
  style), conform to the file the new code lives in, not to the profile.
  Local consistency beats global consistency.
- If a hard rule (correctness, security, data integrity) is violated by
  the project's style, escalate via `pragya`. Do not unilaterally rewrite.

**Steps:**

1. Before writing the diff, look up the relevant profile dimensions for
   the target file.
2. If the target file's local style differs from the profile, prefer
   local — annotate with a comment in the audit log:
   `[local-style-preferred] file=… dimension=… profile=… local=…`.
3. Apply formatter/linter via the project's existing pipeline (e.g.,
   `prettier --write` on changed lines only when supported). Do not
   reformat lines outside the diff.

### 6. Deviation Surfacing 🌿 (Eco Mode)

**Goal:** When the agent notices style issues outside the change scope,
record them — never auto-fix.

**Steps:**

1. During the change, log any deviations the agent observed in
   surrounding code into a `deviations.suggested` list.
2. On task completion, present the list to the user as a separate
   "follow-up suggestions" block — clearly labelled as **not part of
   this diff**.
3. Optionally write the suggestions to `docs/style-followups.md` if the
   user opts in.

---

## Inputs

| Parameter            | Type       | Required | Description                                                       |
|----------------------|------------|----------|-------------------------------------------------------------------|
| `repo_root`          | `string`   | yes      | Absolute path to the repository root.                             |
| `target_files`       | `string[]` | no       | Files the impending change will touch (used to bias sampling).    |
| `force_resample`     | `boolean`  | no       | Re-sample even if a recent profile is cached. Default: `false`.   |
| `persist_profile_to` | `string`   | no       | Path where the profile should be written. Otherwise in-memory.    |

## Outputs

| Field                | Type     | Description                                                              |
|----------------------|----------|--------------------------------------------------------------------------|
| `profile`            | `object` | The structured house style profile (configured + inferred).              |
| `inconsistencies`    | `object[]` | Dimensions with low confidence and competing variants.                  |
| `local_overrides`    | `object[]` | When target_files have local style differing from profile, listed here.|
| `deviations_logged`  | `object[]` | Style issues observed outside the change scope.                        |

---

## Guardrails

- **No edits to existing code.** Profile is read-only with respect to the
  codebase.
- **Local beats global.** When the target file's local style differs from
  the project profile, follow the local file. Preserve micro-context.
- **Configuration beats inference.** Declared lint/format rules are
  authoritative; inference fills gaps only.
- **Confidence honesty.** Never present an inferred rule with > 90%
  confidence unless the sample actually supports it. Low confidence must
  be reported as low.
- **No silent migrations.** Never refactor existing code outside scope to
  match the profile, even when it would "improve" consistency.
- **Aparigraha hierarchy.** If the project's style violates correctness,
  security, or data integrity, escalate via `pragya` rather than
  silently conforming.

## Ask-When-Ambiguous

**Triggers:**

- Two configured tools disagree (e.g., `.editorconfig` says 4 spaces but
  `.prettierrc` says 2 spaces).
- The project has no clear dominant pattern for a critical dimension
  (e.g., error handling) and the new code must pick one.
- The agent's change crosses two modules with sharply different local
  styles.
- The user asked the agent to "follow best practices" — the agent must
  reconcile that with the project's existing style.

**Question Templates:**

- "`.editorconfig` says `[X]` and `.prettierrc` says `[Y]`. Which one is
  authoritative for the new code?"
- "Error handling in this project is split: 72% typed errors, 28% bare
  throws. New code in `[file]` should follow which? (Recommendation:
  typed errors — matches the dominant pattern.)"
- "You asked for 'best practices', and this project's current pattern
  for `[X]` differs from the textbook. Stick to current pattern, follow
  the textbook, or propose a scoped migration?"

## Decision Criteria

| Situation                                                         | Action                                                               |
|-------------------------------------------------------------------|----------------------------------------------------------------------|
| Configured rule exists                                            | Use it. Inference is irrelevant for that dimension.                  |
| Inference confidence ≥ 70%                                        | Adopt the dominant pattern.                                          |
| Inference confidence < 70%                                        | Mark `inconsistent`; ask the user before picking for new code.       |
| Target file's local style differs from project-wide style         | Follow local. Note the override.                                     |
| User says "follow best practices"                                 | Conform to project unless it violates correctness/security; surface. |
| Existing style violates correctness/security/data integrity       | Escalate via `pragya`. Do not rewrite silently.                      |
| Drive-by formatting opportunity outside the diff                  | Log as a deviation suggestion. Never apply.                          |

## Success Criteria

- New code reads as if written by the project's incumbent author.
- Configured rules are honoured byte-for-byte.
- Local context wins over global profile when they conflict.
- Out-of-scope code is untouched.
- Deviation suggestions are surfaced explicitly, never smuggled in.

## Failure Modes

- **Style perfectionism.** Agent rewrites surrounding code in "the right"
  style despite the project's clear convention.
  **Recovery:** Reset the diff to in-scope changes only. Move the style
  cleanup to a separate, scoped task.

- **Stale profile.** Profile was inferred a week ago; new patterns have
  emerged.
  **Recovery:** Re-sample if the most-recent-N files have changed
  significantly. The profile is cheap to rebuild.

- **Outlier worship.** Agent treats a single outlier file as the truth.
  **Recovery:** Always weight by frequency; require ≥ 70% to declare a
  dominant pattern.

- **Hidden migrations.** Agent picks the "future" style for new code in
  a file dominated by the legacy style, breaking local consistency.
  **Recovery:** Local style wins. Surface the migration as a follow-up.

- **Best-practice steamroller.** User says "follow best practices" and
  the agent ignores the project's current pattern.
  **Recovery:** Conform to project; surface the gap with a recommendation.
  Let the user decide whether to schedule a migration.

## Audit Log

```
[style-profile-built]    sources_count={N} configured={list} inferred_dims={list}
[inconsistency-flagged]  dimension={name} dominant_share={pct} variants={list}
[local-style-preferred]  file="{path}" dimension={name} profile="{P}" local="{L}"
[deviation-logged]       file="{path}" dimension={name} note="{summary}"
[profile-persisted]      path="{persist_path}" (only on user opt-in)
[escalation]             reason="style-violates-correctness|security|data-integrity"
```

---

## Examples

### Example 1 — TypeScript service, configured rules win

**Input:**

```
repo_root = /work/billing-web
target_files = ["src/invoices/InvoiceService.ts"]
```

**Detected:**

- `.prettierrc.json`: single quotes, 2 spaces, semicolons, trailing
  commas (es5).
- `.eslintrc.cjs`: `import/order` enforces `external > internal >
  relative`.

**Inferred (gaps):**

- `naming.classes`: `PascalCase` (confidence 0.97).
- `naming.files`: `PascalCase.ts` for classes, `kebab-case.ts` for
  utilities (confidence 0.86).
- `errors`: typed errors extending `AppError` (confidence 0.78).

**Local override:**

- `InvoiceService.ts` uses `EventEmitter`-style callbacks; the rest of
  the codebase uses `async`/`await`. The new code in `InvoiceService.ts`
  follows the file's local style (callbacks), not the project default.

### Example 2 — Java service, mixed error handling

**Detected:**

- `commons-lang3`-style `Validate.notNull(...)` is the dominant null-
  guard pattern (confidence 0.81).
- Error handling: 64% wrap-and-rethrow as `BusinessException`; 36% raw
  `RuntimeException`. **Inconsistency flagged.**

**Action:**

- For new code, the agent asks: "New error in `OrderService` — wrap as
  `BusinessException` (dominant pattern) or escalate the inconsistency
  for a scoped migration?"

### Example 3 — Drive-by formatting suggestion

**Scenario:**

- The agent fixes a bug in `auth/middleware.ts`. While reading, it
  notices `auth/utils.ts` has inconsistent indentation (mix of tabs and
  spaces).
- The fix in `middleware.ts` does not touch `utils.ts`.

**Action:**

- Profile records the deviation under `deviations_logged`.
- On task completion, the user sees:

```
Follow-up suggestions (NOT in this diff):
  - auth/utils.ts: mixed tab/space indentation (16 lines).
    Suggest: run prettier on this file as a separate commit.
```

The agent does **not** include the formatting fix in this diff.

---

## Edge Cases

- **No configuration and a tiny project (< 10 files).** Inference has
  little to work with. Pick reasonable defaults for the language and
  surface them as "best guess — please confirm".

- **Generated code in scope.** Skip generated files when sampling. They
  bias inference and are not under the team's stylistic control.

- **Polyglot repo.** Build a profile per language, keyed by file
  extension. Cross-language conventions (commit style, comment density)
  can stay shared.

- **Lint config is aspirational, not enforced** (CI ignores warnings;
  style violations widespread). The configured rules still win — they
  represent the team's stated direction. Surface the gap as an
  inconsistency.

- **Mono-author repo with bespoke style.** Honour it. Bespoke is not
  wrong; it's just unfamiliar.

- **Strong textbook violation in dominant style** (e.g., catching and
  swallowing exceptions everywhere). Surface as an inconsistency with a
  high-priority follow-up. Escalate via `pragya` if it crosses into
  correctness/security territory.

- **Project mid-migration** (e.g., callbacks → Promises in progress).
  Both variants will appear with significant share. Prefer the *target*
  pattern for new code, but check with the user — the migration plan
  may have rules about which folders are "new style only".
