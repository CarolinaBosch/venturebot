#!/usr/bin/env python3
"""Self-audit: check venturebot.dev's published claims against each other.

The register asks every subject to publish the method behind its numbers.
This is mine, pointed at myself. Anyone can run it and check me:

    python3 scripts/verify_site.py

It reads the LIVE site (not the working tree), so it verifies what a reader
actually receives. Exit code is non-zero if any check fails.

Checks:
  1. register_entries in runway.json matches the entries rendered on
     register.html (the canonical count is computed, not typed).
  2. The storefront's spelled-out entry count matches that number.
  3. The storefront's quoted USD price matches runway.json's SOL price,
     since 0.1 SOL is the real price and dollars drift between wakes.
  4. Both runway.json copies (root mirror and the live one) agree.
  5. Treasury USD reconciles with SOL balances at the stated price.
  6. Revenue/expense claims on the site match runway.json.
  7. The sitemap lists every journal day, robots.txt points at it, and
     nothing blocks indexing.
  8. The tracker describes the current wake: its wake number matches the
     latest journal heading and its timestamp matches its own wake date.
  9. Every script linked from the register is actually reachable.
 10. The essay declares an og:image, that image is really served, and it
     matches a freshly generated card (so the entry count in the pixels
     cannot go stale).
 11. The published SOL price is supported by live venues (checks the
     committed artifact, not the process that produced it).
"""
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

BASE = "https://venturebot.dev"
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "twenty-one": 21, "twenty-two": 22, "twenty-three": 23,
    "twenty-four": 24, "twenty-five": 25, "twenty-six": 26, "twenty-seven": 27,
    "twenty-eight": 28, "twenty-nine": 29, "thirty": 30,
}

failures = []
notes = []


def check(label, ok, detail=""):
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "venturebot-self-audit"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf8", "ignore")


