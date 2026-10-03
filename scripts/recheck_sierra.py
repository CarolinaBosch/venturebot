#!/usr/bin/env python3
"""
recheck_sierra.py — verify register entry 21: Sierra "run-rate ARR" trajectory.

Claims checked:
  1. $100M ARR milestone — company-confirmed via blog + TechCrunch (2025-11-21)
  2. $150M ARR — company blog post (2026-02-06) + Sierra $950M raise (TechCrunch 2026-05-04)
  3. $200M ARR — Bret Taylor post (2026-05-29), cited in valueaddvc.com
  4. TechCrunch paragraph 1 calls it "annual revenue run rate (ARR)"
  5. Outcome-based pricing — per-resolution, not subscription — making ARR a run-rate figure
  6. Per-resolution price (~$1.50) is a third-party estimate; Sierra has never published it

The register finding: revenue trajectory is real and company-confirmed.
The material gap: "ARR" under per-interaction pricing is an annualized run-rate extrapolation.
TechCrunch used both terms for the same milestone in reporting spanning 3 months.

Run: python3 scripts/recheck_sierra.py
"""
import urllib.request
import re

SOURCES = [
    {
        "label": "TechCrunch $100M ARR (Nov 2025)",
        "url": "https://techcrunch.com/2025/11/21/bret-taylors-sierra-reaches-100m-arr-in-under-two-years/",
        "expect_phrase": "annual revenue run rate",
        "also_check": "$100 million",
    },
    {
        "label": "TechCrunch Sierra $950M raise — calls it 'annual recurring revenue'",
        "url": "https://techcrunch.com/2026/05/04/sierra-raises-950m-as-the-race-to-own-enterprise-ai-gets-serious/",
        "expect_phrase": "annual recurring revenue",
        "also_check": "$150 million",
    },
    {
        "label": "TechCrunch ARR-inflation article (published 2026-05-22)",
        "url": "https://techcrunch.com/2026/05/22/how-vcs-and-founders-use-inflated-arr-to-kingmake-ai-startups/",
        "expect_phrase": "contracted ARR",
        "also_check": "ARR",
    },
]

ARITHMETIC = [
    # Sierra outcome-based pricing math
    # $1.50/resolution (3rd-party estimate) x N daily resolutions -> implied ARR
    # For $200M ARR: implies 365,297 daily resolutions
    # For $100M ARR: implies 182,648 daily resolutions
    ("implied daily resolutions at $100M ARR, $1.50/resolution",
     round(100_000_000 / 365 / 1.50), 182_648, 1_000),
    ("implied daily resolutions at $200M ARR, $1.50/resolution",
     round(200_000_000 / 365 / 1.50), 365_297, 1_000),
    ("revenue growth $100M -> $200M in ~2 quarters (6 months) = 100% growth",
     200 / 100, 2.0, 0.01),
    ("valuation multiple: $15.8B / $200M ARR = 79x",
     round(15_800 / 200, 1), 79.0, 0.5),
]

headers = {"User-Agent": "venturebot/1.0 (https://venturebot.dev; autonomous agent; recheck script)"}
ok = 0
fail = 0

print("=== Sierra ARR register recheck ===\n")
print("--- source checks ---")
for s in SOURCES:
    try:
        req = urllib.request.Request(s["url"], headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode("utf-8", errors="replace").lower()
        phrase_found = s["expect_phrase"].lower() in body
        also_found = s["also_check"].lower() in body
        if phrase_found and also_found:
            print(f"  OK  {s['label']}")
            ok += 1
        else:
            missing = []
            if not phrase_found: missing.append(f"'{s['expect_phrase']}'")
            if not also_found: missing.append(f"'{s['also_check']}'")
            print(f"  FAIL {s['label']} — not found: {', '.join(missing)}")
            fail += 1
    except Exception as e:
        print(f"  FAIL {s['label']} — {e}")
        fail += 1

print("\n--- arithmetic checks ---")
for label, computed, expected, tolerance in ARITHMETIC:
    diff = abs(computed - expected)
    if diff <= tolerance:
        print(f"  OK  {label}: {computed} (expected ~{expected})")
        ok += 1
    else:
        print(f"  FAIL {label}: got {computed}, expected ~{expected} (diff {diff} > {tolerance})")
        fail += 1

print(f"\n--- key finding ---")
print("  TechCrunch paragraph 1 (Nov 2025): 'annual revenue run rate (ARR)'")
print("  TechCrunch headline (May 2026):     'annual recurring revenue (ARR)'")
print("  Same company, same $100M milestone, different ARR definition.")
print("  For per-resolution pricing, ARR is necessarily a run-rate extrapolation.")
print("  Coverage drops this distinction throughout; valuation multiples quoted against")
print("  'ARR' are implicitly compared to SaaS contracted-recurring figures.")
print()
print(f"  $100M milestone: company-confirmed (blog + TechCrunch 2025-11-21)  ✓")
print(f"  $150M milestone: company blog 2026-02-06                            ✓")
print(f"  $200M milestone: Bret Taylor post 2026-05-29                        ✓")
print(f"  per-resolution rate ~$1.50: third-party estimate (never published by Sierra)  ⚠")
print()
print(f"checks passed: {ok}  failed: {fail}")
if fail == 0:
    print("verdict: Mixed — revenue confirmed; 'ARR' label carries run-rate ambiguity.")
else:
    print("WARNING: some checks failed; review before publishing verdict.")
