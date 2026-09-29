#!/usr/bin/env python3
"""Check the arithmetic in agent-economy market-size forecasts.

Register entry 18. The register has audited agents claiming revenue; this
audits the layer above - the market-size figures those claims are justified
by, and that infrastructure companies cite when selling to the category.

Every number here is published. The test is whether the published growth
rates match the published endpoints, and whether forecasts that sound
like corroboration are measuring the same thing.

    /usr/bin/python3 scripts/recheck_market_forecasts.py
"""
import sys


def cagr(start, end, years):
    return (end / start) ** (1.0 / years) - 1.0


def main():
    print("=== the most-repeated pair of endpoints ===")
    # MarketsandMarkets, as quoted by TNW and agentmarketcap.ai
    start, end, years = 5.26, 52.62, 6      # 2024 -> 2030
    computed = cagr(start, end, years)
    print(f"  ${start}B (2024) -> ${end}B (2030), {years} years")
    print(f"  computed CAGR: {computed:.1%}")
    print(f"  TNW quotes MarketsandMarkets at 46.3% -> "
          f"{abs(computed - 0.463) < 0.01}")
    print(f"  agentmarketcap.ai quotes the SAME endpoints at 41% -> "
          f"{abs(computed - 0.41) < 0.01}")
    print()
    print("  Two outlets cite one forecast's own endpoints and report growth")
    print("  rates five points apart. The endpoints imply 46.8%. A reader")
    print("  seeing '41% CAGR' next to '$5.25B to $52.62B' is seeing a rate")
    print("  that does not follow from the numbers beside it.")

    print("\n=== what 41% would actually produce ===")
    wrong = start * (1.41 ** years)
    print(f"  ${start}B compounding at 41% for {years} years = ${wrong:.1f}B")
    print(f"  published endpoint is ${end}B - a ${end - wrong:.1f}B gap")

    print("\n=== two forecasts, same horizon, different universes ===")
    gvr_s, gvr_e = 2.6, 24.5               # Grand View, enterprise deployment
    mm_s, mm_e = 5.26, 52.62               # MarketsandMarkets, agent software
    print(f"  Grand View       ${gvr_s}B -> ${gvr_e}B   CAGR "
          f"{cagr(gvr_s, gvr_e, years):.1%}")
    print(f"  MarketsandMarkets ${mm_s}B -> ${mm_e}B  CAGR "
          f"{cagr(mm_s, mm_e, years):.1%}")
    print(f"  2030 figures differ by {mm_e / gvr_e:.1f}x")
    print()
    print("  The RATES agree within a point; the absolute sizes differ 2.1x.")
    print("  That is not two studies confirming each other - it is two")
    print("  definitions of 'the market' growing at a similar speed. Citing")
    print("  them together as corroboration conflates agreement about")
    print("  momentum with agreement about size.")

    print("\n=== the machine-customer figures ===")
    gartner_b2b, gartner_all = 15e12, 30e12
    mck_lo, mck_hi = 3e12, 5e12
    print(f"  Gartner: ${gartner_all/1e12:.0f}T machine-customer purchases by 2030")
    print(f"  McKinsey: ${mck_lo/1e12:.0f}T-${mck_hi/1e12:.0f}T "
          f"agent-mediated consumer commerce by 2030")
    print(f"  ratio at the midpoints: {gartner_all / ((mck_lo + mck_hi)/2):.1f}x")
    print()
    print("  These are routinely quoted in the same breath. They measure")
    print("  different things (all machine purchasing vs consumer commerce)")
    print("  and differ by roughly 7.5x. Neither is wrong; quoting the")
    print("  larger without its boundary is.")

    print("\n=== the figure that cuts the other way ===")
    print("  Gartner also predicts >40% of agentic AI projects CANCELLED by")
    print("  end-2027 on cost, unclear value or inadequate risk controls.")
    print("  Stacklok's 2026 survey: ~41% of software organisations running")
    print("  MCP in production of any kind, security the leading barrier.")
    print()
    print("  The same research house supplies both the $30T ceiling and the")
    print("  40% cancellation rate. Coverage reliably carries the first.")

    print("\n=== what this establishes ===")
    print("  NOT that the market is small, or that the forecasters are wrong.")
    print("  NOT a verdict on any company's revenue - no company is audited")
    print("  here.")
    print("  YES: a widely-repeated CAGR (41%) does not follow from the")
    print("  endpoints printed beside it (46.8%).")
    print("  YES: forecasts spanning a 2.1x range in size are cited as")
    print("  mutual confirmation because their growth rates coincide.")
    print("  YES: the same source's downside figure travels far less than")
    print("  its upside figure.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
