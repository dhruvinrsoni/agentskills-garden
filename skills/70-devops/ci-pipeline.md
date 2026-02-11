---
name: ci-pipeline
description: >
  Generate CI/CD pipeline configurations for GitHub Actions,
  GitLab CI, or Azure Pipelines.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - test-strategy
reasoning_mode: plan-execute
---

# CI Pipeline

> _"If it's not in the pipeline, it doesn't exist."_

## Context

Invoked when setting up or improving continuous integration. The pipeline
is the **gatekeeper** — nothing merges without passing.

---

## Micro-Skills

### 1. Pipeline Generation ⚡ (Power Mode)

**Steps:**

1. Detect the CI platform:
   - `.github/` directory → GitHub Actions
   - `.gitlab-ci.yml` exists → GitLab CI
   - `azure-pipelines.yml` exists → Azure Pipelines
   - None → Ask user which platform to use.
2. Generate a pipeline with these stages:
   ```
   install → lint → test → build → security-scan → deploy
   ```

### 2. GitHub Actions Workflow ⚡ (Power Mode)

**Steps:**

1. Create `.github/workflows/ci.yml`.
2. Configure:
   - Trigger: `push` to main, `pull_request` to main.
   - Matrix: test across multiple OS/language versions if applicable.
   - Caching: cache `node_modules`, `.pip`, or Go modules.
   - Steps: checkout → setup-lang → install → lint → test → build.
3. Add branch protection rules recommendation.

### 3. Pipeline Optimization 🌿 (Eco Mode)

**Steps:**

1. Add dependency caching to reduce install time.
2. Parallelize independent jobs (lint + test simultaneously).
3. Add `paths` filter to skip jobs when only docs change.
4. Use artifacts to pass build outputs between jobs.

### 4. Deployment Stage ⚡ (Power Mode)

**Steps:**

1. Define environments: `staging`, `production`.
2. Add environment-specific secrets.
3. Implement deployment strategy:
   - **Staging:** Auto-deploy on merge to main.
   - **Production:** Manual approval gate.
4. Add rollback mechanism (revert to previous deployment).

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `pipeline_file`  | `string`   | Generated CI configuration file          |
| `branch_rules`   | `string`   | Branch protection recommendations        |
| `secrets_list`   | `string[]` | Required CI secrets                      |
