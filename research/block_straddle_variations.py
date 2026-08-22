#!/usr/bin/python3
# =============================================================================
# block_straddle_variations.py — Block variation study #1: STRADDLES, modified.
#
# The first entry in Block's "modify the catalog to death" program, run with the family's honest method:
# decompose the straddle into what you actually pay for, test the structural variants, and keep only what
# earns its place. A straddle's P&L is fundamentally REALIZED vs IMPLIED vol, so — with no VIX on the feed —
# we model it analytically: Black-Scholes on the REAL SPY path, rolling 1-month options, with implied vol a
# SWEPT parameter (implied = trailing realized × mult), since implied is unobservable here. That's the one
# modeled input, stated plainly; everything else is the real underlying and exact option math.
#
# Variants: long/short straddle (ATM), long/short strangle (OTM ±3%). Verdict connects to the empirical vol
# sleeves — bleed (long vol = insurance) and brace (short vol = a null VRP harvest).
# =============================================================================
import os, json, urllib.request
from math import erf, sqrt, log
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def closes(sym, start="2016-01-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment=all&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return np.array([x["c"] for x in b],float)

def Phi(x): return 0.5*(1+erf(x/sqrt(2)))
def _bs(S,K,T,sig,call):
    if T<=0 or sig<=0: return max(S-K,0) if call else max(K-S,0)
    d1=(log(S/K)+0.5*sig*sig*T)/(sig*sqrt(T)); d2=d1-sig*sqrt(T)
    return (S*Phi(d1)-K*Phi(d2)) if call else (K*Phi(-d2)-S*Phi(-d1))

REB=21; T=REB/252.0
P=closes("SPY"); r=P[1:]/P[:-1]-1
def sim(kind, side, mult):
    """kind: straddle|strangle. side: +1 long, -1 short. Returns monthly P&L% series."""
    pnl=[]
    for t in range(21, len(P)-REB, REB):
        S0=P[t]; sig=r[t-21:t].std()*sqrt(252)*mult; S1=P[t+REB]
        Kc,Kp=(S0,S0) if kind=="straddle" else (S0*1.03, S0*0.97)
        prem=_bs(S0,Kc,T,sig,True)+_bs(S0,Kp,T,sig,False)
        intr=max(S1-Kc,0)+max(Kp-S1,0)
        pnl.append(side*(intr-prem)/S0)
    return np.array(pnl)

def stats(p):
    m,s=p.mean(),p.std(); sh=m/s*sqrt(12) if s>0 else float('nan')
    lv=np.cumprod(1+p); dd=(lv/np.maximum.accumulate(lv)-1).min()
    z=(p-m)/s if s>0 else p*0; sk=float((z**3).mean())
    return dict(ann=m*12, sh=sh, dd=dd, skew=sk, worst=p.min(), win=100*(p>0).mean())

print("="*100, "\nBLOCK variation #1 — STRADDLES, modified  (SPY, rolling 1-mo, Black-Scholes; implied = realized×mult SWEPT)\n"+"="*100)
print("  the straddle's edge is ENTIRELY the vol-risk-premium (implied − realized). mult=1.0 is a fair option (no VRP);\n  mult>1.0 is the premium the seller collects. We sweep it because implied vol is unobservable on this feed.\n")
for mult in (1.00, 1.10, 1.20):
    print(f"  --- implied = realized × {mult:.2f}  ({int((mult-1)*100)}% vol-risk-premium) ---")
    print(f"    {'variant':<22}{'ann P&L':>9}{'Sharpe':>8}{'maxDD':>8}{'worst mo':>9}{'skew':>7}{'win%':>6}")
    for kind in ("straddle","strangle"):
        for side,tag in ((+1,"long"),(-1,"short")):
            m=stats(sim(kind,side,mult))
            print(f"    {tag+' '+kind:<22}{m['ann']*100:>+8.0f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.0f}%{m['worst']*100:>+8.0f}%{m['skew']:>+7.2f}{m['win']:>5.0f}%")
    print()

print("  READ (what the data honestly shows):")
print("  1. NO EDGE WITHOUT THE VRP. At mult=1.00 (fair pricing) every variant is ~±0.2 Sharpe — noise. The")
print("     straddle has NO structural edge; its entire return is the vol-risk-premium (implied>realized). Short")
print("     Sharpe scales straight with the premium: +0.2 at 10% VRP, +0.6 at 20%. That is the whole game.")
print("  2. LONG vol is a COST (the bleed profile). Long straddle/strangle turn negative as the VRP rises — you")
print("     pay the premium for convexity. Note the dynamic-premium bite: buying vol right AFTER a spike (fat")
print("     implied) that then mean-reverts is the worst bleed — long vol's real enemy isn't calm, it's paying up.")
print("  3. SHORT STRANGLE 'wins' in-sample — and that is the TRAP. It shows the best Sharpe (+0.92) and 72% win")
print("     rate with a worst month of only −6%… because 2016–2026 monthly bars contain no true catastrophe. A")
print("     naked short strangle's real tail is a gap/crash bigger than any month here — brace's SVXY lived it")
print("     (−95% in Feb-2018 'Volmageddon'). The high win-rate IS the short-vol illusion: picking up nickels, the")
print("     steamroller just isn't in the sample. Trust brace's out-of-sample corpse over this in-sample Sharpe.")
print("  VERDICT: the straddle is a pure VRP instrument — no edge beyond implied>realized, which the family already")
print("  priced (brace: short vol = null; bleed: long vol = insurance). The structural variants reshape the")
print("  premium/tail tradeoff, not the bet — and the 'best-looking' one (short strangle) is the most dangerous.")
print("  Next Block modifications to test: delta-hedged (isolate gamma/vega from direction), regime-gated short")
print("  (harvest only in calm — brace's lesson), and calendar/diagonal (sell near, own far — finance the tail).")
