#!/usr/bin/env python3
"""
benchmark.py — prove the architecture stays cheap at thousands of skills.

Generates N synthetic skills into a scratch tree (.bench/, gitignored — never
the real skills/), runs the REAL build against it via build.py's
--skills-dir/--out-dir overrides, and measures the metrics that matter for
token-efficient agent discovery:

  * Tier-0 MAP.md size           — must stay tiny regardless of N
  * largest Tier-1 file size     — bounded by skills-per-category
  * single-skill lookup cost     — MAP.md + one Tier-1 + one SKILL.md
                                   (what an agent actually loads per task)
  * build time, total _site size, search-index.json size

The synthetic generator mirrors real authoring discipline: as the garden grows
you add CATEGORIES (and domains), keeping ~25 skills per category — you do NOT
pile thousands into one bucket. That is exactly what keeps each Tier-1 file (and
therefore each lookup) bounded. The benchmark demonstrates that property.

Usage:
  python scripts/benchmark.py                 # counts 1000, 5000
  python scripts/benchmark.py --counts 1000   # single run
  python scripts/benchmark.py --counts 500,2000,5000
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from typing import Dict, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
BENCH_DIR = os.path.join(REPO_ROOT, ".bench")
BUILD_SCRIPT = os.path.join(SCRIPT_DIR, "build.py")

NON_FLAT_DOMAINS = ["engineering", "writing", "data-ml", "business"]
FOUNDATION_MAX = 20
SKILLS_PER_CAT = 25  # authoring discipline: keep categories small, add more of them

_BODY = ("\n## Context\n" + ("Synthetic skill body for benchmarking. " * 12) +
         "\n\n## Micro-Skills\n" + ("Step text. " * 20) +
         "\n\n## Guardrails\n" + ("Constraint. " * 14) +
         "\n\n## Examples\n" + ("Example line. " * 16) + "\n")


def _skill_md(name: str, domain: str, category: str | None) -> str:
    desc = (f"Synthetic {domain} skill {name}: exercises the build and tiered "
            f"index at scale with a realistic description length for search.")
    tags = ("[core, principles, advisory]" if domain == "foundation"
            else "[category, build, coding, reversible]")
    cat_line = f"category: {category}\n" if category else ""
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {desc}\n"
        "license: Apache-2.0\n"
        f"domain: {domain}\n"
        f"{cat_line}"
        "status: published\n"
        f"tags: {tags}\n"
        f"keywords: [{name}, synthetic, benchmark]\n"
        "metadata:\n"
        "  version: 1.0.0\n"
        "  skill_type: standard\n"
        "---\n\n"
        f"# {name}\n"
        + _BODY
    )


def generate(count: int, skills_dir: str) -> int:
    if os.path.isdir(skills_dir):
        shutil.rmtree(skills_dir)
    n_written = 0

    # Foundation (flat, small — like the real garden).
    n_found = min(FOUNDATION_MAX, count)
    for i in range(n_found):
        name = f"foundation-{i:05d}"
        d = os.path.join(skills_dir, "000-foundation", name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
            fh.write(_skill_md(name, "foundation", None))
        n_written += 1

    remaining = count - n_found
    prefixes = {"engineering": "100", "writing": "200", "data-ml": "300", "business": "400"}
    # round-robin remaining across non-flat domains
    per_domain = [remaining // len(NON_FLAT_DOMAINS)] * len(NON_FLAT_DOMAINS)
    for i in range(remaining % len(NON_FLAT_DOMAINS)):
        per_domain[i] += 1

    for di, domain in enumerate(NON_FLAT_DOMAINS):
        dn = per_domain[di]
        n_cats = max(1, -(-dn // SKILLS_PER_CAT))  # ceil
        for c in range(n_cats):
            cat = f"{(c + 1) * 10}-cat{c}"
            start = c * SKILLS_PER_CAT
            for k in range(start, min(start + SKILLS_PER_CAT, dn)):
                name = f"{domain}-{k:05d}"
                d = os.path.join(skills_dir, f"{prefixes[domain]}-{domain}", cat, name)
                os.makedirs(d, exist_ok=True)
                with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
                    fh.write(_skill_md(name, domain, cat))
                n_written += 1
    return n_written


def _dir_size(path: str) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    return total


def _avg_skill_bytes(skills_dir: str, sample: int = 200) -> float:
    sizes, seen = [], 0
    for root, _dirs, files in os.walk(skills_dir):
        if "_index" in root:
            continue
        if "SKILL.md" in files:
            sizes.append(os.path.getsize(os.path.join(root, "SKILL.md")))
            seen += 1
            if seen >= sample:
                break
    return sum(sizes) / len(sizes) if sizes else 0.0


def _largest_tier1(index_dir: str) -> int:
    """Largest per-category skill table (excludes MAP.md and domain INDEX.md)."""
    largest = 0
    for root, _dirs, files in os.walk(index_dir):
        for f in files:
            if f.endswith(".md") and f not in ("MAP.md", "INDEX.md"):
                largest = max(largest, os.path.getsize(os.path.join(root, f)))
    return largest


def _largest_domain_index(index_dir: str) -> int:
    """Largest per-domain category list (Tier-0.5 INDEX.md)."""
    largest = 0
    for root, _dirs, files in os.walk(index_dir):
        if "INDEX.md" in files:
            largest = max(largest, os.path.getsize(os.path.join(root, "INDEX.md")))
    return largest


def measure(skills_dir: str, out_dir: str, count: int) -> Dict:
    index_dir = os.path.join(skills_dir, "_index")
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, BUILD_SCRIPT, "--skills-dir", skills_dir, "--out-dir", out_dir],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    build_s = time.perf_counter() - t0
    if proc.returncode != 0:
        print(proc.stdout); print(proc.stderr)
        raise RuntimeError(f"build failed for N={count}")

    map_b = os.path.getsize(os.path.join(index_dir, "MAP.md"))
    tier1_b = _largest_tier1(index_dir)
    dindex_b = _largest_domain_index(index_dir)
    avg_skill_b = _avg_skill_bytes(skills_dir)
    search_b = os.path.getsize(os.path.join(out_dir, "search-index.json"))
    site_b = _dir_size(out_dir)
    # Worst-case lookup an agent loads: MAP + one domain index + one category
    # table + one SKILL.md.
    lookup_b = map_b + dindex_b + tier1_b + avg_skill_b
    return {
        "count": count,
        "build_s": round(build_s, 2),
        "site_mb": round(site_b / 1024 / 1024, 2),
        "search_kb": round(search_b / 1024, 1),
        "map_bytes": map_b,
        "largest_domain_index_bytes": dindex_b,
        "largest_tier1_bytes": tier1_b,
        "avg_skill_bytes": int(avg_skill_b),
        "lookup_bytes": int(lookup_b),
        "lookup_tokens": int(lookup_b / 4),  # ~4 bytes/token
    }


def baseline_real() -> Dict | None:
    """Measure the real garden (current N) from its committed _index, for the
    flatness comparison row. None if the real index hasn't been built."""
    skills_dir = os.path.join(REPO_ROOT, "skills")
    index_dir = os.path.join(skills_dir, "_index")
    if not os.path.isfile(os.path.join(index_dir, "MAP.md")):
        return None
    count = sum(1 for r, _d, f in os.walk(skills_dir) if "SKILL.md" in f and "_index" not in r)
    map_b = os.path.getsize(os.path.join(index_dir, "MAP.md"))
    tier1_b = _largest_tier1(index_dir)
    dindex_b = _largest_domain_index(index_dir)
    avg_skill_b = _avg_skill_bytes(skills_dir)
    lookup_b = map_b + dindex_b + tier1_b + avg_skill_b
    return {
        "count": count, "build_s": None, "site_mb": None, "search_kb": None,
        "map_bytes": map_b, "largest_domain_index_bytes": dindex_b,
        "largest_tier1_bytes": tier1_b, "avg_skill_bytes": int(avg_skill_b),
        "lookup_bytes": int(lookup_b), "lookup_tokens": int(lookup_b / 4),
    }


