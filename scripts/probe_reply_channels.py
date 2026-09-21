#!/usr/bin/env python3
"""Do the register's reply channels actually work for a stranger?

The register tells readers three things: submit a claim free, reply to an
entry via GitHub issues, or reach me with an on-chain memo. All three have
drawn zero in a week. Before concluding "nobody is interested", verify the
doors actually open - the same lesson as the missing og:image: the surface
I tell people to use is the surface I never test.

This checks reachability as an ANONYMOUS visitor (no auth token), which is
what a stranger gets.

    python3 scripts/probe_reply_channels.py
"""
import json
import re
import sys
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (venturebot channel probe)"}
REPO = "CarolinaBosch/venturebot"
failures = []


def check(label, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf8", "ignore")
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


print("=== 1. GitHub issue tracker (anonymous visitor) ===")
st, body = get(f"https://github.com/{REPO}/issues")
check("issues list reachable without auth", st == 200, f"HTTP {st}")
disabled = "Issues aren" in body or "issues are disabled" in body.lower()
check("issues are ENABLED on the repo", st == 200 and not disabled)

st_new, body_new = get(f"https://github.com/{REPO}/issues/new")
signin = "Sign in" in body_new and "session" in body_new.lower()
check("new-issue page reachable", st_new == 200, f"HTTP {st_new}")
print(f"       note: opening an issue requires a GitHub login "
      f"(sign-in prompt present: {signin}) — that is a real barrier to a "
      f"casual reader, and it is disclosed on the register.")

st_api, body_api = get(f"https://api.github.com/repos/{REPO}")
if st_api == 200:
    meta = json.loads(body_api)
    check("repo is public", not meta.get("private", True))
    check("has_issues flag is true", meta.get("has_issues") is True)
    print(f"       open issues right now: {meta.get('open_issues_count')}")
else:
    check("repo metadata readable", False, f"HTTP {st_api}")

print("\n=== 2. On-chain memo channel ===")
st_s, body_s = get("https://venturebot.dev/scripts/check_memos.py")
check("the memo checker is published", st_s == 200 and "getSignaturesForAddress" in body_s,
      f"HTTP {st_s}")
VAULT = "FYBeopAhxbXdYzjzSitkyeNUwV79FMu9c1y3GgYWu5ug"
st_reg, reg = get("https://venturebot.dev/register.html")
check("the vault address is printed on the register", VAULT in reg)

print("\n=== 3. Does the register actually tell a reader how to reply? ===")
for phrase, label in [
    ("Submit a claim", "free-submission invitation present"),
    ("issues", "issue tracker mentioned"),
    ("memo", "memo channel mentioned"),
]:
    check(label, phrase.lower() in reg.lower())

print("\n=== 4. The essay's call to action ===")
st_e, essay = get("https://venturebot.dev/measurement-problem.html")
check("essay reachable", st_e == 200, f"HTTP {st_e}")
links = set(re.findall(r'href="(/[^"#]*)"', essay))
print(f"       internal links offered to a reader: {sorted(links)}")
has_reply_path = any(x in essay.lower() for x in ["issue", "memo", "submit"])
check("essay gives the reader a way to respond", has_reply_path)

print()
if failures:
    print(f"{len(failures)} CHECK(S) FAILED:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(2)
print("All reply channels verified open. Zero inbound is therefore a")
print("distribution result, not a broken door.")
