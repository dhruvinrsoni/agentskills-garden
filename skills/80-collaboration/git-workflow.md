````markdown
---
name: git-workflow
description: >
  Guide branching strategies, commit conventions, merge vs rebase decisions,
  and conflict resolution workflows for consistent version control practices.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: plan-execute
---

# Git Workflow

> _"A clean history tells the story of a project; a messy one hides the plot."_

## Context

Invoked when establishing or enforcing Git workflows across a team — choosing
branching models, standardizing commit messages, deciding merge strategies, and
resolving conflicts. Ensures the version control history remains navigable,
bisectable, and aligned with release processes.

---

## Micro-Skills

### 1. Branching Strategy Selection ⚡ (Power Mode)

**Steps:**

1. Assess project cadence:
   - Continuous deployment → Trunk-based development.
   - Scheduled releases → GitFlow or release-branch model.
   - Open-source with maintainers → Fork-and-PR model.
2. Define branch naming conventions:
   - `feature/<ticket>-<short-description>`
   - `bugfix/<ticket>-<short-description>`
   - `hotfix/<version>-<short-description>`
   - `release/<version>`
3. Document branch lifecycle: creation → development → review → merge → deletion.

### 2. Commit Convention Enforcement 🌿 (Eco Mode)

**Steps:**

1. Adopt Conventional Commits format:
   ```
   <type>(<scope>): <subject>

   [optional body]

   [optional footer(s)]
   ```
