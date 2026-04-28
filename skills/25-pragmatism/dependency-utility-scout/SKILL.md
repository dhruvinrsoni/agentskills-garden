---
name: dependency-utility-scout
description: >
  Mine the project's declared dependencies (BOM, package.json,
  requirements.txt, Pipfile, go.mod, Cargo.toml, etc.) and produce a
  curated inventory of the utilities they expose, so reuse-first and
  other Aparigraha skills can decide quickly without rediscovering the
  graph each time. Consults; never auto-rewrites.
license: Apache-2.0
compatibility: Designed for Claude Code and compatible AI agent environments
metadata:
  version: "1.0.0"
  dependencies: "constitution, scratchpad, pragmatism"
  reasoning_mode: plan-execute
---


# Dependency Utility Scout

> _"You almost certainly already imported what you need. Find it before
> you write it."_

## Context

Invoked the first time a project's dependency graph needs to be turned
into something the agent can search efficiently — and then on demand
afterwards. It builds a **utility inventory** keyed by capability (e.g.,
`string.normalize`, `collections.dedupe`, `date.diff`) so that
`reuse-first` and other Aparigraha skills can answer "is this already in
our dependency graph?" in O(1) lookups instead of re-searching the world.

The scout is strictly **advisory**. It does not edit code, does not
auto-rewrite existing call sites to use newly discovered utilities, and
does not introduce new dependencies. It surfaces leverage; the agent and
the user decide what to do with it.

## Scope

**In scope:**

- Reading dependency manifests across the project's primary languages.
- Resolving dependency versions and producing a flattened list of direct
  + transitive deps (when required).
- Curating utilities exposed by *known leverage libraries* (Apache
  Commons, Lodash, Guava, etc.) into a per-capability index.
- Caching the inventory for the session, with invalidation on manifest
  change.
- Producing a leverage report on request.

**Out of scope:**

- Deciding whether to reuse — owned by `reuse-first`.
- Adding or removing dependencies — owned by `dependency-updates`.
- Vulnerability/CVE assessment — owned by `dependency-scanning`.
- License compliance — owned by project policy (escalate via `pragya`).
- Auto-rewriting existing code to use a newly discovered helper. Forbidden
  by Aparigraha; out of scope for this skill.

---

## Micro-Skills

### 1. Manifest Discovery 🌿 (Eco Mode)

**Goal:** Locate every dependency manifest in the project.

**Steps:**

1. Glob the repo (excluding `node_modules/`, `vendor/`, `.git/`,
   `target/`, `build/`, `dist/`) for known manifest patterns:

| Ecosystem      | Manifest patterns                                                |
|----------------|------------------------------------------------------------------|
| Java / JVM     | `pom.xml`, `build.gradle`, `build.gradle.kts`, `*.bom`           |
| JavaScript / TS| `package.json`, `pnpm-workspace.yaml`, `lerna.json`              |
| Python         | `requirements*.txt`, `Pipfile`, `pyproject.toml`, `setup.py`     |
| Go             | `go.mod`                                                         |
| Rust           | `Cargo.toml`                                                     |
| .NET           | `*.csproj`, `Directory.Packages.props`, `packages.config`        |
| Ruby           | `Gemfile`                                                        |
| PHP            | `composer.json`                                                  |

2. Record each manifest's path and ecosystem.
3. If multiple manifests exist (monorepo), keep them per-module; the
   inventory is keyed by module path.

### 2. Dependency Resolution ⚡ (Power Mode)

**Goal:** Resolve direct + transitive dependencies and their versions.

**Steps:**

1. **Nano: Direct First** — parse the manifest for *declared* deps only.
   This is enough for the common case.
2. **Nano: Transitive on Demand** — if `reuse-first` asks for a
   transitively-available utility, fall back to the package manager:

| Ecosystem | Command                                  |
|-----------|------------------------------------------|
| Maven     | `mvn dependency:list -DoutputFile=...`   |
| Gradle    | `gradle dependencies --configuration ...`|
| npm       | `npm ls --all --json`                    |
| pnpm      | `pnpm list --recursive --json`           |
| pip       | `pip list --format=json`                 |
| Go        | `go list -m all`                         |
| Cargo     | `cargo metadata --format-version 1`      |
| .NET      | `dotnet list package --include-transitive`|

3. Record `{ecosystem, name, version, declared_or_transitive, manifest_path}`.

### 3. Capability Indexing ⚡ (Power Mode)

**Goal:** Curate a per-capability index of utilities exposed by libraries
the project already depends on.

