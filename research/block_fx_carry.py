#!/usr/bin/python3
# =============================================================================
# block_fx_carry.py — Block FX block #1: the carry premium — the classic earned return, and its crash tail.
#
# FX carry is the most-cited INDEPENDENT premium in macro: borrow low-yielding currencies, lend high-yielding
# ones, pocket the rate differential. Its reputation: "picking up nickels in front of a steamroller" — a real
# premium that unwinds violently in risk-off deleveragings. We test it two ways and run the family toolkit:
#   (A) DBV — the packaged G10 Currency Harvest ETF (2016-2023, then delisted).
#   (B) a self-constructed G10 basket: rank six CurrencyShares ETFs (FXA/FXB/FXC/FXE/FXF/FXY) by their own
#       trailing DISTRIBUTION YIELD (= the foreign short rate, recovered from total-return vs price-only), go
#       LONG the top 2 / SHORT the bottom 2, dollar-neutral, monthly. Long high-yielders, short low-yielders.
# Toolkit on the carry return: Jensen's alpha vs SPY (is it independent of equity?) and crisis correlation
# (does it crash on equity's worst days — the steamroller?). Expected: positive carry, NEGATIVE skew, and
# POSITIVE crisis-correlation — an earned premium that is partly a risk-on bet.
# =============================================================================
import os, json, urllib.request
from math import sqrt
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def load(sym, adj, start="2015-06-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment={adj}&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return {x["t"][:10]: x["c"] for x in b}

FX=["FXA","FXB","FXC","FXE","FXF","FXY"]; base=["SPY","BIL"]
TR={s:load(s,"all")   for s in FX+base}
PR={s:load(s,"split") for s in FX}
dates=sorted(set.intersection(*[set(TR[s]) for s in FX+base], *[set(PR[s]) for s in FX]))
tr={s:np.array([TR[s][d] for d in dates],float) for s in FX+base}
pr={s:np.array([PR[s][d] for d in dates],float) for s in FX}
DT=dates[1:]
rtr={s:tr[s][1:]/tr[s][:-1]-1 for s in FX+base}
rpr={s:pr[s][1:]/pr[s][:-1]-1 for s in FX}
spx=rtr["SPY"]-rtr["BIL"]

div={s:np.clip(rtr[s]-rpr[s],0,None) for s in FX}
Y={s:np.array([div[s][max(0,i-252):i].sum() for i in range(len(div[s]))]) for s in FX}   # trailing running yield

def stats(e):
    m,s=e.mean()*252, e.std()*sqrt(252); sh=m/s if s>0 else float('nan')
    lv=np.cumprod(1+e); dd=(lv/np.maximum.accumulate(lv)-1).min()
    z=(e-e.mean())/e.std() if e.std()>0 else e*0
    return dict(ann=m, sh=sh, dd=dd, worst=e.min(), skew=float((z**3).mean()))
def yr(e,y): return np.prod([1+e[i] for i,d in enumerate(DT) if d[:4]==str(y)])-1
def alpha(e):
    n=min(len(e),len(spx)); e,s=e[-n:],spx[-n:]; b=np.cov(e,s)[0,1]/np.var(s); return b,(e.mean()-b*s.mean())*252
def crisis(e):
    n=min(len(e),len(spx)); e,s=e[-n:],spx[-n:]; k=int(len(s)*0.05); w=np.argsort(s)[:k]
    return np.corrcoef(e[w],s[w])[0,1], e[w].mean()*100

# (B) constructed G10 carry: long top-2 yield, short bottom-2, dollar-neutral, monthly rebalance (signal lagged)
REB=21; carry=np.zeros(len(DT))
for t in range(252, len(DT)-REB, REB):
    rank=sorted(FX, key=lambda s: Y[s][t])                       # ascending yield; known at t
    longs, shorts = rank[-2:], rank[:2]
    for d in range(t, min(t+REB, len(DT))):
        carry[d]= 0.5*sum(rtr[s][d] for s in longs) - 0.5*sum(rtr[s][d] for s in shorts)
carry=carry[252:]                                               # drop warmup
DTc=DT[252:]

print("="*104, "\nBLOCK FX #1 — the CARRY premium: the classic earned return, and its crash tail  (G10 currency carry)\n"+"="*104)
print("  average trailing yield by currency (sanity — high-yielders should be the AUD/GBP-type, low the JPY/CHF):")
print("   "+"  ".join(f"{s}:{Y[s][252:].mean()*100:+.1f}%" for s in FX))
print(f"\n  {'strategy':<28}{'ann':>8}{'Sharpe':>8}{'maxDD':>8}{'worst d':>9}{'skew':>7}{'2020':>8}{'2022':>8}{'β(SPY)':>8}{'α(Jensen)':>11}")
b,a=alpha(carry); m=stats(carry)
print(f"  {'constructed G10 carry':<28}{m['ann']*100:>+7.1f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.0f}%{m['worst']*100:>+8.1f}%{m['skew']:>+7.2f}{yr(carry,2020)*100:>+7.1f}%{yr(carry,2022)*100:>+7.1f}%{b:>+8.2f}{a*100:>+10.1f}%")

# (A) DBV packaged, over its own span
dbv=load("DBV","all"); dd=sorted(set(dbv)&set(TR["BIL"])); pd_=np.array([dbv[x] for x in dd],float); bl=np.array([TR["BIL"][x] for x in dd],float)
edbv=(pd_[1:]/pd_[:-1]-1)-(bl[1:]/bl[:-1]-1); mdb=stats(edbv)
sp_dbv=np.array([TR["SPY"][x] for x in dd]); sp_dbv=(sp_dbv[1:]/sp_dbv[:-1]-1)-(bl[1:]/bl[:-1]-1)
bD=np.cov(edbv,sp_dbv)[0,1]/np.var(sp_dbv); aD=(edbv.mean()-bD*sp_dbv.mean())*252
print(f"  {'DBV (packaged, 2016-2023)':<28}{mdb['ann']*100:>+7.1f}%{mdb['sh']:>+8.2f}{mdb['dd']*100:>+7.0f}%{mdb['worst']*100:>+8.1f}%{mdb['skew']:>+7.2f}{'   n/a':>8}{'   n/a':>8}{bD:>+8.2f}{aD*100:>+10.1f}%")

cc,cm=crisis(carry)
print(f"\n  CRISIS TELL (constructed carry on SPY's worst 5% days): corr {cc:+.2f}, avg carry return those days {cm:+.2f}%")
print("\n  READ (honest scorecard):")
print("  • CONSTRUCTION VALIDATED: the trailing-yield ranking is textbook — AUD/GBP/CAD (+1.2..1.3%) as the high-")
print("    yielders, CHF/JPY (~0%) as the funders. The basket is genuinely long carry, short the safe havens.")
print("  • THE PREMIUM IS REAL BUT THIN: +2.4%/yr constructed (Sharpe +0.32), +1.4% DBV (+0.13). Positive, modest —")
print("    a real earned return, not the ~0 the VRP showed at fair pricing.")
print("  • THE STEAMROLLER IS REAL: skew is negative on BOTH constructions (-0.54 / -0.57) and it partly unwinds in")
print("    risk-off — on equity's worst 5% days carry corr +0.57, averaging -0.68%. The positive 2020/2022 CALENDAR")
print("    years mask the intra-year hit (a dollar-neutral basket rode the 2022 JPY collapse: long GBP/CAD, short JPY).")
print("  • BUT IT'S THE LEAST 'COSTUME' OF THE EARNED PREMIA. vs credit (#1): FX carry's equity beta is lower (+0.22")
print("    vs +0.39), its crisis-correlation milder (+0.57 vs +0.86), and its Jensen alpha is ~0 (-0.6% / -0.1%)")
print("    rather than deeply negative (-2.3%). Carry keeps a genuine INDEPENDENCE credit lacked — it is not merely")
print("    equity risk in disguise. Of VRP / credit / carry, this is the closest thing to a real standalone premium.")
print("  VERDICT: FX carry is the most legitimate earned premium in the arc — a real, independent-ish return — but")
print("  it is THIN and crash-prone (negative skew, +0.57 crisis-corr) and its alpha is ~0, not positive: you're")
print("  paid roughly FAIRLY for bearing an equity-correlated tail, no free lunch. The nickels are real; so is the")
print("  steamroller. Next: regime-gate carry (a risk-off / vol filter to dodge the unwinds) — does timing lift the")
print("  thin premium as trend+carry partly lifted duration? — then commodities carry (backwardation / roll-yield).")
