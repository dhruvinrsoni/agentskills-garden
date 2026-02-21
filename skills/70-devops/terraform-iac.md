---
name: terraform-iac
description: >
  Generate Infrastructure as Code using Terraform (or OpenTofu).
  Modules, state management, and environment separation.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - system-design
reasoning_mode: plan-execute
---

# Terraform / Infrastructure as Code

> _"If you can't reproduce your infrastructure from code, it's not infrastructure."_

## Context

Invoked when provisioning cloud infrastructure. Generates Terraform modules
following best practices for state management, security, and reusability.

---

## Micro-Skills

### 1. Module Generation ⚡ (Power Mode)

**Steps:**

1. Identify required resources from the system design.
2. Generate Terraform module structure:
   ```
   terraform/
   ├── main.tf           # Resource definitions
   ├── variables.tf      # Input variables
   ├── outputs.tf        # Output values
   ├── providers.tf      # Provider configuration
   ├── versions.tf       # Terraform and provider version constraints
   └── terraform.tfvars  # (gitignored) Environment-specific values
   ```
3. Use data sources for existing resources (don't recreate).
4. Tag all resources consistently (team, project, environment).

### 2. State Management ⚡ (Power Mode)

**Steps:**

1. Configure remote state backend:
   - AWS: S3 + DynamoDB for locking.
   - Azure: Storage Account + Blob.
   - GCP: GCS bucket.
2. Enable state encryption.
3. Set up state locking to prevent concurrent modifications.
4. Never commit `terraform.tfstate` or `.tfvars` with secrets.

### 3. Environment Separation ⚡ (Power Mode)

**Steps:**

1. Use workspaces or directory-based separation:
   ```
   environments/
   ├── dev/
   │   ├── main.tf → ../../modules/
   │   └── terraform.tfvars
   ├── staging/
   └── production/
   ```
2. Use the same modules across environments with different variables.
3. Implement environment promotion (dev → staging → prod).

### 4. Security & Compliance ⚡ (Power Mode)

**Steps:**

1. Use `tfsec` or `checkov` to scan for misconfigurations.
2. Encrypt sensitive outputs.
3. Use IAM roles with least privilege.
4. Enable audit logging for infrastructure changes.
5. Run `terraform plan` in CI, require approval for `apply`.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `modules`        | `string[]` | Generated Terraform module files         |
| `env_configs`    | `string[]` | Environment-specific configurations      |
| `state_config`   | `string`   | Backend configuration                    |
| `scan_results`   | `string`   | Security scan output                     |

---

## Scope

### In Scope

- Generating Terraform (and OpenTofu) modules, configurations, and variable definitions
- Supporting alternative IaC tools: Pulumi, CloudFormation, and Bicep when requested
- Remote state backend configuration with locking and encryption (S3/DynamoDB, Azure Blob, GCS)
- Environment separation strategies: workspaces, directory-based, or Terragrunt hierarchies
- Drift detection: comparing deployed resources against declared state via `terraform plan`
- Modular design: composable, reusable modules with well-defined inputs, outputs, and versioning
- Security scanning of IaC files with `tfsec`, `checkov`, or `trivy config`
- Resource tagging standards and naming conventions across all managed resources
- Import of existing (manually created) resources into Terraform state

### Out of Scope

- Application source code or runtime configuration changes
- CI/CD pipeline design (handled by `ci-pipeline`; this skill produces the IaC files the pipeline deploys)
- Kubernetes manifest or Helm chart authoring (handled by `kubernetes-helm`)
- Cloud console or CLI-based manual resource creation
- Cost optimization analysis (pricing model assessment, reserved-instance planning)
- IAM policy design beyond what is needed for Terraform execution roles

---

## Guardrails

- Never commit `terraform.tfstate`, `.tfvars` files with secrets, or provider credentials to version control.
- Always configure a remote backend with state locking before any `apply` operation.
- Pin provider versions in `versions.tf` to prevent unexpected upgrades.
- Tag every resource with at minimum: `project`, `environment`, `managed-by=terraform`.
- Run `terraform fmt` and `terraform validate` before committing any changes.
- Run security scanner (`tfsec` / `checkov`) on every change; do not merge with unresolved critical findings.
- Use `data` sources to reference existing resources — never recreate resources managed outside this configuration.
- All sensitive variables must be marked `sensitive = true` and must never appear in plan output or logs.
- Require `terraform plan` output review in CI before any `terraform apply` execution.

---

## Ask-When-Ambiguous

### Triggers

- The target cloud provider is not specified or the project spans multiple providers
- State backend preferences are unknown (S3, Azure Blob, GCS, Terraform Cloud)
- The environment separation strategy is not defined (workspaces vs. directory-based vs. Terragrunt)
- Existing infrastructure needs to be imported but the resource IDs are not provided
- The desired IaC tool is not Terraform (user may prefer Pulumi, CloudFormation, or Bicep)

### Question Templates

1. "Which cloud provider(s) are you targeting — AWS, Azure, GCP, or multi-cloud?"
2. "Where should Terraform state be stored — S3 + DynamoDB, Azure Storage, GCS, or Terraform Cloud?"
3. "How do you want to separate environments — Terraform workspaces, directory-per-env, or Terragrunt?"
4. "Are there existing cloud resources that need to be imported into Terraform state? If so, provide the resource IDs."
5. "Do you want to use Terraform/OpenTofu, or would you prefer Pulumi, CloudFormation, or Bicep?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Single cloud provider, simple project | Use flat module structure with `terraform.workspace` for env separation |
| Multi-environment with divergent configs | Use directory-per-environment pattern with shared modules |
| Many environments with DRY config needs | Recommend Terragrunt for hierarchical variable inheritance |
| Existing resources not managed by IaC | Use `terraform import` and generate corresponding resource blocks |
| Drift detected in `terraform plan` | Investigate cause; if intentional manual change, update code to match; if accidental, apply to restore |
| Module is reused across 3+ projects | Publish module to a private registry with semantic versioning |
| Security scanner reports critical finding | Block merge; remediate finding before proceeding |
| State file is corrupted or locked | Use `terraform force-unlock` (with caution); restore state from backup if corrupted |
| Provider needs upgrading | Pin new version in `versions.tf`; run `terraform init -upgrade`; review plan for breaking changes |

---

## Success Criteria

- [ ] All Terraform files pass `terraform validate` and `terraform fmt` checks
- [ ] Remote state backend is configured with encryption and locking enabled
- [ ] `terraform plan` shows expected changes with zero unexpected resource modifications
- [ ] Security scan (`tfsec`/`checkov`) reports zero critical findings
- [ ] All resources are tagged with `project`, `environment`, and `managed-by` labels
- [ ] Modules have documented `variables.tf` and `outputs.tf` with descriptions for every variable
- [ ] Sensitive values are marked `sensitive = true` and excluded from logs
- [ ] Environment separation is consistent — same modules deployed across dev, staging, and production

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| State lock contention | `terraform apply` fails with "state locked by another process" | Verify no other apply is running; use `terraform force-unlock <lock-id>` as last resort |
| State drift | `terraform plan` shows unexpected changes to resources | Run `terraform refresh`; compare with cloud console; update code or apply to reconcile |
| Provider version incompatibility | `terraform init` fails or plan shows deprecated resource arguments | Pin compatible provider version in `versions.tf`; consult provider changelog |
| Secrets committed to repo | `.tfvars` with credentials appears in git history | Rotate compromised credentials immediately; use `git filter-branch` or BFG to purge; move secrets to vault |
| Circular module dependency | `terraform validate` reports cycle in module references | Refactor modules to break circular dependency; use `data` sources for cross-module references |
| Resource already exists | `apply` fails with "resource already exists" error | Import existing resource with `terraform import`; add matching resource block |
| Insufficient permissions | `apply` fails with "access denied" on resource creation | Verify IAM role/policy attached to Terraform execution identity; follow least-privilege principle |

---

## Audit Log

- `[timestamp]` module-generated: Created Terraform module at `<path>` for `<resource-type>` on `<provider>`
- `[timestamp]` state-backend-configured: Set up `<backend-type>` backend with encryption=`<bool>`, locking=`<bool>`
- `[timestamp]` environment-created: Generated environment config for `<env-name>` using `<separation-strategy>`
- `[timestamp]` drift-detected: `terraform plan` shows `<n>` unexpected changes in `<environment>`
- `[timestamp]` security-scanned: Ran `<scanner>` — `<critical>` critical, `<high>` high findings
- `[timestamp]` resource-imported: Imported `<resource-type>.<resource-name>` with ID `<resource-id>`
- `[timestamp]` plan-approved: `terraform plan` reviewed and approved for `<environment>` with `<n>` changes
