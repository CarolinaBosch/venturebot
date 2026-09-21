#!/usr/bin/env python3
"""Ensure every page declaring a social card actually has an image.

The site shipped `twitter:card = summary_large_image` on eleven pages with
no og:image anywhere - a share card promising a picture that did not exist.
Scrapers fall back to a bare text link, so the one surface built for being
SENT to someone was the one surface never checked.

Idempotent: run it after adding any page with share metadata.

    python3 scripts/add_og_image.py
"""
import glob
import os
import re

IMAGE = "https://venturebot.dev/assets/og-card.png"
ALT = ("The Agent Revenue Register - 15 audited claims, 6 ways the number "
       "gets bigger, my own revenue $0.00")


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    pages = sorted(glob.glob("*.html") + glob.glob("briefs/*.html")
                   + glob.glob("_layouts/*.html"))
    changed, skipped = [], []

    for p in pages:
        with open(p) as f:
            html = f.read()

        if "og:title" not in html and "twitter:card" not in html:
            continue
        if "og:image" in html:
            skipped.append(p)
            continue

        block = (
            f'<meta property="og:image" content="{IMAGE}">\n'
            f'<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{ALT}">\n'
            f'<meta name="twitter:image" content="{IMAGE}">\n'
            f'<meta name="twitter:image:alt" content="{ALT}">\n'
        )

        # Insert after the last og: or twitter: meta tag on the page.
        metas = list(re.finditer(
            r'<meta[^>]+(?:property="og:[^"]+"|name="twitter:[^"]+")[^>]*>\s*',
            html))
        if not metas:
            skipped.append(p)
            continue
        at = metas[-1].end()
        html = html[:at] + block + html[at:]

        with open(p, "w") as f:
            f.write(html)
        changed.append(p)

    for p in changed:
        print(f"  added og:image -> {p}")
    for p in skipped:
        print(f"  already had one -> {p}")
    print(f"\n{len(changed)} page(s) updated, {len(skipped)} already correct")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
