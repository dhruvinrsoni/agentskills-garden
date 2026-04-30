# Tag Taxonomy

Tags are how the [`librarian`](../skills/00-foundation/librarian/SKILL.md) routes a task to the right skill. Inconsistent tags mean missed matches; freeform tags mean noise. This page defines the **canonical taxonomy** every `SKILL.md` and every entry in [`registry.yaml`](../registry.yaml) must follow.

---

## The five axes

Every skill should carry **one tag from each axis that applies**. Total tags per skill: hard cap **6**.

| # | Axis | Question it answers | Required? |
|---|------|---------------------|-----------|
| 1 | **scope** | What kind of skill is this? | Yes — every skill |
| 2 | **lifecycle** | Which phase of the delivery flow does it belong to? | Yes — every skill |
| 3 | **capability** | What does it do? | Yes — every skill |
| 4 | **domain** | Where in the stack does it apply? | Only when domain-specific |
| 5 | **risk** | How costly is a wrong action? | Yes — every skill |

Pick the **smallest closed vocabulary** that lets the librarian find the skill. If you cannot map a tag onto one of these axes, drop it.

---

## Axis 1 — `scope`

What kind of skill this is, in the sense of the [four-level hierarchy](concepts.md#1-the-four-level-hierarchy).

| Tag | Meaning |
|-----|---------|
| `core` | Foundation skill — always loaded ([`00-foundation/`](../skills/00-foundation/)). |
| `category` | Standard skill — loaded on demand ([`10-` through `90-`](../skills/)). The default. |
| `master` | Master skill — orchestrates other skills, no implementation. |
| `meta` | About skills themselves (templates, taxonomy, generators). |

---

## Axis 2 — `lifecycle`

Which phase of the work the skill belongs to. The phases form a loop: `discovery → design → build → ship → operate → maintain → discovery …`

| Tag | What happens here | Categories typically here |
|-----|-------------------|--------------------------|
| `discovery` | Understand the problem before solving it. PRDs, brownfield-onboarding, requirement gathering, glossary. | `10-discovery`, `25-pragmatism/brownfield-onboarding` |
| `design` | Decide *how* before doing. ADRs, system design, architecture, planning, decomposition. | `20-architecture`, `20-planning` |
| `build` | Make the change. Implementation, refactoring, code generation. | `30-implementation` |
| `ship` | Get the change to production. Tests, review, security, performance, devops, release. | `40-quality`, `60-security`, `70-devops`, `80-collaboration/git-workflow` |
| `operate` | Keep it running. Observability, incident response, debugging, monitoring. | `30-debugging`, `70-devops/monitoring` |
| `maintain` | Keep it healthy over time. Upgrades, deprecations, tech-debt tracking, dependency updates, repo cleanup. | `90-maintenance` |

Cross-cutting skills (foundation, pragmatism) usually carry no `lifecycle` tag — they apply everywhere.

---

## Axis 3 — `capability`

What the skill *does*. Closed list — extend only by PR.

| Tag | Examples |
|-----|----------|
| `auditing` | `auditor` |
| `routing` | `librarian`, `orchestrator` |
| `reasoning` | `scratchpad`, `pragya` |
| `principles` | `constitution`, `pragmatism` |
| `efficiency` | `token-efficiency` |
| `requirements` | `prd`, `domain-glossary` |
| `planning` | `task-decomposition`, `risk-assessment`, `dependency-mapping`, `estimation` |
| `architecture` | `system-design`, `adr`, `api-spec`, `data-modeling` |
| `coding` | `api-implementation`, `data-access`, `code-generation`, `tdd-workflow` |
| `refactoring` | `refactoring`, `refactoring-suite`, `cleanup` |
| `resilience` | `resilience-patterns`, `error-handling` |
| `testing` | `unit-testing`, `integration-testing`, `mutation-testing`, `testing-strategy` |
| `review` | `code-review`, `pr-management` |
| `security` | `secure-coding-review`, `auth-patterns`, `dependency-scanning`, `threat-modelling` |
| `performance` | `caching-strategy`, `query-optimization`, `profiling`, `progressive-execution` |
| `docs` | `inline-documentation`, `api-docs`, `readme-authoring`, `changelog-generation`, `release-notes` |
| `collaboration` | `git-workflow`, `pr-management`, `pair-programming`, `knowledge-sharing` |
| `devops` | `ci-pipeline`, `docker-containerization`, `kubernetes-deployment`, `terraform-iac`, `monitoring-observability` |
| `debugging` | `root-cause-analysis`, `log-analysis` |
| `maintenance` | `repo-maintenance`, `tech-debt-tracking`, `dependency-updates`, `deprecation-strategy`, `legacy-modernization`, `version-migration` |
| `pragmatism` | every `25-pragmatism/*` skill carries this |
| `discovery` | `brownfield-onboarding`, glossary builders |

Aim for **one** capability tag per skill. Two only when the skill genuinely sits at the boundary (e.g. `pr-management` is `review` + `collaboration`).

---

## Axis 4 — `domain`

Where in the stack the skill applies. Most skills are stack-agnostic and carry **no domain tag**. Only add one when the skill genuinely cannot help outside that stack.

| Tag | When to use |
|-----|-------------|
| `backend` | Server-side-only patterns. |
| `frontend` | UI-only patterns. |
| `db` | Database, schema, query, migration patterns. |
| `infra` | Infra, IaC, container, cluster patterns. |
| `cross-cutting` | Explicitly applies to all stacks (only if useful as a search term). |

If you find yourself reaching for `cross-cutting`, you probably do not need a domain tag at all.

---

## Axis 5 — `risk`

The cost of a wrong action by the agent. Drives mode selection ([`Eco vs Power`](concepts.md#3-eco--and-power--tags-on-micro-skills)) and `auditor` strictness.

| Tag | Meaning | Examples |
|-----|---------|----------|
| `advisory` | Skill only emits suggestions; cannot break anything. | `dependency-utility-scout`, `style-conformance`, `tech-debt-tracking` |
| `reversible` | Changes things, but a single revert restores the previous state. | `cleanup`, `inline-documentation`, `formatting` skills |
| `irreversible` | Changes that are hard or impossible to undo without data loss or migration. | `data-modeling` migrations, `version-migration`, `deprecation-strategy` |
| `safety-critical` | Touches security, authentication, production, or release surface. | `auth-patterns`, `secure-coding-review`, `release-notes`, `kubernetes-deployment` |

If unsure, prefer the *higher* risk tag — the auditor will be stricter, which is the safe failure mode.

---

## Authoring rules

1. **Lowercase, hyphen-separated, ≤3 words.** `secure-coding-review` ✅. `Secure_Coding_Review` ✗. `secure-coding-review-process` ✗.
2. **No synonyms.** Pick one. `refactor` (not `refactoring`, not `refactor-skills`). `db` (not `database`, not `db-schema`).
3. **Max ~6 tags per skill.** If you need more, your skill is doing too much — split it.
4. **One per axis.** Two in the same axis means the axis is wrong or the skill should be split.
5. **No "decorative" tags.** Every tag must serve discovery. `important`, `useful`, `recommended` ≠ tags.
6. **Closed vocabulary.** New tags are added by PR to this file before being used. The `librarian` only knows what is documented here.

---

## Worked examples

```yaml
# Foundation skill, cross-cutting
- name: pragmatism
  tags: [core, principles, pragmatism, advisory]
  # axes covered: scope=core, capability=principles+pragmatism, risk=advisory
  # lifecycle: cross-cutting → omitted; domain: cross-cutting → omitted

# Category skill in 30-implementation, build phase
- name: refactoring
  tags: [category, build, refactoring, reversible]
  # axes covered: scope=category, lifecycle=build, capability=refactoring, risk=reversible
  # domain: stack-agnostic → omitted

# Category skill in 70-devops, ship phase, infra-specific, dangerous
- name: kubernetes-deployment
  tags: [category, ship, devops, infra, safety-critical]
  # all five axes used

# Master skill (planned)
- name: release-pipeline
  tags: [master, ship, devops, irreversible]
```

---

## See also

- [`registry.yaml`](../registry.yaml) — where these tags actually live.
- [`docs/concepts.md`](concepts.md) — what the four-level hierarchy and Eco/Power modes mean.
- [`skills/00-foundation/librarian/SKILL.md`](../skills/00-foundation/librarian/SKILL.md) — how tags are consumed.
