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

---

## Scope

### In Scope

- Designing and generating CI/CD pipeline configuration files (GitHub Actions, GitLab CI, Azure Pipelines, Jenkins)
- Stage orchestration: ordering build, test, lint, security-scan, and deploy stages with correct dependency graphs
- Artifact management: producing, uploading, and passing build artifacts between pipeline stages
- Deployment gates: manual approvals, environment protection rules, and promotion strategies
- Pipeline caching strategies for dependencies and build outputs
- Branch protection rules and merge-request policies tied to pipeline status
- Secret and environment variable configuration for pipeline contexts
- Matrix builds and parallel job fan-out/fan-in patterns

### Out of Scope

- Application source code changes unrelated to pipeline configuration
- Cloud infrastructure provisioning (handled by `terraform-iac`)
- Container image authoring (handled by `docker-containerization`)
- Runtime monitoring and alerting configuration
- Manual deployment scripts that bypass the pipeline
- Source control server administration (e.g., GitLab Runner installation, GitHub-hosted runner fleet management)

---

## Guardrails

- Never hard-code secrets, tokens, or credentials in pipeline files; always reference secret stores or masked variables.
- Every pipeline must include at least `lint`, `test`, and `build` stages before any deployment stage.
- Production deployment stages must require an explicit approval gate or manual trigger.
- Pin all action/image versions to a specific SHA or tag — never use `@latest` or `@main` in production pipelines.
- Validate pipeline YAML syntax before committing (`actionlint`, `gitlab-ci-lint`, or equivalent).
- Do not disable or skip security-scan stages without documenting the justification in the PR description.
- Preserve existing pipeline stages when adding new ones; never silently remove stages.
- Ensure every job defines a `timeout` to prevent runaway builds from consuming resources.

---

## Ask-When-Ambiguous

### Triggers

- The repository has no existing CI configuration and the platform cannot be auto-detected
- Multiple deployment targets exist (e.g., Kubernetes, serverless, VM) and the strategy is unclear
- The desired branching model (trunk-based, GitFlow, release branches) is not documented
- Artifact retention policy is unspecified (how long to keep, where to store)
- The project uses a monorepo and it is unclear which paths should trigger which pipelines

### Question Templates

1. "Which CI/CD platform should the pipeline target — GitHub Actions, GitLab CI, Azure Pipelines, or another?"
2. "What deployment strategy do you want for production: blue-green, canary, rolling update, or manual push?"
3. "Should the pipeline include a matrix build across multiple OS or language versions? If so, which combinations?"
4. "What is the artifact retention policy — how many days should build artifacts be kept?"
5. "Is this a monorepo? If yes, which directory paths should trigger this pipeline?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Repository has `.github/` directory or `CODEOWNERS` | Default to GitHub Actions |
| Repository has `.gitlab-ci.yml` | Default to GitLab CI |
| Repository has `azure-pipelines.yml` | Default to Azure Pipelines |
| No CI config detected and user does not specify | Ask user for platform preference |
| Pipeline has > 5 independent jobs | Fan-out with parallel jobs and fan-in for deploy |
| Build time exceeds 10 minutes | Add dependency caching and investigate parallelization |
| Deploying to multiple environments | Use staged deployment with gates between each environment |
| Security scan finds critical vulnerabilities | Block the pipeline and require manual override to proceed |
| Monorepo detected with multiple services | Generate path-filtered pipelines per service |

---

## Success Criteria

- [ ] Pipeline YAML is syntactically valid and passes platform-specific linting
- [ ] All stages execute in correct dependency order (lint → test → build → scan → deploy)
- [ ] Secrets are referenced via secret stores, never inline
- [ ] Production deployment requires a manual approval gate
- [ ] Dependency and build caching reduces install time by ≥ 30% on cache hit
- [ ] Pipeline completes a full green run on the target branch
- [ ] Artifacts are uploaded and accessible between stages
- [ ] Branch protection rules enforce pipeline passage before merge

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Secret not available in CI context | Job fails with "undefined variable" or empty credential errors | Verify secret is configured in the correct environment scope; check secret name casing |
| Cache key mismatch | Dependencies re-install on every run despite caching config | Use lock-file hash in cache key (e.g., `hashFiles('**/package-lock.json')`) |
| Stage ordering error | Deploy runs before tests complete | Add explicit `needs` / `dependencies` between jobs; validate DAG |
| Action/image version drift | Pipeline breaks after upstream action publishes breaking change | Pin actions to full SHA; use Dependabot or Renovate to manage updates |
| Pipeline timeout | Job hangs indefinitely on flaky test or network call | Set per-job `timeout-minutes`; add retry with backoff for flaky steps |
| Artifact expiration | Downstream stage cannot find artifacts from prior stage | Ensure artifact upload/download names match; extend retention if pipeline spans multiple days |
| Matrix explosion | Too many parallel jobs exhaust runner capacity | Limit matrix combinations with `include`/`exclude`; run full matrix only on main branch |

---

## Audit Log

- `[timestamp]` pipeline-generated: Created `<platform>` pipeline config at `<file-path>` with stages `<stage-list>`
- `[timestamp]` stage-added: Appended stage `<stage-name>` to pipeline with dependency on `<upstream-stage>`
- `[timestamp]` cache-configured: Added dependency cache with key `<cache-key-expression>`
- `[timestamp]` gate-added: Configured manual approval gate for `<environment>` deployment
- `[timestamp]` secret-referenced: Added secret reference `<secret-name>` to `<job-name>`
- `[timestamp]` optimization-applied: Enabled parallel fan-out for `<job-list>`, estimated time saving `<percent>`%
- `[timestamp]` validation-passed: Pipeline YAML passed `<linter>` with 0 errors
