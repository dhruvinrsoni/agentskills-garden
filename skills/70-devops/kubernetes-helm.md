---
name: kubernetes-helm
description: >
  Generate Kubernetes manifests and Helm charts for deploying
  containerized applications to K8s clusters.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - docker-containerization
reasoning_mode: plan-execute
---

# Kubernetes & Helm

> _"Declare the desired state. Let the cluster figure out the rest."_

## Context

Invoked when deploying containerized applications to Kubernetes. Generates
production-grade manifests or Helm charts with best practices baked in.

---

## Micro-Skills

### 1. Manifest Generation ⚡ (Power Mode)

**Steps:**

1. Generate core K8s resources:
   - `Deployment` (or `StatefulSet` for stateful apps).
   - `Service` (ClusterIP, LoadBalancer, or NodePort).
   - `Ingress` (with TLS termination).
   - `ConfigMap` and `Secret` for configuration.
   - `HorizontalPodAutoscaler` (HPA).
2. Set resource requests and limits (CPU, memory).
3. Add liveness, readiness, and startup probes.
4. Set `PodDisruptionBudget` for high-availability deployments.

### 2. Helm Chart Scaffolding ⚡ (Power Mode)

**Steps:**

1. Create Helm chart structure:
   ```
   chart/
   ├── Chart.yaml
   ├── values.yaml
   ├── templates/
   │   ├── deployment.yaml
   │   ├── service.yaml
   │   ├── ingress.yaml
   │   ├── configmap.yaml
   │   ├── secret.yaml
   │   ├── hpa.yaml
   │   └── _helpers.tpl
   └── .helmignore
   ```
2. Parameterize everything in `values.yaml` (image, replicas, resources,
   env vars, ingress host).
3. Add `{{ include }}` helpers for labels and selectors.

### 3. Security Policies ⚡ (Power Mode)

**Steps:**

1. Add `NetworkPolicy` to restrict pod-to-pod traffic.
2. Set `securityContext`:
   - `runAsNonRoot: true`
   - `readOnlyRootFilesystem: true`
   - `allowPrivilegeEscalation: false`
3. Use `ServiceAccount` with minimal RBAC.
4. Scan manifests with `kubesec` or `kube-linter`.

### 4. Rollout Strategy ⚡ (Power Mode)

**Steps:**

1. Configure rolling update strategy:
   - `maxUnavailable: 0` (zero downtime).
   - `maxSurge: 25%`.
2. Add rollback command reference: `helm rollback <release> <revision>`.
3. Configure pre/post-deploy hooks if needed.

---

## Outputs

| Field            | Type       | Description                              |
|------------------|------------|------------------------------------------|
| `manifests`      | `string[]` | Generated K8s YAML files                 |
| `helm_chart`     | `string`   | Helm chart directory path                |
| `values`         | `string`   | Default values.yaml                      |

---

## Scope

### In Scope

- Generating Kubernetes Deployment, Service, Ingress, ConfigMap, Secret, HPA, PDB, and NetworkPolicy manifests.
- Scaffolding Helm charts with parameterized `values.yaml` and `_helpers.tpl`.
- Configuring security contexts, RBAC roles, and service accounts.
- Setting resource requests/limits, probes, and rollout strategies.
- Kustomize overlay generation for multi-environment deployments.

### Out of Scope

- Provisioning cloud infrastructure (VPCs, node pools, managed services) — defer to `terraform-iac`.
- Building or pushing container images — defer to `docker-containerization`.
- Cluster administration (upgrades, node management, etcd backups).
- Writing application code or modifying business logic.
- Managing DNS records or TLS certificate issuance outside of Ingress annotations.

## Guardrails

- Never hardcode secrets in manifests; always use `Secret` resources or external secrets operators.
- Set `resources.requests` and `resources.limits` on every container — never leave them empty.
- Always set `runAsNonRoot: true` and `readOnlyRootFilesystem: true` unless the user explicitly opts out.
- Validate generated YAML with `kubectl --dry-run=client` or `helm template` before presenting output.
- Never set `replicas` below 2 for production workloads without explicit user approval.
- Do not generate `hostNetwork: true`, `privileged: true`, or `hostPID: true` unless the user explicitly requests it and confirms the security implications.
- Preserve existing labels, annotations, and custom resources already present in the project.

