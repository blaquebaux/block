#!/usr/bin/python3
# =============================================================================
# block_funding_premium.py — Block FUNDING block #1: the front-end money-market premium — pennies, then a gap.
#
# Funding is the last catalog category: the money-market / short-end world (repo, SOFR, bills, the basis). Its
# premium is what you earn for lending SHORT-TERM to non-government borrowers — pure funding/liquidity risk, with
# NO duration and (almost) no default risk in calm. We isolate it cleanly with FLOATING-rate pairs, which strip
# duration entirely (both legs reset to the front rate):
#   funding spread = FLOT (floating IG corp) − USFR (floating Treasury)     [also FLRN − TFLO as a check]
#   bill carry     = MINT / NEAR / ICSH (ultra-short corp) − BIL (T-bills)
# The classic profile: a thin, STEADY positive carry (so calm-Sharpe looks high on tiny vol) that GAPS in a
# funding freeze (March-2020). The honest test: is the high Sharpe real, or is it short-liquidity — pennies in
# front of a steamroller at the money-market level (negative skew, a sharp crisis-correlated tail)?
# =============================================================================
import os, json, urllib.request
from math import sqrt
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def load(sym, start="2015-06-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment=all&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return {x["t"][:10]: x["c"] for x in b}

syms=["FLOT","USFR","FLRN","TFLO","MINT","NEAR","ICSH","BIL","SPY"]
TR={s:load(s) for s in syms}
dates=sorted(set.intersection(*[set(TR[s]) for s in syms]))
P={s:np.array([TR[s][d] for d in dates],float) for s in syms}
R={s:P[s][1:]/P[s][:-1]-1 for s in syms}; DT=dates[1:]
spx=R["SPY"]-R["BIL"]

def stats(e):
    m,s=e.mean()*252,e.std()*sqrt(252); sh=m/s if s>0 else float('nan')
    lv=np.cumprod(1+e); dd=(lv/np.maximum.accumulate(lv)-1).min()
    z=(e-e.mean())/e.std() if e.std()>0 else e*0
    return dict(ann=m,vol=s,sh=sh,dd=dd,worst=e.min(),skew=float((z**3).mean()))
def yr(e,y): return np.prod([1+e[i] for i,d in enumerate(DT) if d[:4]==str(y)])-1
def beta_alpha(e):
    b=np.cov(e,spx)[0,1]/np.var(spx); return b,(e.mean()-b*spx.mean())*252
def crisis(e):
    k=int(len(spx)*0.05); w=np.argsort(spx)[:k]; return np.corrcoef(e[w],spx[w])[0,1], e[w].mean()*100
def march2020(e): return sum(e[i] for i,d in enumerate(DT) if "2020-03" in d)*100

print("="*106, "\nBLOCK FUNDING #1 — the front-end money-market premium: pennies, then a gap  (floating-rate, duration-stripped)\n"+"="*106)
print(f"  {'spread':<24}{'ann':>8}{'vol':>7}{'Sharpe':>8}{'maxDD':>8}{'worst d':>9}{'skew':>7}{'Mar-20':>8}{'β(SPY)':>8}{'crisisρ':>9}")
pairs=[("FLOT−USFR (float IG−Tsy)",R["FLOT"]-R["USFR"]),("FLRN−TFLO (float IG−Tsy)",R["FLRN"]-R["TFLO"]),
       ("MINT−BIL (ultrashort−bill)",R["MINT"]-R["BIL"]),("NEAR−BIL",R["NEAR"]-R["BIL"]),("ICSH−BIL",R["ICSH"]-R["BIL"])]
for nm,e in pairs:
    m=stats(e); b,_=beta_alpha(e); cc,_=crisis(e)
    print(f"  {nm:<24}{m['ann']*100:>+7.2f}%{m['vol']*100:>6.1f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.1f}%{m['worst']*100:>+8.2f}%{m['skew']:>+7.2f}{march2020(e):>+7.1f}%{b:>+8.2f}{cc:>+9.2f}")

fl=R["FLOT"]-R["USFR"]; m=stats(fl)
# what the calm-only Sharpe looks like if you EXCLUDE the March-2020 gap — the illusion, quantified
mask=np.array([("2020-03" not in d) for d in DT]); mc=stats(fl[mask])
print(f"\n  THE ILLUSION, QUANTIFIED (FLOT−USFR): full-sample Sharpe {m['sh']:+.2f}  |  excluding Mar-2020 alone {mc['sh']:+.2f}")
print(f"    one month (Mar-2020) carries the entire tail — worst day {m['worst']*100:.2f}%, skew {m['skew']:+.2f}. Pennies all year, one steamroller.")
print("\n  READ (honest scorecard):")
print("  • A REAL, INDEPENDENT, STEADY CARRY. Every pair earns a small positive premium (+0.5..0.75%/yr) for bearing")
print("    front-end funding/liquidity risk, at near-ZERO equity beta (+0.01..+0.08) — genuinely uncorrelated in LEVEL.")
print("    You are truly paid for warehousing money-market risk.")
print("  • BUT IT IS PURE SHORT-LIQUIDITY — pennies in front of a steamroller. The skew is the most extreme in the")
print("    entire seven-block study (-9.3, -11.9, even -23.6): the worst DAY (-6.9% on FLOT−USFR) erases ~a DECADE of")
print("    the +0.6%/yr carry, and it gaps exactly in a freeze (Mar-2020, crisis-corr +0.62). Independent in calm,")
print("    crisis-correlated in the tail.")
print("  • THE SHARPE IS AN ILLUSION. MINT−BIL shows Sharpe +0.63 — but that's tiny vol masking a -6.2 skew; and")
print("    FLOT−USFR's full-sample +0.15 becomes +0.61 once you EXCLUDE March-2020 alone. One month IS the risk.")
print("    Low-vol carry with a rare gap is the canonical case of a headline metric hiding the whole tail.")
print("  VERDICT: the funding premium is real and independent, but it is fairly-priced LIQUIDITY-CRISIS INSURANCE-")
print("  SELLING — thin steady pennies for a rare, violent, crisis-correlated gap. It belongs in a book as SIZED")
print("  insurance-selling, never dressed up as 'high-Sharpe carry.' The seductive calm-Sharpe is exactly the trap")
print("  the whole premium arc keeps exposing — the metric flatters, the tail decides.")
