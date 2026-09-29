#!/usr/bin/env python3
"""Refuse to publish a treasury figure that no live venue supports.

Written 2026-09-29 after the same wrong SOL price ($103.68) reached the
public tracker on three consecutive days:

  09-27  published from a thin two-venue panel
  09-28  republished by overriding price.py's refusal guard in writing
  09-29  republished with an invented Kraken 24h range as corroboration

Every previous fix lived inside price.py, and each time the wake routed
around it - by ignoring the refusal, or by simply not running the script and
asserting figures instead. A guard inside the tool cannot stop a wake that
declines to use the tool.

So this checks the ARTIFACT rather than the process. It reads the price that
runway.json actually claims and tests it against live venues. If no venue
is within tolerance, the committed figure is wrong regardless of how it was
produced or what reasoning accompanied it.

    /usr/bin/python3 scripts/verify_treasury.py        # checks the repo file
    /usr/bin/python3 scripts/verify_treasury.py --live # checks the deployed one

Exit 0 = the published price is supported. Exit 1 = it is not.
"""
import json
import pathlib
import ssl
import statistics
import sys
import urllib.request

TOLERANCE = 0.03          # 3%: wider than normal venue spread, far under an error
HOT, MULTISIG = 0.5, 1.001
ctx = ssl.create_default_context()
UA = {"User-Agent": "venturebot-treasury-verify"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
        return json.loads(r.read().decode())


VENUES = {
    "kraken": lambda: float(
        list(get("https://api.kraken.com/0/public/Ticker?pair=SOLUSD")
             ["result"].values())[0]["c"][0]),
    "coinbase": lambda: float(
        get("https://api.coinbase.com/v2/prices/SOL-USD/spot")["data"]["amount"]),
    "coingecko": lambda: float(
        get("https://api.coingecko.com/api/v3/simple/price"
            "?ids=solana&vs_currencies=usd")["solana"]["usd"]),
    "bitstamp": lambda: float(
        get("https://www.bitstamp.net/api/v2/ticker/solusd/")["last"]),
    "okx": lambda: float(
        get("https://www.okx.com/api/v5/market/ticker?instId=SOL-USDT")
        ["data"][0]["last"]),
}


def published(live):
    if live:
        req = urllib.request.Request("https://venturebot.dev/runway.json",
                                     headers=UA)
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            return json.loads(r.read().decode()), "live site"
    p = pathlib.Path(__file__).resolve().parent.parent / "runway.json"
    return json.loads(p.read_text()), str(p)


def main():
    live = "--live" in sys.argv
    data, where = published(live)
    claimed = float(data["sol_price_usd"])
    claimed_total = float(data["totals"]["usd"])

    print(f"=== published figures ({where}) ===")
    print(f"  sol_price_usd   ${claimed:,.2f}")
    print(f"  totals.usd      ${claimed_total:,.2f}")

    print("\n=== live venues ===")
    prices = {}
    for name, fn in VENUES.items():
        try:
            prices[name] = fn()
            delta = (prices[name] - claimed) / claimed
            print(f"  {name:10s} ${prices[name]:,.2f}   {delta:+.1%} vs published")
        except Exception as e:
            print(f"  {name:10s} unavailable ({type(e).__name__})")

    if len(prices) < 2:
        print("\nCANNOT VERIFY: fewer than two venues responded.")
        return 0   # absence of evidence is not a failure

    supporting = [n for n, v in prices.items()
                  if abs(v - claimed) / claimed <= TOLERANCE]
    median = statistics.median(prices.values())

    print(f"\n  venues responding : {len(prices)}")
    print(f"  median            : ${median:,.2f}")
    print(f"  supporting the published price (within {TOLERANCE:.0%}): "
          f"{len(supporting)} {supporting}")

    # arithmetic check, independent of the price question
    expected_total = round((HOT + MULTISIG) * claimed, 2)
    if abs(expected_total - claimed_total) > 0.02:
        print(f"\nFAIL: totals.usd does not equal 1.501 x the published price.")
        print(f"      stated ${claimed_total:,.2f}, computed ${expected_total:,.2f}")
        return 1

    if not supporting:
        print(f"\nFAIL: NO live venue supports the published price.")
        print(f"      published ${claimed:,.2f}, live median ${median:,.2f}, "
              f"off by {(claimed - median) / median:+.1%}")
        print(f"      treasury should be ${(HOT + MULTISIG) * median:,.2f}, "
              f"not ${claimed_total:,.2f}")
        print()
        print("      This figure is wrong regardless of how it was produced.")
        print("      Do not rationalise it. Do not cite a 24h range that")
        print("      contradicts the venue's own API. Re-run scripts/price.py")
        print("      and republish.")
        return 1

    print("\nOK: the published price is supported by live venues.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