## Ask-When-Ambiguous

### Triggers

- Deployment type is unclear (Deployment vs StatefulSet vs DaemonSet).
- Target namespace or cluster environment (dev/staging/prod) is not specified.
- Service exposure model is ambiguous (ClusterIP vs LoadBalancer vs Ingress).
- Persistence requirements are mentioned but volume type is unspecified.
- The user references Helm but doesn't clarify whether to create a new chart or add to an existing one.

### Question Templates

- "Does this workload need persistent storage? If so, what access mode (ReadWriteOnce, ReadWriteMany) and size?"
- "Which namespace and environment (dev/staging/prod) should these manifests target?"
- "Should the service be exposed externally via Ingress, or kept internal as a ClusterIP?"
- "Is this a new Helm chart or should I add templates to the existing chart at `<path>`?"
- "Are there existing resource quotas or LimitRanges in the target namespace I should respect?"

## Decision Criteria

| Situation | Action |
|---|---|
| Stateless HTTP service | Use `Deployment` + `HPA` with rolling update strategy |
| Database or message queue | Use `StatefulSet` with `volumeClaimTemplates` |
| Log collector or node agent | Use `DaemonSet` |
| Single environment, no parameterization needed | Generate plain YAML manifests |
| Multi-environment or reuse required | Scaffold a Helm chart with `values.yaml` per env |
| Fewer than 3 microservices | Individual manifests per service |
| 3+ microservices with shared config | Helm umbrella chart with subcharts |
| Service needs zero-downtime deploys | Set `maxUnavailable: 0`, add `PodDisruptionBudget` |
| External traffic required | Add `Ingress` with TLS; annotate for cert-manager |

## Success Criteria

- [ ] All generated manifests pass `kubectl apply --dry-run=client` without errors.
- [ ] `helm template` renders the chart without warnings or unresolved values.
- [ ] Every container has `resources.requests` and `resources.limits` defined.
- [ ] Liveness, readiness, and startup probes are configured on all application containers.
- [ ] Security contexts enforce non-root execution and read-only filesystems.
- [ ] No secrets appear in plaintext within manifests or `values.yaml`.
- [ ] NetworkPolicy restricts ingress/egress to only required paths.
- [ ] Generated manifests are idempotent — re-applying produces no diff.

## Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| Missing resource limits | Pod gets OOMKilled or starves other workloads | Always set CPU/memory requests and limits; validate with `kube-linter` |
| No health probes | Failed pods stay in Running state, receive traffic | Add liveness + readiness probes matching actual health endpoints |
| Hardcoded secrets | Credentials exposed in version control | Use `Secret` resources with `stringData`; flag for external secrets operator |
| Image tag set to `latest` | Non-deterministic deployments, rollback fails | Pin image tags to digest or semver; warn if `latest` detected |
| Missing `PodDisruptionBudget` | Cluster upgrades or node drains cause downtime | Add PDB with `minAvailable` for production workloads |
| Helm values not parameterized | Chart works only for one environment | Ensure all environment-specific values flow through `values.yaml` |
| RBAC too permissive | Service account has cluster-admin privileges | Scope roles to minimum verbs and resources; use `Role` over `ClusterRole` |

## Audit Log

- `[{timestamp}]` Skill invoked — mode: `{manifest|helm}`, target namespace: `{namespace}`, environment: `{env}`.
- `[{timestamp}]` Resources generated: `{resource_list}` (e.g., Deployment, Service, Ingress, HPA).
- `[{timestamp}]` Helm chart scaffolded at `{chart_path}` — templates: `{template_count}`, values keys: `{key_count}`.
- `[{timestamp}]` Security scan result: `{pass|fail}` — issues: `{issue_list}`.
- `[{timestamp}]` Dry-run validation: `{pass|fail}` — errors: `{error_count}`.
- `[{timestamp}]` Files written: `{file_paths}`, total size: `{bytes}` bytes.
