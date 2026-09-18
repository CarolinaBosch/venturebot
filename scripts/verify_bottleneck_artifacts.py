#!/usr/bin/env python3
"""Verify the independently-checkable artifacts cited by the Bottleneck Labs
'7 AI models ran real businesses' report. Read-only."""
import json, re, ssl, urllib.request, urllib.error, datetime

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")

TARGETS = [
    ("hn_applyboost_thread", "https://news.ycombinator.com/item?id=49264777",
     ["ApplyBoost"]),
    ("devto_audited_25", "https://dev.to/conversionrescue/i-audited-25-software-landing-pages-the-same-5-conversion-leaks-kept-appearing-5f91",
     ["Conversion", "landing"]),
    ("devto_one_html_file", "https://dev.to/conversionrescue/i-shipped-a-paid-service-with-one-html-file-and-a-45-line-node-server-26hh",
     ["HTML"]),
    ("devto_58_distribution", "https://dev.to/conversionrescue/i-spent-58-testing-founder-distribution-here-is-what-happened-39h4",
     ["distribution"]),
    ("favors_leaderboard", "https://favors.dev/leaderboard", ["leaderboard"]),
    ("report_traces", "https://www.bottlenecklabs.com/blog/benchmarking-7-autonomous-businesses/traces",
     ["trace"]),
]

ctx = ssl.create_default_context()
out = {"checked_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "artifacts": {}}

def strip(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", h))

for name, url, expect in TARGETS:
    rec = {"url": url}
    body = ""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA,
              "Accept": "text/html,application/xhtml+xml,*/*"})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            body = r.read().decode("utf-8", "replace")
            rec["status"] = r.status
            rec["final_url"] = r.geturl()
    except urllib.error.HTTPError as e:
        rec["status"] = e.code
        try: body = e.read().decode("utf-8", "replace")
        except Exception: pass
    except Exception as e:
        rec["status"] = "ERROR"; rec["error"] = str(e)[:200]

    text = strip(body)
    rec["bytes"] = len(body)
    # body validation, not status+length
    rec["expected_strings_present"] = {s: (s.lower() in text.lower()) for s in expect}
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", body)
    rec["title"] = (m.group(1).strip()[:160] if m else None)
    # HN specific: comment count + whether the thread text survives
    if "ycombinator" in url:
        c = re.search(r"(\d+)\s+comments?", text)
        rec["hn_comments"] = c.group(1) if c else None
        rec["hn_has_spam_word"] = "spam" in text.lower()
    # dev.to specific: reaction / comment counters
    if "dev.to" in url:
        for label, pat in (("reactions", r"(\d+)\s*reactions?"),
                           ("comments", r"(\d+)\s*comments?")):
            mm = re.search(pat, text, re.I)
            rec[label] = mm.group(1) if mm else None
    out["artifacts"][name] = rec
    print(f"{name:24} {str(rec.get('status')):6} {rec['bytes']:>8}b "
          f"expect={rec['expected_strings_present']} "
          f"extra={{k:v for k,v in rec.items() if k in ('hn_comments','reactions','comments')}}".replace(
              "{k:v for k,v in rec.items() if k in ('hn_comments','reactions','comments')}",
              str({k: rec[k] for k in ('hn_comments', 'reactions', 'comments') if k in rec})))

with open("/tmp/vb_bottleneck.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nwrote /tmp/vb_bottleneck.json")
