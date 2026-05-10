"""
build_site.py — Static site generator for agentskills-garden.

Reads registry.yaml + skills/**/SKILL.md + docs/**/*.md and emits a static
site to _site/. Open-closed: adding a skill or category does not require
touching this script. The 5-axis tag taxonomy is consumed from
scripts/tag_axes.py (the same source of truth validate_skills.py uses).

Usage:
  python scripts/build_site.py            # build to _site/
  python scripts/build_site.py --serve    # build then serve at :8000

Env vars:
  BASE_URL         path prefix for production (e.g. /agentskills-garden).
                   Defaults to "" for local serve.
  CANONICAL_ROOT   absolute origin used in canonical/OG tags.
                   Defaults to https://dhruvinrsoni.github.io/agentskills-garden.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import http.server
import json
import os
import re
import shutil
import socketserver
import sys
from typing import Any, Dict, List, Optional, Tuple

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

try:
    import markdown as md_lib
except ImportError:
    md_lib = None

# Local helper module — same axis vocab the validator uses.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tag_axes import AXES, classify  # noqa: E402

# ──────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
REGISTRY_PATH = os.path.join(REPO_ROOT, "registry.yaml")
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "site_templates")
OUTPUT_DIR = os.path.join(REPO_ROOT, "_site")

GITHUB_REPO_URL = "https://github.com/dhruvinrsoni/agentskills-garden"
DEFAULT_CANONICAL = "https://dhruvinrsoni.github.io/agentskills-garden"

SITE_NAME = "Agent Skills Garden"
SITE_TAGLINE = "A constitution-driven skill library for AI agents."

PILLARS = [
    {"name": "Satya", "meaning": "truth & determinism"},
    {"name": "Dharma", "meaning": "right action & safety"},
    {"name": "Ahimsa", "meaning": "non-destruction"},
    {"name": "Pragya", "meaning": "wisdom & direction"},
]

CATEGORY_DISPLAY = {
    "00-foundation":   "Foundation",
    "10-discovery":    "Discovery",
    "20-architecture": "Architecture",
    "20-planning":     "Planning",
    "25-pragmatism":   "Pragmatism",
    "30-implementation": "Implementation",
    "30-debugging":    "Debugging",
    "40-quality":      "Quality",
    "50-performance":  "Performance",
    "50-documentation": "Documentation",
    "60-security":     "Security",
    "60-debugging":    "Debugging",
    "70-devops":       "DevOps",
    "80-docs":         "Docs",
    "80-collaboration": "Collaboration",
    "90-maintenance":  "Maintenance",
}

# Top-level docs to surface as prose pages. Path is relative to docs/.
PROSE_PAGES = [
    {"file": "concepts.md",         "slug": "docs/concepts",
     "title": "Concepts",           "subtitle": "Hierarchy & cognitive modes"},
    {"file": "master-skills.md",    "slug": "docs/master-skills",
     "title": "Master skills",      "subtitle": "Orchestration guide"},
    {"file": "named-principles.md", "slug": "docs/named-principles",
     "title": "Named principles",   "subtitle": "Industry vocab mapping"},
    {"file": "skills-bridge.md",    "slug": "docs/skills-bridge",
     "title": "Skills bridge",      "subtitle": "Bridge-link install"},
    {"file": "tags.md",             "slug": "docs/tag-taxonomy",
     "title": "Tag taxonomy",       "subtitle": "The five-axis system"},
]

_META_KEYS = {"version", "templates"}


# ──────────────────────────────────────────────────────────────────────────
# Frontmatter / markdown parsing
# ──────────────────────────────────────────────────────────────────────────
def split_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
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


def extract_h1(body: str) -> Optional[str]:
    for line in body.splitlines():
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return None


def extract_first_section_md(body: str) -> str:
    """Return the markdown of the first prose paragraph under the first ## heading.

    Fallback: first 500 chars of body if no `## ` section is found.
    """
    lines = body.splitlines()
    in_section = False
    section_lines: List[str] = []
    for line in lines:
        if not in_section:
            if re.match(r"^##\s+", line):
                in_section = True
            continue
        # Inside the first section. Stop at the next ## heading.
        if re.match(r"^##\s+", line):
            break
        section_lines.append(line)
        # Trim once we've hit an empty line after at least some content.
        if section_lines and len(section_lines) > 6 and not line.strip():
            break

    text = "\n".join(section_lines).strip()
    if not text:
        # Fallback: trim the body to first 500 chars at a word boundary.
        snippet = body.strip()[:500]
        if len(body.strip()) > 500:
            snippet = snippet.rsplit(" ", 1)[0] + "&hellip;"
        return snippet
    return text


def list_section_headings(body: str) -> List[str]:
    headings = []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            headings.append(m.group(1).strip())
    return headings


def md_to_html(text: str) -> str:
    if md_lib is not None:
        return md_lib.markdown(
            text,
            extensions=["extra", "sane_lists", "toc"],
            output_format="html5",
        )
    # Minimal fallback: paragraph-wrap and escape.
    import html as _html
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return "\n".join("<p>" + _html.escape(p).replace("\n", "<br>") + "</p>" for p in paras)


# ──────────────────────────────────────────────────────────────────────────
# Data model
# ──────────────────────────────────────────────────────────────────────────
def axis_split(tags: List[str]) -> Dict[str, List[str]]:
    """Group tags by the axis they belong to (per scripts/tag_axes.py)."""
    out = {axis: [] for axis in AXES}
    for tag in tags:
        axis = classify(str(tag))
        if axis:
            out[axis].append(str(tag))
    return out


def build_skill(entry: Dict[str, Any]) -> Dict[str, Any]:
    name = entry["name"]
    rel_path = entry["path"]
    abs_path = os.path.join(REPO_ROOT, rel_path.replace("/", os.sep))
    tags = list(entry.get("tags") or [])

    fm: Dict[str, Any] = {}
    body = ""
    if os.path.isfile(abs_path):
        with open(abs_path, "r", encoding="utf-8") as fh:
            text = fh.read()
        fm, body = split_frontmatter(text)

    meta = (fm.get("metadata") or {}) if isinstance(fm, dict) else {}
    deps_raw = meta.get("dependencies") or ""
    deps = [d.strip() for d in str(deps_raw).split(",") if d.strip()]

    title = extract_h1(body) or name
    first_md = extract_first_section_md(body)
    first_html = md_to_html(first_md)
    sections = list_section_headings(body)
    # Skip the first section in the "what the full skill covers" list, since
    # we already render it on the page. Keep up to 8 follow-on sections.
    preview_sections = sections[1:9] if len(sections) > 1 else []

    parts = rel_path.split("/")
    category_dir = parts[1] if len(parts) >= 3 else ""

    return {
        "name": name,
        "description": entry.get("description", "").strip(),
        "tags": tags,
        "axes": axis_split(tags),
        "reasoning_mode": entry.get("reasoning_mode", meta.get("reasoning_mode", "")),
        "category_dir": category_dir,
        "category_section": entry.get("_section", ""),
        "rel_path": rel_path,
        "github_blob_url": f"{GITHUB_REPO_URL}/blob/main/{rel_path}",
        "github_edit_url": f"{GITHUB_REPO_URL}/edit/main/{rel_path}",
        "title": title,
        "first_paragraph_html": first_html,
        "preview_sections": preview_sections,
        "version": str(meta.get("version", "")),
        "skill_type": str(meta.get("skill_type", "standard")),
        "license": str(fm.get("license", "")),
        "dependencies": deps,
        "search_text": (name + " " + entry.get("description", "")).lower(),
    }


def load_registry() -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    with open(REGISTRY_PATH, "r", encoding="utf-8") as fh:
        reg = yaml.safe_load(fh)

    skills: List[Dict[str, Any]] = []
    by_section: Dict[str, List[Dict[str, Any]]] = {}

    for section, items in reg.items():
        if section in _META_KEYS or not isinstance(items, list):
            continue
        for entry in items:
            if not isinstance(entry, dict) or "name" not in entry:
                continue
            entry = dict(entry)  # don't mutate the parsed yaml
            entry["_section"] = section
            # Skip entries that don't point at a SKILL.md (templates excluded).
            path = entry.get("path", "")
            if not path.endswith("SKILL.md"):
                continue
            built = build_skill(entry)
            skills.append(built)
            by_section.setdefault(section, []).append(built)

    skills.sort(key=lambda s: (s["category_dir"], s["name"]))
    return skills, by_section


def build_categories(skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_dir: Dict[str, List[Dict[str, Any]]] = {}
    for s in skills:
        if not s["category_dir"]:
            continue
        by_dir.setdefault(s["category_dir"], []).append(s)
    cats = []
    for d, ss in sorted(by_dir.items()):
        cats.append({
            "dir": d,
            "name": CATEGORY_DISPLAY.get(d, d.split("-", 1)[-1].title()),
            "skills": ss,
            "count": len(ss),
        })
    return cats


def build_tag_indexes(skills: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Return {tag: {axis, skills}}. Sorted skills per tag by name."""
    out: Dict[str, Dict[str, Any]] = {}
    for s in skills:
        for tag in s["tags"]:
            entry = out.setdefault(tag, {"axis": classify(tag) or "other", "skills": []})
            entry["skills"].append(s)
    for tag in out:
        out[tag]["skills"].sort(key=lambda s: s["name"])
    return out


