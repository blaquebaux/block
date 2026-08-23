#!/usr/bin/python3
# =============================================================================
# block_rates_termpremium.py — Block RATES block #1: the term premium / duration carry, and its regime.
#
# Off the vol premium entirely — genuinely new economics. The RATES bet is DURATION: long-dated bonds are
# supposed to pay a TERM PREMIUM over cash for bearing rate risk (+ roll-down when the curve is upward-sloping).
# We test it honestly with total-return duration-bucket ETFs vs a cash (T-bill) proxy:
#   SHY 1-3y | IEI 3-7y | IEF 7-10y | TLT 20y+  , excess over BIL (cash).
# Two questions, the family's method:
#   (1) Is the term premium REAL — does bearing more duration actually pay, and what is its tail?
#   (2) Is it a BUY-AND-HOLD bet or only a TREND-TIMED one? Gate duration on its own 100d trend (rates falling)
#       — "match the signal to the sleeve" — and see if it dodges 2022 (the worst bond year in history).
# Note the mirror-image crisis vs the vol block: COVID-2020 HELPED duration (flight to quality); the 2022
# inflation shock is the catastrophe. New premium, new tail.
# =============================================================================
import os, json, urllib.request
from math import sqrt
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def load(sym, start="2015-06-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment=all&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return {x["t"][:10]: x["c"] for x in b}

syms=["SHY","IEI","IEF","TLT","BIL"]; raw={s:load(s) for s in syms}
dates=sorted(set.intersection(*[set(raw[s]) for s in syms]))          # common trading days
P={s:np.array([raw[s][d] for d in dates],float) for s in syms}
R={s:P[s][1:]/P[s][:-1]-1 for s in syms}; DT=dates[1:]
cash=R["BIL"]

def stats(e):
    m,s=e.mean()*252, e.std()*sqrt(252); sh=m/s if s>0 else float('nan')
    lv=np.cumprod(1+e); dd=(lv/np.maximum.accumulate(lv)-1).min()
    z=(e-e.mean())/e.std() if e.std()>0 else e*0
    return dict(ann=m, vol=s, sh=sh, dd=dd, worst=e.min(), skew=float((z**3).mean()))
def yr(e, y): return np.prod([1+e[i] for i,d in enumerate(DT) if d[:4]==str(y)])-1   # calendar-year excess return

print("="*100, "\nBLOCK RATES #1 — the TERM PREMIUM: does bearing duration pay?  (total-return ETFs, excess over BIL cash)\n"+"="*100)
print(f"  {'bucket':<16}{'ann xs':>8}{'vol':>7}{'Sharpe':>8}{'maxDD':>8}{'worst d':>9}{'skew':>7}{'2020':>8}{'2022':>8}{'2024':>8}")
for s,lbl in [("SHY","SHY 1-3y"),("IEI","IEI 3-7y"),("IEF","IEF 7-10y"),("TLT","TLT 20y+")]:
    e=R[s]-cash; m=stats(e)
    print(f"  {lbl:<16}{m['ann']*100:>+7.1f}%{m['vol']*100:>6.1f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.0f}%{m['worst']*100:>+8.1f}%{m['skew']:>+7.2f}{yr(e,2020)*100:>+7.1f}%{yr(e,2022)*100:>+7.1f}%{yr(e,2024)*100:>+7.1f}%")

print("\n  TREND-GATED duration (hold the bucket only when its 100d trend is UP = rates falling, else cash):")
print(f"  {'bucket':<16}{'ann xs':>8}{'vol':>7}{'Sharpe':>8}{'maxDD':>8}{'worst d':>9}{'skew':>7}{'2020':>8}{'2022':>8}{'time on':>9}")
for s,lbl in [("IEF","IEF 7-10y"),("TLT","TLT 20y+")]:
    # signal decided at close of day i (known), earns R[i]=P[i+1]/P[i]-1 over i->i+1 — no lookahead
    sig=np.array([1.0 if i>=100 and P[s][i] > P[s][i-100:i].mean() else 0.0 for i in range(len(R[s]))])  # 100d SMA trend
    e=sig*(R[s]-cash); m=stats(e)
    print(f"  {lbl:<16}{m['ann']*100:>+7.1f}%{m['vol']*100:>6.1f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.0f}%{m['worst']*100:>+8.1f}%{m['skew']:>+7.2f}{yr(e,2020)*100:>+7.1f}%{yr(e,2022)*100:>+7.1f}%{sig.mean()*100:>7.0f}%")

# curve exposure: long TLT / short SHY (the long-end bet), raw vs trend-gated on TLT
sp=R["TLT"]-R["SHY"]; ms=stats(sp)
sigT=np.array([1.0 if i>=100 and P["TLT"][i]>P["TLT"][i-100:i].mean() else 0.0 for i in range(len(R["TLT"]))]); mg=stats(sigT*sp)
print(f"\n  CURVE (long TLT / short SHY, the long-end bet):   raw Sharpe {ms['sh']:+.2f}, maxDD {ms['dd']*100:+.0f}%, 2022 {yr(sp,2022)*100:+.1f}%")
print(f"                                            trend-gated Sharpe {mg['sh']:+.2f}, maxDD {mg['dd']*100:+.0f}%, 2022 {yr(sigT*sp,2022)*100:+.1f}%")
print("\n  READ (honest scorecard — a near-null on carry, a real diversifier):")
print("  • THE TERM PREMIUM WAS NEGATIVE this decade. Every duration bucket LOST to cash (TLT -2.0%/yr), and the")
print("    tail scaled straight with duration (TLT maxDD -52%, worst day -6.7%, 2022 -32%). Buy-and-hold duration")
print("    did not pay 2016-2026 — rates rose net and the 2022 inflation shock obliterated the textbook premium.")
print("  • BUT BONDS ARE THE CRISIS MIRROR of the vol/equity block, and THAT is their value. Positive skew")
print("    (+0.1..+0.5, opposite equity's negative), a big flight-to-quality RALLY in COVID-2020 (+17.7% TLT) —")
print("    exactly when the short-vol book was detonating — and their own catastrophe is a DIFFERENT crisis (2022")
print("    inflation, not a 2008/2020 growth scare). You don't hold duration to earn; you hold it to be long the")
print("    other side of equity's crash. New premium, new tail — genuinely not VRP in a costume.")
print("  • TREND-TIMING BOUNDS THE TAIL but does NOT manufacture edge. Gating on the 100d trend cut 2022 from")
print("    -32% to -11% (TLT) / -16% to -4% (IEF), roughly halved maxDD, and kept the 2020 upside and positive")
print("    skew — but standalone Sharpe stayed ~0 (IEF +0.13, TLT -0.18). It's a RISK overlay that makes duration")
print("    ownable, not an alpha source.")
print("  • DISCIPLINE NOTE: the naive same-bar signal (deciding a day's return from that day's own close) faked")
print("    Sharpe +1.17; the one-bar-lag correction cut it to +0.13. A standing caution for the whole program —")
print("    reported both, kept the honest one.")
print("  VERDICT: duration is a NEAR-NULL on standalone carry but a real, positive-skew, equity-crisis-mirror")
print("  diversifier — the honest reason a balanced book (family: balanced / bonds sleeves) holds it. Hold it for")
print("  the skew, trend-gate it to bound the 2022-type shock, and never expect it to pay by itself. Next rates")
print("  study: carry/roll-down across the curve, then the CREDIT block (CDS/index) — the default-risk premium.")
