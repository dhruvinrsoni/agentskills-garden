#!/usr/bin/env python3
"""
migrate.py — One-shot migration to the domain-namespace layout.

Moves the v1 phase folders into domain namespaces and injects the v2
frontmatter fields (domain, tags, keywords, status). Frontmatter becomes the
single source of truth for tags (copied here from registry.yaml).

  skills/00-foundation/<skill>/SKILL.md      -> skills/000-foundation/<skill>/SKILL.md
  skills/<NN-phase>/<skill>/SKILL.md         -> skills/100-engineering/<NN-phase>/<skill>/SKILL.md

Foundation skills are universal/cross-cutting and land flat under 000-foundation
(no phase level). Everything else keeps its NN-phase folder, now nested under
100-engineering. Directories are moved with `git mv` so history is preserved.

Frontmatter injection is surgical (line insertion before `metadata:`) so the
existing human formatting — block-scalar descriptions, key order — is kept.

Idempotent: re-running skips folders already moved and fields already present.

Usage:
  python scripts/migrate.py            # dry-run (default): print the plan
  python scripts/migrate.py --apply    # perform git mv + inject frontmatter
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from typing import Dict, List, Tuple

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill_lib import split_frontmatter  # noqa: E402

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
REGISTRY_PATH = os.path.join(REPO_ROOT, "registry.yaml")
_META_KEYS = {"version", "templates"}

FOUNDATION_SRC = os.path.join(SKILLS_DIR, "00-foundation")
FOUNDATION_DST = os.path.join(SKILLS_DIR, "000-foundation")
ENGINEERING_DST = os.path.join(SKILLS_DIR, "100-engineering")

# Top-level entries that are not v1 phase folders to migrate.
_SKIP_TOPLEVEL = {"00-foundation", "000-foundation", "100-engineering", "_index", "legacy"}

# Injected, in this order, immediately before the `metadata:` line.
_INJECT_ORDER = ("domain", "status", "tags", "keywords")


# ---------------------------------------------------------------------------
# Registry tag lookup (last use of registry as a source)
# ---------------------------------------------------------------------------

def load_registry_tags() -> Dict[str, List[str]]:
    with open(REGISTRY_PATH, "r", encoding="utf-8") as fh:
        reg = yaml.safe_load(fh) or {}
    out: Dict[str, List[str]] = {}
    for section, items in reg.items():
        if section in _META_KEYS or not isinstance(items, list):
            continue
        for entry in items:
            if isinstance(entry, dict) and entry.get("name"):
                out[entry["name"]] = list(entry.get("tags") or [])
    return out


# ---------------------------------------------------------------------------
# git mv moves
# ---------------------------------------------------------------------------

def _git_mv(src: str, dst: str, apply: bool) -> None:
    rel_src = os.path.relpath(src, REPO_ROOT).replace(os.sep, "/")
    rel_dst = os.path.relpath(dst, REPO_ROOT).replace(os.sep, "/")
    print(f"  [MOVE] {rel_src} -> {rel_dst}")
    if apply:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        subprocess.run(["git", "mv", rel_src, rel_dst], cwd=REPO_ROOT, check=True)


def plan_moves(apply: bool) -> None:
    print("Moves:")
    moved_any = False

    # Foundation: move each child of 00-foundation into flat 000-foundation/.
    if os.path.isdir(FOUNDATION_SRC):
        moved_any = True
        if apply:
            os.makedirs(FOUNDATION_DST, exist_ok=True)
        for child in sorted(os.listdir(FOUNDATION_SRC)):
            src = os.path.join(FOUNDATION_SRC, child)
            dst = os.path.join(FOUNDATION_DST, child)
            if os.path.exists(dst):
                print(f"  [SKIP] 000-foundation/{child} already exists")
                continue
            _git_mv(src, dst, apply)
        # Remove the now-empty source folder.
        if apply and os.path.isdir(FOUNDATION_SRC) and not os.listdir(FOUNDATION_SRC):
            os.rmdir(FOUNDATION_SRC)

    # Engineering: move each remaining NN-phase folder under 100-engineering/.
    for name in sorted(os.listdir(SKILLS_DIR)):
        if name in _SKIP_TOPLEVEL:
            continue
        src = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(src):
            continue
        dst = os.path.join(ENGINEERING_DST, name)
        if os.path.exists(dst):
            print(f"  [SKIP] 100-engineering/{name} already exists")
            continue
        moved_any = True
        _git_mv(src, dst, apply)

    if not moved_any:
        print("  (nothing to move — already migrated)")


# ---------------------------------------------------------------------------
# Surgical frontmatter injection
# ---------------------------------------------------------------------------

def _format_tags(tags: List[str]) -> str:
    return "[" + ", ".join(str(t) for t in tags) + "]"


def _inject_lines(text: str, fields: Dict[str, str]) -> str:
    """Insert `key: value` lines before the top-level `metadata:` line (or before
    the closing '---' if none), skipping keys already present in frontmatter."""
    end = text.find("\n---", 3)
    if not text.startswith("---") or end == -1:
        return text  # no frontmatter; caller handles/skips
    fm_lines = text[:end].split("\n")
    body_tail = text[end:]  # starts with "\n---"

    fm_dict, _ = split_frontmatter(text)
    to_add = [f"{k}: {v}" for k, v in fields.items() if k not in fm_dict]
    if not to_add:
        return text

    insert_at = next(
        (i for i, ln in enumerate(fm_lines) if ln.startswith("metadata:")),
        len(fm_lines),
    )
    new_lines = fm_lines[:insert_at] + to_add + fm_lines[insert_at:]
    return "\n".join(new_lines) + body_tail


def inject_frontmatter(apply: bool, reg_tags: Dict[str, List[str]]) -> Tuple[int, int]:
    print("\nFrontmatter injection:")
    injected = 0
    warned = 0
    for root, dirs, files in os.walk(SKILLS_DIR):
        dirs[:] = [d for d in dirs if d not in {"_index", "legacy", "__pycache__"}]
        if "SKILL.md" not in files:
            continue
        abs_path = os.path.join(root, "SKILL.md")
        rel = os.path.relpath(abs_path, REPO_ROOT).replace(os.sep, "/")
        below = os.path.relpath(abs_path, SKILLS_DIR).replace(os.sep, "/").split("/")[:-1]
        # Compute the POST-move domain so the dry-run preview is accurate even
        # before folders are moved: foundation if it lives under a foundation
        # folder, otherwise engineering.
        top = below[0] if below else ""
        domain = "foundation" if top in ("00-foundation", "000-foundation") else "engineering"

        with open(abs_path, "r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        fm, _ = split_frontmatter(text)
        name = fm.get("name", below[-1] if below else "")

        tags = reg_tags.get(name)
        if tags is None:
            print(f"  [WARN] {rel}: {name!r} not in registry; tags not injected")
            warned += 1
            tags = []

        fields = {
            "domain": domain,
            "status": "published",
            "tags": _format_tags(tags),
            "keywords": "[]",
        }
        new_text = _inject_lines(text, fields)
        if new_text != text:
            injected += 1
            print(f"  [INJ ] {rel}  (+{', '.join(k for k in _INJECT_ORDER if k not in fm)})")
            if apply:
                with open(abs_path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(new_text)
        else:
            print(f"  [ ok ] {rel}  (already has v2 fields)")
    return injected, warned


# ---------------------------------------------------------------------------
# Internal-link repair (the move changed both link targets AND link depth)
# ---------------------------------------------------------------------------

_ENG_PHASES = {
    "10-discovery", "20-architecture", "20-planning", "25-pragmatism",
    "30-implementation", "40-quality", "50-documentation", "50-performance",
    "60-debugging", "60-security", "70-devops", "80-collaboration", "80-docs",
    "90-maintenance",
}
_LINK_RE = re.compile(r"(!?\[[^\]]*\])\(([^)]+)\)")


def _remap_old_to_new(abs_old: str) -> str:
    """Map an OLD repo-relative path to its NEW location under the namespaces."""
    rel = os.path.relpath(abs_old, REPO_ROOT).replace(os.sep, "/")
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] == "skills":
        seg = parts[1]
        if seg == "00-foundation":
            parts[1] = "000-foundation"
        elif seg in _ENG_PHASES:
            parts.insert(1, "100-engineering")
        return os.path.join(REPO_ROOT, *parts)
    return abs_old


def _old_location(new_abs: str) -> str:
    """Inverse of the move for a source file: where it lived BEFORE migration."""
    rel = os.path.relpath(new_abs, REPO_ROOT).replace(os.sep, "/")
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] == "skills":
        if parts[1] == "000-foundation":
            parts[1] = "00-foundation"
        elif parts[1] == "100-engineering":
            del parts[1]
        return os.path.join(REPO_ROOT, *parts)
    return new_abs


def fix_internal_links(apply: bool) -> int:
    """Rewrite internal markdown links broken by the move. For each link, resolve
    it against the source file's OLD directory, remap the target to its new home,
    and recompute the relative path from the source's CURRENT directory. Only
    touches links that are currently broken and become valid after remapping."""
    print("\nLink repair:")
    md_files: List[str] = []
    for base in (os.path.join(REPO_ROOT, "docs"), SKILLS_DIR):
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in {"_index", "legacy", "__pycache__", ".git"}]
            md_files += [os.path.join(root, f) for f in files if f.endswith(".md")]
    # Root-level markdown (README.md, README_LOCAL.md, …) — didn't move, but its
    # links into skills/ still need the namespace/rename fix.
    md_files += [os.path.join(REPO_ROOT, f) for f in os.listdir(REPO_ROOT)
                 if f.endswith(".md") and os.path.isfile(os.path.join(REPO_ROOT, f))]

    fixed_links = 0
    fixed_files = 0
    for path in md_files:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        new_dir = os.path.dirname(path)
        old_dir = os.path.dirname(_old_location(path))
        file_changed = False

        def repl(m):
            nonlocal fixed_links, file_changed
            label, target = m.group(1), m.group(2)
            url = target.split(" ", 1)[0].strip()
            if re.match(r"^(https?:|mailto:|ftp:|tel:|#|//)", url) or not url:
                return m.group(0)
            frag = ""
            if "#" in url:
                url, frag = url.split("#", 1); frag = "#" + frag
            # already valid from the current location? leave it.
            if os.path.exists(os.path.normpath(os.path.join(new_dir, url))):
                return m.group(0)
            old_target = os.path.normpath(os.path.join(old_dir, url))
            new_target = _remap_old_to_new(old_target)
            if not os.path.exists(new_target):
                return m.group(0)
            new_rel = os.path.relpath(new_target, new_dir).replace(os.sep, "/")
            fixed_links += 1
            file_changed = True
            return f"{label}({new_rel}{frag})"

        new_text = _LINK_RE.sub(repl, text)
        if file_changed:
            fixed_files += 1
            rel = os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")
            print(f"  [LINK] {rel}")
            if apply:
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(new_text)
    print(f"  {fixed_links} link(s) across {fixed_files} file(s)")
    return fixed_links


def main() -> int:
    ap = argparse.ArgumentParser(description="Migrate skills to domain namespaces.")
    ap.add_argument("--apply", action="store_true",
                    help="perform the migration (default is a dry-run preview)")
    ap.add_argument("--fix-links", action="store_true",
                    help="only repair internal markdown links broken by the move")
    args = ap.parse_args()

    if args.fix_links:
        n = fix_internal_links(apply=True)
        print(f"\nLink repair applied ({n} links).")
        return 0

    if not args.apply:
        print("=== DRY RUN — no files will be modified (pass --apply to execute) ===\n")

    reg_tags = load_registry_tags()
    plan_moves(args.apply)
    injected, warned = inject_frontmatter(args.apply, reg_tags)
    fix_internal_links(args.apply)

    print(f"\n{'='*60}")
    print(f"Frontmatter: {injected} file(s) to inject, {warned} warning(s)")
    if not args.apply:
        print("Dry run complete. Re-run with --apply to perform the migration.")
    else:
        print("Migration applied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
