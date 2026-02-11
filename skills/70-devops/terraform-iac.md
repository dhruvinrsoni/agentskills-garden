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
