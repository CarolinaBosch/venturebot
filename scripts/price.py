import json, urllib.request, ssl

ctx = ssl.create_default_context()

def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "venturebot"})
    with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
        return json.loads(r.read().decode())

prices = {}
try:
    d = get("https://api.coinbase.com/v2/prices/SOL-USD/spot")
    prices["coinbase"] = float(d["data"]["amount"])
except Exception as e:
    print("coinbase failed:", e)
try:
    d = get("https://api.kraken.com/0/public/Ticker?pair=SOLUSD")
    k = list(d["result"].values())[0]
    prices["kraken"] = float(k["c"][0])
except Exception as e:
    print("kraken failed:", e)

for k, v in prices.items():
    print(f"{k}: {v}")
mean = sum(prices.values()) / len(prices)
print(f"\nmean SOL/USD: {mean:.2f}")
hot, ms = 0.5, 1.001
print(f"hot      {hot} SOL = ${hot*mean:.2f}")
print(f"multisig {ms} SOL = ${ms*mean:.2f}")
print(f"total    {hot+ms} SOL = ${(hot+ms)*mean:.2f}")
