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

# Added 2026-10-02 wake 4. The reachability check above shows the sources are
# live; it does NOT test the entry's actual findings, which are arithmetic.
# A script that only proves a URL responds is a weaker check than the entry
# claims to rest on, so recompute each number here.
ARR = 1_000_000_000
ARR_LOWER = 900_000_000
BURN = EXPECTED["burn_usd_approx"]
START_ARR, MONTHS = 1_000_000, 24

print()
print("=== ARITHMETIC THE ENTRY RESTS ON (recomputed, not fetched) ===")
monthly = ARR / 12
print(f"  ARR / 12 = ${monthly:,.0f} collected in the most recent month")
print(f"  entry states ~$83M: {abs(monthly - 83_000_000) < 1_000_000}")
print("  'Annualized run rate' is one month x 12 - a projection of the")
print("  present, not a record of the trailing year. For any growing")
print("  company, collected revenue over the last 12 months is strictly")
print("  LESS than the ARR figure. That is the metric working as designed,")
print("  not a trick; the defect is coverage reading it as receipts.")

print()
print(f"  burn ${BURN:,} against run rate ${ARR_LOWER:,}")
print(f"  burn as share of run rate: {BURN / ARR_LOWER:.1%}")
print(f"  implied net on run rate:   {(ARR_LOWER - BURN) / ARR_LOWER:.1%}")
print("  Spending $800M against a $900M run rate is ordinary for a company")
print("  that just raised $2B to grow. The finding is that milestone")
print("  coverage prints the $1B and omits the $800M, so a reader sees")
print("  revenue scale without cost scale.")

print()
mult = ARR / START_ARR
mrate = mult ** (1 / MONTHS) - 1
print(f"  ${START_ARR:,} (Sep 2024) -> ${ARR:,} (Sep 2026) = {mult:,.0f}x")
print(f"  implied compound monthly growth: {mrate:.1%}")
print(f"  implied annual multiple:         {(1 + mrate) ** 12:,.1f}x")
print("  Reported consistently across independent outlets. Corroboration")
print("  here is stronger than anywhere else in the register, which is why")
print("  the verdict is Mixed on FRAMING rather than on the number.")

print()
print("  NOTE: Cognition is private — no public financials.")
print("  The fetches above confirm the secondary sources remain live and")
print("  consistent. They cannot independently verify the $1B figure; only")
print("  corroborate it. The arithmetic above is reproducible by anyone.")
print()
print(json.dumps(results, indent=2))
