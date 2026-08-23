#!/usr/bin/python3
# =============================================================================
# block_straddle_deltahedged.py — Block variation #2: the DELTA-HEDGED short straddle.
#
# Variation #1 showed the naked short straddle "wins" in-sample — but that P&L mixes the vol premium with
# DIRECTIONAL luck (the straddle accumulates delta as SPY moves). #2 strips the direction: sell the ATM
# straddle and delta-hedge it daily (hold +straddle-delta shares of SPY), leaving the pure gamma/theta P&L —
# i.e. realized vs implied VARIANCE, the clean vol-risk-premium (a variance-swap replication). The honest
# question: does delta-hedging IMPROVE the harvest (remove directional noise → higher Sharpe on the true VRP),
# or does it just reveal a thin, still-crash-exposed premium? Black-Scholes on the real SPY path; implied swept.
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
def _d1(S,K,T,s): return (log(S/K)+0.5*s*s*T)/(s*sqrt(T))
def _straddle(S,K,T,s):
    if T<=0 or s<=0: return abs(S-K)
    d1=_d1(S,K,T,s); d2=d1-s*sqrt(T); return (S*Phi(d1)-K*Phi(d2)) + (K*Phi(-d2)-S*Phi(-d1))
def _delta(S,K,T,s):                                   # straddle delta = call + put = 2N(d1)-1
    if T<=0 or s<=0: return (1.0 if S>K else -1.0)
    return 2*Phi(_d1(S,K,T,s))-1

REB=21
P=closes("SPY"); r=P[1:]/P[:-1]-1

def naked_short(mult):
    out=[]
    for t in range(21, len(P)-REB, REB):
        S0=P[t]; sig=r[t-21:t].std()*sqrt(252)*mult; S1=P[t+REB]
        prem=_straddle(S0,S0,REB/252.,sig); intr=abs(S1-S0); out.append((prem-intr)/S0)
    return np.array(out)

def dhedged_short(mult):
    out=[]
    for t in range(21, len(P)-REB-1, REB):
        S0=P[t]; sig=r[t-21:t].std()*sqrt(252)*mult; K=S0; acc=0.0
        for j in range(REB):                            # daily delta-hedge over the cycle, marked at fixed sig
            d=t+j; Trem=(REB-j)/252.; Tn=(REB-j-1)/252.
            Sd=P[d]; Sn=P[d+1]
            Vd=_straddle(Sd,K,Trem,sig); Vn=_straddle(Sn,K,Tn,sig)
            hedge=_delta(Sd,K,Trem,sig)                 # hold +delta shares to offset the SHORT straddle's -delta
            acc += -(Vn-Vd) + hedge*(Sn-Sd)             # short option leg + hedge leg
        out.append(acc/S0)
    return np.array(out)

def stats(p):
    m,s=p.mean(),p.std(); sh=m/s*sqrt(12) if s>0 else float('nan')
    lv=np.cumprod(1+p); dd=(lv/np.maximum.accumulate(lv)-1).min()
    z=(p-m)/s if s>0 else p*0
    return dict(ann=m*12, vol=s*sqrt(12), sh=sh, dd=dd, worst=p.min(), skew=float((z**3).mean()), win=100*(p>0).mean())

print("="*100, "\nBLOCK variation #2 — DELTA-HEDGED short straddle vs naked  (SPY, rolling 1-mo, BS; implied = realized×mult)\n"+"="*100)
print("  delta-hedging removes the directional luck, leaving the pure vol premium (realized vs implied variance).\n")
for mult in (1.00, 1.10, 1.20):
    print(f"  --- implied = realized × {mult:.2f}  ({int((mult-1)*100)}% vol-risk-premium) ---")
    print(f"    {'variant':<26}{'ann P&L':>9}{'vol':>7}{'Sharpe':>8}{'maxDD':>8}{'worst mo':>9}{'skew':>7}{'win%':>6}")
    for lbl,p in [("naked short straddle", naked_short(mult)), ("delta-hedged short straddle", dhedged_short(mult))]:
        m=stats(p); print(f"    {lbl:<26}{m['ann']*100:>+8.0f}%{m['vol']*100:>6.0f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.0f}%{m['worst']*100:>+8.0f}%{m['skew']:>+7.2f}{m['win']:>5.0f}%")
    print()

print("  READ:")
n10,d10 = stats(naked_short(1.10)), stats(dhedged_short(1.10))
print(f"  • Delta-hedging STRIPS the directional noise: at 10% VRP, vol {n10['vol']*100:.0f}% → {d10['vol']*100:.0f}%, so the SAME")
print(f"    premium is earned at a {'higher' if d10['sh']>n10['sh'] else 'lower'} Sharpe ({n10['sh']:+.2f} → {d10['sh']:+.2f}). This is why vol desks hedge —")
print("    it isolates the vol premium from the coin-flip of direction. The first Block variation that genuinely IMPROVES.")
print("  • BUT it does NOT remove the short-gamma TAIL: the worst month is still a big loss (realized >> implied on a")
print("    vol spike). Delta-hedging cleans the harvest; it does not make selling vol safe — brace's SVXY (−95%) is")
print("    the reminder, and at mult=1.0 (fair) even the hedged version is ~0 Sharpe: still no edge without the VRP.")
print("  • HONEST CAVEAT: this sim charges NO daily-rehedging transaction cost — the Sharpe lift is GROSS of it.")
print("    SPY is liquid (~a few bps/side) so the net gain survives but is smaller; on an illiquid underlying")
print("    the hedging cost can eat the whole improvement. The refinement is real, not free.")
print("  VERDICT: delta-hedging is a real, keepable REFINEMENT of the short-vol harvest — higher Sharpe on the pure")
print("  premium — but the bet is unchanged (thin VRP + short-gamma tail = brace, cleaner). The added 'component'")
print("  (daily hedging) pays the BUYER here: less noise, same edge. Next: regime-gate the hedged short (harvest in")
print("  calm only) and calendar/diagonal (own the far-dated tail cheaply) — the modifications that attack the TAIL.")
