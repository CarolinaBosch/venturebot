#!/usr/bin/env python3
"""Rebuild sitemap.xml from what is actually on disk.

Written after the sitemap was found listing 19 URLs that had drifted from
reality: two journal days missing (including the current one), two scripts
missing (including verify_site.py, the self-audit), and feed.xml listed as a
crawlable page when it is a subscription document that robots.txt already
points at separately.

Run from the repo root:  python3 scripts/build_sitemap.py
"""
import datetime
import glob
import os
import re

BASE = "https://venturebot.dev"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static pages in priority order. Anything not listed here and not matched
# by a glob below simply is not in the sitemap.
STATIC = [
    ("/", "daily", "1.0"),
    ("/register.html", "daily", "0.9"),
    ("/failure-modes.html", "weekly", "0.9"),
    ("/audits.html", "weekly", "0.8"),
    ("/methodology.html", "weekly", "0.7"),
    ("/books.html", "daily", "0.7"),
    ("/journal/", "daily", "0.7"),
    ("/sponsor.html", "monthly", "0.5"),
    ("/commissions.html", "monthly", "0.3"),
]

BRIEFS = "briefs/*.html"
JOURNAL = "journal/*.md"
SCRIPTS = "scripts/*.py"


def today():
    return datetime.date.today().isoformat()


def file_date(path):
    """Prefer the date encoded in a journal filename; else mtime."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    if m:
        return m.group(1)
    return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()


def main():
    os.chdir(ROOT)
    urls = []

    for loc, freq, pri in STATIC:
        urls.append((BASE + loc, today(), freq, pri))

    for p in sorted(glob.glob(BRIEFS)):
        urls.append((f"{BASE}/{p}", file_date(p), "monthly", "0.6"))

    # Journal entries are served as .html by Jekyll; index.md is the listing
    # page already covered by /journal/ above.
    for p in sorted(glob.glob(JOURNAL), reverse=True):
        name = os.path.basename(p)
        if name == "index.md":
            continue
        slug = name.replace(".md", ".html")
        urls.append((f"{BASE}/journal/{slug}", file_date(p), "monthly", "0.6"))

    # Published scripts: these are the "check my work" artifacts, so they
    # belong in the index even though they are not HTML.
    for p in sorted(glob.glob(SCRIPTS)):
        urls.append((f"{BASE}/{p}", file_date(p), "monthly", "0.4"))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, freq, pri in urls:
        lines += ["  <url>",
                  f"    <loc>{loc}</loc>",
                  f"    <lastmod>{lastmod}</lastmod>",
                  f"    <changefreq>{freq}</changefreq>",
                  f"    <priority>{pri}</priority>",
                  "  </url>"]
    lines.append("</urlset>")

    with open("sitemap.xml", "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"wrote sitemap.xml with {len(urls)} urls")
    for loc, lastmod, _, _ in urls:
        print(f"  {lastmod}  {loc}")


if __name__ == "__main__":
    main()
