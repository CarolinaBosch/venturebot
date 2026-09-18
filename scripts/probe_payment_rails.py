#!/usr/bin/env python3
"""Probe monetization rails for what they require of a signup.
READ ONLY. Never submits a form, never supplies identity data.
Records: HTTP status, whether the page is reachable, and which
identity-requirement keywords appear in the delivered HTML."""
import json, re, ssl, urllib.request, urllib.error, datetime

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"

# service -> urls to read (signup / pricing / requirements docs)
TARGETS = {
    "stripe":        ["https://stripe.com/docs/connect/identity-verification",
                      "https://support.stripe.com/questions/know-your-customer-obligations"],
    "gumroad":       ["https://gumroad.com/signup", "https://help.gumroad.com/article/121-getting-paid"],
    "payhip":        ["https://payhip.com/signup"],
    "kofi":          ["https://ko-fi.com/signup"],
    "buymeacoffee":  ["https://buymeacoffee.com/signup"],
    "lemonsqueezy":  ["https://app.lemonsqueezy.com/register"],
    "polar":         ["https://polar.sh/signup", "https://docs.polar.sh/merchant-of-record/account-setup"],
    "paddle":        ["https://www.paddle.com/signup"],
    "github_sponsors":["https://github.com/sponsors"],
    "openrouter":    ["https://openrouter.ai/docs/api-reference/overview"],
}

KEYS = {
    "government id": r"government[- ]issued|government id|photo id|passport|driver'?s licen[cs]e",
    "ssn/tax id":    r"\bssn\b|social security|\bein\b|tax identification|tax id\b|w-?9\b|w-?8ben",
    "bank account":  r"bank account|routing number|iban\b|sort code|payout method",
    "phone/sms":     r"phone number|sms|text message|two-factor|2fa",
    "date of birth": r"date of birth|\bdob\b",
    "address":       r"home address|residential address|business address|street address",
    "legal entity":  r"legal entity|business entity|sole proprietor|incorporat",
    "kyc wording":   r"\bkyc\b|know your customer|identity verification|verify your identity",
}

ctx = ssl.create_default_context()
out = {"probed_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "method": "unauthenticated GET, browser UA; no form submitted, no identity data supplied",
       "services": {}}

for svc, urls in TARGETS.items():
    rows = []
    for u in urls:
        rec = {"url": u}
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA,
                    "Accept": "text/html,application/xhtml+xml,*/*"})
            with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
                body = r.read().decode("utf-8", "replace")
                rec["status"] = r.status
                rec["final_url"] = r.geturl()
                rec["bytes"] = len(body)
        except urllib.error.HTTPError as e:
            rec["status"] = e.code
            try: body = e.read().decode("utf-8", "replace")
            except Exception: body = ""
            rec["bytes"] = len(body)
        except Exception as e:
            rec["status"] = "ERROR"
            rec["error"] = str(e)[:160]
            body = ""
        low = body.lower()
        hits = sorted([k for k, pat in KEYS.items() if re.search(pat, low)])
        rec["requirement_keywords_found"] = hits
        rows.append(rec)
    out["services"][svc] = rows
    print(svc, [(r.get("status"), r.get("requirement_keywords_found")) for r in rows])

with open("/tmp/vb_rails.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nwrote /tmp/vb_rails.json")
