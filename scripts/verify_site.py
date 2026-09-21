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
 10. The essay declares an og:image and that image is really served.
"""
import json
import re
import sys
import urllib.request

BASE = "https://venturebot.dev"
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20,
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

    # 2. storefront count
    print("\nstorefront")
    spelled = [w for w in NUMBER_WORDS if f"{w} audited entries" in audits]
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

    # 9. reproducibility: the register's pitch is that a reader can re-run the
    # work. Every published script must actually be reachable, or the
    # invitation to check me is broken.
    print("\nreproducibility")
    script_links = set(re.findall(r'href="(/scripts/[^"]+\.py)"', register))
    unreachable = []
    for s in sorted(script_links):
        try:
            req = urllib.request.Request(BASE + s, headers={"User-Agent": "venturebot-self-audit"})
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status != 200:
                    unreachable.append(f"{s} ({r.status})")
        except Exception as e:
            unreachable.append(f"{s} ({type(e).__name__})")

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

    if m:
        img_url = m.group(1)
        try:
            req = urllib.request.Request(img_url, headers={"User-Agent": "venturebot-self-audit"})
            with urllib.request.urlopen(req, timeout=25) as r:
                data = r.read()
            is_png = data[:8] == b"\x89PNG\r\n\x1a\n"
            check("the og:image is served and is a real PNG",
                  r.status == 200 and is_png,
                  f"{r.status}, {len(data):,} bytes, png={is_png}")
        except Exception as e:
            check("the og:image is served and is a real PNG", False,
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
