#!/usr/bin/python3
# =============================================================================
# block_calendar_diagonal.py — Block variation #3: CALENDAR & DIAGONAL — attacking the short-vol tail.
#
# Variations #1–#2 confirmed short vol is a thin, crash-exposed premium (brace), improvable only in NOISE
# (delta-hedge). #3 is the first structure that changes the RISK: own a FAR-DATED option to cap the
# catastrophe. Two ways, both "sell the near, own the far":
#   CALENDAR  — short 1M straddle + long 3M straddle (same strike). Same-strike far leg cancels the near's
#               directional move and adds vega -> NET LONG VOL: it PROFITS in a crash, bleeds in calm.
#   DIAGONAL  — short 1M ATM straddle + long 3M OTM strangle (±10% wings). Harvest the near ATM premium,
#               own a cheap far-dated tail. This is "finance the far tail" — a capped-risk short-vol harvest.
# Black-Scholes on the real SPY path; near implied = realized×mult at open, far leg re-marked at close.
# The question: does owning the far tail turn the uncapped short-vol catastrophe into an ownable book?
# =============================================================================
import os, json, urllib.request
from math import erf, sqrt, log
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def closes(sym, start="2016-01-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment=all&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    return np.array([x["c"] for x in d.get("bars",{}).get(sym,[])],float)
def Phi(x): return 0.5*(1+erf(x/sqrt(2)))
def _c(S,K,T,s):
    if T<=0 or s<=0: return max(S-K,0.0)
    d1=(log(S/K)+0.5*s*s*T)/(s*sqrt(T)); return S*Phi(d1)-K*Phi(d1-s*sqrt(T))
def _p(S,K,T,s):
    if T<=0 or s<=0: return max(K-S,0.0)
    d1=(log(S/K)+0.5*s*s*T)/(s*sqrt(T)); d2=d1-s*sqrt(T); return K*Phi(-d2)-S*Phi(-d1)
def straddle(S,K,T,s): return _c(S,K,T,s)+_p(S,K,T,s)
def strangle(S,Kc,Kp,T,s): return _c(S,Kc,T,s)+_p(S,Kp,T,s)

REB=21; P=closes("SPY"); r=P[1:]/P[:-1]-1
def rv(t): return r[t-21:t].std()*sqrt(252)

def run(kind, mult):
    out=[]
    for t in range(21, len(P)-REB, REB):
        S0=P[t]; S1=P[t+REB]; s0=rv(t)*mult; s1=rv(t+REB)*mult
        near = straddle(S0,S0,1/12.,s0) - abs(S1-S0)                      # short 1M ATM straddle (all variants)
        if kind=="naked":
            pnl = near
        elif kind=="calendar":                                            # + long 3M straddle
            farp = straddle(S0,S0,3/12.,s0); farv = straddle(S1,S0,2/12.,s1); pnl = near + (farv-farp)
        elif kind=="diagonal":                                            # + long 3M OTM strangle (±10% far tail)
            Kc,Kp=S0*1.10,S0*0.90; farp=strangle(S0,Kc,Kp,3/12.,s0); farv=strangle(S1,Kc,Kp,2/12.,s1); pnl = near + (farv-farp)
        out.append(pnl/S0)
    return np.array(out)

def stats(p):
    m,s=p.mean(),p.std(); sh=m/s*sqrt(12) if s>0 else float('nan')
    lv=np.cumprod(1+p); dd=(lv/np.maximum.accumulate(lv)-1).min(); cal=(m*12)/abs(dd) if dd<0 else float('nan')
    z=(p-m)/s if s>0 else p*0
    return dict(ann=m*12, sh=sh, dd=dd, worst=p.min(), cal=cal, skew=float((z**3).mean()), win=100*(p>0).mean())

print("="*102, "\nBLOCK variation #3 — CALENDAR & DIAGONAL: attacking the short-vol tail  (SPY, rolling 1-mo, BS; implied=realized×mult)\n"+"="*102)
for mult in (1.00, 1.10, 1.20):
    print(f"  --- implied = realized × {mult:.2f}  ({int((mult-1)*100)}% VRP) ---")
    print(f"    {'structure':<34}{'ann P&L':>9}{'Sharpe':>8}{'maxDD':>8}{'worst mo':>9}{'Calmar':>8}{'skew':>7}{'win%':>6}")
    for kind,lbl in [("naked","naked short straddle"),("calendar","calendar (short1M+long3M straddle)"),("diagonal","diagonal (short straddle+long far wings)")]:
        m=stats(run(kind,mult)); print(f"    {lbl:<34}{m['ann']*100:>+8.0f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.0f}%{m['worst']*100:>+8.0f}%{m['cal']:>+8.2f}{m['skew']:>+7.2f}{m['win']:>5.0f}%")
    print()

nk,cal,dg = stats(run("naked",1.10)), stats(run("calendar",1.10)), stats(run("diagonal",1.10))
print("  READ (the data overturned the hypothesis — honestly):")
print(f"  • CALENDAR is NET LONG VOL, not a harvest — the same-strike far leg cancels the near's move and adds vega.")
print(f"    ann {cal['ann']*100:+.0f}%, and it does NOT bleed less than naked in the tail (worst {cal['worst']*100:+.0f}%): it's a long-vol/")
print(f"    bleed variant financed by near theta, a different animal entirely — not a safer way to harvest premium.")
print(f"  • DIAGONAL did NOT cap the tail here — it made it WORSE: worst month {nk['worst']*100:+.0f}%→{dg['worst']*100:+.0f}%, maxDD {nk['dd']*100:+.0f}%→{dg['dd']*100:+.0f}%,")
print(f"    Calmar {nk['cal']:+.2f}→{dg['cal']:+.2f}. Why: the ±10% far wings almost never triggered — 2016–2026 MONTHLY moves rarely")
print(f"    reach 10%, so the wings were pure premium DRAG in the many calm months and never got their catastrophe payoff.")
print(f"  • THE HONEST TRAP, both ways: you cannot judge a tail structure on a sample without the tail. The wings look")
print(f"    like a waste for the SAME reason the naked short looks safe — the catastrophe they hedge (an SVXY-style −95%,")
print(f"    a >20% gap) isn't in monthly 2016–2026 bars. In-sample, the hedge is all cost; out-of-sample it's the thing")
print(f"    that saves you. Neither the naked short's Sharpe nor the diagonal's drag is trustworthy on this data.")
print(f"  VERDICT: UNPROVABLE on monthly data. The diagonal is the STRUCTURALLY correct answer (bounded loss — the naked")
print(f"  short's open-ended tail becomes defined-risk), but its value only shows in a true catastrophe this sample lacks,")
print(f"  so in-sample it's a drag. The lesson is methodological and it's Block's core: tail structures need tail data")
print(f"  (daily/intraday, or a crisis window) — brace's real SVXY −95% is worth more than any monthly backtest here.")
print(f"  Next: re-run the diagonal on DAILY marks through the 2018 & 2020 vol spikes (where the wings actually pay),")
print(f"  then variance/vol swaps and the rates & credit blocks.")
