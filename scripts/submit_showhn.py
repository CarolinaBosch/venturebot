#!/usr/bin/env python3
"""Attempt a Show HN submission for the register. This is the one probe that
submits: the /showlim gate renders identically on /submit either way, so the
only check that reveals whether the restriction lifted is an actual POST.

Reads credentials from the keystore outside the repo; never prints them.

    python3 scripts/submit_showhn.py

Exit codes:
  0  submitted (redirect to a story/item id, not /showlim)
  1  rejected by /showlim (the account-maturity gate)
  2  error (login failed, no tokens, or an unexpected response)
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

# The submission. Title must lead with "Show HN:". URL is the register page.
TITLE = "Show HN: The Agent Revenue Register — which AI revenue claims survive an audit"
URL = "https://venturebot.dev/register.html"


def main():
    if not os.path.exists(CREDS):
        print("no credentials at", CREDS)
        return 2
    with open(CREDS) as f:
        c = json.load(f)
    user, pw = c["username"], c["password"]

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
        return 2
    print("session: established")

    # Fetch the submit form to obtain fnid/fnop.
    form = op.open("https://news.ycombinator.com/submit", timeout=30).read().decode("utf8", "ignore")
    fnid = re.search(r'name="fnid"\s+value="([^"]+)"', form)
    fnop = re.search(r'name="fnop"\s+value="([^"]+)"', form)
    if not (fnid and fnop):
        print("FAIL: no fnid/fnop on /submit")
        return 2
    print("submit form: fnid/fnop present")

    # POST the real submission.
    body = urllib.parse.urlencode({
        "fnid": fnid.group(1),
        "fnop": fnop.group(1),
        "title": TITLE,
        "url": URL,
    }).encode()
    op.addheaders = [
        ("User-Agent", UA),
        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
        ("Content-Type", "application/x-www-form-urlencoded"),
        ("Origin", "https://news.ycombinator.com"),
        ("Referer", "https://news.ycombinator.com/submit"),
    ]
    resp = op.open("https://news.ycombinator.com/r", data=body, timeout=30)
    final_url = resp.geturl()
    html = resp.read().decode("utf8", "ignore")
    print("final url:", final_url)

    if "showlim" in final_url or "temporarily restricting" in html:
        print("RESULT: REJECTED by /showlim (account-maturity gate still up)")
        print(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))[:400])
        return 1

    # On success HN redirects to /newest or /item?id=NNN. Look for a story id.
    m = re.search(r"item\?id=(\d+)", final_url)
    if m:
        print(f"RESULT: SUBMITTED — item id {m.group(1)}")
        return 0
    if "newest" in final_url or "item" in final_url:
        print("RESULT: appears submitted (redirect to", final_url, ")")
        return 0

    print("RESULT: UNKNOWN — see response body")
    print(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))[:500])
    return 2


if __name__ == "__main__":
    sys.exit(main())
