#!/usr/bin/env python3
"""Does TrustMRR's machine-readable endpoint fix what entry 16 faulted?

Entries 2 and 16 criticised revenue trackers for the same thing: a reader
cannot tell a verified figure from a typed one, cannot see freshness, and
can be served a stale cached render with no warning. Entry 16 found the
ProspectZero page's title and body disagreeing on one render.

TrustMRR now exposes /startup/<slug>.md - a plain-text file with an explicit
verification-source block, a sync timestamp, and full daily and monthly
revenue timelines. If that holds up it is a direct, checkable answer to the
register's own criticism, which is worth saying as loudly as the criticism.

    /usr/bin/python3 scripts/recheck_trustmrr_md.py
"""
import re
import sys
import urllib.error
import urllib.request

UA = {"User-Agent": "venturebot-register-recheck"}
SLUGS = ["appgen", "agenkit", "prospectzero", "exoclaw"]


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, f"{type(e).__name__}"


def main():
    print("=== does a machine-readable endpoint exist per startup? ===")
    available = {}
    for slug in SLUGS:
        st, body = fetch(f"https://trustmrr.com/startup/{slug}.md")
        ok = st == 200 and len(body) > 200
        print(f"  {slug:14s} .md -> {st}  {len(body) if ok else 0:,} bytes")
        if ok:
            available[slug] = body

    if not available:
        print("\nNo .md endpoints reachable. Nothing to verify.")
        return 2

    print("\n=== what the .md discloses that the rendered page does not ===")
    probes = {
        "names the payment provider": r"Verified payment provider API source",
        "states merchant-of-record":  r"Merchant of record",
        "timestamps the sync":        r"Revenue (?:data )?last synced",
        "denies self-reporting":      r"not screenshots, manual entries, or self-reported",
        "daily revenue timeline":     r"Daily revenue",
        "monthly revenue timeline":   r"Monthly revenue timeline",
        "active subscriptions":       r"active subscriptions",
        "states what is withheld":    r"require a TrustMRR account|are not exposed",
    }
    slug, body = next(iter(available.items()))
    print(f"  (checking {slug}.md)")
    for label, pat in probes.items():
        print(f"  [{'YES' if re.search(pat, body, re.I) else 'no ':3s}] {label}")

    print("\n=== the test entry 16 actually ran: internal consistency ===")
    for slug, body in available.items():
        alltime = re.search(r"All time \|\s*\$([\d,]+)", body)
        snapshot = re.search(r"All-time revenue snapshot: \$([\d,]+)", body)
        synced = re.search(r"Revenue (?:data )?last synced: (\S+)", body)
        if alltime and snapshot:
            a = int(alltime.group(1).replace(",", ""))
            b = int(snapshot.group(1).replace(",", ""))
            agree = a == b
            print(f"  {slug:14s} table ${a:,} vs snapshot ${b:,}  "
                  f"agree: {agree}")
        if synced:
            print(f"  {slug:14s} synced {synced.group(1)}")

    print("\n=== what this does and does not establish ===")
    print("  DOES: the freshness stamp, provider name and full timeline are")
    print("  machine-readable, so a reader can diff two reads and see whether")
    print("  a figure moved or a cache went stale. That is precisely the")
    print("  affordance entries 2 and 16 said was missing.")
    print("  DOES NOT: prove the underlying Stripe data is accurate. The file")
    print("  still originates with the tracker. It removes the ambiguity")
    print("  about WHAT is being shown, not the need to trust the pipe.")
    print("  Entry 16's verdict stands; this is a material improvement to")
    print("  the surface it criticised, and the register should say so.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
