"""Recheck entry 14 against the TrustMRR page read live on 2026-09-19."""

# Figures on the TrustMRR page read directly today (2026-09-19 02:15 PM)
now = {"mrr": 40981, "subs": 561, "all_time": 1870397, "rank": 54}
# The story's own body cites these as "as of June 2026" (Stripe-verified)
june = {"mrr": 55400, "subs": 751, "all_time": 1730000}

print("=== the '$1M ARR' headline vs the verified figure ===")
arr_now = now["mrr"] * 12
arr_june = june["mrr"] * 12
print(f"  current MRR ${now['mrr']:,} x 12 = ${arr_now:,} ARR")
print(f"  -> '$1M ARR' is {1000000/arr_now:.2f}x the verified current ARR")
print(f"  story's own June MRR ${june['mrr']:,} x 12 = ${arr_june:,} ARR")
print(f"  -> even the June figure is {1000000/arr_june:.2f}x short of $1M ARR")

print()
print("=== the contraction (churn) ===")
mrr_chg = (now["mrr"] - june["mrr"]) / june["mrr"] * 100
subs_chg = (now["subs"] - june["subs"]) / june["subs"] * 100
at_chg = (now["all_time"] - june["all_time"]) / june["all_time"] * 100
print(f"  MRR:        ${june['mrr']:,} -> ${now['mrr']:,}   {mrr_chg:+.1f}%")
print(f"  subs:       {june['subs']} -> {now['subs']}   {subs_chg:+.1f}%")
print(f"  all-time:   ${june['all_time']:,} -> ${now['all_time']:,}   {at_chg:+.1f}%")
print("  -> new revenue arrives while the base shrinks: churn, not growth")

print()
print("=== ARPU vs the published price ===")
arpu = now["mrr"] / now["subs"]
print(f"  ${now['mrr']:,} / {now['subs']} subscriptions = ${arpu:.2f} ARPU")
print("  published entry price: $49/month")
print("  -> ARPU above the entry price implies higher tiers (pSEO / mini apps)")
