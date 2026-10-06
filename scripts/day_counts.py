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
    print(f"{'key':14s} {'origin':12s} {'days':>5s}  measures")
    for key, (origin, meaning) in sorted(ORIGINS.items(),
                                         key=lambda kv: kv[1][0]):
        print(f"  {key:14s} {origin}  {(today - origin).days:>4}  {meaning}")

    print()
    print("  Report the number beside the key you mean. These origins are")
    print("  within days of each other and have been conflated twice:")
    print("    2026-09-26: 'day twelve/fourteen' of analytics, actually nine")
    print("    2026-10-06: 'day 19' of the moratorium, actually twelve")
    print("  In both cases the wrong number was the count from a NEARBY")
    print("  origin, which is why it survived a sanity check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
