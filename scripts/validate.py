"""
validate.py — Skill Garden Validator (agentskills.io spec)

Two modes:

  default (legacy, registry-driven)
    Reads registry.yaml, resolves each path to a SKILL.md, validates base
    frontmatter (name/description/license/metadata) and the registry entry's
    five-axis tags. Used while the garden is still on the v1 layout.

  --strict (frontmatter-driven, v2)
    Walks skills/ directly (no registry), and additionally requires the v2
    fields: domain, keywords, status, and frontmatter `tags`. Cross-checks the
    frontmatter domain/category against the folder path. This is the mode CI
    runs once the garden has migrated to domain namespaces.

Exit code 0 = all good, exit code 1 = validation errors found.
"""

import argparse
import os
import sys
import yaml
from typing import Any, Dict, List

from skill_lib import (
    parse_frontmatter,
    split_frontmatter,
    walk_skills,
    known_categories_for,
    validate_skill_frontmatter,
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REGISTRY_PATH = os.path.join(REPO_ROOT, "registry.yaml")
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")

# Registry sections that are not skill groups
_META_KEYS = {"version", "templates"}


# ---------------------------------------------------------------------------
# Legacy (registry-driven) validation
# ---------------------------------------------------------------------------

def validate_legacy() -> int:
    print(f"Validating skill garden (legacy/registry mode) at: {REPO_ROOT}\n")

    if not os.path.exists(REGISTRY_PATH):
        print(f"[FAIL] registry.yaml not found at {REGISTRY_PATH}")
        return 1
    with open(REGISTRY_PATH, "r", encoding="utf-8") as fh:
        try:
            reg = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            print(f"[FAIL] registry.yaml YAML parse error: {exc}")
            return 1
    if not isinstance(reg, dict):
        print("[FAIL] registry.yaml must be a YAML mapping at the top level")
        return 1

    all_entries: List[Dict[str, Any]] = []
    for section, items in reg.items():
        if section in _META_KEYS or not isinstance(items, list):
            continue
        for entry in items:
            if isinstance(entry, dict):
                entry["_section"] = section
                all_entries.append(entry)

    all_names = frozenset(e["name"] for e in all_entries if "name" in e)
    print(f"Registry: {len(all_entries)} skills across "
          f"{len([k for k in reg if k not in _META_KEYS])} sections\n")

    error_count = 0
    warn_count = 0
    for entry in all_entries:
        skill_name = entry.get("name", "<unnamed>")
        skill_path = entry.get("path", "")
        abs_path = os.path.join(REPO_ROOT, skill_path.replace("/", os.sep))
        prefix = f"  [{entry['_section']}] {skill_name}"
        errors: List[str] = []

        if not skill_path:
            errors.append("registry entry missing 'path'")
        elif not skill_path.endswith("SKILL.md"):
            errors.append(f"path must point to SKILL.md, got: {skill_path}")
        elif not os.path.isfile(abs_path):
            errors.append(f"file not found: {skill_path}")
        else:
            dir_name = os.path.basename(os.path.dirname(abs_path))
            with open(abs_path, "r", encoding="utf-8") as sf:
                fm, _body, perrs = parse_frontmatter(sf.read())
            errors.extend(perrs)
            if fm:
                errors.extend(validate_skill_frontmatter(
                    fm,
                    dir_name=dir_name,
                    all_names=all_names,
                    strict=False,
                    expected_name=skill_name,
                    tags_override=list(entry.get("tags") or []) if "tags" in entry else None,
                ))
            # tags missing entirely from the registry entry is an error
            if "tags" not in entry:
                errors.append("registry entry missing 'tags'")

        if not entry.get("description", "").strip():
            warn_count += 1
            print(f"  [WARN] {prefix}: registry entry has no description")

        if errors:
            error_count += len(errors)
            print(f"  [FAIL] {prefix}:")
            for err in errors:
                print(f"         - {err}")
        else:
            print(f"  [ OK ] {prefix}")

    return _summary(len(all_entries), error_count, warn_count)


# ---------------------------------------------------------------------------
# Strict (frontmatter-driven, v2) validation
# ---------------------------------------------------------------------------

def validate_strict() -> int:
    print(f"Validating skill garden (strict/frontmatter mode) at: {REPO_ROOT}\n")
    if not os.path.isdir(SKILLS_DIR):
        print(f"[FAIL] skills/ not found at {SKILLS_DIR}")
        return 1

    records = walk_skills(SKILLS_DIR)
    all_names = frozenset(
        str(r["fm"].get("name", r["dir_name"])) for r in records
    )
    print(f"Tree: {len(records)} skills under skills/\n")

    error_count = 0
    for r in records:
        name = r["fm"].get("name", r["dir_name"])
        prefix = f"  [{r['domain']}{('/' + r['category']) if r['category'] else ''}] {name}"
        errors: List[str] = list(r["parse_errors"])
        if r["fm"]:
            errors.extend(validate_skill_frontmatter(
                r["fm"],
                dir_name=r["dir_name"],
                all_names=all_names,
                strict=True,
                domain_from_path=r["domain"],
                category_from_path=r["category"],
                known_categories=known_categories_for(records, r["domain"]),
            ))
        if errors:
            error_count += len(errors)
            print(f"  [FAIL] {prefix}:")
            for err in errors:
                print(f"         - {err}")
        else:
            print(f"  [ OK ] {prefix}")

    return _summary(len(records), error_count, 0)


def _summary(checked: int, error_count: int, warn_count: int) -> int:
    print(f"\n{'='*60}")
    print(f"Results: {checked} skills checked")
    print(f"  Errors:   {error_count}")
    print(f"  Warnings: {warn_count}")
    if error_count == 0:
        print("\nAll skills passed validation.")
        return 0
    print(f"\n{error_count} error(s) found. Fix them before merging.")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate the agentskills-garden skills.")
    ap.add_argument("--strict", action="store_true",
                    help="frontmatter-driven v2 validation (walks skills/, requires "
                         "domain/keywords/status/tags). Default is legacy registry mode.")
    args = ap.parse_args()
    return validate_strict() if args.strict else validate_legacy()


if __name__ == "__main__":
    sys.exit(main())
