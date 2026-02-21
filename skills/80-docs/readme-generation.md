---
name: readme-generation
description: >
  Create comprehensive README files with installation instructions,
  usage examples, API reference, and contribution guidelines.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# README Generation

> _"If the README doesn't explain it, it doesn't exist to newcomers."_

## Context

Invoked when a project needs a README, or when the existing README is
outdated. A good README is the most impactful documentation a project has.

---

## Micro-Skills

### 1. README Structure 🌿 (Eco Mode)

**Steps:**

1. Generate the standard README sections:
   - **Title + Badges** (build status, coverage, version, license).
   - **Description** (what, why, for whom — 2-3 sentences).
   - **Quick Start** (clone, install, run — under 5 commands).
   - **Installation** (prerequisites, step-by-step).
   - **Usage** (code examples for common use cases).
   - **API Reference** (link to OpenAPI spec or inline).
   - **Architecture** (link to system design docs or brief overview).
   - **Contributing** (how to set up dev environment, run tests, PR process).
   - **License** (SPDX identifier and link).

### 2. Badge Generation 🌿 (Eco Mode)

**Steps:**

1. Detect CI platform and add build status badge.
2. Add coverage badge (Codecov, Coveralls).
3. Add version badge (npm, PyPI, Go).
4. Add license badge.
5. Format as a single line of shields.io badges.

### 3. Example Generation 🌿 (Eco Mode)

**Steps:**

1. Identify the top 3 use cases from the codebase.
2. Write minimal code examples that are copy-paste ready.
3. Include expected output for each example.
4. Test that examples actually work (no broken code in docs).

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `readme`        | `string` | Generated README.md content              |
| `badges`        | `string` | Badge markdown                           |

---

## Scope

### In Scope

- Generating complete README.md files with standard sections (title, description, installation, usage, API reference, contributing, license).
- Creating shields.io badge markup for CI status, coverage, version, and license.
- Writing copy-paste-ready code examples derived from actual project source.
- Updating an outdated README to reflect current project state (new dependencies, changed commands, added features).
- Adapting tone and depth to the project type (library, CLI tool, web app, monorepo).

### Out of Scope

- Writing full API reference documentation — defer to `api-documentation` or `openapi-specs`.
- Generating architecture diagrams or design docs — defer to `system-design`.
- Modifying application code, tests, or configuration files.
- Creating non-README documentation (CONTRIBUTING.md, CODE_OF_CONDUCT.md) unless part of README scaffolding.
- Publishing or deploying documentation to external hosting (GitHub Pages, ReadTheDocs).

## Guardrails

- Never overwrite an existing README without showing a diff to the user first.
- Preserve any custom sections the user has added that are not part of the standard template.
- All code examples must be syntactically valid and reflect the project's actual API; never invent functions or flags.
- Badge URLs must point to real services detected in the project (CI config, coverage tool, package registry).
- Do not include placeholder text like "TODO" or "Lorem ipsum" — either fill in real content or omit the section.
- Keep the Quick Start section under 5 commands; link to detailed docs for complex setups.
- Detect the project's license file and reference the correct SPDX identifier; never guess a license.

## Ask-When-Ambiguous

### Triggers

- The project has no existing README and the intended audience (developers, end-users, both) is unclear.
- Multiple package managers or installation methods are available (npm, yarn, pnpm; pip, poetry, conda).
- The project is a monorepo and it's unclear whether to generate a root README, sub-package READMEs, or both.
- No license file is present in the repository.
- The project name or tagline to use in the title is ambiguous.

### Question Templates

- "Who is the primary audience for this README — library consumers, application deployers, or contributors?"
- "The project supports `{pkg_manager_a}` and `{pkg_manager_b}`. Should I show installation instructions for both or just one?"
- "This is a monorepo with `{n}` packages. Should I generate a root-level README, per-package READMEs, or both?"
- "I don't see a LICENSE file. Which license should I reference, or should I omit the license section?"
- "Should the README include an Architecture section, or is a link to separate design docs sufficient?"

## Decision Criteria

| Situation | Action |
|---|---|
| New project, no README exists | Generate full README with all standard sections |
| README exists but is outdated | Diff against project state; update changed sections only |
| Library / npm-style package | Emphasize Installation, API Reference, and Usage examples |
| CLI tool | Emphasize Quick Start, command reference with flags, and output examples |
| Web application | Emphasize Prerequisites, Environment Setup, and Running Locally |
| Monorepo root | Generate overview README with links to sub-package READMEs |
| Project has CI config but no badges | Auto-generate badge line from detected CI/CD platform |
| No tests or coverage tool detected | Omit coverage badge rather than showing a broken link |

## Success Criteria

- [ ] README contains all standard sections: title, description, quick start, installation, usage, contributing, license.
- [ ] A new user can clone, install, and run the project using only the README instructions.
- [ ] All code examples execute without errors when copy-pasted.
- [ ] Badge links resolve to valid URLs (no 404s or broken shields).
- [ ] The README accurately reflects the current project state (dependencies, commands, configuration).
- [ ] No placeholder or dummy text remains in the output.
- [ ] Markdown renders correctly on GitHub / GitLab (headings, tables, code blocks, badges).

## Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| Outdated install commands | User runs `npm install` but project uses `pnpm` | Detect lockfile (`pnpm-lock.yaml`, `yarn.lock`) to infer package manager |
| Broken code examples | Example references a function that was renamed or removed | Derive examples from actual exports/entry points; cross-check imports |
| Wrong badge URLs | Shields show "not found" or link to wrong repo | Build badge URLs from detected CI config and `package.json`/`pyproject.toml` |
| Missing prerequisites | User can't run the project because Node/Python version isn't mentioned | Read `.nvmrc`, `engines`, `python_requires` and list prerequisites explicitly |
| Overwritten custom sections | User's hand-written "Sponsors" or "Roadmap" section is deleted | Detect non-standard sections and preserve them in-place during updates |
| Monorepo confusion | Root README describes one package instead of the whole repo | Detect workspaces config; generate overview with sub-package links |

## Audit Log

- `[{timestamp}]` Skill invoked — mode: `{generate|update}`, project type: `{library|cli|webapp|monorepo}`.
- `[{timestamp}]` Sections generated: `{section_list}`, badges: `{badge_count}`.
- `[{timestamp}]` Code examples created: `{example_count}`, validated: `{pass|fail}`.
- `[{timestamp}]` Existing README preserved sections: `{preserved_sections}`, updated sections: `{updated_sections}`.
- `[{timestamp}]` Output written to `{file_path}`, total lines: `{line_count}`.
- `[{timestamp}]` Markdown lint result: `{pass|fail}`, issues: `{issue_count}`.
