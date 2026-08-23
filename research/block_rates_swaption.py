#!/usr/bin/python3
# =============================================================================
# block_rates_swaption.py — Block RATES catalog variation #5: SWAPTIONS — the rate-vol premium and its tail.
#
# Continuing the "modify to death" program into the rates block of the 120-catalog (Swaption / European /
# Bermudan / Straddle Swaption). A swaption is an option on the forward swap rate; the ETF-tradeable analog is
# an option on DURATION — a PAYER swaption (gains when rates RISE) ≈ a PUT on TLT; a RECEIVER swaption ≈ a CALL
# on TLT. So we model payer/receiver/straddle swaptions with Black-Scholes on the real TLT path (implied vol
# swept, since MOVE isn't on the feed), exactly as the equity straddle arc did on SPY. The honest questions:
#   (1) Is there a RATE vol-risk-premium (does selling rate vol pay, like equity)?
#   (2) Where is the TAIL — the equity straddle's tail is the downside crash (2020); rates should MIRROR it,
#       the tail on the PAYER side (rates spiking UP, 2022 — the worst bond year on record, MOVE at records).
#   (3) Is the extra optionality (Bermudan early exercise) worth its fee, or fee-in-a-suit?  [discussed]
# Caveat: a TLT option ≠ a true swaption (duration/convexity, no annuity), but it is the honest ETF analog.
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

REB=21; D,P=load("TLT"); r=P[1:]/P[:-1]-1
def rv(t): return r[t-21:t].std()*sqrt(252)
def yr_of(i): return D[i][:4]

def leg(kind, mult, short=False):
    out=[]; idx=[]
    for t in range(21, len(P)-REB, REB):
        S0=P[t]; S1=P[t+REB]; sig=rv(t)*mult
        payer = _p(S0,S0,REB/252.,sig) - max(S0-S1,0.0)     # payer≈put on TLT: premium − intrinsic(rates up→TLT down)
        recv  = _c(S0,S0,REB/252.,sig) - max(S1-S0,0.0)     # receiver≈call on TLT
        pnl = {"payer":payer,"receiver":recv,"straddle":payer+recv}[kind]
        if short: pnl = pnl              # already premium−intrinsic = the SHORT (seller) P&L
        else:     pnl = -pnl             # long = pay premium, receive intrinsic
        out.append(pnl/S0); idx.append(t+REB)
    return np.array(out), idx

def stats(p):
    m,s=p.mean(),p.std(); sh=m/s*sqrt(12) if s>0 else float('nan')
    lv=np.cumprod(1+p); dd=(lv/np.maximum.accumulate(lv)-1).min()
    z=(p-m)/s if s>0 else p*0
    return dict(ann=m*12, sh=sh, dd=dd, worst=p.min(), skew=float((z**3).mean()), win=100*(p>0).mean())
def yr(p,idx,y): return np.prod([1+p[i] for i,t in enumerate(idx) if yr_of(t)==str(y)])-1

print("="*104, "\nBLOCK RATES #5 — SWAPTIONS: the rate-vol premium and its tail  (payer≈put/receiver≈call on TLT; implied=realized×mult)\n"+"="*104)
for mult in (1.00, 1.10, 1.20):
    print(f"  --- implied = realized × {mult:.2f}  ({int((mult-1)*100)}% rate-vol premium) ---")
    print(f"    {'position':<26}{'ann':>8}{'Sharpe':>8}{'maxDD':>8}{'worst mo':>9}{'skew':>7}{'win%':>6}{'2020':>8}{'2022':>8}")
    for kind in ("payer","receiver","straddle"):
        p,idx=leg(kind,mult,short=True); m=stats(p)
        print(f"    short {kind:<20}{m['ann']*100:>+7.0f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.0f}%{m['worst']*100:>+8.0f}%{m['skew']:>+7.2f}{m['win']:>5.0f}%{yr(p,idx,2020)*100:>+7.0f}%{yr(p,idx,2022)*100:>+7.0f}%")
    print()

# the payer/receiver asymmetry — which side is the tail?
pp,idx=leg("payer",1.10,short=True); rr,_=leg("receiver",1.10,short=True)
print(f"  THE TAIL, by side (short, 10% premium): short PAYER worst mo {stats(pp)['worst']*100:+.0f}% (skew {stats(pp)['skew']:+.2f}, 2022 {yr(pp,idx,2022)*100:+.0f}%)")
print(f"                                           short RECEIVER worst mo {stats(rr)['worst']*100:+.0f}% (skew {stats(rr)['skew']:+.2f}, 2022 {yr(rr,idx,2022)*100:+.0f}%)")
print("\n  READ (the data corrected the prior — honestly):")
print("  • A RATE VOL-RISK-PREMIUM EXISTS, like equity. Selling the rate straddle pays and scales with the premium:")
print("    short-straddle Sharpe +0.17 (fair) → +0.53 (10% VRP) → +0.89 (19%), win-rate ~65-70%. Rate vol, like")
print("    equity vol, is sold rich on average — the desk's carry, in calm.")
print("  • BUT RATES HAVE TWO TAILS, not equity's one — and the VIOLENT one is the side I did NOT expect. My prior")
print("    was that the tail is the PAYER/rates-up side (2022). The data says the worst SINGLE-MONTH tail is the")
print("    RECEIVER/rates-DOWN side: short receiver worst month -16%, skew -2.66, hit in the Mar-2020 flight-to-")
print("    quality BOND SPIKE (rates collapsed, TLT surged). The PAYER tail (rates rising) is real but a SLOW")
print("    GRIND — cumulative 2022 -17% yet worst month only -8%, skew -1.64. Selling receivers = writing crash")
print("    insurance on a bond spike; selling payers = bleeding through a rate-hike cycle. Corrected to the data.")
print("  • A TWIST vs the equity straddle arc: equity short-vol's Sharpe was UNtrustworthy because its -95% tail")
print("    (SVXY) sat OUTSIDE the monthly 2016-26 sample. Rates are different — the rate-vol sample CONTAINS its")
print("    worst episode (2022, the worst bond year on record), so the short-straddle Sharpe is somewhat MORE")
print("    trustworthy here. Still: negative skew on BOTH sides means it remains insurance-writing, not free carry.")
print("  • BERMUDAN / EXTRA OPTIONALITY (the catalog's European→Bermudan step): for a vol SELLER the early-exercise")
print("    right adds nothing you can harvest — it's fee-in-a-suit unless the buyer holds a specific path-dependent")
print("    early-call view. Optionality you can't express is the desk's margin, not the buyer's edge.")
print("  VERDICT: the rate-vol premium is REAL and — unlike equity VRP — tested against its own worst year in-sample,")
print("  but it is DOUBLE-TAILED (a violent bond-spike on the receiver side, a grinding rate-rise on the payer side)")
print("  and negative-skew both ways. Sell rate vol as insurance-writing sized for BOTH tails, never as clean carry.")
print("  Next catalog section: CDS index TRANCHES — the credit correlation trade, the instrument that broke in 2008.")