def build_axis_choices(skills: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Per-axis sorted list of values actually present in the registry."""
    found: Dict[str, set] = {axis: set() for axis in AXES}
    for s in skills:
        for axis, tags in s["axes"].items():
            for t in tags:
                found[axis].add(t)
    return {axis: sorted(found[axis]) for axis in AXES}


def find_related(skills: List[Dict[str, Any]], skill: Dict[str, Any], limit: int = 4) -> List[Dict[str, Any]]:
    """Skills sharing the most tags (excluding scope/risk which are too generic)."""
    weight_axes = {"lifecycle", "capability", "domain"}
    own_tags = set()
    for axis in weight_axes:
        own_tags.update(skill["axes"].get(axis, []))

    scored: List[Tuple[int, Dict[str, Any]]] = []
    for other in skills:
        if other["name"] == skill["name"]:
            continue
        other_tags = set()
        for axis in weight_axes:
            other_tags.update(other["axes"].get(axis, []))
        overlap = len(own_tags & other_tags)
        if overlap > 0:
            scored.append((overlap, other))
    scored.sort(key=lambda t: (-t[0], t[1]["name"]))
    return [o for _, o in scored[:limit]]


# ──────────────────────────────────────────────────────────────────────────
# Output
# ──────────────────────────────────────────────────────────────────────────
def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def render_site(base_url: str, canonical_root: str) -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=False,
        lstrip_blocks=False,
    )

    skills, _by_section = load_registry()
    categories = build_categories(skills)
    tag_indexes = build_tag_indexes(skills)
    axes_choices = build_axis_choices(skills)

    scope_set = set(AXES["scope"])

    if os.path.isdir(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    site = {
        "name": SITE_NAME,
        "tagline": SITE_TAGLINE,
        "github_url": GITHUB_REPO_URL,
        "repo_name": "agentskills-garden",
        "skill_count": len(skills),
        "category_count": len(categories),
        "generated_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d"),
        "canonical_root": canonical_root,
    }

    common = {
        "site": site,
        "base_url": base_url,
        "scope_set": scope_set,
    }

    routes: List[str] = []  # for sitemap

    # ── Home ───────────────────────────────────────────────────────────────
    home_html = env.get_template("home.html").render(
        **common,
        page_url="/",
        skills=skills,
        categories=categories,
        axes=axes_choices,
        pillars=PILLARS,
        prose_docs=[{"slug": p["slug"], "title": p["title"], "subtitle": p["subtitle"]}
                    for p in PROSE_PAGES],
    )
    write(os.path.join(OUTPUT_DIR, "index.html"), home_html)
    routes.append("/")

    # ── Skill pages ────────────────────────────────────────────────────────
    for s in skills:
        related = find_related(skills, s)
        page_url = f"/skills/{s['name']}/"
        html = env.get_template("skill.html").render(
            **common,
            page_url=page_url,
            skill=s,
            related=related,
        )
        write(os.path.join(OUTPUT_DIR, "skills", s["name"], "index.html"), html)
        routes.append(page_url)

    # ── Category pages ─────────────────────────────────────────────────────
    for cat in categories:
        page_url = f"/categories/{cat['dir']}/"
        html = env.get_template("category.html").render(
            **common,
            page_url=page_url,
            category=cat,
            skills=cat["skills"],
        )
        write(os.path.join(OUTPUT_DIR, "categories", cat["dir"], "index.html"), html)
        routes.append(page_url)

    # ── Tag pages ──────────────────────────────────────────────────────────
    for tag, info in sorted(tag_indexes.items()):
        page_url = f"/tags/{tag}/"
        html = env.get_template("tag.html").render(
            **common,
            page_url=page_url,
            tag=tag,
            axis=info["axis"],
            skills=info["skills"],
        )
        write(os.path.join(OUTPUT_DIR, "tags", tag, "index.html"), html)
        routes.append(page_url)

    # ── Tags index page ────────────────────────────────────────────────────
    tags_index_html_parts = ["<h1>Tags</h1>",
                             "<p>Tags are how the librarian routes a task to the right skill. "
                             "Every skill carries one tag from each applicable axis. "
                             "See the <a href=\"" + base_url + "/docs/tag-taxonomy/\">tag taxonomy</a> "
                             "for the canonical vocabulary.</p>"]
    for axis_name in AXES:
        in_axis = sorted(t for t, info in tag_indexes.items() if info["axis"] == axis_name)
        if not in_axis:
            continue
        tags_index_html_parts.append(f"<h2>{axis_name}</h2>")
        tags_index_html_parts.append('<div class="tag-list" style="display:flex; flex-wrap:wrap; gap:0.4rem;">')
        for t in in_axis:
            count = len(tag_indexes[t]["skills"])
            tags_index_html_parts.append(
                f'<a class="tag" href="{base_url}/tags/{t}/">{t} <span style="opacity:.6">({count})</span></a>'
            )
        tags_index_html_parts.append("</div>")
    tags_index_html = "\n".join(tags_index_html_parts)
    html = env.get_template("prose.html").render(
        **common,
        page_url="/tags/",
        title="Tags",
        subtitle="All tags grouped by axis",
        breadcrumb=True,
        body_html=tags_index_html,
        source_url=None,
        source_label=None,
    )
    write(os.path.join(OUTPUT_DIR, "tags", "index.html"), html)
    routes.append("/tags/")

    # ── Prose pages from docs/ ─────────────────────────────────────────────
    for prose in PROSE_PAGES:
        src = os.path.join(DOCS_DIR, prose["file"])
        if not os.path.isfile(src):
            continue
        with open(src, "r", encoding="utf-8") as fh:
            text = fh.read()
        body_html = md_to_html(text)
        page_url = f"/{prose['slug']}/"
        html = env.get_template("prose.html").render(
            **common,
            page_url=page_url,
            title=prose["title"],
            subtitle=prose["subtitle"],
            breadcrumb=True,
            body_html=body_html,
            source_url=f"{GITHUB_REPO_URL}/blob/main/docs/{prose['file']}",
            source_label=f"docs/{prose['file']}",
        )
        write(os.path.join(OUTPUT_DIR, prose["slug"], "index.html"), html)
        routes.append(page_url)

    # Friendly redirect: /concepts/ -> /docs/concepts/
    write(os.path.join(OUTPUT_DIR, "concepts", "index.html"),
          _redirect_html(f"{base_url}/docs/concepts/"))

    # ── Static assets ──────────────────────────────────────────────────────
    assets_dir = os.path.join(OUTPUT_DIR, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    shutil.copy(os.path.join(TEMPLATES_DIR, "style.css"), os.path.join(assets_dir, "style.css"))
    shutil.copy(os.path.join(TEMPLATES_DIR, "filter.js"), os.path.join(assets_dir, "filter.js"))
    # Web app manifest sits at site root, not under assets/
    shutil.copy(os.path.join(TEMPLATES_DIR, "manifest.webmanifest"), os.path.join(OUTPUT_DIR, "manifest.webmanifest"))

    # ── sitemap.xml + robots.txt ───────────────────────────────────────────
    write(os.path.join(OUTPUT_DIR, "sitemap.xml"), _sitemap(canonical_root, routes))
    write(os.path.join(OUTPUT_DIR, "robots.txt"),
          f"User-agent: *\nAllow: /\nSitemap: {canonical_root}/sitemap.xml\n")

    print(f"[build] {len(skills)} skills, {len(categories)} categories, "
          f"{len(tag_indexes)} tags -> {os.path.relpath(OUTPUT_DIR, REPO_ROOT)}/")
    print(f"[build] base_url={base_url!r}  canonical_root={canonical_root!r}")


def _sitemap(canonical_root: str, routes: List[str]) -> str:
    today = _dt.date.today().isoformat()
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for r in routes:
        parts.append("  <url>")
        parts.append(f"    <loc>{canonical_root}{r}</loc>")
        parts.append(f"    <lastmod>{today}</lastmod>")
        parts.append("  </url>")
    parts.append("</urlset>")
    return "\n".join(parts) + "\n"


def _redirect_html(target: str) -> str:
    return (
        "<!DOCTYPE html><meta charset='utf-8'>"
        f"<meta http-equiv='refresh' content='0; url={target}'>"
        f"<link rel='canonical' href='{target}'>"
        f"<p>Redirecting to <a href='{target}'>{target}</a>.</p>"
    )


# ──────────────────────────────────────────────────────────────────────────
# Local serve
# ──────────────────────────────────────────────────────────────────────────
def serve(port: int = 8000) -> None:
    os.chdir(OUTPUT_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/"
        print(f"[serve] {url}  (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[serve] stopped")


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="Build the agentskills-garden site.")
    ap.add_argument("--serve", action="store_true",
                    help="serve the built site locally on port 8000 after building")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    base_url = os.environ.get("BASE_URL", "")
    canonical_root = os.environ.get("CANONICAL_ROOT", DEFAULT_CANONICAL)

    render_site(base_url=base_url, canonical_root=canonical_root)

    if args.serve:
        serve(args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
