"""Regression test for check 12's venue matcher.

The fix must satisfy BOTH:
  - real venue names (including hyphenated ones) PASS
  - fabricated names (coinmarketcap, ledger) still FAIL

A fix that only makes the check pass is how a broken check becomes a
useless one.
"""
import importlib.util, os, re

here = "/Users/carolinabosch/venturebot-repo/scripts"
spec = importlib.util.spec_from_file_location("vb_price",
                                              os.path.join(here, "price.py"))
if spec is None or spec.loader is None:
    raise SystemExit("could not load price.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

known = set()
for name in mod.SOURCES:
    low = name.lower()
    known.add(low)
    known.update(re.split(r"[-\s]", low))
known.discard("")

CASES = [
    # (tracker line, should_be_accepted)
    ("Coinbase-spot 119.63", True),
    ("Coinbase-xrate 119.58", True),
    ("Kraken 119.67", True),
    ("CoinGecko 119.64", True),
    ("Bitstamp 119.73", True),
    ("OKX 119.69", True),
    ("Binance unavailable (HTTPError)", True),
    ("CoinMarketCap 121.54", False),     # the 10-04 fabrication
    ("Ledger 121.34", False),            # the 10-04 fabrication
    ("Bloomberg 120.00", False),         # plausible but never queried
    ("median published 119.62 (6 venues)", True),   # skipped keyword
]

print(f"known venue tokens: {sorted(known)}\n")
failures = []
for line, should_accept in CASES:
    first = re.split(r"[\s:]", line.strip())[0].lower()
    skipped = first in ("median", "provenance", "mean")
    accepted = skipped or first in known
    ok = accepted == should_accept
    mark = "ok  " if ok else "WRONG"
    print(f"  [{mark}] {line[:40]:42s} accepted={accepted} "
          f"expected={should_accept}")
    if not ok:
        failures.append(line)

print()
if failures:
    print(f"{len(failures)} CASE(S) WRONG: {failures}")
    raise SystemExit(1)
print("All cases correct: real venues accepted, fabricated venues rejected.")
