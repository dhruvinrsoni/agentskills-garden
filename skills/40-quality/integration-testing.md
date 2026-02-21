---
name: integration-testing
description: >
  Test across component boundaries using real databases, HTTP clients,
  and message queues via Docker containers.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
  - test-strategy
  - docker-containerization
reasoning_mode: plan-execute
---

# Integration Testing

> _"Unit tests prove your code works. Integration tests prove your system works."_

## Context

Invoked when testing interactions between components: API endpoints hitting
real databases, services communicating over HTTP/gRPC, or event-driven
message flows.

---

## Micro-Skills

### 1. Test Container Setup ⚡ (Power Mode)

**Steps:**

1. Define required services (Postgres, Redis, Kafka, etc.).
2. Create a `docker-compose.test.yml` with isolated test containers.
3. Configure health checks so tests wait for readiness.
4. Set up automatic teardown after test suite completes.

### 2. API Integration Tests ⚡ (Power Mode)

**Steps:**

1. For each API endpoint, write tests that:
   - Send real HTTP requests to the running server.
   - Use a real database (seeded with known data).
   - Assert on response status, body, and headers.
2. Test error paths: 400, 401, 403, 404, 409, 500.
3. Test pagination, filtering, and sorting.

### 3. Database Integration Tests ⚡ (Power Mode)

**Steps:**

1. Use a real database instance (Docker container).
2. Run migrations before each test suite.
3. Use transactions that rollback after each test (clean slate).
4. Test: CRUD operations, constraints, cascade deletes, concurrent writes.

### 4. Contract Testing ⚡ (Power Mode)

**Steps:**

1. For service-to-service communication, write consumer-driven contracts.
2. Use Pact or similar for HTTP, Buf for Protobuf.
3. Verify both consumer expectations and provider conformance.

---

## Outputs

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| `test_files`       | `string[]` | Generated integration test files         |
| `docker_compose`   | `string`   | Test Docker Compose file                 |
| `test_results`     | `object`   | Pass/fail summary                        |

---

## Scope

### In Scope

- Creating and modifying integration test files across component boundaries.
- Defining `docker-compose.test.yml` and container health-check configs.
- Test fixture and seed-data scripts for databases and message queues.
- Integration test runner configuration (timeouts, retries, parallelism).
- Consumer-driven contract test files (Pact, Buf).

### Out of Scope

- Unit tests (delegate to `unit-testing` skill).
- End-to-end / UI tests (browser automation, Cypress, Playwright).
- Production `docker-compose.yml` or Kubernetes manifests.
- Application source code changes (only test code is modified).
- CI/CD pipeline definitions (delegate to `ci-pipeline` skill).
- Performance or load testing scenarios.

---

## Guardrails

- Never run integration tests against production databases, APIs, or message brokers.
- Always use isolated Docker containers with deterministic seed data; never share containers across test suites.
- Ensure every test suite tears down its containers and volumes automatically—no orphaned resources.
- Do not modify application source code; only create or edit test files and test infrastructure.
- Keep individual test execution under 30 seconds; target full suite completion under 5 minutes.
- Never hard-code credentials or connection strings—use environment variables or Docker secrets.
- Fail fast: if a container health check does not pass within 60 seconds, abort the suite with a clear error.
- Run formatter and linter on generated test files; revert if new lint errors are introduced.

---

## Ask-When-Ambiguous

### Triggers

- No `docker-compose.test.yml` exists and required services are unclear.
- Existing tests blur the line between unit and integration (e.g., mocking the DB vs. using a real container).
- Multiple database engines are present and it is unclear which one the tests target.
- The project uses a custom test harness rather than a standard test runner.
- Contract testing is mentioned but no contract broker (e.g., Pact Broker) is configured.

### Question Templates

- "Which external services (database, cache, queue) should the integration tests run against?"
- "Should I create a new `docker-compose.test.yml` or extend an existing one?"
- "Do you want tests to use transaction rollback for isolation, or full DB reset between tests?"
- "Is there a preferred contract testing tool (Pact, Buf, Spring Cloud Contract), or should I recommend one?"
- "Should the integration test suite run in parallel or sequentially to avoid port/state conflicts?"

---

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Service has a public API with DB backing | Write API-level integration tests with a real DB container |
| Service communicates with another service via HTTP/gRPC | Add consumer-driven contract tests |
| Database has complex constraints or triggers | Write dedicated DB integration tests with migration replay |
| Message queue is involved (Kafka, RabbitMQ) | Spin up queue container; test publish/consume round-trip |
| Test suite exceeds 5-minute target | Parallelize test suites, use container reuse strategies |
| No existing Docker test infrastructure | Create `docker-compose.test.yml` from scratch before writing tests |
| Flaky test detected (passes/fails non-deterministically) | Add explicit waits, health checks, and deterministic seed data |

---

## Success Criteria

- [ ] All integration tests pass in both local Docker and CI environments.
- [ ] Every API endpoint has at least one integration test covering the happy path.
- [ ] Error paths (400, 401, 403, 404, 500) are tested for each endpoint.
- [ ] Database tests leave zero residual state between runs (clean-slate guarantee).
- [ ] Container startup, test execution, and teardown complete within the 5-minute budget.
- [ ] No hard-coded secrets or host-specific paths in test files.
- [ ] Contract tests verify both consumer expectations and provider conformance.

---

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Container fails to start | Tests timeout waiting for health check | Add explicit health-check commands; increase startup timeout; verify Docker daemon is running |
| Port collision | "Address already in use" error | Use dynamic port mapping (`0:5432`) or randomized port assignment in compose |
| Stale seed data | Tests pass locally but fail in CI | Version seed scripts alongside migrations; rebuild containers from scratch in CI |
| Test pollution | Test B fails only when run after Test A | Enforce per-test transaction rollback or truncate all tables in `beforeEach` |
| Flaky network calls | Intermittent connection refused errors | Add retry logic in test setup; ensure `depends_on` with health-check condition |
| Missing migration | Schema mismatch causes SQL errors | Run all pending migrations in container startup script before test execution |
| Orphaned containers | Docker resources leak between runs | Add `--abort-on-container-exit --remove-orphans` flags; implement cleanup in `afterAll` |

---

## Audit Log

- `[{timestamp}]` Integration testing skill invoked for `{service/module}`.
- `[{timestamp}]` Docker services started: `{list of containers}`.
- `[{timestamp}]` Test files generated/modified: `{file list}`.
- `[{timestamp}]` Test suite executed — **{passed}** passed, **{failed}** failed, **{skipped}** skipped.
- `[{timestamp}]` Container teardown completed — orphaned resources: `{none | list}`.
- `[{timestamp}]` Coverage delta: `{before}%` → `{after}%` for integration scope.