The scout ships a **leverage knowledge base** — a hand-curated mapping
from `library@version → capabilities → functions` for the most common
high-leverage libraries. This avoids spawning a JVM/Node/Python
introspector for every lookup.

**Curated baseline (extend over time):**

| Library                          | Example capability buckets                                                |
|----------------------------------|---------------------------------------------------------------------------|
| `commons-lang3`                  | `string.normalize`, `string.compare`, `string.escape`, `lang.equals`      |
| `commons-collections4`           | `collection.dedupe`, `collection.intersect`, `multimap`, `bidi-map`       |
| `commons-io`                     | `io.read`, `io.copy`, `io.path`, `file.compare`                           |
| `guava`                          | `cache`, `collection.immutable`, `eventbus`, `string.splitter`            |
| `jackson-databind`               | `json.parse`, `json.serialize`, `json.tree`                               |
| `lodash`                         | `array.dedupe`, `array.chunk`, `object.merge`, `function.debounce`        |
| `date-fns`                       | `date.parse`, `date.diff`, `date.format`, `date.tz`                       |
| `ramda`                          | `fp.compose`, `fp.curry`, `collection.lens`                               |
| Python `more-itertools`          | `iter.chunked`, `iter.unique_everseen`, `iter.windowed`                   |
| Python `toolz`                   | `fp.compose`, `fp.curry`, `dict.merge_with`                               |
| Python stdlib                    | `itertools`, `functools`, `collections`, `decimal`, `pathlib`             |
| Go `samber/lo`                   | `slice.uniq`, `slice.chunk`, `map.entries`, `parallel.foreach`            |
| Go `golang.org/x/exp/slices`     | `slices.IndexFunc`, `slices.SortFunc`, `slices.BinarySearch`              |
| .NET `System.Linq`               | `Enumerable.Distinct`, `Enumerable.GroupBy`, `Enumerable.Aggregate`       |
| .NET `MoreLinq`                  | `Batch`, `Pairwise`, `Lag`/`Lead`, `OrderBy`/`ThenBy`                     |

**Steps:**

1. Cross the resolved dependency list with the leverage knowledge base.
2. For each match, instantiate `{library, version, capability, function,
   javadoc/url}` entries.
3. For libraries NOT in the curated knowledge base but present in the
   project, mark them as `unindexed` and queue them for on-demand
   inspection (micro-skill 4) when `reuse-first` asks about them.

### 4. On-Demand Library Inspection 🌿 (Eco Mode)

**Goal:** When `reuse-first` asks about a capability that might live in
an `unindexed` library, inspect on demand.

**Steps:**

1. Use the language's lightweight introspection:

| Ecosystem  | Lightweight introspection                                                        |
|------------|----------------------------------------------------------------------------------|
| Java       | Read the JAR's `Manifest`, look up the artifact's online javadoc.                |
| JS / TS    | `npm view <pkg> exports`, read the package's `index.d.ts`.                       |
| Python     | `python -c "import X; print(dir(X))"` then `help(X.fn)`.                         |
| Go         | `go doc <pkg>`.                                                                  |
| .NET       | Read the NuGet package's XML doc or use `dotnet list`.                           |

2. Extract the public surface relevant to the requested capability.
3. Add the entries to the inventory as `{ecosystem, library, version,
   capability, function, signature, source}`.
4. Cache for the session; do not re-introspect on subsequent queries.

### 5. Leverage Report 🌿 (Eco Mode)

**Goal:** Surface "what's available that the team may not be using" —
without auto-rewriting.

**Steps:**

1. Cross the inventory with the project source: which curated capabilities
   are declared in dependencies but not used anywhere in source?
2. Produce a Markdown report grouped by capability bucket, not by library
   — that's what readers care about ("how do I dedupe?" beats "what does
   Lodash export?").
3. Mark each item:
   - `available, unused` — leverage opportunity.
   - `available, in use` — already leveraged.
   - `available, niche` — present but unlikely to apply often.
4. Save the report (when requested) at
   `docs/dependency-leverage-report.md` — never silently committed; the
   user opts in.

### 6. Inventory Cache & Invalidation 🌿 (Eco Mode)

**Goal:** Avoid re-resolving dependencies on every query.

**Steps:**

1. Compute a cache key from `{manifest_paths_hash, manifest_mtimes}`.
2. Store the inventory in agent-session memory keyed by the cache key.
3. Invalidate when any manifest changes (mtime / hash mismatch).
4. Persist the inventory to a session-scoped temporary file when the
   inventory is large enough to be worth the IO; never commit it.

---

## Inputs

