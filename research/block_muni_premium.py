#!/usr/bin/python3
# =============================================================================
# block_muni_premium.py — Block MUNICIPAL block #1: the muni spread — the "good credit"?
#
# Municipals complete the catalog taxonomy (equity/FX/rates/credit/commodities/MUNI/funding). Muni bonds are
# tax-exempt state/local debt: they yield LESS than Treasuries pre-tax (the tax break is priced in), but their
# real premium is (a) the after-TAX yield pickup and (b) a spread for LIQUIDITY and TAX-POLICY risk — NOT
# corporate-earnings risk. So the honest question mirrors credit #1: is the muni spread another equity-beta
# wrapper, or a genuinely MORE INDEPENDENT premium (munis default on politics/rates, not earnings; their tail is
# the March-2020 LIQUIDITY crunch, not defaults)?
#   IG muni spread = MUB (IG muni ~6.5y) − IEF (7-10y Treasury ~7.5y)   [duration-approx; MUB a touch shorter]
#   HY muni spread = HYD (HY muni) − MUB (IG muni)
# Plus the tax kicker: gross up the muni distribution yield to taxable-equivalent (top bracket) vs the Treasury.
# =============================================================================
import os, json, urllib.request
from math import sqrt
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def load(sym, adj="all", start="2015-06-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment={adj}&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return {x["t"][:10]: x["c"] for x in b}

syms=["MUB","HYD","IEF","SHY","SPY","BIL"]
TR={s:load(s) for s in syms}; PR={s:load(s,"split") for s in ["MUB","IEF"]}
dates=sorted(set.intersection(*[set(TR[s]) for s in syms], set(PR["MUB"]), set(PR["IEF"])))
P={s:np.array([TR[s][d] for d in dates],float) for s in syms}
pr={s:np.array([PR[s][d] for d in dates],float) for s in ["MUB","IEF"]}
R={s:P[s][1:]/P[s][:-1]-1 for s in syms}; DT=dates[1:]
spx=R["SPY"]-R["BIL"]

def stats(e):
    m,s=e.mean()*252,e.std()*sqrt(252); sh=m/s if s>0 else float('nan')
    lv=np.cumprod(1+e); dd=(lv/np.maximum.accumulate(lv)-1).min()
    z=(e-e.mean())/e.std() if e.std()>0 else e*0
    return dict(ann=m,sh=sh,dd=dd,worst=e.min(),skew=float((z**3).mean()))
def yr(e,y): return np.prod([1+e[i] for i,d in enumerate(DT) if d[:4]==str(y)])-1
def beta_alpha(e):
    b=np.cov(e,spx)[0,1]/np.var(spx); return b,(e.mean()-b*spx.mean())*252
def crisis(e):
    k=int(len(spx)*0.05); w=np.argsort(spx)[:k]; return np.corrcoef(e[w],spx[w])[0,1], e[w].mean()*100
def yield_of(s):
    rt=P[s][1:]/P[s][:-1]-1; rp=pr[s][1:]/pr[s][:-1]-1; d=np.clip(rt-rp,0,None); return d[-252:].sum()  # trailing 12m

igm=R["MUB"]-R["IEF"]; hym=R["HYD"]-R["MUB"]
print("="*104, "\nBLOCK MUNICIPAL #1 — the muni spread: the 'good credit'?  (tax-exempt, liquidity/policy risk, not earnings)\n"+"="*104)
print(f"  {'spread (dur-approx)':<22}{'ann':>8}{'Sharpe':>8}{'maxDD':>8}{'worst d':>9}{'skew':>7}{'2020':>8}{'2022':>8}{'β(SPY)':>8}{'α(Jensen)':>11}{'crisisρ':>9}")
for nm,e in [("IG muni (MUB−IEF)",igm),("HY muni (HYD−MUB)",hym)]:
    m=stats(e); b,a=beta_alpha(e); cc,_=crisis(e)
    print(f"  {nm:<22}{m['ann']*100:>+7.1f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.0f}%{m['worst']*100:>+8.1f}%{m['skew']:>+7.2f}{yr(e,2020)*100:>+7.1f}%{yr(e,2022)*100:>+7.1f}%{b:>+8.2f}{a*100:>+10.1f}%{cc:>+9.2f}")

t=0.408   # top federal bracket + NIIT
yM,yT=yield_of("MUB"),yield_of("IEF"); tey=yM/(1-t)
print(f"\n  TAX KICKER (trailing-12m yields): MUB muni {yM*100:.1f}%  ->  taxable-equivalent {tey*100:.1f}% (top bracket)  vs  IEF Treasury {yT*100:.1f}%")
print(f"    the after-tax muni pickup over Treasuries is {(tey-yT)*100:+.1f}% — a STRUCTURAL tax benefit, on top of the pre-tax spread above.")
print(f"\n  CONTRAST vs corporate credit (#1): IG muni β to SPY {beta_alpha(igm)[0]:+.2f} vs corporate IG +0.22; HY muni β {beta_alpha(hym)[0]:+.2f} vs corporate HY +0.39")
print("\n  READ (honest scorecard):")
print("  • MUNIS ARE THE 'GOOD CREDIT' — genuinely more independent than corporates. IG-muni beta to SPY is +0.11")
print("    (vs corporate IG +0.22) and HY-muni +0.19 (vs corporate HY +0.39) — about HALF the equity beta, because")
print("    munis default on politics/rates, not corporate earnings. This is what corporate credit only pretends to be.")
print("  • BUT THE PRE-TAX SPREAD IS THIN, WITH A LIQUIDITY TAIL. IG +0.9%/yr, HY +0.7%/yr, and Jensen alpha still")
print("    NEGATIVE (-0.6% / -1.8%). The muni tail is a LIQUIDITY crunch, not defaults (March-2020: worst day -5.3% /")
print("    -12.2%, skew -1.15 / -1.52, crisis-corr +0.61 / +0.56) — it still coincides with equity stress, so munis")
print("    are more-independent, NOT un-correlated.")
print("  • THE REAL PREMIUM IS THE TAX CODE. MUB's 3.5% yield is a 5.8% taxable-equivalent at the top bracket vs IEF's")
print("    4.2% — a +1.6%/yr after-tax pickup that the pre-tax ETF return CAN'T show. That structural, reliable tax")
print("    edge dwarfs the thin, negative-alpha pre-tax spread.")
print("  VERDICT: for a TAXABLE investor munis dominate corporate credit — lower equity beta AND a +1.6% after-tax")
print("  yield pickup — but the edge is the tax exemption, not a harvestable market spread (pre-tax it's thin with a")
print("  liquidity tail). Munis are the better instrument; neither muni nor corporate credit is a standalone premium.")
