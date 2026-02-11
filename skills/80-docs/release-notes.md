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
