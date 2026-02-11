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
