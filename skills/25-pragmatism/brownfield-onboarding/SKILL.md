---
name: brownfield-onboarding
description: >
  Structured first-touch protocol for understanding an existing
  codebase before contributing to it. Reads the README, ADRs,
  most-changed and most-recent files, dependency manifests, build/CI
  config, and test layout, and emits an onboarding cheat-sheet other
  Aparigraha skills (style-conformance, reuse-first, minimal-diff,
  chesterton-fence) consume on subsequent tasks.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, pragmatism"
  reasoning_mode: plan-execute
---


# Brownfield Onboarding

> _"Read the room before you redecorate it. Two hours of reading saves
> two weeks of merge fights."_

## Context

Invoked the first time the agent (or a fresh agent session) interacts
with a project. The skill produces a structured **onboarding
cheat-sheet** — a compact summary of how the project is laid out, how it
builds, how it tests, what its history says, and where its most-changed
and most-touched code lives. Downstream Aparigraha skills consume this
sheet so they don't redo discovery on every task.

The skill is the entry-point of the read-first half of Aparigraha.
`reuse-first`, `style-conformance`, `chesterton-fence`, and
`dependency-utility-scout` all assume the cheat-sheet exists; this
skill is what gets it built.

## Scope

**In scope:**

- Reading project-level documentation (README, CONTRIBUTING, ADRs,
  CHANGELOG, docs/*).
- Discovering build, test, lint, and CI configurations.
- Identifying the project's primary languages and ecosystems.
- Surfacing the most-recently-changed and most-changed files (the "hot
  zones" of active development).
- Identifying the entry points (main / index / cmd / handlers) and
  their public surfaces.
- Mapping the test layout and the dominant test framework.
- Producing the onboarding cheat-sheet for downstream consumption.
- Recording outstanding questions the user may need to answer.

**Out of scope:**

- Building the dependency utility inventory — owned by
  `dependency-utility-scout`.
- Building the house-style profile — owned by `style-conformance`.
- Reconstructing intent of specific code — owned by `chesterton-fence`.
- Authoring requirements for a new feature — owned by
  `requirements-elicitation`.
- Deep architectural review — that's a separate, larger task.

---

## Micro-Skills

### 1. Manifest Pass 🌿 (Eco Mode)

**Goal:** Identify the project's languages, primary build system, and
package layout in a single pass.

**Steps:**

1. Glob the repo for top-level signals:
   - Languages: file extension histogram (`*.java`, `*.ts`, `*.py`, …).
   - Build system: `pom.xml`, `build.gradle*`, `package.json`,
     `pyproject.toml`, `Makefile`, `Cargo.toml`, `go.mod`, `*.csproj`,
     `Gemfile`.
   - Monorepo signals: `pnpm-workspace.yaml`, `lerna.json`, `nx.json`,
     `Cargo.toml [workspace]`, `go.work`, root `pom.xml` with
     `<modules>`.
2. Record `{primary_language, build_system, monorepo: bool, modules:
   [path, ...]}`.

### 2. Documentation Pass ⚡ (Power Mode)

**Goal:** Extract intent and conventions from prose, in priority order.

**Files to read, in this order (skip missing):**

| File / glob                      | What to extract                                                                |
|----------------------------------|--------------------------------------------------------------------------------|
| `README.md`                      | Purpose, quickstart, run/build/test commands, contribution pointers.           |
| `AGENTS.md` / `.cursor/rules/*`  | Project-specific agent guidance — must be honoured.                            |
| `CONTRIBUTING.md`                | Contribution workflow, PR norms, commit-message style.                         |
| `CODE_OF_CONDUCT.md`             | Communication norms.                                                           |
| `LICENSE`                        | Outbound licence; pair with `dependency-utility-scout`'s licence concerns.     |
| `CHANGELOG.md` / `RELEASES.md`   | Recent themes, deprecations, breaking changes.                                 |
| `docs/adr/**` / `architecture/decisions/**` | Standing architectural decisions.                                  |
| `docs/**`                        | Higher-level docs (system overview, runbooks, onboarding pages).               |
| `.github/PULL_REQUEST_TEMPLATE*` | What reviewers look for.                                                       |
| `SECURITY.md`                    | Reporting / handling rules.                                                    |

**Steps:**

1. Read each present file (skim, do not deep-read everything).
2. Extract: `purpose`, `run_commands`, `build_commands`, `test_commands`,
   `commit_style`, `pr_workflow`, `notable_decisions`, `recent_themes`.
3. Record any **agent-specific rules** found in `AGENTS.md` /
   `.cursor/rules/` verbatim — these override defaults.

### 3. Build, Test, Lint, CI Pass ⚡ (Power Mode)

**Goal:** Find the canonical commands and pipelines.

**Sources to inspect:**

| Subject       | Sources                                                                         |
|---------------|---------------------------------------------------------------------------------|
| Build         | Build manifest's standard targets, root `Makefile`, `scripts/` folder.          |
| Test          | Test runner config (`jest.config*`, `pytest.ini`, `pyproject.toml`, `surefire`).|
| Lint / format | `.eslintrc*`, `prettier.*`, `pylintrc`, `ruff.toml`, `checkstyle.xml`, etc.     |
| CI            | `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/config.yml`. |
| Pre-commit    | `.pre-commit-config.yaml`, `lefthook.yml`, `husky/`.                            |

**Steps:**

1. Identify the canonical commands the project uses: `build`, `test`,
   `lint`, `format`, `ci`.
2. Identify which checks are blocking in CI (these are the ones the
   agent's diff must keep green).
3. Note unusual constraints: monorepo affected-only commands, sandboxed
   runners, required environment variables.

### 4. Hot-Zones Pass 🌿 (Eco Mode)

**Goal:** Find where active development happens — useful for
`style-conformance` sampling and for "where will my change probably
land?" intuitions.

**Steps:**

1. **Nano: Recently-modified** —
   `git log --name-only --since="180 days ago" --pretty=format:"" |
    sort | uniq -c | sort -rn | head -50`.
2. **Nano: Most-changed (history-wide)** —
   `git log --all --name-only --pretty=format:"" |
    sort | uniq -c | sort -rn | head -50`.
3. **Nano: Most-recent-author per file** — useful when the agent needs
   to know who to ask. Cache only as part of the cheat-sheet, never
   exposed without the user's request.
4. Cross the two lists with the modules from micro-skill 1 to identify
   "hot modules".

### 5. Entry-Points & Surface Pass ⚡ (Power Mode)

**Goal:** Find the application's entry points and the shape of its
public surface.

**Common entry-point patterns:**

| Ecosystem      | Entry-point hints                                                            |
|----------------|------------------------------------------------------------------------------|
| Java / Spring  | `public static void main`, `@SpringBootApplication`, `*Application.java`.    |
| JS / Node      | `package.json#main`, `package.json#bin`, `index.{js,ts}`, `server.{js,ts}`. |
| Python         | `if __name__ == "__main__"`, `pyproject.toml [project.scripts]`, `manage.py`.|
| Go             | `func main` in `cmd/*` or repo root.                                         |
| .NET           | `Program.cs`, `Startup.cs`.                                                  |
| Ruby           | `bin/*`, `config.ru`, `Rakefile` tasks.                                      |

**Public surface signals:**

- HTTP / RPC route registrations (`@Controller`, `app.get(...)`,
  `router.handle`, gRPC service definitions, OpenAPI specs).
- CLI subcommands.
- Library exports (`index.ts`, `__all__`, `pub use`).
- Background jobs, schedulers, message-queue consumers.

**Steps:**

1. Locate entry points; record `{entry_path, kind: web|cli|worker|lib,
   exposed_surfaces: [...]}`.
2. Note where requirements typically arrive: HTTP route handlers,
   message handlers, batch jobs.

### 6. Test Layout Pass 🌿 (Eco Mode)

**Goal:** Determine the test framework and where tests live, so that
`minimal-diff` and `tdd-workflow` can place new tests correctly.

**Steps:**

1. Identify the test framework from the test runner config.
2. Identify the layout convention:
   - Colocated (`*.test.ts` next to source).
   - Mirrored (`src/test/java/...` or `tests/` mirror of `src/`).
   - Top-level `tests/` flat.
3. Identify the dominant test style (BDD `describe`/`it`, AAA, Given/
   When/Then, parametric data-driven, snapshot-heavy).
4. Identify integration / E2E directories and their special harnesses
   (Docker compose, test containers, fixtures).

### 7. Cheat-Sheet Emission 🌿 (Eco Mode)

**Goal:** Persist a single, compact artefact downstream skills consume.

**Cheat-sheet shape (YAML / JSON):**

```yaml
project: <repo_root>
detected_at: <iso-timestamp>
languages:
  primary: java
  others: [yaml, sh]
build:
  system: maven
  commands:
    build: "mvn -DskipTests package"
    test: "mvn test"
    lint: "mvn checkstyle:check"
    format: "mvn fmt:format"
  ci_blocking_checks: [build, test, checkstyle]
monorepo: false
modules: ["api", "core", "persistence"]
docs:
  readme_summary: "Payments service for the Acme platform."
  contribution_summary: "Conventional commits; PRs squash-merged; ADRs in docs/adr."
  agents_md: |
    <verbatim AGENTS.md content if present>
  notable_adrs:
    - "0007-event-sourcing-vs-state.md"
    - "0014-retry-policy.md"
  recent_themes:
    - "migrating from Java 17 to Java 21"
    - "introducing Resilience4j across services"
entry_points:
  - path: "api/src/main/java/.../ApiApplication.java"
    kind: web
    exposed_surfaces: ["HTTP via @RestController in api/.../controllers/"]
  - path: "core/src/main/java/.../jobs/NightlyReconciler.java"
    kind: worker
hot_zones:
  recent_180d_top: ["api/.../PaymentService.java", "core/.../RetryPolicy.java", ...]
  history_top:     ["api/.../PaymentController.java", "core/.../EventStore.java", ...]
  hot_modules:     ["api", "core"]
tests:
  framework: junit5 + mockito
  layout: mirrored under src/test/java
  style: AAA, parametric tests in JUnit 5 @ParameterizedTest
  integration_dir: "api/src/integration-test/"
  e2e_harness: "docker-compose -f infra/docker-compose.test.yml"
agent_rules:
  - "AGENTS.md says: never edit migrations/ — DBA owns that path."
  - ".cursor/rules/code-style.mdc says: TypeScript files use single quotes."
open_questions:
  - "AGENTS.md missing — confirm there are no hidden agent rules?"
  - "Two distinct logging styles in core/; which should new code follow?"
sources:
  files_read: [...]
  configs_read: [...]
```

**Steps:**

1. Materialise the cheat-sheet in memory.
2. If the user opts in (or it's a long-running session), persist to
   `.cursor/onboarding-cheatsheet.yaml`. Never silently commit.
3. Hand the cheat-sheet to the orchestrator so subsequent
   `style-conformance`, `reuse-first`, `chesterton-fence`, and
   `dependency-utility-scout` invocations read from it instead of
   redoing discovery.

### 8. First-Pass Sanity Check 🌿 (Eco Mode)

**Goal:** Validate the cheat-sheet by running the documented build &
test commands at least once.

**Steps:**

1. Execute the recorded `build` and `test` commands in a dry-run /
   read-only manner where possible (e.g., `mvn -q -DskipTests
   compile`).
2. If commands fail, do not silently fix — record the failure and ask
   the user. The cheat-sheet must reflect the *actual* build, not an
   aspirational one.
3. If commands succeed, record the durations as baselines so
   `minimal-diff`'s future runs can detect significant regressions.

---

## Inputs

| Parameter            | Type       | Required | Description                                                       |
|----------------------|------------|----------|-------------------------------------------------------------------|
| `repo_root`          | `string`   | yes      | Absolute path to the repository root.                             |
| `time_budget_minutes`| `number`   | no       | Wall-clock time the user wants spent on onboarding. Default: 30. |
| `persist_to`         | `string`   | no       | Path to persist the cheat-sheet. Otherwise in-memory.             |
| `run_sanity_check`   | `boolean`  | no       | Whether to invoke build/test commands. Default: `true`.           |

## Outputs

| Field             | Type     | Description                                                                  |
|-------------------|----------|------------------------------------------------------------------------------|
| `cheatsheet`      | `object` | The structured onboarding cheat-sheet.                                       |
| `agent_rules`     | `string[]` | Agent-specific rules extracted verbatim from AGENTS.md / .cursor/rules/.   |
| `open_questions`  | `string[]` | Items the user should clarify before non-trivial work begins.              |
| `sanity_check`    | `object` | Result of running the documented build/test commands once.                   |

---

## Guardrails

- **Read-only.** This skill never modifies source files, configs, or
  ignored files. It may write the cheat-sheet to a non-tracked path
  with the user's opt-in.
- **Honour AGENTS.md and .cursor/rules.** If they exist, their rules
  are quoted verbatim in `agent_rules` and treated as overrides for
  every downstream skill.
- **No silent build/test execution in destructive modes.** The sanity
  check uses dry-run / read-only flags where the build system supports
  them. If only destructive options are available, ask the user first.
- **Time-budget honest.** If the time budget is short, prioritise:
  1. Manifest pass.
  2. Documentation pass (README + AGENTS.md only).
  3. Build/test commands.
  Skip hot-zones and entry-point passes; mark them as TODO.
- **No assumptions about the project's purpose.** If README is missing
  or thin, record `purpose: unknown` rather than guessing.
- **The cheat-sheet is provisional.** It is updated as later skills
  discover corrections; never treated as immutable.

## Ask-When-Ambiguous

**Triggers:**

- README is missing or empty.
- `AGENTS.md` references rules but their files are missing.
- Two manifests declare conflicting build commands.
- The build/test sanity check fails.
- The repo has multiple plausible entry points and it's unclear which
  is "the" service.
- The repo has multiple test layouts coexisting (post-migration).

**Question Templates:**

- "I couldn't find a README. Can you give me a one-paragraph summary
  of what this service does and how to run it?"
- "Build sanity check (`[command]`) failed with `[error]`. Is this
  expected, or is my environment off?"
- "Two entry points found: `[A]` (web) and `[B]` (worker). Which
  should the agent treat as the primary surface for new tasks?"
- "I see both `tests/` and `src/test/java/`. Which is current; is the
  other a migration in progress?"

## Decision Criteria

| Situation                                                  | Action                                                                         |
|------------------------------------------------------------|--------------------------------------------------------------------------------|
| AGENTS.md present                                          | Quote verbatim; treat as override.                                             |
| README absent / thin                                       | Mark `purpose: unknown`; ask the user for a summary.                           |
| Build sanity check passes                                  | Record durations as baselines.                                                 |
| Build sanity check fails                                   | Stop autonomous work; ask the user.                                            |
| Time budget short                                          | Run only manifest + documentation + build/test commands; mark rest TODO.       |
| Multiple entry points found                                | Record all; ask user which is primary.                                         |
| Hot-zone analysis would scan a very large history          | Cap at last 180 days + top 50 files; mention the cap.                          |

## Success Criteria

- The cheat-sheet exists and is self-consistent (e.g., declared
  build command actually exists).
- AGENTS.md / `.cursor/rules` rules are surfaced verbatim.
- Downstream skills can read the cheat-sheet without re-running
  discovery.
- The user has been asked to clarify any items the cheat-sheet
  records as `unknown`.
- Build/test commands have been validated at least once (or the
  failure is documented).

## Failure Modes

- **README-driven hallucination.** Agent treats README as ground truth
  even when commands in it are stale.
  **Recovery:** The build/test sanity check is the tiebreaker. If the
  README and reality disagree, reality wins.

- **Onboarding scope creep.** Agent spends hours producing a
  comprehensive architecture review.
  **Recovery:** Honour the time budget. Onboarding is a cheat-sheet,
  not a thesis. Anything deeper is a separate task.

- **Missed AGENTS.md.** Agent ignores project-specific rules.
  **Recovery:** AGENTS.md and `.cursor/rules/` are mandatory inputs.
  If discovered later, restart the cheat-sheet pass with them
  included; downstream decisions made before discovery may need to
  be revisited.

- **Hot-zone tunnel vision.** Agent treats only the recent-180d files
  as "the codebase".
  **Recovery:** Hot zones are a *bias*, not a *limit*. The whole repo
  is still in scope when needed.

- **Onboarding becomes a one-shot artefact never refreshed.** The
  cheat-sheet rots over time.
  **Recovery:** Re-onboard if the cheat-sheet is older than the
  project's last big change (e.g., dependency major bump, framework
  migration). Cheap to rebuild.

## Audit Log

```
[onboarding-engaged]      repo_root="{path}" time_budget_minutes={N}
[manifest-pass]           primary_language={lang} build_system={system} monorepo={bool} modules={list}
[documentation-pass]      files_read={list} agents_md_found={bool} notable_adrs={list}
[build-test-pass]         build_cmd="{cmd}" test_cmd="{cmd}" lint_cmd="{cmd}" ci_blocking={list}
[hot-zones-pass]          recent_top={list_top_5} history_top={list_top_5} hot_modules={list}
[entry-points-pass]       entries={list} surfaces={list}
[test-layout-pass]        framework={fw} layout={layout_kind} style={style}
[cheatsheet-emitted]      stored_at="{path|memory}"
[sanity-check]            build={ok|failed} test={ok|failed|skipped} duration_seconds={N}
[open-questions]          items={list}
```

---

## Examples

### Example 1 — A Spring Boot service

**Cheat-sheet excerpt:**

```yaml
languages: { primary: java, others: [yaml, sh] }
build:
  system: maven
  commands:
    build: "mvn -DskipTests package"
    test: "mvn test"
    lint: "mvn checkstyle:check"
  ci_blocking_checks: [build, test, checkstyle]
modules: ["api", "core", "persistence"]
entry_points:
  - { path: "api/src/main/java/.../ApiApplication.java", kind: web,
      exposed_surfaces: ["@RestController in api/.../controllers/"] }
hot_zones:
  recent_180d_top:
    - "api/.../PaymentController.java"
    - "core/.../RetryPolicy.java"
  hot_modules: ["api", "core"]
agent_rules:
  - "AGENTS.md says: never edit persistence/migrations — DBA owns that path."
open_questions:
  - "Two logging styles in core/ (slf4j vs structured Logstash). Which is canonical?"
```

`reuse-first` and `style-conformance` consume this directly on the
agent's first task.

### Example 2 — A pnpm monorepo

**Cheat-sheet excerpt:**

```yaml
monorepo: true
modules: ["packages/web", "packages/api", "packages/shared"]
build:
  system: pnpm
  commands:
    build: "pnpm -r build"
    test: "pnpm -r test"
    lint: "pnpm -r lint"
  ci_blocking_checks:
    - "pnpm --filter ...^[origin/main] build"  # affected-only
    - "pnpm --filter ...^[origin/main] test"
agent_rules:
  - ".cursor/rules/style.mdc: TS uses single quotes, no semis."
hot_zones:
  recent_180d_top:
    - "packages/web/src/pages/Checkout.tsx"
    - "packages/api/src/handlers/order.ts"
  hot_modules: ["packages/web", "packages/api"]
```

The "affected-only" CI hint flows into `minimal-diff`'s scope
statement so the agent knows local builds may differ from CI.

### Example 3 — A README-light internal repo

**Cheat-sheet excerpt:**

```yaml
docs:
  readme_summary: unknown
  contribution_summary: unknown
agent_rules: []
open_questions:
  - "README is empty. What does this service do, and how is it run?"
  - "No CONTRIBUTING.md. What is the PR/commit-message convention?"
sanity_check:
  build: ok    (mvn -q -DskipTests compile, 24s)
  test:  failed (mvn test exits 1: 3 tests fail in core/RetryPolicyTest)
```

The agent does not start non-trivial work until the user has answered
the questions and the failing tests are explained or fixed by the
team. The cheat-sheet honestly records "purpose: unknown" rather
than guessing.

---

## Edge Cases

- **Brand new clone, no `.git/` history yet.** Hot-zones pass returns
  empty. Mark accordingly. Style-conformance falls back to whole-repo
  sampling.

- **Shallow clone (`--depth=1`).** History-based passes are limited.
  Note this in the cheat-sheet; ask the user before relying on history
  for risk decisions in `chesterton-fence`.

- **Polyglot repo with one dominant language but a critical secondary
  language** (e.g., a Java service with a TS frontend). Build separate
  cheat-sheet sections per language; do not let the dominant language
  swamp the secondary one.

- **Strictly air-gapped environment.** External docs / package
  registries unreachable; on-demand parts of `dependency-utility-scout`
  fall back to local metadata. The onboarding cheat-sheet records the
  air-gap so downstream skills don't try to fetch.

- **No tests at all.** This is a strong Aparigraha signal: every
  Chesterton-Fence decision must add a characterisation test before
  changing behaviour. The cheat-sheet flags "tests: none" prominently.

- **Heavy generated code (proto/openapi/codegen).** Mark generated
  paths in the cheat-sheet so `style-conformance` and `minimal-diff`
  exclude them from sampling and edits.

- **Repo containing more than one independent project at the root.**
  Onboard each as a separate sub-project; the cheat-sheet becomes a
  list. Subsequent skills are asked which sub-project they're operating
  in.
