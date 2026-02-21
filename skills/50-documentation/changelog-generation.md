```markdown
---
name: changelog-generation
description: >
  Generate changelogs from commit history using semantic versioning and
  conventional commits, including release notes and breaking change notices.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - release-notes
reasoning_mode: linear
---

# Changelog Generation

> _"Every release tells a story — make it readable."_

## Context

Invoked when a project needs a changelog generated or updated from git
history. Parses conventional commits, determines semantic version bumps,
generates structured changelogs following the Keep a Changelog format, and
highlights breaking changes with migration guidance.

---

## Micro-Skills

### 1. Commit Analysis & Classification 🌿 (Eco Mode)

**Steps:**

1. Read git log between two references (tags, SHAs, or HEAD).
2. Parse each commit message against the Conventional Commits specification:
   - `feat:` → Added (MINOR).
   - `fix:` → Fixed (PATCH).
   - `docs:` → Documentation.
   - `refactor:` → Changed (no version bump).
   - `perf:` → Performance.
   - `BREAKING CHANGE:` or `!` suffix → Breaking (MAJOR).
3. Extract scope, body, and footer metadata.
4. Group and sort commits by type and scope.

### 2. Changelog Entry Generation 🌿 (Eco Mode)

**Steps:**

1. Determine the new version number from commit classification.
2. Format entries following Keep a Changelog categories:
   - Added, Changed, Deprecated, Removed, Fixed, Security.
3. Include PR/issue references and contributor attribution.
4. Prepend the new entry to `CHANGELOG.md` under the release date heading.

### 3. Breaking Change Documentation ⚡ (Power Mode)

**Steps:**

1. Extract all commits with `BREAKING CHANGE` footer or `!` type suffix.
2. For each breaking change:
   - Describe what changed and why.
   - Provide before/after code examples.
   - Document the migration path.
3. Generate a dedicated "Migration Guide" section or file.
4. Cross-reference affected API endpoints or public interfaces.

---

## Inputs

| Parameter       | Type     | Required | Description                                        |
|-----------------|----------|----------|----------------------------------------------------|
| `from_ref`      | `string` | no       | Starting git ref (default: last tag)                |
| `to_ref`        | `string` | no       | Ending git ref (default: HEAD)                      |
| `changelog_path`| `string` | no       | Path to CHANGELOG.md (default: repo root)           |
| `include_body`  | `boolean`| no       | Include full commit body in entries                  |

## Outputs

| Field              | Type     | Description                                     |
|--------------------|----------|-------------------------------------------------|
| `changelog_entry`  | `string` | Formatted changelog entry for the release        |
| `version`          | `string` | Computed semantic version number                 |
| `breaking_changes` | `string[]`| List of breaking changes with migration notes   |
| `bump_type`        | `string` | `major`, `minor`, or `patch`                     |

---

## Scope

### In Scope
- Parsing git history for conventional commit messages
- Computing semantic version bumps (major, minor, patch)
- Generating Keep a Changelog-formatted entries
- Documenting breaking changes with migration guidance and code examples
- Updating CHANGELOG.md with new release entries
- Extracting PR/issue references and contributor attribution
- Generating version bump commands for package manifests

### Out of Scope
- Writing or editing individual commit messages retroactively
- Publishing releases to package registries (npm, PyPI, etc.)
- CI/CD pipeline configuration for automated releases
- Managing git tags or branches (only suggests tag commands)
- Writing marketing-oriented release announcements

## Guardrails

- Preview diffs before applying any changes.
- Never touch generated, vendor, third_party, build, or dist folders unless explicitly allowed.
- Run formatter and linter after changes; revert if errors introduced.
- Never delete or modify existing changelog entries — only prepend new entries.
- Follow the project's established changelog format; detect and match it automatically.
- If no conventional commits are found, warn the user rather than generating empty entries.
- Always include the release date in ISO 8601 format (`YYYY-MM-DD`).
- Flag commits that don't follow conventional commit format in a separate "Uncategorized" section.

## Ask-When-Ambiguous

### Triggers
- No git tags exist to determine the baseline version
- Commits use a non-standard or mixed format (some conventional, some freeform)
- A commit has both `feat` and `BREAKING CHANGE` — version bump type is ambiguous without context
- Multiple package manifests exist with conflicting version numbers

### Question Templates
1. "No git tags found. What should the baseline version be for this release (e.g., `0.1.0`, `1.0.0`)?"
2. "{pct}% of commits don't follow Conventional Commits format. Should I classify them as 'Other/Uncategorized' or attempt to infer their type from the message?"
3. "Multiple version files found (`package.json` at `{v1}`, `pyproject.toml` at `{v2}`). Which is the source of truth?"
4. "Commit `{sha_short}` has scope `{scope}` — should this be included in the public changelog or filtered as internal?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| All commits follow Conventional Commits | Parse automatically and generate changelog |
| Mixed commit formats (> 30% non-conventional) | Warn user; categorize non-conventional as "Uncategorized" |
| No commits since last tag | Report "No changes" — do not generate an empty entry |
| Only `chore`/`ci`/`test` commits | Generate entry only if user opts in; default to skipping |
| Breaking change detected | Bump major version; generate migration guide section |
| Pre-1.0 project (`0.x.y`) | Treat breaking changes as minor bumps per semver spec |

## Success Criteria

- [ ] All conventional commits are correctly classified by type
- [ ] Semantic version is correctly computed based on commit classification
- [ ] Changelog entry follows Keep a Changelog format with correct date
- [ ] Breaking changes include migration guidance with before/after examples
- [ ] PR/issue references are linked in changelog entries where available
- [ ] Non-conventional commits are flagged rather than silently dropped
- [ ] CHANGELOG.md is updated without modifying existing entries

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Incorrect version bump | Breaking change missed; minor bump instead of major | Scan commit bodies and footers for `BREAKING CHANGE`, not just subject lines |
| Missing commits in range | Changelog omits changes that shipped in the release | Verify `from_ref` matches the previous release tag exactly |
| Duplicate changelog entry | Same release version appears twice in CHANGELOG.md | Check for existing version heading before prepending |
| Non-conventional commits silently dropped | Users report shipped features missing from changelog | Include "Uncategorized" section for unparseable commits |
| Wrong date on release entry | Changelog shows incorrect release date | Use current date at generation time; allow override via parameter |

## Audit Log

- `[{timestamp}] commits-parsed: Analyzed {commit_count} commits from {from_ref} to {to_ref} — {feat_count} features, {fix_count} fixes, {breaking_count} breaking changes`
- `[{timestamp}] version-computed: Computed version bump {old_version} → {new_version} ({bump_type})`
- `[{timestamp}] changelog-updated: Prepended release entry for v{version} ({date}) to {changelog_path}`
- `[{timestamp}] breaking-changes-documented: Generated migration guidance for {breaking_count} breaking changes`
- `[{timestamp}] uncategorized-flagged: {uncategorized_count} commits did not follow Conventional Commits format`
```
