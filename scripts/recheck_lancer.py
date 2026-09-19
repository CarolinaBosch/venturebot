"""Recheck entry 13 against the TrustMRR page read live on 2026-09-19."""

# Figures published in the entry (read earlier today)
entry = {"all_time": 196474, "rank": 362, "mrr": 21155, "subs": 126, "updated": "2026-09-18"}
# Figures on the page now
now = {"all_time": 196569, "rank": 364, "mrr": 21155, "subs": 126, "updated": "2026-09-19 20:34"}

print("=== drift since the entry was written (hours ago) ===")
for k in ("all_time", "rank", "mrr", "subs"):
    a, b = entry[k], now[k]
    mark = "" if a == b else f"   <-- DRIFTED {a} -> {b}"
    print(f"  {k:10s} entry={a:<10} now={b:<10}{mark}")
print(f"  page last_updated: entry cited {entry['updated']}, page now says {now['updated']}")

print()
print("=== ARPU: what the entry claimed vs what the primary source computes ===")
arpu_now = now["mrr"] / now["subs"]
print(f"  MRR ${now['mrr']:,} / {now['subs']} active subscriptions = ${arpu_now:.2f}")
print(f"  entry says 'roughly 100 users at ~$200/month'")
print(f"  -> subs understated ({now['subs']} not ~100); ARPU overstated (${arpu_now:.2f} not ~$200)")

print()
print("=== the pricing tiers explain the decline exactly ===")
PPL, UNL = 99, 333
early_mrr, early_users = 10000, 30
print(f"  disclosed tiers: Pay-Per-Lead ${PPL}/mo, Unlimited ${UNL}/mo")
print(f"  early: ~${early_mrr:,} MRR / ~{early_users} users = ${early_mrr/early_users:.2f}")
print(f"  ...which is the ${UNL} Unlimited tier almost exactly: {abs(early_mrr/early_users - UNL) < 6}")
print(f"  now:   ${arpu_now:.2f} sits between ${PPL} and ${UNL}")
# what mix produces the current ARPU?
# x * 333 + (1-x) * 99 = arpu_now
x = (arpu_now - PPL) / (UNL - PPL)
print(f"  implied mix: {x*100:.0f}% Unlimited / {(1-x)*100:.0f}% Pay-Per-Lead")
print(f"  i.e. ~{round(x*now['subs'])} on ${UNL}, ~{round((1-x)*now['subs'])} on ${PPL}")
print("  -> ARPU did not drift vaguely; the cheaper tier took share.")

print()
print("=== the entry's own open question, answered by the page it read ===")
print('  entry: "BuiltWithAgents says the founder exited a 15-person dev agency;')
print('          his own interview says he is still running it... recording the')
print('          disagreement rather than resolving it."')
print('  TrustMRR founder message (present tense, on the same page):')
print('    "Primary business is a dev shop that does 7 figures, this is a')
print('     side-project that took off"')
print("  -> the primary source I read directly resolves it: not exited.")
print("  -> and it reframes the subject: Lancer is a SIDE PROJECT of a 7-figure")
print("     dev shop, not a founder's main bet. That is material context for a")
print('     "no time for growth" business at $21K MRR.')
