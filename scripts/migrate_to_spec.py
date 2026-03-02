#!/usr/bin/env python3
"""
migrate_to_spec.py — One-shot migration to agentskills.io spec format.

Converts each skill from:
  skills/<category>/<skill-name>.md
To:
  skills/<category>/<skill-name>/SKILL.md

Frontmatter is transformed to spec-compliant format:
  - Keeps:         name, description
  - Adds:          license, compatibility
  - Moves to metadata: version, dependencies, reasoning_mode

Also updates registry.yaml paths to reflect the new structure.

Usage:
  python scripts/migrate_to_spec.py [--dry-run]
"""

import os
import re
import sys
import textwrap
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REGISTRY_PATH = os.path.join(REPO_ROOT, "registry.yaml")
_META_KEYS = {"version", "templates"}

# Fields moved from top-level frontmatter into metadata
_MIGRATE_TO_META = {"version", "dependencies", "reasoning_mode"}


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str):
    """Return (fm_dict, body_text). body_text starts after the closing ---."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw_yaml = text[3:end].strip()
    try:
        fm = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError:
        fm = {}
    body = text[end + 4:]  # skip \n---
    if body.startswith("\n"):
        body = body[1:]
    return fm, body


def build_frontmatter(fm: dict) -> str:
    """Serialize a spec-compliant frontmatter block from a parsed fm dict."""
    name = fm.get("name", "")
    description = fm.get("description", "")
    if isinstance(description, str):
        description = description.strip()

    lines = ["---", f"name: {name}"]

    # Description — use block scalar for long or multiline content
    if "\n" in description or len(description) > 80:
        lines.append("description: >")
        # Re-wrap at 72 chars, indented 2 spaces
        for para in re.split(r"\n{2,}", description):
            for sentence in para.split("\n"):
                sentence = sentence.strip()
                if not sentence:
                    continue
                wrapped = textwrap.fill(
                    sentence, width=72,
                    initial_indent="  ",
                    subsequent_indent="  ",
                )
                lines.append(wrapped)
    else:
        lines.append(f"description: {description}")

    lines.append("license: Apache-2.0")
    lines.append("compatibility: Designed for Claude Code and compatible AI agent environments")

    # Build metadata from migrated fields + any existing metadata
    metadata = {}

    version = fm.get("version")
    if version:
        metadata["version"] = str(version)

    deps = fm.get("dependencies")
    if deps:
        if isinstance(deps, list):
            metadata["dependencies"] = ", ".join(str(d) for d in deps)
        elif isinstance(deps, str) and deps.strip():
            metadata["dependencies"] = deps.strip()

    reasoning_mode = fm.get("reasoning_mode")
    if reasoning_mode:
        metadata["reasoning_mode"] = str(reasoning_mode)

    # Carry forward any existing metadata keys
    existing_meta = fm.get("metadata") or {}
    if isinstance(existing_meta, dict):
        for k, v in existing_meta.items():
            if k not in metadata:
                metadata[k] = str(v)

    if metadata:
        lines.append("metadata:")
        for k, v in metadata.items():
            # Quote values containing special YAML characters
            if any(c in str(v) for c in (",", ":", "#", "\n", "[")):
                lines.append(f'  {k}: "{v}"')
            else:
                lines.append(f"  {k}: {v}")

    lines.append("---")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------

def migrate(dry_run: bool = False) -> int:
    """Migrate all skills. Returns exit code 0 = success, 1 = errors."""
    if not os.path.exists(REGISTRY_PATH):
        print(f"[ERROR] registry.yaml not found at {REGISTRY_PATH}")
        return 1

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_text = f.read()

    try:
        reg = yaml.safe_load(registry_text)
    except yaml.YAMLError as exc:
        print(f"[ERROR] Failed to parse registry.yaml: {exc}")
        return 1

    # Collect all skill entries from non-meta sections
    entries = []
    for section, items in reg.items():
        if section in _META_KEYS:
            continue
        if not isinstance(items, list):
            continue
        for entry in items:
            if isinstance(entry, dict) and entry.get("name") and entry.get("path"):
                entries.append(entry)

    print(f"Found {len(entries)} skills to migrate\n")

    errors = []
    path_updates = {}  # old_path -> new_path

    for entry in entries:
        skill_name = entry["name"]
        old_path = entry["path"]

        # Only migrate .md files that haven't been migrated yet
        if not old_path.endswith(".md") or old_path.endswith("SKILL.md"):
            print(f"  [SKIP] {skill_name}: already migrated or not .md ({old_path})")
            continue

        abs_old = os.path.join(REPO_ROOT, old_path.replace("/", os.sep))
        if not os.path.isfile(abs_old):
            errors.append(f"  [MISS] {skill_name}: file not found at {old_path}")
            continue

        # Derive new path: same parent dir, new subdir = skill_name, file = SKILL.md
        parent_dir = os.path.dirname(old_path)  # e.g. skills/00-foundation
        new_path = f"{parent_dir}/{skill_name}/SKILL.md"
        abs_new_dir = os.path.join(REPO_ROOT, parent_dir.replace("/", os.sep), skill_name)
        abs_new = os.path.join(abs_new_dir, "SKILL.md")

        # Read, transform, write
        with open(abs_old, "r", encoding="utf-8") as f:
            original = f.read()

        fm, body = parse_frontmatter(original)
        new_fm = build_frontmatter(fm)
        new_content = new_fm + "\n" + body

        if dry_run:
            print(f"  [DRY] {skill_name}: {old_path} -> {new_path}")
            print(f"        new frontmatter preview:\n{new_fm}")
        else:
            os.makedirs(abs_new_dir, exist_ok=True)
            with open(abs_new, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_content)
            os.remove(abs_old)
            print(f"  [OK ] {skill_name}: {old_path} -> {new_path}")

        path_updates[old_path] = new_path

    # Update registry.yaml paths via string replacement
    if not dry_run and path_updates:
        new_registry_text = registry_text
        for old, new in path_updates.items():
            new_registry_text = new_registry_text.replace(old, new)
        with open(REGISTRY_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_registry_text)
        print(f"\n  Registry updated: {len(path_updates)} paths rewritten")

    # Summary
    print(f"\n{'='*60}")
    if errors:
        for e in errors:
            print(e)
    migrated = len(path_updates)
    skipped = len(entries) - migrated - len(errors)
    print(f"Migrated: {migrated}  |  Skipped: {skipped}  |  Errors: {len(errors)}")

    return 0 if not errors else 1


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("=== DRY RUN — no files will be modified ===\n")
    sys.exit(migrate(dry_run=dry_run))
