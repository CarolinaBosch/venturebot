#!/usr/bin/env python3
"""SOL/USD from several independent venues, with an agreement check.

Rewritten 2026-09-27 after a wake published SOL at $103.68 when the real
price was ~$121.67 - a 17% error that understated the treasury by $27.

The previous version queried two venues and took their mean. Two is not
enough. That wake had already done the right-sounding thing - it noticed a
bad Coinbase read, discarded it, and fell back to the others - and still
published a wrong figure, because discarding an outlier only helps if what
remains is trustworthy. With a small panel, one bad read leaves a
"majority" that can be wrong together.

This queries five venues, prints every one, takes the MEDIAN (which a
single bad feed cannot drag), and REFUSES to print a treasury figure when
the sources disagree beyond tolerance. A refusal is a better output than a
confident wrong number.

    /usr/bin/python3 scripts/price.py
"""
import json
import ssl
import statistics
import sys
import urllib.request

UA = {"User-Agent": "venturebot-price"}
HOT, MULTISIG = 0.5, 1.001
TOLERANCE = 0.02          # max spread from the median before refusing
MIN_VENUES = 3            # a median needs at least three to mean anything
ctx = ssl.create_default_context()


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
        return json.loads(r.read().decode())


SOURCES = {
    "coinbase-spot": lambda: float(
        get("https://api.coinbase.com/v2/prices/SOL-USD/spot")["data"]["amount"]),
    "coinbase-xrate": lambda: float(
        get("https://api.coinbase.com/v2/exchange-rates?currency=SOL")
        ["data"]["rates"]["USD"]),
    "kraken": lambda: float(
        list(get("https://api.kraken.com/0/public/Ticker?pair=SOLUSD")
             ["result"].values())[0]["c"][0]),
    "coingecko": lambda: float(
        get("https://api.coingecko.com/api/v3/simple/price"
            "?ids=solana&vs_currencies=usd")["solana"]["usd"]),
    "binance": lambda: float(
        get("https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT")
        ["price"]),
}


def main():
    prices = {}
    print("=== SOL/USD, independent venues ===")
    for name, fn in SOURCES.items():
        try:
            prices[name] = fn()
            print(f"  {name:16s} ${prices[name]:,.2f}")
        except Exception as e:
            print(f"  {name:16s} unavailable ({type(e).__name__})")

    if len(prices) < MIN_VENUES:
        print(f"\nREFUSING TO PUBLISH: only {len(prices)} venue(s) responded; "
              f"{MIN_VENUES} is the minimum for a median to mean anything.")
        return 1

    vals = sorted(prices.values())
    lo, hi = vals[0], vals[-1]
    spread = (hi - lo) / lo
    median = statistics.median(vals)

    print(f"\n  venues {len(vals)}  range ${lo:,.2f}-${hi:,.2f}  "
          f"spread {spread:.2%}  median ${median:,.2f}")

    outliers = {n: v for n, v in prices.items()
                if abs(v - median) / median > TOLERANCE}
    if outliers:
        for n, v in outliers.items():
            print(f"  OUTLIER {n}: ${v:,.2f} "
                  f"({(v - median) / median:+.1%} from median)")

    agree = [v for v in vals if abs(v - median) / median <= TOLERANCE]
    if len(agree) < MIN_VENUES:
        print(f"\nREFUSING TO PUBLISH: only {len(agree)} venue(s) agree within "
              f"{TOLERANCE:.0%} of the median.")
        print("Do not average a disagreement. Widen the panel or wait.")
        return 1

    median = statistics.median(agree)
    total = HOT + MULTISIG
    print(f"\nmean SOL/USD: {median:.2f}   ({len(agree)} venues in agreement)")
    print(f"hot      {HOT} SOL = ${HOT * median:,.2f}")
    print(f"multisig {MULTISIG} SOL = ${MULTISIG * median:,.2f}")
    print(f"total    {total} SOL = ${total * median:,.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
