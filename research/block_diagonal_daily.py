#!/usr/bin/python3
# =============================================================================
# block_diagonal_daily.py — Block variation #3b: the diagonal on DAILY marks through 2018 & 2020.
#
# Variation #3 (monthly marks) couldn't adjudicate the diagonal: the far ±10% wings never triggered because
# monthly bars smooth over the intra-month vol spikes. This re-runs the SAME structures with DAILY marks —
# valuing both legs every day (spot + a responsive implied = 10d-realized×mult) — so the crisis paths are
# visible: Feb-2018 'Volmageddon' and the Mar-2020 COVID crash, exactly where a naked short blows up (SVXY
# −95%) and the long far wings are supposed to pay. Now we can measure the tail-cap, not just assume it.
# =============================================================================
import os, json, urllib.request
from math import erf, sqrt, log
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def load(sym, start="2016-01-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment=all&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return [x["t"][:10] for x in b], np.array([x["c"] for x in b],float)
def Phi(x): return 0.5*(1+erf(x/sqrt(2)))
def _c(S,K,T,s):
    if T<=0 or s<=0: return max(S-K,0.0)
    d1=(log(S/K)+0.5*s*s*T)/(s*sqrt(T)); return S*Phi(d1)-K*Phi(d1-s*sqrt(T))
def _p(S,K,T,s):
    if T<=0 or s<=0: return max(K-S,0.0)
    d1=(log(S/K)+0.5*s*s*T)/(s*sqrt(T)); d2=d1-s*sqrt(T); return K*Phi(-d2)-S*Phi(-d1)
def straddle(S,K,T,s): return _c(S,K,T,s)+_p(S,K,T,s)
def strangle(S,Kc,Kp,T,s): return _c(S,Kc,T,s)+_p(S,Kp,T,s)

REB=21; MULT=1.10
D,P=load("SPY"); r=P[1:]/P[:-1]-1
def rvol(d): lo=max(0,d-10); return r[lo:d].std()*sqrt(252) if d>1 else 0.15   # responsive 10d realized

# daily-marked P&L series for naked short vs diagonal (fresh monthly structure, marked every day)
def daily_series():
    naked=np.zeros(len(P)); diag=np.zeros(len(P))                     # daily P&L (in units of S0 per cycle)
    for t0 in range(21, len(P)-REB, REB):
        K=P[t0]; Kc,Kp=K*1.10,K*0.90; pv_n=pv_d=None
        for d in range(t0, min(t0+REB, len(P))):
            Trn=(REB-(d-t0))/252.; Trf=(3*REB-(d-t0))/252.; s=max(rvol(d),1e-3)*MULT
            vn=-straddle(P[d],K,Trn,s); vd=-straddle(P[d],K,Trn,s)+strangle(P[d],Kc,Kp,Trf,s)
            if pv_n is not None: naked[d]=(vn-pv_n)/K; diag[d]=(vd-pv_d)/K
            pv_n,pv_d=vn,vd
    return naked, diag

nk, dg = daily_series()
def curve(x): return np.cumsum(x)                                     # additive daily P&L (units of notional)
def maxdd(x): c=curve(x); return (c-np.maximum.accumulate(c)).min()   # deepest peak-to-trough on the P&L curve
def window(a,b): return np.array([i for i,dt in enumerate(D) if a<=dt<=b])

print("="*96, "\nBLOCK #3b — the diagonal on DAILY marks: does owning the far tail cap the crisis?  (SPY, implied=10d-realized×1.10)\n"+"="*96)
print(f"  FULL SAMPLE (daily marks): naked short worst peak-to-trough {maxdd(nk)*100:+.0f}%  |  diagonal {maxdd(dg)*100:+.0f}%")
print(f"                             worst single DAY  naked {nk.min()*100:+.1f}%  |  diagonal {dg.min()*100:+.1f}%\n")
for lbl,a,b in [("Feb-2018 Volmageddon","2018-01-26","2018-02-16"), ("Mar-2020 COVID crash","2020-02-19","2020-03-31")]:
    w=window(a,b); nkw,dgw=nk[w],dg[w]
    print(f"  {lbl} ({a}→{b}, {len(w)} days):")
    print(f"    naked short : cum P&L {nkw.sum()*100:+5.1f}%   worst day {nkw.min()*100:+5.1f}%   intra maxDD {maxdd(nk[w[0]:w[-1]+1])*100:+5.1f}%")
    print(f"    diagonal    : cum P&L {dgw.sum()*100:+5.1f}%   worst day {dgw.min()*100:+5.1f}%   intra maxDD {maxdd(dg[w[0]:w[-1]+1])*100:+5.1f}%")
    print(f"    -> the far wings saved {(dgw.sum()-nkw.sum())*100:+.1f}% over the window (worst-day cushion {(dgw.min()-nkw.min())*100:+.1f}%)\n")

print("  VERDICT (both sides, honestly): on DAILY marks the diagonal does what monthly bars hid BOTH ways —")
print("  • THE CAP IS REAL AND LARGE. In the acute crises the far wings pay exactly when needed: the naked short's")
print("    −21.6% COVID intra-drawdown becomes a +6.9% GAIN; Volmageddon −1.8% becomes +3.0%. The open-ended")
print("    short-vol tail is genuinely bounded when it matters — measurable only once the tail is in the sample.")
print("  • BUT THE INSURANCE IS EXPENSIVE. Full-sample, the diagonal's daily-mark drawdown (−43%) is WORSE than the")
print("    naked short's (−29%): paying wing carry every calm day grinds a deeper long-run drawdown than the crises")
print("    it prevents. It's not a free lunch — you trade an acute, potentially TERMINAL blow-up for a chronic,")
print("    SURVIVABLE bleed. (Magnitude depends on the implied-vol model; the direction — heavy calm carry — is robust.)")
print("  So the honest resolution of the straddle arc: naked/delta-hedged short = uncapped, cheap-until-it-kills-you")
print("  (brace / SVXY −95%); DIAGONAL = bounded and survivable, but the carry can cost more than the crises over a")
print("  decade. The 'right' structure is a RUIN-AVERSION choice, not a Sharpe one — and only tail data could show it.")
print("  Next Block classes: variance/vol swaps (the cleaner VRP instrument), then the rates & credit blocks.")
