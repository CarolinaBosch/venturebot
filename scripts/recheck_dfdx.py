#!/usr/bin/env python3
"""Check the arithmetic in the dfdx labs / Hans Krämer experiment.

Primary source: dfdxlabs.com/research/2026/hans-kraemer
    "Our agent used 5B tokens to build a business empire in 3 weeks.
     It made $1.54."
Published 2026-09-15 by Julius Danek (Stripe, personal capacity)
and Matthias Plappert (dfdx labs).

    /usr/bin/python3 scripts/recheck_dfdx.py
"""
import sys

# ── reported figures from the primary source ──────────────────────────────────
RECEIPTS = [0.74, 0.40, 0.24, 0.12, 0.04]      # product-level revenue table
CLAIMED_REVENUE   = 1.54                         # stated in report
HANS_OWN_SPENDING = 47.19                        # Hans spent of his own budget
SUBSCRIPTION_COST = 400.0                        # Codex Pro $200/mo + Claude Max $200/mo (stated)
OTHER_EXPENSES    = 100.0                        # ~$100 other, stated
SERVER_PER_MONTH  = 40.0                         # Hetzner VM, stated
RUN_DAYS          = 21

# The widely-repeated "$6,900" figure
ESTIMATED_TOKEN_COST = 6900  # what API LIST PRICES would total; operators did NOT pay this

PRODUCTS_SHIPPED = 17
TOKENS           = 5_400_000_000
TOKEN_CACHE_READ = 4_980_000_000   # ~92% cache reads, stated


def main():
    print("=== revenue: what the primary source states ===")
    total = round(sum(RECEIPTS), 2)
    names = ["Grant Search", "Agent API Listings", "Bounty Signals", "Cent Board", "OSHA Search"]
    for name, r in zip(names, RECEIPTS):
        print(f"  {name:<25} ${r:.2f}")
    print(f"  {'Total':<25} ${total:.2f}  (claimed ${CLAIMED_REVENUE:.2f}, reconciles: {abs(total-CLAIMED_REVENUE)<0.005})")
    earning = len(RECEIPTS)
    silent  = PRODUCTS_SHIPPED - earning
    print(f"  {earning} products earned anything; {silent} ({silent/PRODUCTS_SHIPPED:.0%}) earned $0")

    print("\n=== cost: what the primary source actually states ===")
    run_months = RUN_DAYS / 30
    sub_pro_rated = SUBSCRIPTION_COST * run_months
    server_pro_rated = SERVER_PER_MONTH * run_months
    total_operator = sub_pro_rated + OTHER_EXPENSES + server_pro_rated
    print(f"  Hans' own spending (his budget):  ${HANS_OWN_SPENDING:.2f}")
    print(f"  Operators - subscriptions ~{run_days_label(RUN_DAYS)}: ${sub_pro_rated:.0f}")
    print(f"  Operators - server ~{run_days_label(RUN_DAYS)}:        ${server_pro_rated:.0f}")
    print(f"  Operators - other:                ${OTHER_EXPENSES:.0f}")
    print(f"  Operators total (approx):         ${total_operator:.0f}")
    print()
    print(f"  List-price TOKEN ESTIMATE:        ${ESTIMATED_TOKEN_COST:,}")
    print(f"  (5.4B tokens at API pricing; PRIMARY SOURCE EXPLICITLY STATES")
    print(f"   operators used subscriptions, not pay-per-token billing)")
    print(f"  Cash cost ≠ token estimate. The two figures are not interchangeable.")

    print("\n=== the ratio that circulates, stated carefully ===")
    ratio = ESTIMATED_TOKEN_COST / CLAIMED_REVENUE
    print(f"  $6,900 (token estimate) / $1.54 revenue = {ratio:,.0f}x")
    print(f"  This ratio uses the list-price estimate, not actual cash cost.")
    print(f"  Operator cash cost / revenue: ~${total_operator:.0f} / $1.54 = {total_operator/CLAIMED_REVENUE:.0f}x")
    print(f"  Both ratios show the business lost money. The spread between")
    print(f"  them (~4,500x vs ~{total_operator/CLAIMED_REVENUE:.0f}x) is the measurement hazard.")

    print("\n=== token breakdown ===")
    pct_cache = TOKEN_CACHE_READ / TOKENS
    pct_non_cache = 1 - pct_cache
    print(f"  Total tokens:     {TOKENS/1e9:.1f}B")
    print(f"  Cache reads:      {TOKEN_CACHE_READ/1e9:.2f}B ({pct_cache:.0%}) — priced much lower at API rates")
    print(f"  Non-cache:        {(TOKENS-TOKEN_CACHE_READ)/1e9:.2f}B ({pct_non_cache:.0%})")
    print(f"  Cache reads are why list-price estimate >> cash; subscription pricing")
    print(f"  made the cache read volume essentially free.")

    print("\n=== verdict-relevant facts established from primary source ===")
    facts = [
        "Revenue $1.54: five receipts named, amounts stated, sum confirmed ($1.54)",
        "12 of 17 products earned $0 (71% of catalog)",
        "Hans's own spending $47.19 (from his initial budget)",
        "Operators' actual cost: ~$400/mo subscriptions + ~$100 other + ~$40/mo server",
        "$6,900 figure is list-price token estimate, explicitly labeled as such",
        "Julius Danek is at Stripe (personal capacity, disclosed); report is primary source",
        "Run period: Aug 17 – Sep 7, 2026 (21 days)",
        "Market: agentic economy only, not general-public commerce (disclosed)",
    ]
    for f in facts:
        print(f"  ✓ {f}")

    print("\n=== now verifiable (primary source read directly) ===")
    print("  Revenue figure, product breakdown, token usage, actual subscription cost,")
    print("  and the explicit labeling of $6,900 as an estimate are all stated in the")
    print("  primary report at dfdxlabs.com/research/2026/hans-kraemer.")
    print("  Independent receipt confirmation remains unverified (no transaction IDs")
    print("  published in the report).")
    return 0


def run_days_label(days):
    return f"{days/30:.1f} mo"


if __name__ == "__main__":
    sys.exit(main())
