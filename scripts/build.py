"""
build.py — Static site generator for agentskills-garden.

Reads registry.yaml + skills/**/SKILL.md + docs/**/*.md and emits a static
site to _site/. Open-closed: adding a skill or category does not require
touching this script. The 5-axis tag taxonomy is consumed from
scripts/taxonomy.py (the same source of truth validate.py uses).

Usage:
  python scripts/build.py            # build to _site/
  python scripts/build.py --serve    # build then serve at :8000

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

# Local helper modules — same vocab + parsing the validator uses.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from taxonomy import (  # noqa: E402
    AXES, classify, REGISTERED_DOMAINS, FLAT_DOMAINS, domain_folder,
)
from skill_lib import walk_skills  # noqa: E402

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
INDEX_DIR = os.path.join(SKILLS_DIR, "_index")  # generated tiered index (committed)
REGISTRY_JSON_PATH = os.path.join(REPO_ROOT, "registry.json")
SEARCH_INDEX_PATH = os.path.join(OUTPUT_DIR, "search-index.json")

REGISTRY_VERSION = "4.0.0"  # v4 = frontmatter-as-source, generated registry

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

# Optional pretty-name overrides. Any folder not listed here derives its display
# name from the folder slug (open-closed: a new category/domain needs no edit).
CATEGORY_DISPLAY = {
    "10-discovery":    "Discovery",
    "20-architecture": "Architecture",
    "20-planning":     "Planning",
    "25-pragmatism":   "Pragmatism",
    "30-implementation": "Implementation",
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

DOMAIN_DISPLAY = {
    "foundation":  "Foundation",
    "engineering": "Engineering",
    "writing":     "Writing",
    "data-ml":     "Data & ML",
    "business":    "Business",
}


def display_name(slug: str, override: Dict[str, str]) -> str:
    """Pretty name for a folder/domain slug, with optional override map."""
    if slug in override:
        return override[slug]
    # '30-implementation' -> 'Implementation'; 'data-ml' -> 'Data Ml'
    tail = slug.split("-", 1)[-1] if slug[:2].isdigit() else slug
    return tail.replace("-", " ").title()

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
    """Group tags by the axis they belong to (per scripts/taxonomy.py)."""
    out = {axis: [] for axis in AXES}
    for tag in tags:
        axis = classify(str(tag))
        if axis:
            out[axis].append(str(tag))
    return out


def _norm(text: str) -> str:
    """Collapse whitespace (block-scalar descriptions span lines)."""
    return " ".join(str(text or "").split())


def build_skill(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Build a render-ready skill dict from a walk_skills() record. Frontmatter
    is the source of truth for tags/description/keywords/status/domain."""
    fm = rec["fm"]
    body = rec["body"]
    name = fm.get("name") or rec["dir_name"]
    rel_path = rec["rel_path"]
    tags = list(fm.get("tags") or [])
    keywords = [str(k) for k in (fm.get("keywords") or [])]

    meta = (fm.get("metadata") or {}) if isinstance(fm, dict) else {}
    deps_raw = meta.get("dependencies") or ""
    deps = [d.strip() for d in str(deps_raw).split(",") if d.strip()]

    title = extract_h1(body) or name
    first_html = md_to_html(extract_first_section_md(body))
    sections = list_section_headings(body)
    preview_sections = sections[1:9] if len(sections) > 1 else []

    description = _norm(fm.get("description", ""))
    domain = rec["domain"]
    category_dir = rec["category_dir"] or ""
    category = rec["category"] or ""

    return {
        "name": name,
        "description": description,
        "tags": tags,
        "axes": axis_split(tags),
        "keywords": keywords,
        "status": str(fm.get("status", "published")),
        "reasoning_mode": str(meta.get("reasoning_mode", "")),
        "domain": domain,
        "domain_name": display_name(domain, DOMAIN_DISPLAY),
        "category_dir": category_dir,
        "category": category,
        "category_name": display_name(category_dir, CATEGORY_DISPLAY) if category_dir else "",
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
        "search_text": " ".join([name, description, " ".join(keywords), " ".join(tags)]).lower(),
    }


# Statuses that appear on the public site / in search.
_PUBLIC_STATUSES = {"published", "deprecated"}


def load_skills() -> List[Dict[str, Any]]:
    """Frontmatter-driven discovery: walk skills/ and build every public skill.
    Replaces the old registry-driven load_registry()."""
    skills = [build_skill(rec) for rec in walk_skills(SKILLS_DIR)]
    skills = [s for s in skills if s["status"] in _PUBLIC_STATUSES]
    skills.sort(key=lambda s: (s["domain"], s["category_dir"], s["name"]))
    return skills


