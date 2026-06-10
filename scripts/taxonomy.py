"""Tag taxonomy — Python mirror of docs/tags.md.

Single source of truth for the closed vocabularies used to validate
SKILL.md frontmatter. Every tag must classify into exactly one axis
(scope, lifecycle, capability, stack, risk); tags that do not fit any
axis are validation errors.

Note on naming: axis 4 is `stack` (backend/frontend/db/infra) — *where in
the stack* a skill applies. It used to be called `domain`, but `domain`
is now the top-level namespace dimension (foundation/engineering/writing/…,
see REGISTERED_DOMAINS) carried as a first-class frontmatter field, so the
stack axis was renamed to avoid the collision.

Keep this file in sync with docs/tags.md. If you add a tag here, add
the corresponding row in docs/tags.md (and vice versa).
"""

from typing import Dict, FrozenSet, List, Optional, Tuple


# Axis 1 — scope: what kind of skill this is.
SCOPE_TAGS: FrozenSet[str] = frozenset({
    "core",
    "category",
    "master",
    "meta",
})


# Axis 2 — lifecycle: which delivery phase the skill belongs to.
LIFECYCLE_TAGS: FrozenSet[str] = frozenset({
    "discovery",
    "design",
    "build",
    "ship",
    "operate",
    "maintain",
})


# Axis 3 — capability: what the skill does. Closed list; extend by PR.
CAPABILITY_TAGS: FrozenSet[str] = frozenset({
    "auditing",
    "routing",
    "reasoning",
    "principles",
    "efficiency",
    "requirements",
    "planning",
    "architecture",
    "coding",
    "refactoring",
    "resilience",
    "testing",
    "review",
    "security",
    "performance",
    "docs",
    "collaboration",
    "devops",
    "debugging",
    "maintenance",
    "pragmatism",
    # Note: docs/tags.md lists `discovery` in both lifecycle and capability
    # axes. Actual registry.yaml usage is consistently lifecycle (paired
    # with another capability tag), so we keep `discovery` only in the
    # lifecycle axis here to avoid ambiguous classification.
})


# Axis 4 — stack: where in the stack the skill applies. Optional.
# (Formerly named `domain`; renamed to free that word for the top-level
# namespace dimension — see REGISTERED_DOMAINS below.)
STACK_TAGS: FrozenSet[str] = frozenset({
    "backend",
    "frontend",
    "db",
    "infra",
    "cross-cutting",
})


# Axis 5 — risk: cost of a wrong action.
RISK_TAGS: FrozenSet[str] = frozenset({
    "advisory",
    "reversible",
    "irreversible",
    "safety-critical",
})


AXES: Dict[str, FrozenSet[str]] = {
    "scope":      SCOPE_TAGS,
    "lifecycle":  LIFECYCLE_TAGS,
    "capability": CAPABILITY_TAGS,
    "stack":      STACK_TAGS,
    "risk":       RISK_TAGS,
}


# Required axes per scope. Foundation (core) skills are cross-cutting and
# may omit lifecycle per docs/tags.md axis-2 note. Stack is always
# optional (declared only when stack-specific).
REQUIRED_AXES_BY_SCOPE: Dict[str, Tuple[str, ...]] = {
    "core":     ("scope", "capability", "risk"),
    "category": ("scope", "lifecycle", "capability", "risk"),
    "master":   ("scope", "lifecycle", "capability", "risk"),
    "meta":     ("scope", "capability", "risk"),
}


# Hard cap per docs/tags.md authoring rule 3.
MAX_TAGS_PER_SKILL = 6


# ---------------------------------------------------------------------------
# Domain namespaces — the top-level dimension above the lifecycle phases.
#
# A skill lives under skills/<prefix>-<domain>/...  e.g. skills/100-engineering/.
# Unlike the tag axes (closed vocabularies), this list is meant to GROW: add a
# domain by adding one entry here and creating the matching numbered folder.
# It is still an allowlist so typos in frontmatter `domain:` fail validation.
#
# Maps domain slug -> numeric folder prefix. Foundation (000) is the universal,
# cross-cutting domain (constitution, librarian, auditor, ...); it is flat (no
# lifecycle-phase sub-level). All other domains group skills by phase inside.
# ---------------------------------------------------------------------------
REGISTERED_DOMAINS: Dict[str, str] = {
    "foundation":  "000",
    "engineering": "100",
    "writing":     "200",
    "data-ml":     "300",
    "business":    "400",
}

# The one domain that is flat (no NN-phase level beneath it).
FLAT_DOMAINS: FrozenSet[str] = frozenset({"foundation"})


def classify(tag: str) -> Optional[str]:
    """Return the axis name a tag belongs to, or None if not in any axis."""
    for axis_name, vocab in AXES.items():
        if tag in vocab:
            return axis_name
    return None


def domain_folder(domain: str) -> Optional[str]:
    """Return the numbered folder name for a domain, e.g. 'engineering' ->
    '100-engineering'. None if the domain is not registered."""
    prefix = REGISTERED_DOMAINS.get(domain)
    return f"{prefix}-{domain}" if prefix else None


def validate_domain(value: object) -> List[str]:
    """Validate a frontmatter `domain` value against the registered allowlist."""
    if value is None:
        return ["domain missing (every skill must declare a top-level domain)"]
    if not isinstance(value, str) or not value.strip():
        return ["domain must be a non-empty string"]
    if value not in REGISTERED_DOMAINS:
        return [
            f"unknown domain {value!r} (registered: {sorted(REGISTERED_DOMAINS)}; "
            "add it to REGISTERED_DOMAINS + docs/tags.md to extend)"
        ]
    return []


def validate_category(domain: str, category: str, known_categories: FrozenSet[str]) -> List[str]:
    """Validate a category against the set of categories that actually exist on
    disk for this domain. Open vocabulary: any folder that exists is valid, so
    adding a category needs no code change — but a typo'd category that maps to
    no folder is caught."""
    if domain in FLAT_DOMAINS:
        return []  # flat domains have no category level
    if category and known_categories and category not in known_categories:
        return [
            f"category {category!r} has no matching folder under domain {domain!r} "
            f"(known: {sorted(known_categories)})"
        ]
    return []
