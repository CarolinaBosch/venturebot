#!/usr/bin/env python3
"""Probe the Hacker News Show HN gate. Reads only — submits nothing.

Lives in the repo rather than /tmp because the last two copies of this
script evaporated: /tmp is cleared by the OS, and a check you cannot re-run
is a check you are asking people to take on trust.

Credentials are read from the keystore outside the repo and never printed.

    python3 scripts/probe_hn_gate.py

Note on why this probes by ATTEMPTING nothing: /submit renders identically
for a restricted and an unrestricted account - same form, same tokens, no
warning text. The restriction only appears on POST. So this script reports
account state (karma, age) and whether the submit form is reachable; it
CANNOT tell you the gate has lifted. Only a real submission can, and that
is a deliberate act, not a probe.
"""
import http.cookiejar
import json
import os
import re
import sys
import urllib.parse
import urllib.request

CREDS = os.path.expanduser("~/.hermes/profiles/venturebot/keys/hn-credentials.json")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")


def visible(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def main():
    if not os.path.exists(CREDS):
        print(f"no credentials at {CREDS}")
        return 1
    with open(CREDS) as f:
        c = json.load(f)
    user, pw = c["username"], c["password"]
    print(f"account: {user} (password not displayed)")

    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [
        ("User-Agent", UA),
        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
        ("Origin", "https://news.ycombinator.com"),
        ("Referer", "https://news.ycombinator.com/login"),
    ]
    op.open("https://news.ycombinator.com/login", timeout=30).read()
    op.open("https://news.ycombinator.com/login",
            data=urllib.parse.urlencode({"acct": user, "pw": pw, "goto": "news"}).encode(),
            timeout=30).read()
    if not any(ck.name == "user" for ck in cj):
        print("FAIL: no session established")
        return 1
    print("session: established")

    prof = visible(op.open(f"https://news.ycombinator.com/user?id={user}", timeout=30)
                   .read().decode("utf8", "ignore"))
    karma = re.search(r"karma:\s*(\d+)", prof)
    created = re.search(r"created:\s*(.+?)\s*karma", prof)
    print(f"karma: {karma.group(1) if karma else '?'}")
    print(f"age:   {created.group(1).strip() if created else '?'}")

    sub = op.open("https://news.ycombinator.com/submit", timeout=30).read().decode("utf8", "ignore")
    has_form = 'name="fnid"' in sub and 'name="title"' in sub
    print(f"submit form reachable: {has_form}")

    # Disclosure status - an account that posts must say what it is.
    pub = urllib.request.urlopen(
        urllib.request.Request(f"https://news.ycombinator.com/user?id={user}",
                               headers={"User-Agent": "Mozilla/5.0"}), timeout=30
    ).read().decode("utf8", "ignore")
    disclosed = "Autonomous AI agent" in pub and "Not a human" in pub
    print(f"profile discloses AI-agent status (logged-out view): {disclosed}")

    subs = urllib.request.urlopen(
        urllib.request.Request(f"https://news.ycombinator.com/submitted?id={user}",
                               headers={"User-Agent": "Mozilla/5.0"}), timeout=30
    ).read().decode("utf8", "ignore")
    posted = re.findall(r"item\?id=(\d+)", subs)
    print(f"submissions to date: {len(posted)}")

    print()
    print("This probe cannot determine whether the Show HN restriction has")
    print("lifted - /submit looks identical either way. Only an actual")
    print("submission reveals it, and that is a decision, not a check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
