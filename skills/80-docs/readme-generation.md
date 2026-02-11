---
name: readme-generation
description: >
  Create comprehensive README files with installation instructions,
  usage examples, API reference, and contribution guidelines.
version: "1.0.0"
dependencies:
  - constitution
  - scratchpad
reasoning_mode: linear
---

# README Generation

> _"If the README doesn't explain it, it doesn't exist to newcomers."_

## Context

Invoked when a project needs a README, or when the existing README is
outdated. A good README is the most impactful documentation a project has.

---

## Micro-Skills

### 1. README Structure 🌿 (Eco Mode)

**Steps:**

1. Generate the standard README sections:
   - **Title + Badges** (build status, coverage, version, license).
   - **Description** (what, why, for whom — 2-3 sentences).
   - **Quick Start** (clone, install, run — under 5 commands).
   - **Installation** (prerequisites, step-by-step).
   - **Usage** (code examples for common use cases).
   - **API Reference** (link to OpenAPI spec or inline).
   - **Architecture** (link to system design docs or brief overview).
   - **Contributing** (how to set up dev environment, run tests, PR process).
   - **License** (SPDX identifier and link).

### 2. Badge Generation 🌿 (Eco Mode)

**Steps:**

1. Detect CI platform and add build status badge.
2. Add coverage badge (Codecov, Coveralls).
3. Add version badge (npm, PyPI, Go).
4. Add license badge.
5. Format as a single line of shields.io badges.

### 3. Example Generation 🌿 (Eco Mode)

**Steps:**

1. Identify the top 3 use cases from the codebase.
2. Write minimal code examples that are copy-paste ready.
3. Include expected output for each example.
4. Test that examples actually work (no broken code in docs).

---

## Outputs

| Field           | Type     | Description                              |
|-----------------|----------|------------------------------------------|
| `readme`        | `string` | Generated README.md content              |
| `badges`        | `string` | Badge markdown                           |