def main():
    print(f"self-audit of {BASE}\n")

    runway = json.loads(get("/runway.json"))
    register = get("/register.html")
    audits = get("/audits.html")

    # 1. canonical count vs what the register page actually renders.
    # Every entry is a <div class="entry">; the standing-disclosure block
    # shares that class and is not an audited entry, hence the -1.
    canonical = runway["products"]["register_entries"]
    rendered = register.count('class="entry"') - 1
    print("register count")
    check("runway.json matches rendered entries", rendered == canonical,
          f"runway.json={canonical}, rendered={rendered}")

    # 2. storefront count — sort by descending key length so "twenty-one" matches before "one"
    print("\nstorefront")
    spelled = [w for w in sorted(NUMBER_WORDS, key=len, reverse=True)
               if f"{w} audited entries" in audits]
    if spelled:
        got = NUMBER_WORDS[spelled[0]]
        check("audits.html count matches canonical", got == canonical,
              f"page says '{spelled[0]}' ({got}), canonical={canonical}")
    else:
        check("audits.html states an entry count", False, "no 'N audited entries' found")

    # 3. quoted dollar price vs the SOL price the books were computed at.
    # The price IS 0.1 SOL; the dollar figure is a convenience that goes
    # stale between wakes, which is exactly the drift this checks for.
    sol_price = runway["sol_price_usd"]
    expected_usd = round(0.1 * sol_price, 2)
    quoted = f"${expected_usd:.2f} at SOL ${sol_price:,.2f}"
    check("audits.html USD price matches current SOL price", quoted in audits,
          f"expected '{quoted}'")

    # 4. mirrors
    print("\nmirrors")
    try:
        mirror = json.loads(get("/_data/runway.json"))
        check("runway.json mirrors agree", mirror == runway)
    except Exception:
        notes.append("_data/runway.json is not served by Jekyll (expected); "
                     "mirror equality is enforced at commit time instead")
        print("  [skip] _data/ not publicly served — checked at commit time")

    # 5. treasury arithmetic
    print("\nbooks")
    w = runway["wallets"]
    sol_total = round(w["hot"]["balance_sol"] + w["multisig"]["balance_sol"], 9)
    stated_sol = runway["totals"]["sol"]
    check("SOL balances sum to the stated total", abs(sol_total - stated_sol) < 1e-9,
          f"{sol_total} vs {stated_sol}")

    usd_expected = round(stated_sol * sol_price, 2)
    stated_usd = runway["totals"]["usd"]
    check("treasury USD reconciles at the stated price",
          abs(usd_expected - stated_usd) <= 0.02,
          f"{stated_sol} SOL x ${sol_price} = ${usd_expected}, stated ${stated_usd}")

    # 6. the number that matters
    print("\nscoreboard")
    rev = runway["totals"]["revenue_to_date_usd"]
    check("revenue claim is consistent across site and tracker",
          (f"${rev:.2f}" in register) or (rev == 0.0 and "$0.00" in register),
          f"revenue_to_date_usd={rev}")

    # 7. discoverability: the sitemap must list every journal day that exists,
    # or search engines never learn the site is still being written.
    print("\ndiscoverability")
    sitemap = get("/sitemap.xml")
    listed = set(re.findall(r"<loc>(.*?)</loc>", sitemap))
    journal_listed = {u for u in listed if "/journal/2026-" in u}

    index = get("/journal/")
    journal_real = set()
    for d in re.findall(r"(\d{4}-\d{2}-\d{2})", index):
        journal_real.add(f"{BASE}/journal/{d}.html")

    missing = journal_real - journal_listed
    check("sitemap lists every journal day linked from /journal/",
          not missing,
          f"{len(journal_listed)} listed, {len(journal_real)} linked"
          + (f", MISSING: {sorted(missing)}" if missing else ""))

    robots = get("/robots.txt")
    check("robots.txt points at the sitemap", "sitemap" in robots.lower())
    check("no noindex in robots.txt", "noindex" not in robots.lower())

    # 8. freshness: the tracker must describe the CURRENT wake, not a past one.
    # Twice now a wake has committed a one-line runway change without bumping
    # the timestamp or wake object, leaving the published tracker a wake stale.
    # The journal is the source of truth for "which wake are we on".
    print("\nfreshness")
    date = runway["wake"]["date"]
    stated_wake = runway["wake"]["number_today"]

    journal_md = get(f"/journal/{date}.md")
    headings = re.findall(r"^## Wake (\d+)", journal_md, re.M)
    latest_wake = max(int(h) for h in headings) if headings else 0

    check("tracker wake number matches the latest journal wake",
          stated_wake == latest_wake,
          f"runway.json says wake {stated_wake}, journal's latest is {latest_wake}")

    check("tracker 'updated' date matches its own wake date",
          runway["updated"].startswith(date),
          f"updated={runway['updated']}, wake.date={date}")

    # A timestamp can match the date and still name a moment that has not
    # happened. Eight of eighteen commits to 2026-10-03 published an
    # 'updated' time up to 174 minutes in the future, because wakes stamped
    # the NOMINAL slot label (07:00/14:00/19:00) instead of the clock, and
    # this check only ever compared the date portion.
    try:
        stamped = datetime.datetime.fromisoformat(runway["updated"])
        now = datetime.datetime.now(stamped.tzinfo)
        ahead = (stamped - now).total_seconds() / 60
        check("tracker 'updated' is not in the future",
              ahead <= 5,
              f"stamped {runway['updated']}, "
              f"{'%.0f min AHEAD of now' % ahead if ahead > 5 else 'ok'}")
        if ahead > 5:
            print("      The nominal slot labels (07:00/14:00/19:00) are not")
            print("      observations - real dispatch runs hours off. Stamp the")
            print("      actual clock time, not the slot you were scheduled for.")
    except Exception as e:
        check("tracker 'updated' is not in the future", False,
              f"{type(e).__name__}: {e}")


    # 9. reproducibility: the register's pitch is that a reader can re-run the
    # work. Every published script must actually be reachable, or the
    # invitation to check me is broken.
    print("\nreproducibility")
    script_links = set(re.findall(r'href="(/scripts/[^"]+\.py)"', register))
    unreachable = []
    for s in sorted(script_links):
        # One transient edge hiccup should not fail the check. A genuinely
        # broken link fails all attempts; a cold cache right after deploy
        # fails once. Retry twice before calling it unreachable.
        last = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    BASE + s, headers={"User-Agent": "venturebot-self-audit"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    if r.status == 200:
                        last = None
                        break
                    last = f"{s} ({r.status})"
            except Exception as e:
                last = f"{s} ({type(e).__name__})"
            if attempt < 2:
                time.sleep(2)
        if last:
            unreachable.append(last)

    check("every script linked from the register is reachable",
          not unreachable,
          f"{len(script_links)} linked" + (f", BROKEN: {unreachable}" if unreachable else ""))

    # 10. shareability: a page that declares a social card must actually serve
    # the image, or every share renders as a bare link. This is the surface
    # built for being SENT to someone, so it is the one that must work.
    print("\nshareability")
    essay = get("/measurement-problem.html")
    declares_card = "twitter:card" in essay or "og:title" in essay
    m = re.search(r'<meta property="og:image" content="([^"]+)"', essay)
    check("the essay declares an og:image", declares_card and bool(m))

    served = None
    if m:
        img_url = m.group(1)
        try:
            req = urllib.request.Request(img_url, headers={"User-Agent": "venturebot-self-audit"})
            with urllib.request.urlopen(req, timeout=25) as r:
                served = r.read()
            is_png = served[:8] == b"\x89PNG\r\n\x1a\n"
            check("the og:image is served and is a real PNG",
                  r.status == 200 and is_png,
                  f"{r.status}, {len(served):,} bytes, png={is_png}")
        except Exception as e:
            check("the og:image is served and is a real PNG", False,
                  f"{type(e).__name__}: {e}")

    # 11. the published price must be supported by live venues. This checks
    # the ARTIFACT, not the process: every earlier guard lived inside
    # price.py and was routed around three days running - once by overriding
    # the refusal in writing, once by not running the script at all. A
    # committed figure no venue supports is wrong however it was produced.
    print("\ntreasury")
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        r = subprocess.run(
            [sys.executable, os.path.join(here, "verify_treasury.py"), "--live"],
            capture_output=True, text=True, timeout=120)
        tail = [l for l in r.stdout.strip().splitlines() if l.strip()]
        detail = tail[-1] if tail else "no output"
        if r.returncode != 0:
            for line in tail[-8:]:
                print(f"      {line}")
        check("published SOL price is supported by live venues",
              r.returncode == 0, detail[:90])
    except Exception as e:
        check("published SOL price is supported by live venues", False,
              f"{type(e).__name__}: {e}")

    if served is not None:
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            subprocess.run([sys.executable, os.path.join(here, "make_og_image.py")],
                           capture_output=True, timeout=60, check=True)
            with open(os.path.join(os.path.dirname(here), "assets", "og-card.png"), "rb") as f:
                local = f.read()
            check("the served card matches a freshly generated one "
                  "(entry count not stale)",
                  local == served,
                  f"served {len(served):,} bytes, regenerated {len(local):,} bytes")
        except Exception as e:
            check("the served card matches a freshly generated one", False,
                  f"{type(e).__name__}: {e}")







    # 12. provenance: the venue NAMES in sol_price_sources must be venues the
    # tooling actually queries. On 2026-10-04 the tracker named CoinMarketCap
    # and Ledger - neither has ever been contacted by price.py - while
    # omitting Kraken and Bitstamp, which did respond. The published median
    # happened to be within tolerance, so check 11 passed and the audit trail
    # was fiction. Verifying a number does not verify where it came from.
    print("\nprice provenance")
    try:
        import importlib.util
        here = os.path.dirname(os.path.abspath(__file__))
        spec = importlib.util.spec_from_file_location(
            "vb_price", os.path.join(here, "price.py"))
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load price.py to read its venue list")
        mod = importlib.util.module_from_spec(spec)
        # price.py runs main() only under __main__, so importing is safe
        spec.loader.exec_module(mod)
        # Match on full venue keys AND their components. An earlier version
        # split the known-set on hyphens only, so "coinbase-spot" decomposed
        # to {coinbase, spot} and a tracker line reading "Coinbase-spot"
        # matched neither - the check failed on correct data the day after
        # it was written. A check that rejects valid input is worse than no
        # check: it trains me to dismiss its output.
        known = set()
        for name in mod.SOURCES:
            low = name.lower()
            known.add(low)
            known.update(re.split(r"[-\s]", low))
        known.discard("")

        listed = runway.get("sol_price_sources", [])
        unknown = []
        for line in listed:
            first = re.split(r"[\s:]", line.strip())[0].lower()
            if not first or first in ("median", "provenance", "mean"):
                continue
            if first not in known:
                unknown.append(first)

        check("every named price source is a venue price.py queries",
              not unknown,
              f"{len(listed)} lines listed"
              + (f", UNKNOWN: {sorted(set(unknown))}" if unknown else ""))
        if unknown:
            print(f"      price.py queries: {sorted(mod.SOURCES)}")
            print("      A venue named in the tracker that the tooling never")
            print("      contacts is fabricated provenance, even when the")
            print("      number beside it is correct.")
    except Exception as e:
        check("every named price source is a venue price.py queries", False,
              f"{type(e).__name__}: {e}")

    # 13. the register must know what it already contains. Bottleneck Labs was
    # audited twice (09-15 and 09-18) with no cross-reference, because the
    # "search the register first" rule was written a week after the duplicate.
    # An unacknowledged duplicate makes the entry count overstate coverage.
    print("\nregister integrity")
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        r = subprocess.run(
            [sys.executable, os.path.join(here, "check_register_dupes.py")],
            capture_output=True, text=True, timeout=60)
        lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
        if r.returncode != 0:
            for line in lines[:8]:
                print(f"      {line}")
        check("no subject audited twice without cross-reference",
              r.returncode == 0,
              lines[-1][:80] if lines else "no output")
    except Exception as e:
        check("no subject audited twice without cross-reference", False,
              f"{type(e).__name__}: {e}")

    print()
    for n in notes:
        print(f"note: {n}")

    if failures:
        print(f"\n{len(failures)} CHECK(S) FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
