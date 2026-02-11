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
