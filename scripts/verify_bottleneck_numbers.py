#!/usr/bin/env python3
"""Pull specific numbers off the Bottleneck artifacts: HN thread engagement,
dev.to reaction/comment counts, and whether venturebot appears on favors.dev."""
import re, ssl, json, urllib.request, datetime

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
ctx = ssl.create_default_context()

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
          "Accept": "text/html,application/xhtml+xml,*/*"})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", "replace")

res = {"checked_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}

# --- HN thread via the official Firebase API (primary source, not scraping) ---
try:
    item = json.loads(get("https://hacker-news.firebaseio.com/v0/item/49264777.json"))
    res["hn_thread"] = {
        "title": item.get("title"),
        "by": item.get("by"),
        "score": item.get("score"),
        "descendants": item.get("descendants"),
        "time_utc": datetime.datetime.utcfromtimestamp(item["time"]).isoformat() + "Z" if item.get("time") else None,
        "type": item.get("type"),
        "dead": item.get("dead", False),
        "text_excerpt": re.sub(r"<[^>]+>", " ", item.get("text", ""))[:400],
    }
except Exception as e:
    res["hn_thread"] = {"error": str(e)[:200]}
print("HN:", json.dumps(res["hn_thread"], indent=2)[:900])

# --- dev.to via its public API (primary source) ---
res["devto"] = {}
for slug in ["i-audited-25-software-landing-pages-the-same-5-conversion-leaks-kept-appearing-5f91",
             "i-shipped-a-paid-service-with-one-html-file-and-a-45-line-node-server-26hh",
             "i-spent-58-testing-founder-distribution-here-is-what-happened-39h4"]:
    try:
        a = json.loads(get(f"https://dev.to/api/articles/conversionrescue/{slug}"))
        res["devto"][slug[:40]] = {
            "title": a.get("title"),
            "published_at": a.get("published_at"),
            "public_reactions_count": a.get("public_reactions_count"),
            "comments_count": a.get("comments_count"),
            "page_views_count": a.get("page_views_count"),
            "tags": a.get("tag_list"),
        }
    except Exception as e:
        res["devto"][slug[:40]] = {"error": str(e)[:160]}
print("\nDEVTO:", json.dumps(res["devto"], indent=2)[:1400])

# --- favors.dev leaderboard: is Conversion Rescue / Saul still ranked #1? ---
try:
    h = get("https://favors.dev/leaderboard")
    text = re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", " ", h)))
    res["favors"] = {
        "mentions_conversion_rescue": "conversion rescue" in text.lower(),
        "mentions_conversionrescue": "conversionrescue" in text.lower(),
        "excerpt": text[:600],
    }
except Exception as e:
    res["favors"] = {"error": str(e)[:200]}
print("\nFAVORS:", json.dumps(res["favors"], indent=2)[:900])

with open("/tmp/vb_bottleneck_nums.json", "w") as f:
    json.dump(res, f, indent=2)
print("\nwrote /tmp/vb_bottleneck_nums.json")
