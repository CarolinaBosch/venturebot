#!/usr/bin/env python3
"""Check both wallets for inbound transactions carrying an SPL Memo.

This is the register's identity-free right-of-reply channel: anyone can send a
minimal SOL transfer with a memo attached, and it is readable here with no
account, no inbox, and no identity on either side. Run every wake.
"""
import urllib.request, json, sys

RPC = "https://api.mainnet-beta.solana.com"
WALLETS = {
    "vault": "FYBeopAhxbXdYzjzSitkyeNUwV79FMu9c1y3GgYWu5ug",
    "hot": "53Ns752uxr8AT5287MTEYuCpWTbzCKHEGhGbkXK87T9w",
}
# Transactions already known and accounted for (the original funding).
KNOWN = set()


def rpc(method, params):
    req = urllib.request.Request(
        RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req, timeout=30))


def main():
    found_any = False
    for label, addr in WALLETS.items():
        sigs = rpc("getSignaturesForAddress", [addr, {"limit": 100}])["result"]
        print(f"=== {label} ({addr[:8]}…) — {len(sigs)} transactions ===")
        for s in sigs:
            sig = s["signature"]
            memo = s.get("memo")
            marker = ""
            if memo:
                found_any = True
                marker = "  <-- MEMO"
            new = "" if sig in KNOWN else "  [not in KNOWN list]"
            print(f"  {sig[:24]}… slot {s['slot']} err={s['err']}{new}{marker}")
            if memo:
                print(f"      MEMO TEXT: {memo}")
        print()

    if not found_any:
        print("No memos found on any transaction. No subject has replied on-chain.")
        print("register_subject_responses stays 0.")
    else:
        print("MEMO(S) FOUND — a reply may have arrived.")
        print("Per the register's rules: publish it IN FULL, unedited, in the sender's own")
        print("words, above the verdict, free, whether or not it changes the outcome.")
        sys.exit(0)


if __name__ == "__main__":
    main()
