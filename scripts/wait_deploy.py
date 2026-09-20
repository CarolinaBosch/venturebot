#!/usr/bin/env python3
"""Wait for a GitHub Pages deploy, in bounded slices that cannot stall a wake.

Written after the 2026-09-20 07:00 wake was killed by the cron watchdog:

    TimeoutError: Cron job 'VentureBot Wake Cycle' idle for 615s (limit 600s)
    - last activity: sequential tool running (30s): terminal

A wake had been waiting for a Pages deploy inside one long-blocking terminal
call. The scheduler sees no tool activity for the whole wait, so a wait long
enough to be useful is also long enough to look like a hang.

This polls the live site for an expected marker and EXITS after at most
--max-wait seconds (default 75, well under the 600s inactivity limit).
Call it again if it has not landed yet - several short calls keep the
scheduler seeing activity, one long call does not.

    python3 scripts/wait_deploy.py --path /runway.json --contains '"wake": 1'
    python3 scripts/wait_deploy.py --path /journal/2026-09-20.md --contains "Wake 1"

Exit 0 = marker present (deploy landed). Exit 2 = not yet (call again).
"""
import argparse
import sys
import time
import urllib.request

BASE = "https://venturebot.dev"


def fetch(path):
    req = urllib.request.Request(
        BASE + path + f"?cb={int(time.time())}",
        headers={"User-Agent": "venturebot-deploy-wait"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf8", "ignore")
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True)
    ap.add_argument("--contains", required=True)
    ap.add_argument("--max-wait", type=int, default=75,
                    help="seconds; keep well under the 600s cron watchdog")
    ap.add_argument("--interval", type=int, default=15)
    args = ap.parse_args()

    deadline = time.time() + args.max_wait
    attempt = 0
    while True:
        attempt += 1
        st, body = fetch(args.path)
        found = st == 200 and args.contains in body
        print(f"  attempt {attempt}: status={st} marker={'FOUND' if found else 'absent'}",
              flush=True)
        if found:
            print(f"deploy landed: {args.path} contains {args.contains!r}")
            return 0
        if time.time() + args.interval >= deadline:
            break
        time.sleep(args.interval)

    print(f"NOT YET after {args.max_wait}s - run this again rather than "
          f"waiting longer in one call")
    return 2


if __name__ == "__main__":
    sys.exit(main())
