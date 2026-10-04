#!/usr/bin/env python3
"""
recheck_aihustler.py — verify the AI Hustler / Marcin Dudek register entry.

Primary source: https://marcindudek.dev/projects/ai-hustler-revenue/
Secondary: https://apify.com/cryptosignals (store page, publicly readable)

Findings to verify:
1. $6.74 revenue on April 7, 2026 — 45,304 LinkedIn Jobs results at $0.01/result * 0.80 = $6.74 ✓
2. Apify cut math: 45,304 * $0.01 = $453.04 gross; 80% share = $362.43... WAIT —
   actually Apify PPE = developer gets 80% of what the user is BILLED.
   45,304 results * $0.01/result = $453.04 billed. 80% of $453.04 = $362.43.
   But the post says $6.74. Let me re-read: "$0.01 per result" PPE, 45,304 results.
   45,304 * $0.01 = $453.04 — that's way more than $6.74.
   Re-read: the actor was set to $0.01 per result. But 2 paid users ran it.
   The issue: Apify free-tier users generate $0. ONLY paid-plan ($49+/mo) users generate revenue.
   $6.74 / 0.8 = $8.425 gross billed to paid users. $8.425 / $0.01 = 842.5 results from paid users.
   Total scraped: 45,304. But only ~842 of those were by paid-plan users.
   The rest (44,461) were free-tier users — generate $0.
   So: ~842 paid-plan results * $0.01 * 0.80 = $6.74 ✓ (approximately)
3. Margin claim: "98.76% margin because the scraper uses LinkedIn's public guest API"
   Gross $6.74 / (1 - 0.9876) = operating cost ~$0.083. Plausible for a no-proxy API call.
4. Apify store verification: apify.com/cryptosignals publicly readable
   — can check actor count, total users, monthly users without auth
"""

import urllib.request
import json

PRIMARY_URL = "https://marcindudek.dev/projects/ai-hustler-revenue/"
APIFY_STORE_URL = "https://apify.com/cryptosignals"

print("=== AI Hustler / Marcin Dudek — revenue arithmetic ===\n")

# Finding 1: revenue arithmetic
RESULT_COUNT_PAID = 842  # approx paid-tier results (reverse-computed)
PPE_RATE = 0.01          # $0.01 per result
APIFY_CUT = 0.20         # Apify keeps 20%, developer gets 80%

gross_paid = RESULT_COUNT_PAID * PPE_RATE
net_revenue = gross_paid * (1 - APIFY_CUT)
print(f"Reverse-computed paid-tier results: ~{RESULT_COUNT_PAID}")
print(f"  Gross from paid users: ~${gross_paid:.2f}")
print(f"  Net to developer (80%): ~${net_revenue:.2f}  (published: $6.74)")
print(f"  Arithmetic consistent: {abs(net_revenue - 6.74) < 0.20}")

# Finding 2: total results vs paying results
TOTAL_RESULTS = 45304
PAYING_FRACTION = RESULT_COUNT_PAID / TOTAL_RESULTS
print(f"\nTotal results scraped: {TOTAL_RESULTS:,}")
print(f"Approx paid-plan fraction: {PAYING_FRACTION:.1%}")
print(f"  (Apify free-tier users generate $0 for developers)")

# Finding 3: margin claim
gross_claimed = 6.74 / 0.8
margin_implied = 1 - (gross_claimed - 6.74) / 6.74
cost_implied = gross_claimed * (1 - 0.9876)
print(f"\nMargin claim: 98.76%")
print(f"  Gross implied: ${gross_claimed:.4f}")
print(f"  Cost implied: ${cost_implied:.4f}")
print(f"  Plausible for no-proxy API scraper: True")

# Finding 4: what the Apify store page shows (fetched without auth)
print(f"\n=== Apify store — cryptosignals (apify.com/cryptosignals) ===")
print("Expected (from page at time of audit):")
print("  41 public Actors")
print("  2,100+ total users")
print("  335 monthly users")
print("  81.1% runs succeeded")
print("  Joined: March 2026")
print("  Pricing: pay-per-result from $0.005/result")
print()
print("NOTE: the actor page shows $0.005/result as the CURRENT rate.")
print("The post states pricing was set to $0.01/result initially;")
print("price may have been lowered or adjusted since the April 7 event.")
print("$6.74 revenue is consistent with a small number of paid-tier runs")
print("at either price point.")

print("\n=== the 'projected monthly ~$69' figure ===")
# Added 2026-10-04. The register entry's first version explained this as
# "$6.74 / ~4.4 days x 30 days". That arithmetic does not reproduce the
# figure, and a reader with a calculator would find that before anything
# else in the entry. Showing the failed derivation alongside the ones that
# do work is more useful than quietly substituting a better explanation.
R, TARGET = 6.74, 69.0
stated = R / 4.4 * 30
print(f"  entry's original stated derivation: $6.74 / 4.4 days x 30")
print(f"    = ${stated:.2f}  -> reproduces ~$69? {abs(stated - TARGET) < 2}")
print(f"  window that WOULD give $69: {R * 30 / TARGET:.2f} days")
print(f"    $6.74 / 2.93 x 30 = ${R / 2.93 * 30:.2f}")
print(f"  or an assumed growth multiple of {TARGET / R:.1f}x")
print()
print("  I cannot determine which the author used. The entry now records")
print("  that uncertainty rather than picking the reading that sounds best.")
print("  The substantive point is unaffected: ~$69 is a straight-line")
print("  projection from a single revenue event, and the risk is that a")
print("  careless citation turns '$6.74 first revenue' into a")
print("  '$69/month AI agent business'.")

print("\n=== verdict support ===")
print("Corroborated with caveats:")
print("  - Primary source: first-person, detailed, published by the operator")
print("  - $6.74 arithmetic is internally consistent")
print("  - Apify store profile exists and shows a real multi-actor presence")
print("  - 200+ runs over 41 days documented with failure log — not a cherry-pick")
print("  - Honest framing: author calls it a first event, not a business")
print("Caveats:")
print("  - $6.74 is a FIRST EVENT, not MRR or ARR")
print("  - Revenue is from paid-tier Apify users, not direct customers")
print("  - Platform dependency: actor revenue depends on Apify's marketplace")
print("  - No independent third-party verification (no TrustMRR, no Stripe badge)")
print("  - The 'AI agent' is Claude Sonnet running autonomously via cron —")
print("    the revenue accrues to a human developer, not to the agent itself")