def build_categories(skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_dir: Dict[str, List[Dict[str, Any]]] = {}
    domain_of: Dict[str, str] = {}
    for s in skills:
        if not s["category_dir"]:
            continue
        by_dir.setdefault(s["category_dir"], []).append(s)
        domain_of[s["category_dir"]] = s["domain"]
    cats = []
    for d, ss in sorted(by_dir.items()):
        cats.append({
            "dir": d,
            "name": display_name(d, CATEGORY_DISPLAY),
            "domain": domain_of[d],
            "domain_name": display_name(domain_of[d], DOMAIN_DISPLAY),
            "skills": ss,
            "count": len(ss),
        })
    return cats


def build_domains(skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group skills by top-level domain, preserving REGISTERED_DOMAINS order."""
    by_domain: Dict[str, List[Dict[str, Any]]] = {}
    for s in skills:
        by_domain.setdefault(s["domain"], []).append(s)

    order = list(REGISTERED_DOMAINS.keys())
    def dkey(d: str) -> int:
        return order.index(d) if d in order else len(order)

    domains = []
    for d in sorted(by_domain, key=dkey):
        ss = sorted(by_domain[d], key=lambda s: (s["category_dir"], s["name"]))
        cat_dirs = sorted({s["category_dir"] for s in ss if s["category_dir"]})
        domains.append({
            "slug": d,
            "name": display_name(d, DOMAIN_DISPLAY),
            "folder": domain_folder(d) or d,
            "skills": ss,
            "count": len(ss),
            "categories": [
                {"dir": cd, "name": display_name(cd, CATEGORY_DISPLAY),
                 "count": sum(1 for s in ss if s["category_dir"] == cd)}
                for cd in cat_dirs
            ],
        })
    return domains


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
    weight_axes = {"lifecycle", "capability", "stack"}
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
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


# ──────────────────────────────────────────────────────────────────────────
# Generated artifacts: tiered index, registry, search index
# ──────────────────────────────────────────────────────────────────────────
def _md_cell(text: str) -> str:
    """Escape a value for a markdown table cell."""
    return _norm(text).replace("|", "\\|")


def _tier1_table(skills: List[Dict[str, Any]]) -> str:
    rows = ["| skill | what it does | keywords | path |",
            "|---|---|---|---|"]
    for s in sorted(skills, key=lambda s: s["name"]):
        kw = ", ".join(s["keywords"])
        rows.append(f"| {s['name']} | {_md_cell(s['description'])} | "
                    f"{_md_cell(kw)} | {s['rel_path']} |")
    return "\n".join(rows) + "\n"


def generate_index(domains: List[Dict[str, Any]]) -> Dict[str, int]:
    """Write the tiered discovery index under skills/_index/:
      Tier 0  MAP.md                  domains -> categories (always-load map)
      Tier 1  <domain>/<cat>.md       per-category skill tables (load on demand)
              <domain>.md             flat domains (foundation)
      plus    index.json             flat machine-readable mirror
    Returns size stats for the build log / benchmark."""
    if os.path.isdir(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)
    os.makedirs(INDEX_DIR, exist_ok=True)

    # ── The map (MAP.md) — DOMAINS ONLY, so it stays tiny no matter how many ─
    #    skills/categories exist — it grows only with the number of domains. ──
    #    Every domain links to its own <domain>/INDEX.md (consistent shape).
    lines = ["# Skill Garden Map (generated — do not edit)", "",
             "Pick a domain and open its INDEX. A flat domain's INDEX lists its "
             "skills directly; other domains' INDEX lists categories, and each "
             "category file lists its skills. Paths are relative to this folder.",
             "", "Navigation: map -> domain index -> category index -> skill.", ""]
    for dom in domains:
        flat = dom["slug"] in FLAT_DOMAINS or not dom["categories"]
        suffix = "" if flat else f", {len(dom['categories'])} categories"
        lines.append(f"## {dom['slug']} ({dom['count']} skills{suffix})  ->  {dom['slug']}/INDEX.md")
    write(os.path.join(INDEX_DIR, "MAP.md"), "\n".join(lines) + "\n")

    # ── Domain index (<domain>/INDEX.md) + category index (<domain>/<cat>.md) ─
    largest_category_index = 0   # largest per-category SKILL table
    largest_domain_index = 0     # largest per-domain index file
    for dom in domains:
        flat = dom["slug"] in FLAT_DOMAINS or not dom["categories"]
        if flat:
            # Flat domain: its INDEX.md IS the skill table.
            content = (f"# {dom['name']} skills (generated)\n\n"
                       + _tier1_table(dom["skills"]))
            write(os.path.join(INDEX_DIR, dom["slug"], "INDEX.md"), content)
            largest_domain_index = max(largest_domain_index, len(content.encode("utf-8")))
            continue
        # Domain index: lists the domain's categories.
        idx = [f"# {dom['name']} categories (generated)", ""]
        for cat in dom["categories"]:
            idx.append(f"- {cat['dir']} ({cat['count']} skills)  ->  {cat['dir']}.md")
        idx_content = "\n".join(idx) + "\n"
        write(os.path.join(INDEX_DIR, dom["slug"], "INDEX.md"), idx_content)
        largest_domain_index = max(largest_domain_index, len(idx_content.encode("utf-8")))
        # Category index: one skill table per category.
        for cat in dom["categories"]:
            cat_skills = [s for s in dom["skills"] if s["category_dir"] == cat["dir"]]
            content = (f"# {dom['name']} / {cat['name']} (generated)\n\n"
                       + _tier1_table(cat_skills))
            write(os.path.join(INDEX_DIR, dom["slug"], f"{cat['dir']}.md"), content)
            largest_category_index = max(largest_category_index, len(content.encode("utf-8")))

    # ── index.json — flat machine-readable mirror ──────────────────────────
    flat_rows = []
    for dom in domains:
        for s in dom["skills"]:
            flat_rows.append({
                "name": s["name"], "domain": s["domain"], "category": s["category"],
                "status": s["status"], "description": s["description"],
                "keywords": s["keywords"], "tags": s["tags"], "path": s["rel_path"],
            })
    write(os.path.join(INDEX_DIR, "index.json"),
          json.dumps(flat_rows, indent=2, ensure_ascii=False) + "\n")

    map_bytes = os.path.getsize(os.path.join(INDEX_DIR, "MAP.md"))
    return {"map_bytes": map_bytes, "largest_category_index_bytes": largest_category_index,
            "largest_domain_index_bytes": largest_domain_index, "skills": len(flat_rows)}


def generate_registry(domains: List[Dict[str, Any]]) -> None:
    """Emit a GENERATED registry.yaml + registry.json for back-compat
    (skills_loader.py and external consumers). Frontmatter is the real source;
    this is a derived artifact — never hand-edit it."""
    sections: Dict[str, List[Dict[str, Any]]] = {}
    for dom in domains:
        for s in dom["skills"]:
            section = s["category"] or s["domain"]
            sections.setdefault(section, []).append({
                "name": s["name"],
                "path": s["rel_path"],
                "description": s["description"],
                "domain": s["domain"],
                "tags": s["tags"],
                "reasoning_mode": s["reasoning_mode"],
                "status": s["status"],
            })

    data: Dict[str, Any] = {"version": REGISTRY_VERSION}
    data.update(sections)

    header = ("# ==========================================================================\n"
              "# GENERATED by scripts/build.py — DO NOT EDIT.\n"
              "# Source of truth is each skill's SKILL.md frontmatter. Re-run the build\n"
              "# to regenerate. Kept for back-compat with skills_loader.py / consumers.\n"
              "# ==========================================================================\n")
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)
    write(REGISTRY_PATH, header + body)
    write(REGISTRY_JSON_PATH, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def generate_search_index(skills: List[Dict[str, Any]], base_url: str) -> None:
    """Emit _site/search-index.json for client-side fuzzy search."""
    rows = [{
        "name": s["name"], "domain": s["domain"], "category": s["category"],
        "description": s["description"], "keywords": s["keywords"],
        "tags": s["tags"], "status": s["status"],
        "reasoning_mode": s["reasoning_mode"], "version": s["version"],
        "url": f"{base_url}/skills/{s['name']}/",
    } for s in skills if s["status"] != "draft"]
    write(SEARCH_INDEX_PATH, json.dumps(rows, ensure_ascii=False))


def render_site(base_url: str, canonical_root: str) -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=False,
        lstrip_blocks=False,
    )

    skills = load_skills()
    categories = build_categories(skills)
    domains = build_domains(skills)
    tag_indexes = build_tag_indexes(skills)
    axes_choices = build_axis_choices(skills)

    scope_set = set(AXES["scope"])

    # Generated artifacts (committed into the repo, not just _site/).
    index_stats = generate_index(domains)
    generate_registry(domains)

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
        "domain_count": len(domains),
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
        domains=domains,
        axes=axes_choices,
        pillars=PILLARS,
        prose_docs=[{"slug": p["slug"], "title": p["title"], "subtitle": p["subtitle"]}
                    for p in PROSE_PAGES],
    )
    write(os.path.join(OUTPUT_DIR, "index.html"), home_html)
    routes.append("/")

    # ── Domain pages ─────────────────────────────────────────────────────────
    for dom in domains:
        page_url = f"/domains/{dom['slug']}/"
        html = env.get_template("domain.html").render(
            **common,
            page_url=page_url,
            domain=dom,
            skills=dom["skills"],
        )
        write(os.path.join(OUTPUT_DIR, "domains", dom["slug"], "index.html"), html)
        routes.append(page_url)

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
    # Web app manifest + service worker sit at site root, not under assets/
    shutil.copy(os.path.join(TEMPLATES_DIR, "manifest.webmanifest"), os.path.join(OUTPUT_DIR, "manifest.webmanifest"))
    if os.path.exists(os.path.join(TEMPLATES_DIR, "sw.js")):
        shutil.copy(os.path.join(TEMPLATES_DIR, "sw.js"), os.path.join(OUTPUT_DIR, "sw.js"))
    # PWA icons (192/512/maskable + apple-touch)
    if os.path.isdir(os.path.join(TEMPLATES_DIR, "icons")):
        shutil.copytree(os.path.join(TEMPLATES_DIR, "icons"), os.path.join(OUTPUT_DIR, "icons"), dirs_exist_ok=True)
    # OG image for social sharing
    if os.path.exists(os.path.join(TEMPLATES_DIR, "og-image.png")):
        shutil.copy(os.path.join(TEMPLATES_DIR, "og-image.png"), os.path.join(OUTPUT_DIR, "og-image.png"))

    # ── Search index (client-side fuzzy search) ────────────────────────────
    generate_search_index(skills, base_url)

    # ── Mirror the tiered index into the published site ─────────────────────
    if os.path.isdir(INDEX_DIR):
        shutil.copytree(INDEX_DIR, os.path.join(OUTPUT_DIR, "index"))

    # ── sitemap.xml + robots.txt ───────────────────────────────────────────
    write(os.path.join(OUTPUT_DIR, "sitemap.xml"), _sitemap(canonical_root, routes))
    write(os.path.join(OUTPUT_DIR, "robots.txt"),
          f"User-agent: *\nAllow: /\nSitemap: {canonical_root}/sitemap.xml\n")

    print(f"[build] {len(skills)} skills, {len(domains)} domains, {len(categories)} categories, "
          f"{len(tag_indexes)} tags -> {os.path.relpath(OUTPUT_DIR, REPO_ROOT)}/")
    print(f"[index] Tier-0 MAP.md={index_stats['map_bytes']}B  "
          f"largest domain-index={index_stats['largest_domain_index_bytes']}B  "
          f"largest category-index={index_stats['largest_category_index_bytes']}B")
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
    ap.add_argument("--skills-dir", help="override the skills/ source dir (used by benchmark.py)")
    ap.add_argument("--out-dir", help="override the _site/ output dir; also redirects "
                                      "the generated index/registry there (keeps the real ones safe)")
    args = ap.parse_args()

    # Path overrides for isolated builds (benchmark / experiments). Reassign the
    # module globals the rest of the build reads.
    global SKILLS_DIR, INDEX_DIR, OUTPUT_DIR, SEARCH_INDEX_PATH, REGISTRY_PATH, REGISTRY_JSON_PATH
    if args.skills_dir:
        SKILLS_DIR = os.path.abspath(args.skills_dir)
        INDEX_DIR = os.path.join(SKILLS_DIR, "_index")
    if args.out_dir:
        OUTPUT_DIR = os.path.abspath(args.out_dir)
        SEARCH_INDEX_PATH = os.path.join(OUTPUT_DIR, "search-index.json")
        # keep the real registry.yaml safe — write the isolated build's into out-dir
        REGISTRY_PATH = os.path.join(OUTPUT_DIR, "registry.yaml")
        REGISTRY_JSON_PATH = os.path.join(OUTPUT_DIR, "registry.json")

    base_url = os.environ.get("BASE_URL", "")
    canonical_root = os.environ.get("CANONICAL_ROOT", DEFAULT_CANONICAL)

    render_site(base_url=base_url, canonical_root=canonical_root)

    if args.serve:
        serve(args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
