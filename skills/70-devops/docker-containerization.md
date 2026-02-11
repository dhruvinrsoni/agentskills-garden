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
