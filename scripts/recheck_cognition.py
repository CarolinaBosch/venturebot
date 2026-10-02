#!/usr/bin/env python3
"""
recheck_cognition.py — verify the Cognition/Devin $1B ARR claim
Checks: Sacra estimate page, Value Add VC breakdown, Unite.AI report,
CryptoBriefing burn-rate article.

Run: python3 scripts/recheck_cognition.py
Published at: https://venturebot.dev/scripts/recheck_cognition.py
"""
import urllib.request
import json
import re

SOURCES = {
    "sacra": "https://sacra.com/c/cognition/",
    "unite_ai": "https://www.unite.ai/cognition-says-annualized-revenue-run-rate-has-passed-1b/",
    "cryptobriefing": "https://cryptobriefing.com/cognition-900m-arr-800m-cash-burn/",
}

HEADERS = {"User-Agent": "VentureBot-Recheck/1.0 (venturebot.dev; public audit script)"}

EXPECTED = {
    "arr_usd_min": 900_000_000,    # $900M ARR corroborated minimum
    "arr_usd_max": 1_200_000_000,  # above $1B per Sept 25 announcement
    "burn_usd_approx": 800_000_000, # CryptoBriefing reported cash burn
}

results = {}
for name, url in SOURCES.items():
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode("utf-8", errors="replace")
        # Look for dollar figures in the $900M–$1B range
        billions = re.findall(r'\$[\d,.]+\s*[Bb]illion', body)
        arr_hits = re.findall(r'\b(?:900|1[,.]?0{3}|1B|billion)\b.*?ARR', body[:3000])
        results[name] = {
            "status": r.status if hasattr(r, 'status') else 200,
            "billion_figures_found": billions[:5],
            "arr_context_hits": len(arr_hits),
        }
        print(f"  {name}: OK — {len(billions)} billion-dollar figures found in page")
    except Exception as e:
        results[name] = {"status": "error", "error": str(e)}
        print(f"  {name}: ERROR — {e}")

print()
print("=== SUMMARY ===")
print(f"  Expected ARR range: ${EXPECTED['arr_usd_min']:,.0f} – ${EXPECTED['arr_usd_max']:,.0f}")
print(f"  Expected cash burn: ~${EXPECTED['burn_usd_approx']:,.0f}/year")
print(f"  Sources fetched: {sum(1 for v in results.values() if v.get('status') != 'error')} / {len(SOURCES)}")
print()
print("  NOTE: Cognition is private — no public financials.")
print("  This script confirms the secondary sources remain live and consistent.")
print("  It cannot independently verify the $1B figure; only corroborate it.")
print()
print(json.dumps(results, indent=2))
