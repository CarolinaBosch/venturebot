#!/usr/bin/env python3
"""Rewrite the storefront's USD conversion from runway.json.

Written 2026-09-30. Of the last 14 commits touching audits.html, SEVEN were
corrective resyncs of one sentence: "Roughly $X at SOL $Y". Every wake
updates runway.json, verify_site check 3 then fails, and a follow-up commit
fixes the storefront by hand.

That is the defect the register documents in other people - a figure typed
by hand where every neighbouring figure is computed. The count on this same
page is already generated; the price was not.

This derives the sentence from runway.json, so the storefront cannot drift
from the canonical price by construction.

    /usr/bin/python3 scripts/sync_storefront.py
"""
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRICE_RE = re.compile(
    r"Roughly \$[\d,]+\.\d{2} at SOL \$[\d,]+\.\d{2} \(\d{4}-\d{2}-\d{2}\)")


def main():
    runway = json.loads((ROOT / "runway.json").read_text())
    sol = float(runway["sol_price_usd"])
    stamp = runway["updated"][:10]
    commission = round(0.1 * sol, 2)

    replacement = f"Roughly ${commission:,.2f} at SOL ${sol:,.2f} ({stamp})"

    page = ROOT / "audits.html"
    html = page.read_text()
    found = PRICE_RE.findall(html)

    if not found:
        print("FAIL: could not locate the price sentence in audits.html.")
        print("      The wording changed; update PRICE_RE rather than")
        print("      hand-editing the page, or this drifts again.")
        return 1

    if all(f == replacement for f in found):
        print(f"already in sync: {replacement}")
        return 0

    html = PRICE_RE.sub(replacement, html)
    page.write_text(html)
    for old in dict.fromkeys(found):
        print(f"  {old}  ->  {replacement}")
    print(f"\nrewrote {len(found)} occurrence(s) in audits.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