def write_report(rows: List[Dict], verdicts: List[str]) -> None:
    os.makedirs(BENCH_DIR, exist_ok=True)
    hdr = ("| N skills | build (s) | site (MB) | search idx (KB) | Tier-0 MAP | "
           "domain index | largest Tier-1 | avg SKILL.md | lookup bytes | lookup ~tokens |")
    sep = "|" + "---|" * 10
    lines = ["# Scaling benchmark report (generated)", "",
             "Single-skill lookup = Tier-0 MAP.md + one domain index + one category "
             "Tier-1 table + one SKILL.md — what an agent loads per task. It should "
             "stay ~flat as N grows.", "",
             hdr, sep]
    for r in rows:
        lines.append("| {count} | {build_s} | {site_mb} | {search_kb} | {map_bytes} B | "
                     "{largest_domain_index_bytes} B | {largest_tier1_bytes} B | "
                     "{avg_skill_bytes} B | {lookup_bytes} B | {lookup_tokens} |".format(**r))
    lines += ["", "## Verdicts", ""] + [f"- {v}" for v in verdicts] + [""]
    with open(os.path.join(BENCH_DIR, "report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    with open(os.path.join(BENCH_DIR, "report.json"), "w", encoding="utf-8") as fh:
        json.dump({"rows": rows, "verdicts": verdicts}, fh, indent=2)


def main() -> int:
    ap = argparse.ArgumentParser(description="Benchmark the garden at scale.")
    ap.add_argument("--counts", default="1000,5000",
                    help="comma-separated skill counts to generate (default 1000,5000)")
    args = ap.parse_args()
    counts = [int(c) for c in args.counts.split(",") if c.strip()]

    rows: List[Dict] = []
    base = baseline_real()
    if base:
        base = dict(base); base["_label"] = "current (real)"
        rows.append(base)
        print(f"[bench] baseline (real): N={base['count']} "
              f"lookup~{base['lookup_tokens']} tokens")

    skills_dir = os.path.join(BENCH_DIR, "skills")
    out_dir = os.path.join(BENCH_DIR, "_site")
    for n in counts:
        print(f"[bench] generating {n} synthetic skills…")
        written = generate(n, skills_dir)
        print(f"[bench] building {written} skills…")
        r = measure(skills_dir, out_dir, n)
        rows.append(r)
        print(f"[bench] N={n}: build {r['build_s']}s, MAP {r['map_bytes']}B, "
              f"largest Tier-1 {r['largest_tier1_bytes']}B, "
              f"lookup ~{r['lookup_tokens']} tokens")

    # ── verdicts ───────────────────────────────────────────────────────────
    verdicts: List[str] = []
    max_map = max(r["map_bytes"] for r in rows)
    max_di = max(r["largest_domain_index_bytes"] for r in rows)
    max_t1 = max(r["largest_tier1_bytes"] for r in rows)
    verdicts.append(("PASS" if max_map < 4096 else "FAIL")
                    + f": Tier-0 MAP.md stays < 4 KB (max {max_map} B)")
    verdicts.append(("PASS" if max_di < 16384 else "FAIL")
                    + f": largest domain index stays < 16 KB (max {max_di} B)")
    verdicts.append(("PASS" if max_t1 < 8192 else "FAIL")
                    + f": largest Tier-1 stays < 8 KB (max {max_t1} B)")
    if base:
        biggest = max(rows, key=lambda r: r["count"])
        ratio = biggest["lookup_tokens"] / base["lookup_tokens"] if base["lookup_tokens"] else 0
        verdicts.append(("PASS" if ratio <= 1.5 else "FAIL")
                        + f": lookup cost at N={biggest['count']} is {ratio:.2f}x the "
                          f"real N={base['count']} baseline (flatness; target <= 1.5x)")

    write_report(rows, verdicts)
    print("\n".join(["", "Verdicts:"] + ["  " + v for v in verdicts]))
    print(f"\n[bench] report -> {os.path.relpath(os.path.join(BENCH_DIR, 'report.md'), REPO_ROOT)}")
    # clean the bulky synthetic tree, keep the report
    if os.path.isdir(skills_dir): shutil.rmtree(skills_dir)
    if os.path.isdir(out_dir): shutil.rmtree(out_dir)
    return 0 if all(v.startswith("PASS") for v in verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
