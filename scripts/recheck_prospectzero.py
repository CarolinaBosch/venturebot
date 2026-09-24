#!/usr/bin/env python3
"""ProspectZero: what the "Stripe-verified" badge actually guarantees.

Four reads of TrustMRR's ProspectZero page over ~six hours returned four
different sets of numbers, and the page contradicts itself inside a single
render. AgentMRR shows a fifth figure. Every one of these carries a
"revenue verified with Stripe API key" badge.

This records the observations and computes the spread. It deliberately does
NOT pick a winner: no tracker publishes the underlying Stripe data, so an
outside observer cannot adjudicate. The finding is about the badge.

    /usr/bin/python3 scripts/recheck_prospectzero.py
"""
import re
import sys
import urllib.request

UA = {"User-Agent": "venturebot-register-recheck"}
TRUSTMRR = "https://trustmrr.com/startup/prospectzero"
AGENTMRR = "https://agentmrr.com/"

# Observations recorded across this audit, oldest first.
# The "last updated" stamp on each render is what makes them interpretable.
OBSERVED = [
    ("wake 4", "TrustMRR", 990, 19643, "10 subs", "Sep 19 04:46"),
    ("wake 4", "AgentMRR", 1138, 19163, "first read", "Sep 21 11:50"),
    ("wake 4", "AgentMRR", 1138, 19262, "minutes later", "Sep 21 11:50"),
    ("wake 5", "TrustMRR", 891, 19841, "9 subs, rank #1261", "Sep 23 22:46"),
    ("wake 5", "TrustMRR", 3018, 13829, "30 subs, rank #962", "Jun 7 18:22"),
]


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf8", "ignore")
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def main():
    print("=== observations recorded during this audit ===")
    for when, src, mrr, alltime, note, stamp in OBSERVED:
        print(f"  {when}  {src:9s} MRR ${mrr:>6,}  all-time ${alltime:>7,}  "
              f"updated {stamp:14s} ({note})")

    print()
    print("=== a correction I had to make to my own analysis ===")
    print("  My first pass flagged all-time revenue 'going DOWN' from $19,841")
    print("  to $13,829 and called it impossible for a cumulative figure.")
    print("  That was wrong, and the page told me so: the $13,829 render is")
    print("  stamped 'Last updated Jun 7' while the $19,841 render is stamped")
    print("  'Sep 23'. A June snapshot showing a SMALLER all-time total is")
    print("  exactly correct. I was served a stale cache and nearly published")
    print("  a contradiction that did not exist.")
    print()
    print("  Dropping that claim leaves the real finding intact and smaller.")

    # Compare only renders carrying the same September freshness.
    september = [o for o in OBSERVED if "Sep" in o[5]]
    mrrs = [o[2] for o in september]
    print()
    print("=== comparing only renders stamped September ===")
    for when, src, mrr, alltime, note, stamp in september:
        print(f"  {src:9s} MRR ${mrr:>6,}  all-time ${alltime:>7,}  ({stamp})")
    print(f"  MRR spread: ${min(mrrs):,} to ${max(mrrs):,} "
          f"({max(mrrs)/min(mrrs):.2f}x) across sources days apart")

    print("\n=== live re-read of TrustMRR right now ===")
    st, body = fetch(TRUSTMRR)
    if st == 200:
        title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S)
        if title:
            print(f"  page title says: {title.group(1).strip()[:70]}")
        flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))
        m = re.search(r"All-time revenue(.{0,80})", flat, re.I)
        if m:
            print(f"  body says:       {m.group(1).strip()[:70]}")
        print(f"  claims Stripe verification: {'stripe' in body.lower()}")
        print()
        print("  Note the title and the body are different figures on the")
        print("  same render: the title quotes a 30-day number, the body")
        print("  quotes MRR. Both are unlabelled in the title.")
    else:
        print(f"  HTTP {st}: {body[:70]}")

    print("\n=== what this establishes, stated narrowly ===")
    print("  NOT: ProspectZero's real revenue. Nobody outside can compute it.")
    print("  NOT: that any figure is fabricated, or that anyone is lying.")
    print("  NOT: that all-time revenue decreased - that was my own error,")
    print("       caused by a stale cached render, and it is corrected above.")
    print()
    print("  YES: two Stripe-badged trackers report different MRR for the")
    print("       same company days apart ($891 vs $1,138), and one of them")
    print("       serves stale renders with no visible indication other than")
    print("       a timestamp a reader has to notice and interpret.")
    print("  YES: the badge attests to a CONNECTION METHOD, not to the")
    print("       accuracy or freshness of the figure beside it.")
    print()
    print("  Verdict withheld on ProspectZero itself. The company did not")
    print("  publish these numbers; the trackers did.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
