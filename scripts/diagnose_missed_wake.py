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
    """Real Sleep/Wake/DarkWake state changes for a day.

    pmset's log is dominated by 'Assertions' lines (processes asking to keep
    the machine awake) that contain the words Sleep and Wake without being
    state changes. An earlier version of this script matched those loosely
    and then found none of them, reporting 'cannot determine cause' for a
    day whose log was complete - a false unknown.

    Real state changes appear in the event-type column, which follows the
    timestamp and timezone, e.g.:
        2026-09-22 06:47:49 -0700 Sleep               Entering Sleep state...
    """
    out = subprocess.run(["pmset", "-g", "log"],
                         capture_output=True, text=True).stdout
    events = []
    for line in out.splitlines():
        if not line.startswith(day):
            continue
        # timestamp(2) + timezone(1) = 3 fields before the event type
        parts = line.split(None, 4)
        if len(parts) >= 4 and parts[3] in ("Sleep", "Wake", "DarkWake"):
            events.append((line[:19], parts[3]))
    return events


def log_covers(day):
    """Did pmset record ANYTHING that day? Distinguishes 'no events' from
    'no log'. Without this, a rotated log looks identical to a quiet day."""
    out = subprocess.run(["pmset", "-g", "log"],
                         capture_output=True, text=True).stdout
    hours = {l[11:13] for l in out.splitlines() if l.startswith(day)}
    return len(hours)


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
    hours_logged = log_covers(day)

    if hours_logged == 0:
        print(f"\npmset has NO log coverage for {day} (rotated out).")
        print("Cannot determine the cause. Say 'unknown' and mean it.")
        return 2

    prior = [e for e in events
             if datetime.datetime.strptime(e[0], "%Y-%m-%d %H:%M:%S") <= target]
    after = [e for e in events
             if datetime.datetime.strptime(e[0], "%Y-%m-%d %H:%M:%S") > target]

    print(f"\n=== power state at {target} ===")
    print(f"  pmset log covers {hours_logged}/24 hours of {day}")
    print(f"  Sleep/Wake state changes that day: {len(events)}")
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

    # Coverage gate. pmset's log rotates, so an old day can show zero events
    # simply because its lines are gone. Only claim the machine was awake
    # when the log is dense enough to have recorded a sleep had one occurred.
    if hours_logged < 20:
        print(f"VERDICT: INSUFFICIENT EVIDENCE. pmset covers only "
              f"{hours_logged}/24 hours")
        print("of that day - its log has rotated - so the absence of sleep")
        print("events proves nothing about the slot. No run record exists,")
        print("but the cause cannot be established from here. Unknown, and")
        print("saying so is the honest answer rather than inferring 'awake'")
        print("from a log that is simply missing.")
        return 2

    print("VERDICT: the machine was AWAKE through the slot - pmset logged")
    print(f"activity across {hours_logged}/24 hours of that day and recorded")
    print("zero sleep/wake transitions - yet no run record exists and no")
    print("commit landed. Sleep is ruled out. The job did not fire at all,")
    print("which points at the scheduler or the host process, not at the")
    print("agent: a wake that ran and failed would have left an output")
    print("file, as the 2026-09-20 watchdog kill did.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
