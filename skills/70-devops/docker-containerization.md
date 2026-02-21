---
name: docker-containerization
description: >
  Write optimized Dockerfiles with multi-stage builds,
  security best practices, and minimal image sizes.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# Docker Containerization

> _"Ship the app, not the toolchain."_

## Context

Invoked when containerizing an application. Focuses on security, image size,
build speed, and reproducibility.

---

## Micro-Skills

### 1. Dockerfile Generation 🌿 (Eco Mode)

**Steps:**

1. Detect the application type (Node.js, Python, Go, Java, .NET).
2. Generate a multi-stage Dockerfile:

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine AS runtime
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER app
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

### 2. Security Hardening 🌿 (Eco Mode)

**Steps:**

1. Use minimal base images (`-alpine`, `-slim`, `distroless`).
2. Run as non-root user (never `USER root` in final stage).
3. Add `.dockerignore` (exclude `.git`, `node_modules`, `.env`).
4. Pin image versions (no `latest` tag).
5. Scan image with `docker scout` or `trivy`.

### 3. Build Optimization 🌿 (Eco Mode)

**Steps:**

1. Order layers from least-changed to most-changed (maximize cache).
2. Separate dependency install from code copy.
3. Use BuildKit features (`--mount=type=cache` for package managers).
4. Set `.dockerignore` to exclude test files and docs from build context.

### 4. Docker Compose 🌿 (Eco Mode)

**Steps:**

1. Create `docker-compose.yml` for local development.
2. Include: app, database, cache (if applicable).
3. Use named volumes for data persistence.
4. Add health checks for all services.
5. Create `docker-compose.override.yml` for dev-specific settings
   (hot reload, debug ports).

---

## Outputs

| Field           | Type       | Description                              |
|-----------------|------------|------------------------------------------|
| `dockerfile`    | `string`   | Optimized Dockerfile                     |
| `dockerignore`  | `string`   | .dockerignore file                       |
| `compose`       | `string`   | Docker Compose configuration             |
| `image_size`    | `string`   | Estimated image size                     |

---

## Scope

### In Scope

- Writing and optimizing Dockerfiles with multi-stage builds for any application stack
- Base image selection: choosing minimal, secure images (`alpine`, `slim`, `distroless`)
- Layer ordering and caching strategies to minimize rebuild time
- `.dockerignore` generation to reduce build context size
- Security hardening: non-root users, read-only filesystems, pinned image digests
- Image scanning integration (Trivy, Docker Scout, Grype) and vulnerability remediation
- Docker Compose configuration for local development and testing environments
- BuildKit features: cache mounts, secret mounts, multi-platform builds

### Out of Scope

- Kubernetes manifest generation or Helm chart authoring (handled by `kubernetes-helm`)
- Container orchestration, scheduling, and scaling policies
- CI/CD pipeline configuration (handled by `ci-pipeline`)
- Host OS configuration or Docker daemon tuning
- Container registry administration (ACR, ECR, GCR setup)
- Application code changes unrelated to containerization

---

## Guardrails

- Never use `latest` as a base image tag; always pin to a specific version or digest.
- Final stage must run as a non-root user (`USER` directive required).
- Never copy `.git`, `.env`, `node_modules`, or secret files into the image; enforce via `.dockerignore`.
- Multi-stage builds are mandatory — build tools must not appear in the runtime image.
- Every `RUN` instruction that installs packages must clean up caches in the same layer (e.g., `rm -rf /var/cache/apk/*`).
- Do not use `COPY . .` before dependency installation; separate dependency copy from source copy for cache efficiency.
- Health checks must be defined for all services in Docker Compose files.
- Image size must be justified — flag any runtime image exceeding 500 MB for review.

---

## Ask-When-Ambiguous

### Triggers

- The application runtime cannot be auto-detected from the project structure
- Multiple services exist in the repository and it is unclear which to containerize
- The target deployment platform imposes specific image constraints (e.g., distroless required, specific UID)
- The user has not specified whether a Docker Compose setup is needed for local development
- The application requires access to GPUs, host networking, or privileged capabilities