| Parameter            | Type       | Required | Description                                                            |
|----------------------|------------|----------|------------------------------------------------------------------------|
| `repo_root`          | `string`   | yes      | Absolute path to the repository root.                                  |
| `query_capability`   | `string`   | no       | If set, return only entries matching this capability bucket.           |
| `include_transitive` | `boolean`  | no       | Whether to resolve transitive deps. Default: `false`.                  |
| `produce_report`     | `boolean`  | no       | Whether to emit the human-readable leverage report. Default: `false`.  |

## Outputs

| Field             | Type       | Description                                                              |
|-------------------|------------|--------------------------------------------------------------------------|
| `manifests`       | `object[]` | Discovered manifests with ecosystem and path.                            |
| `dependencies`    | `object[]` | `{ecosystem, name, version, declared_or_transitive, manifest_path}`      |
| `inventory`       | `object[]` | `{library, version, capability, function, signature, source}`            |
| `unindexed_libs`  | `string[]` | Libraries present in the project but not in the curated KB.              |
| `report_path`     | `string`   | Path to the generated leverage report (only if `produce_report=true`).   |

---

## Guardrails

- **No code edits.** This skill never modifies source files. It does not
  auto-rewrite call sites to use a newly discovered utility — that
  decision belongs to `reuse-first` (per call site) under user control.
- **No new dependencies.** Adding a library is `dependency-updates`'
  job. The scout only inventories what the project already imports.
- **No security claims.** The scout is not a vulnerability scanner. CVE
  / supply-chain checks belong to `dependency-scanning`.
- **No license claims.** Defer license compatibility decisions to project
  policy.
- **Deterministic output.** Same manifests + same KB = same inventory.
  Report ordering is stable (alphabetical within capability buckets).
- **Do not silently commit reports.** The leverage report is opt-in,
  written only when `produce_report=true` and the user has accepted.

## Ask-When-Ambiguous

**Triggers:**

- Multiple manifests exist with conflicting versions of the same library
  (monorepo skew).
- A declared dependency has no version pin.
- The user is on a corporate JFrog/Nexus mirror and online docs aren't
  reachable for on-demand inspection.
- The leverage report would be very large (> 50 unused capabilities) —
  user may want it filtered.

**Question Templates:**

- "I found `[lib]` declared at version `[A]` in `[manifest1]` and `[B]`
  in `[manifest2]`. Which version should the inventory reflect?"
- "The leverage report would surface `[N]` unused capabilities across
  `[M]` libraries. Want the full report, or filtered to capabilities
  used by code I'm about to touch?"
- "On-demand inspection requires reaching `[npm/pypi/maven]`. Is that
  permitted from this environment, or should I rely on the curated KB
  only?"

## Decision Criteria

| Situation                                                              | Action                                                                  |
|------------------------------------------------------------------------|-------------------------------------------------------------------------|
| Curated KB has the capability                                          | Return inventory entry; no introspection needed.                        |
| Library present, capability not in KB                                  | Mark `unindexed`; introspect on demand.                                 |
| Capability in multiple libraries already imported                      | Return all; let `reuse-first` choose by usage prevalence in the repo.   |
| Capability not in any current dependency                               | Return empty; do NOT propose adding a library.                          |
| Manifest changed since last cache                                      | Invalidate, re-resolve.                                                 |
| User asks for a leverage report                                        | Produce; never auto-write to a tracked path without confirmation.       |

## Success Criteria

- Inventory entries have stable, deterministic shape and ordering.
- `reuse-first` can answer "is `[capability]` available?" in a single
  lookup against the cached inventory.
- No source files are modified by this skill.
- The leverage report (when produced) is human-readable and grouped by
  capability bucket, not by library.

## Failure Modes

- **Stale inventory.** Manifest changed but cache wasn't invalidated.
  **Recovery:** Re-run manifest-discovery; recompute the cache key.

- **Curated KB drift.** A library's API changed in a major version and
  the KB still points at the old surface.
  **Recovery:** When inventory entries reference functions that
  introspection can't confirm, mark them `kb-stale` and prefer
  on-demand inspection. Open a follow-up to update the KB.

- **Monorepo version skew.** Two modules pin different versions of the
  same library; the inventory conflates them.
  **Recovery:** Key inventory by manifest path. Surface the skew to the
  user via Ask-When-Ambiguous.

- **Network-restricted environments.** On-demand inspection can't reach
  upstream registries.
  **Recovery:** Fall back to whatever metadata is local (extracted
  jars, `node_modules/*/package.json`, installed `site-packages/`).
  Mark uncovered capabilities as `unconfirmed` and let `reuse-first`
  decide whether to ask the user.

- **Inventory becomes too large to keep hot.** Memory pressure or noisy
  reports.
  **Recovery:** Persist to a temp file scoped to the session; lazy-load
  on query. Filter reports by capability buckets the agent is actively
  touching.

