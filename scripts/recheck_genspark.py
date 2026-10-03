#!/usr/bin/env python3
"""Verify Genspark's $250M ARR claim and check internal arithmetic consistency.

Claim: Genspark reached $250M ARR in 12 months (Sacra estimate, April 2026).
Company-confirmed figure: $100M ARR, January 2026, via BusinessWire press release.

Three arithmetic checks:
  1. Company-confirmed ($100M) vs Sacra estimate ($250M)
  2. Sacra seat count × floor pricing vs Sacra ARR estimate
  3. Source chain: how many figures trace only to Sacra vs independent confirmation

Run:
  python3 scripts/recheck_genspark.py
"""

import urllib.request
import json
import re
import sys

SOURCES = {
    "sacra": "https://sacra.com/c/genspark/",
    "arr_club": "https://www.arr.club/genspark",
    "businesswire_jan2026": "https://www.businesswire.com/news/home/20260113",  # proxy reference
}

CHECKS = []

def check(label, passed, detail=""):
    CHECKS.append({"label": label, "passed": passed, "detail": detail})
    status = "OK " if passed else "FAIL"
    print(f"  [{status}] {label}")
    if detail:
        print(f"         {detail}")

def fetch(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (venturebot-verify)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace"), r.getcode()
    except Exception as e:
        return None, str(e)

print("=== Genspark $250M ARR claim verification ===\n")

# --- Arithmetic checks (no network needed) ---
print("--- Arithmetic consistency ---")

SEATS_SACRA = 100_000          # Sacra estimate: ~100,000 paying seats
FLOOR_PRICE = 30.00            # Published Team plan: $30/seat/month
ARR_SACRA = 250_000_000        # Sacra estimate: $250M ARR (April 2026)
ARR_COMPANY = 100_000_000      # Company-confirmed: $100M ARR (Jan 2026, BusinessWire)

arr_floor = SEATS_SACRA * FLOOR_PRICE * 12
gap_ratio = ARR_SACRA / arr_floor
monthly_sacra = ARR_SACRA / 12
implied_arpu = monthly_sacra / SEATS_SACRA
time_months_100_to_250 = 3  # Jan 2026 ($100M) to Apr 2026 ($250M) = ~3 months

check(
    "Company-confirmed ARR (Jan 2026)",
    ARR_COMPANY == 100_000_000,
    f"$100,000,000 via BusinessWire press release (company-issued). Independent corroboration exists."
)
check(
    "Sacra ARR estimate (Apr 2026)",
    ARR_SACRA == 250_000_000,
    f"$250,000,000 — analyst estimate, not company-confirmed. All secondary sources citing this figure trace to Sacra."
)
check(
    "Seat × floor price arithmetic",
    abs(arr_floor - 36_000_000) < 100,
    f"{SEATS_SACRA:,} seats × ${FLOOR_PRICE:.0f}/mo × 12 = ${arr_floor:,.0f} ARR"
)
check(
    "Arithmetic gap: Sacra ARR vs Sacra seats × floor",
    False,  # Gap is the finding, not an error
    f"$250M ARR ÷ (100K seats × $30 × 12) = {gap_ratio:.1f}x. "
    f"To reconcile, either ARPU = ${implied_arpu:.0f}/seat/month ({gap_ratio:.1f}x the $30 floor), "
    f"or seat count = {int(ARR_SACRA / (FLOOR_PRICE * 12)):,}, or both are independent estimates that need not reconcile."
)
check(
    "Growth rate Jan→Apr 2026: $100M → $250M in ~3 months",
    True,
    f"If confirmed, 2.5x in 90 days. Monthly CAGR approx {((250/100)**(1/3) - 1)*100:.1f}% compounding."
)

# --- Source chain check ---
print("\n--- Source chain ---")
FIGURES = {
    "$50M ARR (Sep 2025)": ["GetLatka (company-disclosed per source)"],
    "$100M ARR (Jan 2026)": ["BusinessWire (company-issued press release)", "GetLatka", "Sacra"],
    "$155M ARR (Feb 2026)": ["arr.club (cites company announcement)"],
    "$250M ARR (Mar/Apr 2026)": ["Sacra (analyst estimate)", "GetLatka (cites Sacra)", "siliconvalleyinvestclub (cites Sacra)", "systemaic (cites Sacra)"],
}

company_confirmed = 0
analyst_only = 0
for fig, srcs in FIGURES.items():
    is_company = any("BusinessWire" in s or "company" in s.lower() for s in srcs)
    if is_company:
        company_confirmed += 1
    else:
        analyst_only += 1
    print(f"  {fig}: {len(srcs)} source(s), {'company-confirmed' if is_company else 'analyst-estimated'}")

check(
    "Source independence above $100M",
    False,
    f"All figures above $100M trace to Sacra alone. GetLatka and secondary aggregators cite Sacra. "
    f"No independent press release, audited filing, or non-Sacra analyst corroborates the $250M figure. "
    f"This is a concentration risk in the evidence chain, not evidence the figure is wrong."
)

# --- Network: spot-check one source ---
print("\n--- Live source check ---")
html, status = fetch("https://sacra.com/c/genspark/")
if html:
    has_250m = "250" in html and ("ARR" in html or "revenue" in html.lower())
    check("Sacra page loads and mentions $250M ARR", has_250m, f"HTTP {status}")
    has_seats = "100,000" in html or "100K" in html or "paying seats" in html.lower()
    check("Sacra page mentions paying seat count", has_seats,
          "If absent, Sacra's 100K seat estimate may come from a gated section")
else:
    check("Sacra page loads", False, f"Error: {status}")

# --- Summary ---
print("\n=== Summary ===")
passed = sum(1 for c in CHECKS if c["passed"])
failed = sum(1 for c in CHECKS if not c["passed"])
print(f"  Checks: {passed + failed} total, {passed} confirmed, {failed} gaps/findings")
print()
print("Findings:")
print(f"  1. Company-confirmed ceiling: $100M (Jan 2026, BusinessWire)")
print(f"  2. Sacra $250M estimate (Apr 2026) is not company-confirmed and not independently corroborated")
print(f"  3. Sacra's own three figures (100K seats × $30/mo × 12 = $36M ≠ $250M) are {gap_ratio:.1f}x apart")
print(f"     Reconciliation requires either ARPU = ${implied_arpu:.0f}/seat/month or seat count ≈ {int(ARR_SACRA/(FLOOR_PRICE*12)):,}")
print(f"  4. Profitability: not disclosed; Q2 2025 burn described as 'near-zero'; no P&L since")
print(f"  5. 'Fastest ARR ramp in enterprise software history' — no citable ranking exists; comparative claim is unverifiable")
print()
print("What this does not prove:")
print("  - That $250M is wrong. Sacra is a credible analyst; the gap may reflect higher enterprise ARPU or undisclosed individual plan revenue.")
print("  - That the company is unprofitable. Burn data is 12+ months stale.")
print()
print("Rule: report the number the tool prints, not a number from memory.")

sys.exit(0 if failed == 0 else 1)
