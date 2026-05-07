"""Tag taxonomy — Python mirror of docs/tags.md.

Single source of truth for the closed vocabularies used to validate
registry.yaml entries. Every tag must classify into exactly one axis
(scope, lifecycle, capability, domain, risk); tags that do not fit any
axis are validation errors.

Keep this file in sync with docs/tags.md. If you add a tag here, add
the corresponding row in docs/tags.md (and vice versa).
"""

from typing import Dict, FrozenSet, Optional, Tuple


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


# Axis 4 — domain: where in the stack the skill applies. Optional.
DOMAIN_TAGS: FrozenSet[str] = frozenset({
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
    "domain":     DOMAIN_TAGS,
    "risk":       RISK_TAGS,
}


# Required axes per scope. Foundation (core) skills are cross-cutting and
# may omit lifecycle per docs/tags.md axis-2 note. Domain is always
# optional (declared only when stack-specific).
REQUIRED_AXES_BY_SCOPE: Dict[str, Tuple[str, ...]] = {
    "core":     ("scope", "capability", "risk"),
    "category": ("scope", "lifecycle", "capability", "risk"),
    "master":   ("scope", "lifecycle", "capability", "risk"),
    "meta":     ("scope", "capability", "risk"),
}


# Hard cap per docs/tags.md authoring rule 3.
MAX_TAGS_PER_SKILL = 6


def classify(tag: str) -> Optional[str]:
    """Return the axis name a tag belongs to, or None if not in any axis."""
    for axis_name, vocab in AXES.items():
        if tag in vocab:
            return axis_name
    return None