2. Define allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`.
3. Configure commit-msg hook (commitlint or similar) to validate messages.
4. Enforce atomic commits — each commit compiles and passes tests independently.

### 3. Merge Strategy Decision 🌿 (Eco Mode)

**Steps:**

1. Evaluate options:
   - **Merge commit** — Preserves full branch history; best for feature branches with meaningful intermediate commits.
   - **Squash merge** — Collapses branch into single commit; best for small PRs or noisy histories.
   - **Rebase** — Linear history; best for trunk-based workflows with short-lived branches.
2. Set default strategy per branch target:
   - Into `main` → Squash merge (clean release history).
   - Into `develop` → Merge commit (preserve feature context).
   - Local cleanup → Interactive rebase before pushing.
3. Document when to deviate from the default.

### 4. Conflict Resolution 🌿 (Eco Mode)

**Steps:**

1. Identify conflict scope — file-level vs semantic-level.
2. Pull latest target branch into feature branch: `git fetch origin && git rebase origin/main`.
3. Resolve conflicts file-by-file:
   - Accept incoming for auto-generated files (lock files, schemas).
   - Manual merge for application logic — verify intent of both sides.
4. Run tests after resolution to confirm no regressions.
5. If conflict is complex (3+ files, cross-cutting logic), escalate to pair resolution.

---

## Inputs

| Parameter          | Type       | Required | Description                                    |
|--------------------|------------|----------|------------------------------------------------|
| `repo_url`         | `string`   | yes      | Repository to apply workflow conventions to    |
| `team_size`        | `integer`  | no       | Number of contributors (affects strategy)      |
| `release_cadence`  | `string`   | no       | e.g., "continuous", "weekly", "quarterly"      |
| `existing_model`   | `string`   | no       | Current branching model if any                 |

## Outputs

| Field               | Type       | Description                                    |
|---------------------|------------|------------------------------------------------|
| `branching_model`   | `string`   | Recommended branching strategy                 |
| `commit_convention` | `string`   | Commit message format and rules                |
| `merge_strategy`    | `string`   | Default merge approach per target branch       |
| `hook_configs`      | `string[]` | Git hook configurations generated              |

---

## Edge Cases

- Monorepo with multiple teams — Use path-scoped branch protections and CODEOWNERS; commit scopes must include the package name.
- Long-lived feature branches (> 2 weeks) — Require periodic rebases against the target branch; flag as process risk.
- Force-push to shared branches — Block via branch protection; allow only on personal feature branches.
- Submodule or subtree usage — Document update workflow separately; conflicts in submodule pointers need special handling.

---

## Scope

### In Scope

- Selecting and documenting branching strategies (trunk-based, GitFlow, GitHub Flow, fork-and-PR)
- Defining and enforcing commit message conventions (Conventional Commits, Angular, custom)
- Configuring Git hooks for commit-msg linting, pre-push checks, and pre-commit formatting
- Advising on merge vs rebase vs squash strategies per branch target
- Conflict resolution guidance and escalation procedures
- Branch naming conventions and lifecycle policies (creation, protection, deletion)
- Tag and release branch management tied to versioning schemes
- Git configuration recommendations (`.gitattributes`, `.gitignore`, merge drivers)

### Out of Scope

- CI/CD pipeline configuration (handled by `ci-pipeline`)
- Pull request review process and feedback (handled by `pr-management`)
- Repository hosting administration (GitHub org settings, GitLab group config)
- Code review content and defect classification (handled by `code-review`)
- Deployment orchestration triggered by Git events
- Git server installation or maintenance

---

## Guardrails

- Never recommend force-pushing to shared or protected branches (`main`, `develop`, `release/*`).
- Always preserve merge-base integrity — do not advise rewriting published history that other contributors have based work on.
- Commit hooks must be bypassable with `--no-verify` for emergency hotfixes, but usage must be logged.
- Branch protection rules must require at least one approving review and passing CI before merge to `main`.
- Do not delete branches that have unmerged commits without explicit confirmation.
- Generated lock files (`package-lock.json`, `yarn.lock`, `poetry.lock`) should use the "ours" merge strategy to avoid manual conflict resolution.
- Never recommend credential storage in Git config; use credential helpers or SSH keys.

## Ask-When-Ambiguous

### Triggers

- Project has no documented branching strategy and multiple active branches exist
- Team members disagree on merge vs rebase approach
- Repository uses both merge commits and squash merges inconsistently
- Release process is unclear (continuous vs scheduled vs ad-hoc)
- Multiple remotes or forks are in play and upstream sync strategy is undefined

### Question Templates

1. "What is your release cadence — continuous deployment, scheduled releases, or ad-hoc?"
2. "Do you prefer a linear commit history (rebase/squash) or a history that preserves branch topology (merge commits)?"
3. "Are there existing commit message conventions the team follows, or should we adopt Conventional Commits?"
4. "How many developers actively push to this repository, and do they work on shared branches?"
5. "Should hotfixes go directly to `main`, or through a dedicated `hotfix/*` branch workflow?"

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Team ≤ 3 developers, continuous deployment | Recommend trunk-based development with short-lived feature branches |
| Team > 5 developers, scheduled releases | Recommend GitFlow or release-branch model |
| PR typically has < 5 commits of incremental work | Default to squash merge for clean history |
| PR has meaningful, atomic intermediate commits | Default to merge commit to preserve context |
| Feature branch is > 5 days old | Prompt developer to rebase against target branch |
| Conflict involves only lock files or generated code | Auto-resolve with "theirs" strategy; regenerate locally |
| Conflict involves business logic in 3+ files | Escalate to pair resolution with the other author |
| Repository is a monorepo with independent packages | Use scoped branch naming and path-based CODEOWNERS |
| Tag-based releases are used | Enforce annotated tags with version and changelog summary |

## Success Criteria

- [ ] Branching strategy is documented and agreed upon by the team
- [ ] All commits on the default branch follow the defined commit convention
- [ ] Git hooks are installed and validating commit messages on every commit
- [ ] Merge strategy is configured per target branch in repository settings
- [ ] Branch protection rules enforce CI passage and review requirements
- [ ] No force-pushes to protected branches in the last 30 days
- [ ] Stale branches (> 30 days, merged) are cleaned up automatically or on schedule
- [ ] Conflict resolution does not introduce test regressions

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| History rewrite on shared branch | Other developers' branches diverge; push rejected errors | Enable branch protection; block force-push on shared branches |
| Inconsistent commit messages | Changelog generation produces garbage; `git log` is unreadable | Enforce commitlint hook; reject non-conforming commits in CI |
| Merge conflict avalanche | Long-lived branch accumulates dozens of conflicts at merge time | Require periodic rebase (at least weekly); set branch age alerts |
| Wrong merge strategy applied | Squash merge loses meaningful intermediate history; merge commit clutters log | Configure repository-level default merge strategy; document exceptions |
| Orphaned branches | Repository accumulates hundreds of stale branches | Automate branch cleanup after merge; set branch expiration policy |
| Tag collision | Two releases tagged with the same version | Use CI to validate tag uniqueness before publish; enforce semver |
| Hook bypass abuse | Developers routinely skip hooks with `--no-verify` | Monitor bypass frequency; require CI-level validation as backstop |

## Audit Log

- `[timestamp]` branching-strategy-set: Adopted `<strategy>` for repository `<repo>` with branch naming convention `<pattern>`
- `[timestamp]` commit-convention-configured: Installed commitlint with ruleset `<config>` and pre-commit hook
- `[timestamp]` merge-strategy-set: Default merge method for `<target-branch>` set to `<strategy>`
- `[timestamp]` branch-protection-applied: Protected `<branch>` requiring `<review-count>` reviews and CI passage
- `[timestamp]` conflict-resolved: Resolved `<file-count>` conflicts in `<branch>` via `<method>` (manual/auto)
- `[timestamp]` stale-branches-cleaned: Deleted `<count>` merged branches older than `<days>` days
- `[timestamp]` hook-bypass-detected: `--no-verify` used by `<author>` on commit `<sha-short>`

````