### Question Templates

1. "What is the application runtime and version — Node.js 20, Python 3.12, Go 1.22, Java 21, .NET 8, or another?"
2. "Should the image use `alpine`, `slim`, or `distroless` as the base — do you have a preference or a platform constraint?"
3. "Is a Docker Compose file needed for local development? If so, what supporting services are required (database, cache, message queue)?"
4. "Does the application need to expose multiple ports, or is a single port sufficient?"
5. "Are there build-time secrets (private registry tokens, SSH keys) that need to be injected securely during the build?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Application is statically compiled (Go, Rust) | Use `scratch` or `distroless/static` as final base |
| Application needs a system shell for debugging | Use `alpine` or `slim` instead of `distroless` |
| Build produces a single binary | Use two-stage build: builder → copy binary to minimal base |
| Application has native dependencies (e.g., `bcrypt`, `sharp`) | Build native modules in builder stage on matching architecture |
| Image size exceeds 500 MB | Audit layers with `docker history`; switch to slimmer base or reduce copied files |
| Image scan reports critical CVE in base image | Upgrade base image version; if no fix available, document accepted risk |
| Multiple services in monorepo | Generate separate Dockerfiles per service with shared base builder stage |
| Local development requires hot-reload | Use bind mounts in `docker-compose.override.yml`; do not bake source into dev image |

---

## Success Criteria

- [ ] Dockerfile builds successfully without errors or warnings
- [ ] Final image runs as a non-root user
- [ ] Multi-stage build ensures no build tooling is present in the runtime image
- [ ] `.dockerignore` prevents `.git`, secrets, and unnecessary files from entering the build context
- [ ] Image scan (Trivy/Scout) reports zero critical or high vulnerabilities in application layers
- [ ] Image size is within acceptable bounds (< 200 MB for interpreted runtimes, < 50 MB for compiled)
- [ ] Container starts and passes health check within 30 seconds
- [ ] Docker Compose `up` brings all services to healthy state without manual intervention

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Base image CVE | Security scan flags critical vulnerability in OS packages | Upgrade to latest patched base image; rebuild and rescan |
| Layer cache invalidation | Changing one source file triggers full dependency reinstall | Reorder Dockerfile: copy lock files → install deps → copy source |
| Image bloat | Runtime image is unexpectedly large (> 500 MB) | Run `docker history --no-trunc` to find large layers; remove unnecessary files or switch base |
| Permission denied at runtime | Container crashes with EACCES on file or port operations | Ensure files are owned by the non-root user; use ports > 1024 |
| Build-time secret leakage | Secret token visible in image layers via `docker history` | Use `--mount=type=secret` with BuildKit instead of `ARG`/`ENV` for secrets |
| Missing native dependency | App crashes at start with "module not found" for native addon | Install build toolchain in builder stage; ensure architecture matches runtime base |
| Docker Compose port conflict | `docker compose up` fails with "port already in use" | Use `.env` to parameterize ports; check for conflicting local services |

---

## Audit Log

- `[timestamp]` dockerfile-generated: Created Dockerfile for `<runtime>` app at `<path>` with base `<base-image>`
- `[timestamp]` multistage-configured: Builder stage uses `<builder-image>`, runtime stage uses `<runtime-image>`
- `[timestamp]` security-hardened: Set `USER <user>`, `readOnlyRootFilesystem`, pinned base to `<digest>`
- `[timestamp]` image-scanned: Ran `<scanner>` — `<critical>` critical, `<high>` high, `<medium>` medium vulnerabilities
- `[timestamp]` dockerignore-created: Generated `.dockerignore` excluding `<pattern-list>`
- `[timestamp]` compose-generated: Created `docker-compose.yml` with services `<service-list>`
- `[timestamp]` image-size: Final image size `<size>` MB (base: `<base-size>` MB, app layers: `<app-size>` MB)