## Audit Log

```
[scout-engaged]            repo_root="{path}"
[manifests-discovered]     count={N} ecosystems={list}
[dependencies-resolved]    direct={N} transitive={N|skipped}
[inventory-built]          entries={N} unindexed_libs={list}
[on-demand-inspected]      library="{lib}" capability="{cap}" entries_added={N}
[report-emitted]           path="{report_path}" buckets={N} unused={N}
[cache-invalidated]        reason="{manifest_change|user_request}"
```

---

## Examples

### Example 1 — Java service, Apache Commons Lang already imported

**Input:**

```
repo_root = /work/payments-service
query_capability = "string.normalize"
```

**Inventory hit:**

```yaml
- library: org.apache.commons:commons-lang3
  version: "3.13.0"
  capability: string.normalize
  function: StringUtils.normalizeSpace(String)
  signature: "static String normalizeSpace(String str)"
  source: "https://commons.apache.org/proper/commons-lang/javadocs/api-release/org/apache/commons/lang3/StringUtils.html#normalizeSpace-java.lang.String-"

- library: org.apache.commons:commons-lang3
  version: "3.13.0"
  capability: string.normalize
  function: StringUtils.stripAccents(String)
  signature: "static String stripAccents(String input)"
  source: "https://commons.apache.org/proper/commons-lang/javadocs/api-release/org/apache/commons/lang3/StringUtils.html#stripAccents-java.lang.String-"
```

`reuse-first` consumes this and continues with edge-case validation.

### Example 2 — Node service, leverage report

**Input:**

```
repo_root = /work/billing-web
produce_report = true
```

**Excerpt of `docs/dependency-leverage-report.md`:**

```markdown
## array.dedupe

| Status              | Provider                  | Function                          |
|---------------------|---------------------------|-----------------------------------|
| available, in use   | lodash@4.17.21            | _.uniqBy(arr, key)                |
| available, unused   | lodash@4.17.21            | _.uniqWith(arr, comparator)       |
| available, unused   | ramda@0.29.1              | R.uniq, R.uniqBy, R.uniqWith      |

## function.debounce

| Status              | Provider                  | Function                          |
|---------------------|---------------------------|-----------------------------------|
| available, unused   | lodash@4.17.21            | _.debounce(fn, wait, options)     |
| available, unused   | lodash@4.17.21            | _.throttle(fn, wait, options)     |
```

The report is informational. Nothing in the source is rewritten. The user
can take it as input to a separate, scoped refactor request.

### Example 3 — Python project, on-demand inspection

**Input:**

```
repo_root = /work/etl-pipeline
query_capability = "iter.windowed"
```

The curated KB knows `more-itertools.windowed` is in `more-itertools`.
`pyproject.toml` does NOT list `more-itertools`, but does list `toolz`.
The scout introspects `toolz`:

```text
[on-demand-inspected] library="toolz" capability="iter.windowed"
  entries_added=1: toolz.itertoolz.sliding_window(n, seq)
```

`reuse-first` can now consider `toolz.itertoolz.sliding_window` instead
of suggesting a new dependency.

---

## Edge Cases

- **No manifests at all.** Project is a script-only repo or pre-build
  artifact. The scout returns an empty inventory and tells `reuse-first`
  the project has no declared leverage to mine.

- **Vendored / committed dependencies (`vendor/`, `node_modules/`
  in-tree).** Treat them as the source of truth over the manifest if
  versions disagree; surface the divergence to the user.

- **Private / internal libraries.** The curated KB won't know them. They
  flow through the on-demand inspection path. If introspection isn't
  possible, mark them `unindexed` and let `reuse-first` decide whether
  to ask the user about them.

- **Polyglot monorepos.** Run manifest discovery once at the root, then
  group inventory entries by module path so cross-module conclusions
  don't accidentally apply.

- **Build-only / dev-only dependencies.** Tag entries with their scope
  (`compile`, `runtime`, `dev`, `peer`, `test`). `reuse-first` should
  not propose using a `dev` dependency in production code.

- **Dependency listed but not actually on the runtime classpath**
  (e.g., a Maven `provided` scope or a Gradle `compileOnly`). Surface
  this in the inventory entry so the agent doesn't mistakenly reuse
  something that won't be there at runtime.

- **The user asks for the inventory in a non-Java/JS/Python ecosystem
  the curated KB doesn't cover deeply.** Return the resolved
  dependency list with `unindexed` flags; rely on on-demand inspection.
  Open a follow-up to extend the curated KB for that ecosystem.
