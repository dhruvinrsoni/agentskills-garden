# PowerShell script to create the Agent Skills Garden repository

# Create the directory structure
New-Item -ItemType Directory -Force -Path skills/00-foundation
New-Item -ItemType Directory -Force -Path skills/10-discovery
New-Item -ItemType Directory -Force -Path skills/20-architecture
New-Item -ItemType Directory -Force -Path skills/30-implementation
New-Item -ItemType Directory -Force -Path skills/40-quality
New-Item -ItemType Directory -Force -Path skills/50-performance
New-Item -ItemType Directory -Force -Path skills/60-security
New-Item -ItemType Directory -Force -Path skills/70-devops
New-Item -ItemType Directory -Force -Path skills/80-docs
New-Item -ItemType Directory -Force -Path skills/90-maintenance

# Create and populate SKILL.md files
$skills = @{
    "skills/00-foundation/constitution.md" = @"
---
title: "Constitution"
description: "The principles of Satya, Dharma, Ahimsa."
---

# Constitution

## Satya (Truth)
- Ensure deterministic execution.
- Avoid hallucinated APIs.

## Dharma (Right Action)
- "Ask-First" if ambiguous.
- Perform safety checks before destructive actions.

## Ahimsa (Non-Destruction)
- Always preview diffs.
- Never overwrite without version control.

## Cognitive Modes
- **Eco Mode:** Linear execution for low-risk tasks (formatting, docs).
- **Power Mode:** Plan-Execute-Verify loops for high-risk tasks (refactoring, security).
"@

    "skills/00-foundation/scratchpad.md" = @"
---
title: "Scratchpad"
description: "Instructions for 'Internal Monologue' (Eco vs. Power reasoning)."
---

# Scratchpad

## Internal Monologue
- Use Eco Mode for low-risk tasks.
- Use Power Mode for high-risk tasks.
"@

    "skills/00-foundation/auditor.md" = @"
---
title: "Auditor"
description: "Validates that other skills followed the Constitution."
---

# Auditor

## Purpose
- Ensure all skills adhere to the principles of Satya, Dharma, and Ahimsa.
"@

    "skills/00-foundation/librarian.md" = @"
---
title: "Librarian"
description: "Fuzzy search to find skills (e.g., 'fix bug' -> loads `refactoring.md` or `cleanup.md`)."
---

# Librarian

## Purpose
- Provide a search mechanism to locate relevant skills.
"@
}

foreach ($file in $skills.Keys) {
    $content = $skills[$file]
    $directory = Split-Path -Path $file -Parent
    if (!(Test-Path -Path $directory)) {
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
    }
    $content | Set-Content -Path $file -Encoding UTF8
}

# Create the registry.yaml file
$registryContent = @"
skills:
  - foundation:
      - constitution.md
      - scratchpad.md
      - auditor.md
      - librarian.md
  - discovery:
      - requirements-elicitation.md
      - domain-modeling.md
  - architecture:
      - adr-management.md
      - api-contract-design.md
      - database-design.md
      - system-design.md
  - implementation:
      - cleanup.md
      - api-implementation.md
      - data-access.md
      - refactoring-suite.md
      - error-handling.md
  - quality:
      - test-strategy.md
      - unit-testing.md
      - integration-testing.md
      - mutation-testing.md
  - performance:
      - profiling-analysis.md
      - caching-strategy.md
      - db-tuning.md
  - security:
      - threat-modeling.md
      - secure-coding-review.md
      - auth-implementation.md
      - dependency-scanning.md
  - devops:
      - ci-pipeline.md
      - docker-containerization.md
      - kubernetes-helm.md
      - terraform-iac.md
  - docs:
      - openapi-specs.md
      - readme-generation.md
      - release-notes.md
  - maintenance:
      - incident-response.md
      - legacy-upgrade.md
"@

$registryContent | Set-Content -Path skills/registry.yaml -Encoding UTF8

Write-Host "Skills directory and files have been created successfully."
