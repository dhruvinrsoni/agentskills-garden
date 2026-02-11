---
title: "Auditor"
description: "Validates that other skills followed the Constitution."
---

# Auditor

## Purpose
- Ensure all skills adhere to the principles of Satya, Dharma, and Ahimsa.
EOF

cat << 'EOF' > skills/00-foundation/librarian.md
---
title: "Librarian"
description: "Fuzzy search to find skills (e.g., 'fix bug' -> loads `refactoring.md` or `cleanup.md`)."
---

# Librarian

## Purpose
- Provide a search mechanism to locate relevant skills.
EOF

# Repeat similar blocks for all other SKILL.md files in the Skill Manifest

# Create the registry.yaml file
cat << 'EOF' > skills/registry.yaml
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
EOF

# Print completion message
echo "Skills directory and files have been created successfully."
