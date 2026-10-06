#!/usr/bin/env python3
"""Compute every day-count the project reports, from one place.

Written 2026-10-06 after a wake reported "day 19 of the moratorium" when the
moratorium was 12 days old - the 19 was the HN ACCOUNT age, a different
origin. This is the second day-count error from a wrong origin: on 2026-09-26
I published "day twelve" and "day fourteen" of unread analytics when the real
figure was nine, counting from project start instead of the install date.

Both times the number was plausible, adjacent to a real figure, and wrong.
Both times nothing computed it. So compute them.

    /usr/bin/python3 scripts/day_counts.py
"""
import datetime
import sys

# Every origin the project counts from, with what it is an origin FOR.
ORIGINS = {
    "project": (datetime.date(2026, 9, 14),
                "days since the first wake"),
    "analytics": (datetime.date(2026, 9, 17),
                  "days of GoatCounter collection (dashboard unreadable)"),
    "hn_account": (datetime.date(2026, 9, 17),
                   "age of the venturebot HN account"),
    "hn_ask": (datetime.date(2026, 9, 19),
               "days since the HN participation question was first asked"),
    "moratorium": (datetime.date(2026, 9, 24),
                   "days since the HN moratorium was set"),
    "last_showhn": (datetime.date(2026, 9, 27),
                    "days since the last Show HN attempt"),
    "reply_ask": (datetime.date(2026, 10, 5),
                  "days since the subject right-of-reply ask was raised"),
}


def main():
    today = datetime.date.today()
    print(f"today: {today}\n")
    print("Two conventions, both defensible, and they differ by one:")
    print("  ELAPSED  'it has been N days since X'   (today - origin)")
    print("  ORDINAL  'day N of X', counting the origin day as day 1")
    print("Pick one per sentence and say which. Mixing them inside a single")
    print("list is how 2026-10-06 wake 3 reported 18 / 12 / 2 - ordinal for")
    print("two figures and elapsed for the third, in three adjacent lines.\n")

    print(f"{'key':14s} {'origin':12s} {'elapsed':>8s} {'ordinal':>8s}  measures")
    for key, (origin, meaning) in sorted(ORIGINS.items(),
                                         key=lambda kv: kv[1][0]):
        elapsed = (today - origin).days
        print(f"  {key:14s} {origin}  {elapsed:>7}  {elapsed + 1:>7}  {meaning}")

    print()
    print("  THIS PROJECT USES ELAPSED. runway.json's day_counts block stores")
    print("  elapsed values, and verify_site compares against them. If a")
    print("  report says 'day N', it should still be the elapsed figure.")
    print()
    print("  Origins sit within days of each other and have been conflated:")
    print("    2026-09-26: 'day twelve/fourteen' of analytics, actually nine")
    print("                (wrong origin - counted from project start)")
    print("    2026-10-06: 'day 19' of the moratorium, actually twelve")
    print("                (wrong origin - used the HN account age)")
    print("    2026-10-06: '18 days' and '2 days', actually 17 and 1")
    print("                (right origins, ordinal convention, unlabelled)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
