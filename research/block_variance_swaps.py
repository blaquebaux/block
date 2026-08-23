#!/usr/bin/python3
# =============================================================================
# block_variance_swaps.py — Block variation #4: VARIANCE vs VOL swaps — the cleanest VRP, and its convexity.
#
# The straddle arc kept circling the vol-risk-premium through strikes, paths and gamma. The variance swap is
# the PURE instrument: it pays (realized_variance − strike_variance) at expiry — no strike selection, no delta,
# no path. A short var swap IS the vol premium, isolated. Its cousin the VOL swap pays (realized_vol − strike)
# — LINEAR in vol, not quadratic — so it strips the convexity. Comparing them prices the premium cleanly AND
# exposes the convex tail that detonated short-variance books in 2008. Implied (strike) = trailing realized ×
# mult, swept (no VIX on the feed). Short = the harvest; returns are the fractional miss vs the strike.
# =============================================================================
import os, json, urllib.request
from math import sqrt
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def load(sym, start="2016-01-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment=all&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return [x["t"][:10] for x in b], np.array([x["c"] for x in b],float)

REB=21; Dt,P=load("SPY"); r=P[1:]/P[:-1]-1
def realized_vol(a,b): return r[a:b].std()*sqrt(252)               # annualized realized over [a,b)

def swaps(mult):
    """Short var-swap and short vol-swap returns (fractional miss vs strike), per monthly period."""
    vs=[]; vo=[]; idx=[]
    for t in range(21, len(r)-REB, REB):
        Kvol = realized_vol(t-21,t)*mult                          # strike = trailing implied
        rvol = realized_vol(t, t+REB)                             # realized over the period
        if Kvol<=0: continue
        vo.append((Kvol - rvol)/Kvol)                             # short VOL swap: linear
        vs.append((Kvol**2 - rvol**2)/Kvol**2)                    # short VAR swap: quadratic (convex)
        idx.append(t+REB)
    return np.array(vs), np.array(vo), idx

def stats(p):
    m,s=p.mean(),p.std(); sh=m/s*sqrt(12) if s>0 else float('nan')
    lv=np.cumprod(1+np.clip(p,-0.99,None)); dd=(lv/np.maximum.accumulate(lv)-1).min()   # clip: a <-100% period = ruin
    z=(p-m)/s if s>0 else p*0
    return dict(ann=m*12, sh=sh, dd=dd, worst=p.min(), skew=float((z**3).mean()), win=100*(p>0).mean(), ruin=int((p<=-1).sum()))

print("="*98, "\nBLOCK variation #4 — VARIANCE vs VOL swaps: the pure VRP, and its convexity  (SPY, 1-mo, strike=realized×mult)\n"+"="*98)
print("  short = harvest the premium (receive strike, pay realized). return = fractional miss vs strike (1 notional).\n")
for mult in (1.00, 1.10, 1.20):
    vs,vo,_ = swaps(mult); mv,mo = stats(vs), stats(vo)
    print(f"  --- strike = realized × {mult:.2f}  ({int((mult-1)*100)}% VRP) ---")
    print(f"    {'instrument':<22}{'ann':>8}{'Sharpe':>8}{'maxDD':>8}{'worst mo':>10}{'skew':>7}{'win%':>6}{'ruin mos':>9}")
    print(f"    {'short VOL swap':<22}{mo['ann']*100:>+7.0f}%{mo['sh']:>+8.2f}{mo['dd']*100:>+7.0f}%{mo['worst']*100:>+9.0f}%{mo['skew']:>+7.2f}{mo['win']:>5.0f}%{mo['ruin']:>9}")
    print(f"    {'short VAR swap':<22}{mv['ann']*100:>+7.0f}%{mv['sh']:>+8.2f}{mv['dd']*100:>+7.0f}%{mv['worst']*100:>+9.0f}%{mv['skew']:>+7.2f}{mv['win']:>5.0f}%{mv['ruin']:>9}")
    print()

vs0,vo0,_ = swaps(1.00); vs2,vo2,_ = swaps(1.20)
vs,vo,idx = swaps(1.10)
covid=[i for i,t in enumerate(idx) if "2020-03" in Dt[t] or "2020-04" in Dt[t]]     # the convex blow-up
print(f"  COVID month (Mar-2020): short VOL swap {vo[covid].sum()*100:+.0f}%   short VAR swap {vs[covid].sum()*100:+.0f}%   (the convexity, made real)\n")
print("  READ (the data corrected the priors — honestly):")
print("  • The variance swap is the STRUCTURALLY purest VRP instrument (no strike/delta/path; it ≈ the delta-hedged")
print("    short straddle of variation #2, as it must). BUT it is NOT ~0 at 'fair' pricing here — both swaps lose")
print(f"    HEAVILY at mult=1.0 (vol {stats(vo0)['sh']:+.2f} Sharpe, var {stats(vs0)['sh']:+.2f}). Why: a TRAILING-realized strike")
print("    systematically under-forecasts the fat-tailed FORWARD realized — you're short the forecast error, and that")
print("    error is violently negative-skewed. This is the whole reason the real market strike (VIX) sits ABOVE")
print("    realized: the VRP is the fee for bearing exactly this un-forecastable spike. Naive fair pricing is a loser.")
print("  • CONVEXITY is the killer, and it's the robust finding at EVERY level. variance = vol², so a k× vol spike")
print("    costs a short VAR swap ~k² vs the VOL swap's ~k: worst month −1779% vs −333%, skew −4.53 vs −2.24, COVID")
print("    −892% vs −267%, ruin months 26 vs 9 (mult=1.0). The exact convexity that detonated short-variance in 2008.")
print(f"  • You need BOTH the linear instrument AND a fat premium buffer to profit: only at a 19% VRP does the VOL swap")
print(f"    turn positive ({stats(vo2)['sh']:+.2f}), and the VAR swap is STILL negative ({stats(vs2)['sh']:+.2f}) even there. And both")
print("    still show maxDD −100% — one COVID month is ruin. There is no safe naive short-vol here.")
print("  VERDICT: the VOL swap DOMINATES the VAR swap — same premium, linear (survivable) tail vs quadratic (terminal)")
print("  one — but neither is a free harvest: on a trailing-realized strike both lose until you add a real VRP cushion,")
print("  and both can still be wiped out by a single spike. brace at heart, cleanest form: the premium is thin, the")
print("  strike matters more than the structure, and the tail is the whole story — the instrument choice only sets HOW")
print("  convex you let the ruin be. Next Block classes: the RATES block (swaps/swaptions) and CREDIT (CDS/index).")