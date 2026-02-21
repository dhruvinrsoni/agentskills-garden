---
name: release-notes
description: >
  Parse git history to generate changelogs and release notes
  following Conventional Commits and Keep a Changelog formats.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# Release Notes

> _"Users don't read code diffs. Give them a story."_

## Context

Invoked before a release to generate user-facing changelogs from the
git history, or to maintain a running CHANGELOG.md.

---

## Micro-Skills

### 1. Conventional Commit Parsing 🌿 (Eco Mode)

**Steps:**

1. Read git log since the last release tag.
2. Parse commits following the Conventional Commits spec:
   - `feat:` → Features (MINOR version bump).
   - `fix:` → Bug Fixes (PATCH version bump).
   - `BREAKING CHANGE:` → Breaking Changes (MAJOR version bump).
   - `docs:`, `chore:`, `refactor:`, `test:` → Other.
3. Group commits by type.
4. Extract scope if present: `feat(auth): add OAuth2`.

### 2. Changelog Generation 🌿 (Eco Mode)

**Steps:**

1. Generate entries following Keep a Changelog format:
   ```markdown
   ## [1.2.0] - 2025-01-15

   ### Added
   - OAuth2 authentication support (#45)

   ### Fixed
   - Connection pool exhaustion under load (#42)

   ### Changed
   - Upgraded Redis client to v5 (#43)
   ```
2. Include PR/issue references where available.
3. Prepend to `CHANGELOG.md`.

### 3. Version Bump 🌿 (Eco Mode)

**Steps:**

1. Determine the version bump type from commit analysis:
   - Any `BREAKING CHANGE` → MAJOR.
   - Any `feat` → MINOR.
   - Only `fix` → PATCH.
2. Update version in `package.json`, `pyproject.toml`, `Cargo.toml`, etc.
3. Create a git tag: `v{major}.{minor}.{patch}`.

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `changelog`     | `string` | Generated changelog entry                |
| `version`       | `string` | New version number                       |
| `tag_command`   | `string` | Git tag command to run                   |

---

## Scope

### In Scope

- Parsing git log history since the last release tag using Conventional Commits format.
- Generating changelog entries following the Keep a Changelog specification.
- Determining semver version bumps (MAJOR / MINOR / PATCH) from commit types.
- Updating `CHANGELOG.md` by prepending new release entries.
- Bumping version strings in manifest files (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).
- Generating git tag commands for the new version.

### Out of Scope

- Actually executing git commands (tag, push) — output commands for the user to run.
- Writing marketing copy or blog-style release announcements.
- Managing GitHub/GitLab release objects or uploading release assets.
- Modifying application code, tests, or CI pipelines.
- Backporting fixes or managing release branches — defer to `git-workflow`.
- Deciding what to include in a release (feature planning) — defer to `task-decomposition`.

## Guardrails

- Never overwrite `CHANGELOG.md` — always prepend new entries above existing content.
- Preserve all prior changelog entries verbatim; do not reformat or re-sort historical entries.
- Only parse commits between the last release tag and HEAD; never re-process already-released commits.
- Do not bump the version if there are zero parseable commits since the last release.
- Always include the release date in ISO 8601 format (`YYYY-MM-DD`).
- Link PR/issue references only when they are real (detected from commit trailers or message body); never fabricate references.
- If the version manifest file cannot be detected, output the new version string without modifying any file.

## Ask-When-Ambiguous

### Triggers

- No release tags exist in the repository history.
- Multiple version manifest files are found (`package.json` + `pyproject.toml`).
- Commits don't follow Conventional Commits and cannot be auto-categorized.
- A `BREAKING CHANGE` is detected but the current major version is 0.x (pre-1.0 semantics).
- The user says "generate release notes" but doesn't specify the tag range.

### Question Templates

- "No release tags found. What should the initial version be (e.g., `0.1.0`, `1.0.0`)?"
- "I found version files at `{path_a}` and `{path_b}`. Which should I update, or both?"
- "`{n}` commits don't follow Conventional Commits format. Should I group them under 'Other' or skip them?"
- "A breaking change was detected in a 0.x version. Should I bump to 1.0.0 or to 0.{next_minor}.0?"
- "Should I generate notes from `{tag}` to HEAD, or specify a different range?"

## Decision Criteria

| Situation | Action |
|---|---|
| Any commit has `BREAKING CHANGE` footer or `!` after type | Bump MAJOR version |
| Any `feat:` commit present, no breaking changes | Bump MINOR version |
| Only `fix:` commits present | Bump PATCH version |
| Only `docs:`, `chore:`, `refactor:`, `test:` commits | Bump PATCH version (configurable: skip release) |
| No Conventional Commits detected | Ask user for categorization or group all under "Changes" |
| Pre-1.0 project with breaking change | Ask user whether to bump to 1.0.0 or next 0.x minor |
| Monorepo with multiple packages | Generate per-package changelogs scoped by path prefix |
| PR/issue numbers in commit messages | Auto-link them in changelog entries |

## Success Criteria

- [ ] All commits since the last tag are accounted for in the changelog (none silently dropped).
- [ ] Changelog entry follows Keep a Changelog format with correct category headings (Added, Fixed, Changed, Removed, Deprecated, Security).
- [ ] Version bump matches the highest-priority commit type (BREAKING > feat > fix).
- [ ] Release date is accurate and in ISO 8601 format.
- [ ] Version string is updated consistently across all relevant manifest files.
- [ ] PR/issue references link to real identifiers found in commit messages.
- [ ] Existing `CHANGELOG.md` content is untouched below the new entry.

## Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| No release tags in history | Cannot determine commit range | Prompt for initial version; use full history from first commit |
| Non-conventional commit messages | Commits end up uncategorized or miscategorized | Fall back to grouping by file path; ask user for overrides |
| Duplicate changelog entries | Same commit appears in multiple releases | Track processed commits by SHA; skip already-released SHAs |
| Wrong version bump | MINOR bump when breaking change was present | Scan all commits for `BREAKING CHANGE` footer and `!` in type before deciding |
| Version file not found | Version string not updated | Warn user; output version string for manual update |
| Stale tag reference | Notes include commits from a previous release | Verify tag exists and points to an ancestor of HEAD before ranging |

## Audit Log

- `[{timestamp}]` Skill invoked — tag range: `{from_tag}..HEAD`, total commits: `{commit_count}`.
- `[{timestamp}]` Commit breakdown: `{feat_count}` feat, `{fix_count}` fix, `{breaking_count}` breaking, `{other_count}` other.
- `[{timestamp}]` Version bump: `{old_version}` → `{new_version}` (`{bump_type}`).
- `[{timestamp}]` Changelog entry prepended to `{changelog_path}` — `{entry_line_count}` lines added.
- `[{timestamp}]` Version updated in: `{manifest_files}`.
- `[{timestamp}]` Git tag command generated: `git tag -a v{new_version} -m "{message}"`.
