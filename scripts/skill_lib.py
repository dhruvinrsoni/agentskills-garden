"""skill_lib.py — shared skill parsing + validation for the Skill Garden.

Single source of truth used by BOTH validate.py and build.py so
the validator and the build agree on what a valid skill is. Holds:

  * frontmatter parsing (split_frontmatter / parse_frontmatter)
  * the skills/ tree walk + path -> (domain, category) derivation
  * field validators (name, description, license, tags, v2 fields)
  * the frontmatter v2 schema (adds domain / keywords / status to the
    pre-existing name / description / license / metadata fields)

Frontmatter is the single source of truth for skill metadata. `tags` (the
five-axis vocabulary) moved out of registry.yaml into frontmatter; registry
is now a GENERATED artifact, not the source.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, FrozenSet, List, Optional, Tuple

import yaml

from taxonomy import (
    AXES,
    REQUIRED_AXES_BY_SCOPE,
    MAX_TAGS_PER_SKILL,
    FLAT_DOMAINS,
    classify,
    validate_domain,
    validate_category,
)

# ---------------------------------------------------------------------------
# Schema constants
# ---------------------------------------------------------------------------

# Base fields required of every skill (pre-existing spec).
REQUIRED_FRONTMATTER: FrozenSet[str] = frozenset({"name", "description", "license"})

# Additional fields required once a skill is on the v2 schema (--strict).
REQUIRED_FRONTMATTER_V2: FrozenSet[str] = frozenset({"domain", "keywords", "status", "tags"})

REQUIRED_LICENSE = "Apache-2.0"

# name: lowercase alphanumeric + hyphens, no leading/trailing/consecutive hyphens
NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")

ALLOWED_REASONING_MODES: FrozenSet[str] = frozenset(
    {"linear", "plan-execute", "tdd", "mixed"}
)
VALID_SKILL_TYPES: FrozenSet[str] = frozenset({"standard", "master"})

# status drives the promotion flow + public-index visibility.
#   draft     — local WIP, never public
#   ready     — finalized, the signal promotion looks for
#   published — lives in the garden, appears in public index
#   deprecated— indexed but flagged, excluded from default search
#   promoted  — source marker set by promote-skills.ps1 after a successful push
VALID_STATUSES: FrozenSet[str] = frozenset(
    {"draft", "ready", "published", "deprecated", "promoted"}
)

MAX_KEYWORDS = 12

SKILL_FILE = "SKILL.md"
# Directory names under skills/ that are not skills.
_NON_SKILL_DIRS: FrozenSet[str] = frozenset({"_index", "legacy", "__pycache__"})


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def split_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Return (frontmatter_dict, body). Empty dict if absent/malformed."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    try:
        fm = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    return fm, body


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str, List[str]]:
    """Like split_frontmatter but also returns a list of structural errors."""
    if not text.startswith("---"):
        return {}, text, ["missing opening '---' frontmatter delimiter"]
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text, ["missing closing '---' frontmatter delimiter"]
    raw = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    try:
        fm = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        return {}, body, [f"YAML parse error in frontmatter: {exc}"]
    if not isinstance(fm, dict):
        return {}, body, ["frontmatter must be a YAML mapping"]
    return fm, body, []


# ---------------------------------------------------------------------------
# Path -> taxonomy derivation
# ---------------------------------------------------------------------------

def strip_num_prefix(folder: str) -> str:
    """'100-engineering' -> 'engineering'; '30-implementation' -> 'implementation';
    'data-ml' (no numeric head) -> 'data-ml'."""
    head, sep, tail = folder.partition("-")
    if sep and head.isdigit():
        return tail
    return folder


def derive_taxonomy(rel_parts: List[str]) -> Tuple[str, Optional[str], Optional[str]]:
    """Given the path parts *below* skills/ for a SKILL.md, return
    (domain, category_dir, category). category_* are None for flat domains.

    rel_parts examples (excluding the trailing 'SKILL.md'):
      ['000-foundation', 'constitution']                  -> ('foundation', None, None)
      ['100-engineering', '30-implementation', 'cleanup']  -> ('engineering', '30-implementation', 'implementation')
    """
    domain = strip_num_prefix(rel_parts[0]) if rel_parts else ""
    if domain in FLAT_DOMAINS or len(rel_parts) < 3:
        return domain, None, None
    category_dir = rel_parts[1]
    return domain, category_dir, strip_num_prefix(category_dir)


def walk_skills(skills_dir: str) -> List[Dict[str, Any]]:
    """Walk skills/ and return one record per SKILL.md. Frontmatter-driven
    discovery — no registry needed. Each record:
      { abs_path, rel_path (posix, from repo root), dir_name,
        domain, category_dir, category, fm, body, parse_errors }
    Sorted by (domain folder, category_dir, name) for stable output.
    """
    repo_root = os.path.abspath(os.path.join(skills_dir, ".."))
    records: List[Dict[str, Any]] = []
    for root, dirs, files in os.walk(skills_dir):
        # prune non-skill dirs in place
        dirs[:] = [d for d in dirs if d not in _NON_SKILL_DIRS]
        if SKILL_FILE not in files:
            continue
        abs_path = os.path.join(root, SKILL_FILE)
        rel = os.path.relpath(abs_path, repo_root).replace(os.sep, "/")
        below = os.path.relpath(abs_path, skills_dir).replace(os.sep, "/").split("/")
        rel_parts = below[:-1]  # drop trailing SKILL.md
        domain, category_dir, category = derive_taxonomy(rel_parts)
        with open(abs_path, "r", encoding="utf-8") as fh:
            text = fh.read()
        fm, body, perrs = parse_frontmatter(text)
        records.append({
            "abs_path": abs_path,
            "rel_path": rel,
            "dir_name": rel_parts[-1] if rel_parts else "",
            "domain": domain,
            "category_dir": category_dir,
            "category": category,
            "fm": fm,
            "body": body,
            "parse_errors": perrs,
        })
    records.sort(key=lambda r: (
        rel_parts_sort_key(r["rel_path"]),
        str(r["fm"].get("name", r["dir_name"])),
    ))
    return records


def rel_parts_sort_key(rel_path: str) -> Tuple[str, ...]:
    return tuple(rel_path.split("/"))


def known_categories_for(records: List[Dict[str, Any]], domain: str) -> FrozenSet[str]:
    return frozenset(
        r["category"] for r in records
        if r["domain"] == domain and r["category"]
    )


# ---------------------------------------------------------------------------
# Field validators (pure)
# ---------------------------------------------------------------------------

def validate_name(name: object) -> List[str]:
    if not isinstance(name, str) or not name:
        return ["name must be a non-empty string"]
    errors: List[str] = []
    if len(name) > 64:
        errors.append(f"name exceeds 64 characters ({len(name)} chars)")
    if "--" in name:
        errors.append("name must not contain consecutive hyphens (--)")
    if not NAME_RE.match(name):
        errors.append(
            f"name {name!r} is invalid: only lowercase alphanumeric and hyphens "
            "allowed, must not start or end with a hyphen"
        )
    return errors


def validate_description(desc: object) -> List[str]:
    if isinstance(desc, str):
        desc = desc.strip()
    if not desc:
        return ["description must be non-empty"]
    if isinstance(desc, str) and len(desc) > 1024:
        return [f"description exceeds 1024 characters ({len(desc)} chars)"]
    return []


def validate_license(value: object) -> List[str]:
    if value is not None and value != REQUIRED_LICENSE:
        return [f"license must be {REQUIRED_LICENSE!r}, got {value!r}"]
    return []


def validate_keywords(value: object) -> List[str]:
    if value is None:
        return ["keywords missing (use [] if none yet)"]
    if not isinstance(value, list):
        return [f"keywords must be a YAML list, got {type(value).__name__}"]
    errors: List[str] = []
    if len(value) > MAX_KEYWORDS:
        errors.append(f"keywords exceed cap of {MAX_KEYWORDS} (got {len(value)})")
    for kw in value:
        if not isinstance(kw, str) or not kw.strip():
            errors.append(f"keyword {kw!r} must be a non-empty string")
    return errors


def validate_status(value: object) -> List[str]:
    if value is None:
        return ["status missing (one of: " + ", ".join(sorted(VALID_STATUSES)) + ")"]
    if str(value) not in VALID_STATUSES:
        return [f"status {value!r} invalid; allowed: {sorted(VALID_STATUSES)}"]
    return []


def validate_tags(tags: object) -> List[str]:
    """Validate a five-axis tag list. See docs/tags.md / taxonomy.py."""
    if tags is None:
        return ["tags missing (every skill must declare tags per docs/tags.md)"]
    if not isinstance(tags, list):
        return [f"tags must be a YAML list, got {type(tags).__name__}"]
    if not tags:
        return ["tags list is empty (every skill must declare tags)"]
    errors: List[str] = []
    if len(tags) > MAX_TAGS_PER_SKILL:
        errors.append(f"tags exceed cap of {MAX_TAGS_PER_SKILL} (got {len(tags)}: {tags})")

    found_axes: set = set()
    for tag in tags:
        axis = classify(str(tag))
        if axis is None:
            errors.append(
                f"unknown tag {tag!r} (not in any of {sorted(AXES)} axes per docs/tags.md)"
            )
        else:
            found_axes.add(axis)

    scope_tag = next((t for t in tags if t in AXES["scope"]), None)
    if scope_tag is None:
        errors.append(f"tags missing a scope tag (one of: {sorted(AXES['scope'])})")
    else:
        missing = [a for a in REQUIRED_AXES_BY_SCOPE.get(scope_tag, ()) if a not in found_axes]
        if missing:
            errors.append(f"tags missing required axes {missing} for scope={scope_tag!r}")
    return errors


def validate_metadata(meta: object, all_names: FrozenSet[str]) -> List[str]:
    errors: List[str] = []
    if meta and not isinstance(meta, dict):
        return ["metadata must be a YAML mapping"]
    if not isinstance(meta, dict):
        return ["metadata.skill_type missing; required: one of "
                + str(sorted(VALID_SKILL_TYPES))]

    rm = meta.get("reasoning_mode")
    if rm and str(rm) not in ALLOWED_REASONING_MODES:
        errors.append(
            f"metadata.reasoning_mode {rm!r} is invalid; "
            f"allowed: {sorted(ALLOWED_REASONING_MODES)}"
        )

    st = meta.get("skill_type")
    if st is None:
        errors.append(f"metadata.skill_type missing; required: one of {sorted(VALID_SKILL_TYPES)}")
    elif str(st) not in VALID_SKILL_TYPES:
        errors.append(f"metadata.skill_type {st!r} is invalid; allowed: {sorted(VALID_SKILL_TYPES)}")

    deps_raw = meta.get("dependencies")
    if deps_raw:
        for dep in [d.strip() for d in str(deps_raw).split(",") if d.strip()]:
            if dep not in all_names:
                errors.append(f"metadata.dependency {dep!r} not found among known skills")
    return errors


# ---------------------------------------------------------------------------
# Orchestrating validator
# ---------------------------------------------------------------------------

def validate_skill_frontmatter(
    fm: Dict[str, Any],
    *,
    dir_name: str,
    all_names: FrozenSet[str],
    strict: bool,
    expected_name: Optional[str] = None,
    domain_from_path: Optional[str] = None,
    known_categories: FrozenSet[str] = frozenset(),
    category_from_path: Optional[str] = None,
    tags_override: Optional[List[str]] = None,
) -> List[str]:
    """Validate one skill's frontmatter.

    strict=False  : base spec only (name/description/license/metadata). Tags are
                    validated from `tags_override` if given (legacy registry path).
    strict=True   : also require + validate the v2 fields (domain, keywords,
                    status, frontmatter tags) and cross-check domain/category
                    against the path.
    """
    errors: List[str] = []

    missing = REQUIRED_FRONTMATTER - fm.keys()
    if missing:
        errors.append(f"missing required frontmatter fields: {sorted(missing)}")

    name_val = fm.get("name", "")
    errors.extend(validate_name(name_val))
    if name_val and expected_name and str(name_val) != expected_name:
        errors.append(f"frontmatter 'name' ({name_val!r}) does not match expected name ({expected_name!r})")
    if name_val and dir_name and str(name_val) != dir_name:
        errors.append(f"frontmatter 'name' ({name_val!r}) does not match directory name ({dir_name!r})")

    errors.extend(validate_description(fm.get("description", "")))
    errors.extend(validate_license(fm.get("license")))
    errors.extend(validate_metadata(fm.get("metadata") or {}, all_names))

    if strict:
        v2_missing = REQUIRED_FRONTMATTER_V2 - fm.keys()
        if v2_missing:
            errors.append(f"missing required v2 frontmatter fields: {sorted(v2_missing)}")
        errors.extend(validate_domain(fm.get("domain")))
        errors.extend(validate_keywords(fm.get("keywords")))
        errors.extend(validate_status(fm.get("status")))
        errors.extend(validate_tags(fm.get("tags")))

        dom = fm.get("domain")
        if dom and domain_from_path and str(dom) != domain_from_path:
            errors.append(
                f"frontmatter domain ({dom!r}) does not match path domain ({domain_from_path!r})"
            )
        if dom and category_from_path:
            errors.extend(validate_category(str(dom), category_from_path, known_categories))
    else:
        if tags_override is not None:
            errors.extend(validate_tags(tags_override))

    return errors
