#!/usr/bin/env python3
"""Check the arithmetic in the dfdx labs / Hans Kraemer claim.

Candidate for register entry seventeen. This verifies only what is
verifiable from the reported figures themselves - it does NOT confirm the
receipts exist, which requires the primary experiment report.

    /usr/bin/python3 scripts/recheck_dfdx.py
"""
import sys

# Reported individual product receipts, per secondary coverage.
RECEIPTS = [0.74, 0.40, 0.24, 0.12, 0.04]
CLAIMED_REVENUE = 1.54
REPORTED_COST = 6900          # widely repeated; an API list-price ESTIMATE
TOKENS = 5_400_000_000
PRODUCTS_SHIPPED = 17
DAYS = 21


def main():
    total = round(sum(RECEIPTS), 2)
    print("=== revenue decomposition ===")
    for r in RECEIPTS:
        print(f"  ${r:>5.2f}")
    print(f"  ------")
    print(f"  ${total:>5.2f}   claimed ${CLAIMED_REVENUE:.2f}   "
          f"reconciles: {abs(total - CLAIMED_REVENUE) < 0.005}")
    print(f"  {len(RECEIPTS)} receipts against {PRODUCTS_SHIPPED} products shipped")
    print(f"  -> {PRODUCTS_SHIPPED - len(RECEIPTS)} products earned nothing "
          f"({(PRODUCTS_SHIPPED-len(RECEIPTS))/PRODUCTS_SHIPPED:.0%} of output)")

    print("\n=== the ratio, stated carefully ===")
    print(f"  reported cost   ${REPORTED_COST:,}")
    print(f"  revenue         ${CLAIMED_REVENUE:.2f}")
    print(f"  cost/revenue    {REPORTED_COST / CLAIMED_REVENUE:,.0f}x")
    print(f"  return          {(CLAIMED_REVENUE - REPORTED_COST) / REPORTED_COST:.2%}")
    print(f"  revenue per day ${CLAIMED_REVENUE / DAYS:.3f}")
    print(f"  tokens/dollar   {TOKENS / CLAIMED_REVENUE:,.0f} tokens per $1 earned")

    print("\n=== what the $6,900 is and is not ===")
    print("  It is an API LIST-PRICE ESTIMATE of token consumption, not a")
    print("  receipt for cash paid. If the operators used a subscription, a")
    print("  credit grant, discounted/batch pricing, or their own hardware,")
    print("  actual cash cost could differ by a large factor in either")
    print("  direction. Quoting '$6,900 spent to earn $1.54' as a cash fact")
    print("  would be the same defect the register catalogues: an estimate")
    print("  hardening into a figure through repetition.")
    print("  The REVENUE side is the solid half - five receipts that sum.")

    print("\n=== still unverified (blocks a verdict) ===")
    for item in [
        "the primary experiment report from dfdx labs",
        "independent confirmation the five receipts exist",
        "actual cash cost, as opposed to list-price token estimate",
        "whether the 17 products were genuinely offered for sale",
    ]:
        print(f"  - {item}")
    print("\n  No verdict. A secondary article repeating operator figures is")
    print("  not corroboration, and the arithmetic reconciling only proves")
    print("  the reported numbers are internally consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
