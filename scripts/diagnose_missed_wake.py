#!/usr/bin/env python3
"""Why did a wake slot produce no commit?

Two very different causes look identical from the outside:
  - the agent ran and failed (a defect I must fix), or
  - the machine was asleep so the cron never fired (not a defect).

Day 7's miss was the first; day 9's 07:00 miss was the second. Guessing
between them is exactly the error this project keeps making, so this
answers it from the power log instead.

    python3 scripts/diagnose_missed_wake.py 2026-09-22 07:00
"""
import datetime
import re
import subprocess
import sys


def power_events(day):
    out = subprocess.run(["pmset", "-g", "log"],
                         capture_output=True, text=True).stdout
    events = []
    for line in out.splitlines():
        if not line.startswith(day):
            continue
        m = re.search(r"\b(DarkWake|Wake|Sleep)\s{2,}", line)
        if m:
            events.append((line[:19], m.group(1)))
    return events


def output_files(day):
    """Did the job actually produce a run record for that day?"""
    import glob
    import os
    d = os.path.expanduser("~/.hermes/cron/output/5d66cb295613")
    return sorted(glob.glob(os.path.join(d, f"{day}_*.md")))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    day, hhmm = sys.argv[1], sys.argv[2]
    target = datetime.datetime.strptime(f"{day} {hhmm}", "%Y-%m-%d %H:%M")

    # Check for a run record FIRST. A machine can be asleep at the exact
    # scheduled minute and the job still fire late on wake - in which case
    # sleep is not the explanation, and an output file proves it ran.
    runs = output_files(day)
    near = []
    for p in runs:
        import os
        stamp = os.path.basename(p)[:19].replace("_", " ").replace("-", ":", 2)
        try:
            t = datetime.datetime.strptime(os.path.basename(p)[:19],
                                           "%Y-%m-%d_%H-%M-%S")
        except ValueError:
            continue
        if abs((t - target).total_seconds()) <= 3600:
            near.append((t, p))

    print(f"=== run records for {day} ===")
    if runs:
        for p in runs:
            print(f"  {p.split('/')[-1]}")
    else:
        print("  (none)")

    if near:
        t, p = near[0]
        print(f"\nA run record EXISTS within an hour of the slot: {t}")
        print("So the job DID fire. Sleep is not the explanation - read that")
        print("file for the real cause (watchdog timeout, crash, error).")
        print(f"  {p}")
        return 2

    events = power_events(day)
    if not events:
        print(f"\nno power events recorded for {day} - cannot determine cause")
        return 2

    prior = [e for e in events
             if datetime.datetime.strptime(e[0], "%Y-%m-%d %H:%M:%S") <= target]
    after = [e for e in events
             if datetime.datetime.strptime(e[0], "%Y-%m-%d %H:%M:%S") > target]

    print(f"\n=== power state at {target} ===")
    if prior:
        ts, kind = prior[-1]
        print(f"  last event before slot: {ts}  {kind}")
    if after:
        ts, kind = after[0]
        print(f"  next event after slot:  {ts}  {kind}")

    print()
    if prior and prior[-1][1] in ("Sleep", "DarkWake"):
        gap = ""
        if after:
            woke = datetime.datetime.strptime(after[0][0], "%Y-%m-%d %H:%M:%S")
            gap = (f" (awake again at {after[0][0]}, "
                   f"{int((woke-target).total_seconds()//60)} min later)")
        print(f"VERDICT: machine asleep at the slot{gap}, and NO run record")
        print("exists for it. The cron could not fire; nothing ran and nothing")
        print("crashed. Not an agent defect - recovery is the next wake.")
        return 0

    print("VERDICT: machine appears to have been awake and no run record")
    print("exists. Neither sleep nor a logged failure explains this - look")
    print("at the scheduler itself before assuming anything.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
