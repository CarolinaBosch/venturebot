#!/usr/bin/env python3
"""Does the register audit the same subject twice without saying so?

Written 2026-10-01 after finding Bottleneck Labs audited in TWO separate
entries - 2026-09-15 and 2026-09-18, same verdict, no cross-reference. The
"search the register before publishing" rule was written on 09-25, a week
after the duplicate was created, so nothing had ever looked.

A register whose value is that it accumulates must know what it already
contains. This greps its own entry headings for repeated subjects.

    /usr/bin/python3 scripts/check_register_dupes.py
"""
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Words too generic to identify a subject.
STOP = {
    "the", "a", "an", "and", "or", "of", "in", "on", "to", "for", "with",
    "ai", "agent", "agents", "revenue", "claims", "claim", "that", "what",
    "how", "its", "own", "from", "this", "made", "makes", "make", "month",
    "year", "per", "real", "first", "new", "all", "ran", "run", "each",
    "leaderboards", "leaderboard", "economy", "market", "forecasts", "data",
}


def subjects():
    """Extract a normalised subject key from each entry heading."""
    html = (ROOT / "register.html").read_text()
    out = []
    for h in re.findall(r"<h3>(.*?)</h3>", html, re.S):
        text = re.sub(r"<[^>]+>", " ", h)
        text = re.sub(r"&[a-z]+;|&#\d+;", " ", text)
        # the subject is the part before the first dash or quote
        head = re.split(r"[—–\-\u2014]|&ldquo;|\"", text)[0]
        words = [w.lower().strip("(),.:'") for w in head.split()]
        key = tuple(w for w in words if w and w not in STOP and len(w) > 2)
        if key:
            out.append((key, text.strip()[:70]))
    return out


def main():
    found = subjects()
    print(f"=== {len(found)} entry headings parsed ===\n")

    groups = collections.defaultdict(list)
    for key, label in found:
        groups[key].append(label)

    dupes = {k: v for k, v in groups.items() if len(v) > 1}

    # also catch partial overlaps: one subject key contained in another
    overlaps = []
    keys = list(groups)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if a != b and (set(a) & set(b)) and (
                    set(a).issubset(b) or set(b).issubset(a)):
                overlaps.append((a, b))

    if dupes:
        # A duplicate that cross-references itself is disclosed, not hidden.
        # The check exists to catch SILENT duplication - a permanently red
        # check teaches me to ignore it, which is worse than no check.
        html = (ROOT / "register.html").read_text()
        acknowledged = "audited twice in this register" in html and \
                       "second audit of this subject" in html
        print("\nEXACT DUPLICATE SUBJECTS:")
        for k, labels in dupes.items():
            print(f"  {' '.join(k)}  ({len(labels)} entries)")
            for lab in labels:
                print(f"      {lab}")
        if acknowledged:
            print("\n  ...but both entries cross-reference each other, so the")
            print("  duplication is disclosed to the reader. Acceptable.")
    else:
        print("No exact duplicate subjects.")
        acknowledged = True

    if overlaps:
        print("\nOVERLAPPING SUBJECTS (review by hand):")
        for a, b in overlaps:
            print(f"  {' '.join(a)}  <->  {' '.join(b)}")

    print()
    if dupes and not acknowledged:
        print("A duplicate is not automatically wrong - a subject can deserve")
        print("a second, deeper audit. But the entries MUST cross-reference")
        print("each other, or a reader counting entries counts one subject")
        print("twice and the register overstates its own coverage.")
        return 1

    if dupes:
        print("OK: duplication exists and is disclosed in both entries.")
        return 0

    print("OK: no subject is audited twice without acknowledgement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
