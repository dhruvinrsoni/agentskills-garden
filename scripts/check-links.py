"""check-links.py — verify internal markdown links resolve.

Walks every *.md file under repo root (excluding .git/, legacy/, and
common vendored dirs), extracts markdown links of the form `[text](path)`
and `![alt](path)`, filters out external URLs and pure fragments, and
verifies each target exists relative to the source file's directory.

Exit code 0 = all internal links resolve; 1 = broken links found.

Code-fence-aware: links inside fenced code blocks (``` or ~~~) are
ignored to avoid false positives in YAML/bash/python examples that
contain bracket/paren sequences.
"""

import os
import re
import sys
from typing import Iterator, List, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Directories to skip during the walk.
EXCLUDE_DIRS = {".git", "legacy", "node_modules", ".venv", "__pycache__"}

# Match [text](url) or ![alt](url). Captures the raw url+optional title.
# Allows escaped brackets in the link text via `\\[` etc.
LINK_RE = re.compile(r'!?\[(?:[^\]\\]|\\.)*\]\(([^)]+)\)')

# Schemes treated as external (no local resolution).
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "ftp://", "tel:")


def iter_md_files(root: str) -> Iterator[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        # Mutate dirnames in place so os.walk skips excluded dirs.
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for f in filenames:
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)


def strip_code_fences(text: str) -> str:
    """Remove fenced code blocks (``` and ~~~) before link extraction."""
    return re.sub(r'(?ms)^(```|~~~).*?^\1\s*$', "", text)


def normalize_target(raw: str) -> str:
    """Strip title and fragment from a link target. Returns the bare path."""
    raw = raw.strip()
    # Drop optional title suffix: `path "title"` or `path 'title'`.
    m = re.match(r'^(\S+)\s+["\'].*["\']$', raw)
    if m:
        raw = m.group(1)
    # Drop fragment after first '#'.
    if "#" in raw:
        raw = raw.split("#", 1)[0]
    return raw


def is_external(target: str) -> bool:
    return target.startswith(EXTERNAL_PREFIXES) or target.startswith("//")


def main() -> int:
    broken: List[Tuple[str, str]] = []
    total_internal = 0

    for md_path in iter_md_files(REPO_ROOT):
        try:
            with open(md_path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"[FAIL] cannot read {md_path}: {exc}")
            return 1

        cleaned = strip_code_fences(text)
        for raw_target in LINK_RE.findall(cleaned):
            target = normalize_target(raw_target)
            if not target or target.startswith("#") or is_external(target):
                continue
            total_internal += 1
            resolved = os.path.normpath(
                os.path.join(os.path.dirname(md_path), target)
            )
            if not os.path.exists(resolved):
                broken.append((md_path, raw_target))

    print(f"check-links.py: scanned {total_internal} internal markdown links")

    if broken:
        print(f"\n[FAIL] {len(broken)} broken link(s) found:")
        for src, target in sorted(broken):
            rel_src = os.path.relpath(src, REPO_ROOT)
            print(f"  {rel_src}  ->  {target}")
        return 1

    print("All internal links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
