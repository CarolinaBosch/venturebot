#!/usr/bin/env python3
"""Does the register contradict itself about ProspectZero?

Entry 2 (AgentMRR leaderboard, checked 2026-09-15) records ProspectZero at
$1,336 MRR. Entry 16 (ProspectZero, 2026-09-25) states that September-stamped
records put it "between $891 and $1,138" and computes a 1.28x spread.

$1,336 is a September-stamped observation sitting in the same HTML file.
Entry 16 computed a range without consulting the register it lives in.

This assembles every ProspectZero figure the register holds and computes the
real spread, separating cross-tracker disagreement from ordinary movement
within one tracker over time.

    /usr/bin/python3 scripts/recheck_prospectzero_spread.py
"""
import sys

# (date, tracker, MRR, all-time, where it is recorded)
OBSERVATIONS = [
    ("2026-09-15", "AgentMRR", 1336, 18965, "register entry 2"),
    ("2026-09-15", "AgentMRR", 1336, 19064, "register entry 2, re-check"),
    ("2026-09-19", "TrustMRR", 990, 19643, "register entry 16"),
    ("2026-09-21", "AgentMRR", 1138, 19163, "register entry 16"),
    ("2026-09-21", "AgentMRR", 1138, 19262, "register entry 16, minutes later"),
    ("2026-09-23", "TrustMRR", 891, 19841, "register entry 16"),
]


def main():
    print("=== every ProspectZero MRR figure the register holds ===")
    for date, tracker, mrr, alltime, where in OBSERVATIONS:
        print(f"  {date}  {tracker:9s} ${mrr:>5,}  all-time ${alltime:>7,}  ({where})")

    mrrs = [o[2] for o in OBSERVATIONS]
    lo, hi = min(mrrs), max(mrrs)
    print()
    print("=== the spread entry 16 published ===")
    print("  'between $891 and $1,138'  ->  1.28x")
    print()
    print("=== the spread the register actually contains ===")
    print(f"  ${lo:,} to ${hi:,}  ->  {hi/lo:.2f}x")
    print(f"  The high end (${hi:,}) comes from MY OWN entry 2, checked")
    print("  2026-09-15. It is September-stamped and it was not consulted.")

    print()
    print("=== separating the two effects ===")
    by_tracker = {}
    for date, tracker, mrr, _, _ in OBSERVATIONS:
        by_tracker.setdefault(tracker, []).append((date, mrr))
    for tracker, rows in sorted(by_tracker.items()):
        vals = [m for _, m in rows]
        span = f"{max(vals)/min(vals):.2f}x" if min(vals) else "n/a"
        first, last = rows[0], rows[-1]
        print(f"  {tracker}: ${min(vals):,}-${max(vals):,} ({span}) "
              f"from {first[0]} to {last[0]}")
    print()
    print("  AgentMRR moved $1,336 -> $1,138 within its own data over six")
    print("  days. That is ordinary MRR movement, not a tracker disagreeing")
    print("  with a rival. Entry 16's 1.28x compares TrustMRR Sep 23 against")
    print("  AgentMRR Sep 21 - a defensible cross-tracker figure.")
    print()
    print("  So entry 16's NUMBER is fine; its SCOPE claim is not. Saying")
    print("  'September-stamped records put it between $891 and $1,138' is")
    print("  false about the register's own contents, which hold $1,336.")

    print()
    print("=== all-time figures, as a consistency check ===")
    ordered = sorted(OBSERVATIONS, key=lambda o: o[0])
    prev = None
    for date, tracker, _, alltime, _ in ordered:
        flag = ""
        if prev and alltime < prev[1] and tracker == prev[0]:
            flag = "  <-- fell within the same tracker"
        print(f"  {date}  {tracker:9s} ${alltime:>7,}{flag}")
        prev = (tracker, alltime)
    print()
    print("  Cross-tracker all-time totals are not comparable: TrustMRR read")
    print("  $19,643 on Sep 19 while AgentMRR read $19,163 on Sep 21. Two")
    print("  databases, different coverage. No contradiction, and no basis")
    print("  to call either wrong.")

    print()
    print("=== what this changes ===")
    print("  Entry 16's verdict (Mixed) stands. Its central finding stands:")
    print("  a Stripe badge attests to a connection method, not to the")
    print("  figure beside it. The scope sentence needs correcting, and the")
    print("  register needs to stop contradicting itself about one company")
    print("  across two entries in the same file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
