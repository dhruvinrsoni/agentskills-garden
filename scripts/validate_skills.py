"""
validate_skills.py — Skill Garden Validator

Checks:
  1. registry.yaml is well-formed and every path resolves to a real file
  2. Each skill file has valid YAML frontmatter with required fields
  3. reasoning_mode is one of the allowed values
  4. version follows semver (X.Y.Z)
  5. Every declared dependency exists in the registry

Exit code 0 = all good, exit code 1 = validation errors found.
"""

import os
import re
import sys
import yaml
from typing import Any, Dict, List, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REGISTRY_PATH = os.path.join(REPO_ROOT, "registry.yaml")

REQUIRED_FRONTMATTER = {"name", "description", "version", "dependencies", "reasoning_mode"}
ALLOWED_REASONING_MODES = {"linear", "plan-execute", "tdd", "mixed"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

# Registry sections that are not skill groups
_META_KEYS = {"version", "templates"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> Tuple[Dict[str, Any], List[str]]:
    """Extract YAML frontmatter between opening and closing '---' delimiters."""
    errors: List[str] = []
    if not text.startswith("---"):
        return {}, ["missing opening '---' frontmatter delimiter"]
    end = text.find("\n---", 3)
    if end == -1:
        return {}, ["missing closing '---' frontmatter delimiter"]
    raw_yaml = text[3:end].strip()
    try:
        data = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError as exc:
        return {}, [f"YAML parse error in frontmatter: {exc}"]
    if not isinstance(data, dict):
        errors.append("frontmatter must be a YAML mapping")
        return {}, errors
    return data, errors


def _validate_frontmatter(fm: Dict[str, Any], skill_name: str, all_names: set) -> List[str]:
    errors: List[str] = []

    # 1. Required fields
    missing = REQUIRED_FRONTMATTER - fm.keys()
    if missing:
        errors.append(f"missing required frontmatter fields: {sorted(missing)}")

    # 2. name must match registry name
    if "name" in fm and fm["name"] != skill_name:
        errors.append(
            f"frontmatter 'name' ({fm['name']!r}) does not match registry name ({skill_name!r})"
        )

    # 3. reasoning_mode
    rm = fm.get("reasoning_mode")
    if rm and rm not in ALLOWED_REASONING_MODES:
        errors.append(
            f"invalid reasoning_mode {rm!r}; allowed: {sorted(ALLOWED_REASONING_MODES)}"
        )

    # 4. version semver
    ver = str(fm.get("version", ""))
    if ver and not SEMVER_RE.match(ver):
        errors.append(f"version {ver!r} is not valid semver (expected X.Y.Z)")

    # 5. dependencies exist
    deps = fm.get("dependencies") or []
    if not isinstance(deps, list):
        errors.append("'dependencies' must be a list")
    else:
        for dep in deps:
            if dep not in all_names:
                errors.append(f"dependency {dep!r} not found in registry")

    return errors


# ---------------------------------------------------------------------------
# Main validator
# ---------------------------------------------------------------------------

def validate() -> int:
    """Run all validations. Returns exit code (0 = pass, 1 = fail)."""
    print(f"Validating skill garden at: {REPO_ROOT}\n")

    # ── 1. Load registry ────────────────────────────────────────────────────
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

    # Collect all skill entries
    all_entries: List[Dict[str, Any]] = []
    for section, items in reg.items():
        if section in _META_KEYS:
            continue
        if not isinstance(items, list):
            continue
        for entry in items:
            if isinstance(entry, dict):
                entry["_section"] = section
                all_entries.append(entry)

    all_names = {e["name"] for e in all_entries if "name" in e}

    print(f"Registry: {len(all_entries)} skills across "
          f"{len([k for k in reg if k not in _META_KEYS])} sections\n")

    # ── 2. Validate each skill ───────────────────────────────────────────────
    error_count = 0
    warn_count = 0

    for entry in all_entries:
        skill_name = entry.get("name", "<unnamed>")
        skill_path = entry.get("path", "")
        abs_path = os.path.join(REPO_ROOT, skill_path.replace("/", os.sep))
        prefix = f"  [{entry['_section']}] {skill_name}"

        skill_errors: List[str] = []

        # a. Path field present
        if not skill_path:
            skill_errors.append("registry entry missing 'path'")
        else:
            # b. File exists
            if not os.path.isfile(abs_path):
                skill_errors.append(f"file not found: {skill_path}")
            else:
                # c. Parse and validate frontmatter
                with open(abs_path, "r", encoding="utf-8") as sf:
                    text = sf.read()
                fm, parse_errs = _parse_frontmatter(text)
                skill_errors.extend(parse_errs)
                if fm:
                    skill_errors.extend(
                        _validate_frontmatter(fm, skill_name, all_names)
                    )

        # d. Registry-level: description present
        if not entry.get("description", "").strip():
            warn_count += 1
            print(f"  [WARN] {prefix}: registry entry has no description")

        if skill_errors:
            error_count += len(skill_errors)
            print(f"  [FAIL] {prefix}:")
            for err in skill_errors:
                print(f"         - {err}")
        else:
            print(f"  [ OK ] {prefix}")

    # ── 3. Summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Results: {len(all_entries)} skills checked")
    print(f"  Errors:   {error_count}")
    print(f"  Warnings: {warn_count}")

    if error_count == 0:
        print("\nAll skills passed validation.")
        return 0
    else:
        print(f"\n{error_count} error(s) found. Fix them before merging.")
        return 1


if __name__ == "__main__":
    sys.exit(validate())
