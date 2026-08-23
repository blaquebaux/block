#!/usr/bin/python3
# =============================================================================
# block_rates_carry.py — Block RATES block #2: carry / roll-down — the curve SLOPE as the signal.
#
# Rates #1: buy-and-hold duration is a negative-carry, crisis-mirror asset, and PRICE TREND bounds its tail but
# makes no edge. #2 asks the carry question properly: an UPWARD-SLOPING curve pays you to hold duration (coupon
# income + ROLL-DOWN as the bond ages toward lower yields); an INVERTED curve does not. So the right signal is
# not price momentum — it's the LEVEL OF THE SLOPE itself, a state/carry signal. "Match the signal to the sleeve."
#
# Slope proxy, price-only (no external rates feed): recover each ETF's trailing-12m DISTRIBUTION YIELD from the
# gap between its total-return series (adjustment=all) and its price-only series (adjustment=split) — the daily
# TR-minus-price return is the dividend drip; sum 252d = running yield. slope = yield(IEF) − yield(BIL cash).
# Positive slope = positive carry -> own duration; inverted (2022-23) -> stand in cash. All signals lagged 1 day.
# =============================================================================
import os, json, urllib.request
from math import sqrt
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def load(sym, adj, start="2015-06-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment={adj}&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return {x["t"][:10]: x["c"] for x in b}

syms=["BIL","IEF","TLT"]
TR ={s:load(s,"all")   for s in syms}          # total return (income reinvested)
PR ={s:load(s,"split") for s in syms}          # price only (splits, no dividends)
dates=sorted(set.intersection(*[set(TR[s]) for s in syms], *[set(PR[s]) for s in syms]))
tr={s:np.array([TR[s][d] for d in dates],float) for s in syms}
pr={s:np.array([PR[s][d] for d in dates],float) for s in syms}
DT=dates[1:]
rtr={s:tr[s][1:]/tr[s][:-1]-1 for s in syms}    # total-return daily
rpr={s:pr[s][1:]/pr[s][:-1]-1 for s in syms}    # price daily
div={s:np.clip(rtr[s]-rpr[s],0,None) for s in syms}                       # daily dividend drip (>=0)
def yld(s):                                                               # trailing-252d running yield
    d=div[s]; y=np.array([d[max(0,i-252):i].sum() for i in range(len(d))]); return y
yB,yI=yld("BIL"),yld("IEF")
slope=yI-yB                                                               # curve slope proxy (long yield - cash)
cash=rtr["BIL"]

def stats(e):
    m,s=e.mean()*252, e.std()*sqrt(252); sh=m/s if s>0 else float('nan')
    lv=np.cumprod(1+e); dd=(lv/np.maximum.accumulate(lv)-1).min()
    z=(e-e.mean())/e.std() if e.std()>0 else e*0
    return dict(ann=m, sh=sh, dd=dd, skew=float((z**3).mean()))
def yr(e,y): return np.prod([1+e[i] for i,d in enumerate(DT) if d[:4]==str(y)])-1

def gate_trend(s):  # 100d price trend, lag-safe (decide at close i, earn r[i] over i->i+1)
    return np.array([1.0 if i>=100 and pr[s][i]>pr[s][i-100:i].mean() else 0.0 for i in range(len(rtr[s]))])
def gate_carry():   # own duration only when the curve slopes up (positive carry), signal lagged 1 day
    g=(slope>0).astype(float); g[1:]=g[:-1]; g[0]=0; return g

inv=(slope<=0)
first=next((DT[i] for i in range(len(DT)) if inv[i]), None)
print("="*102, "\nBLOCK RATES #2 — CARRY / roll-down: the curve SLOPE as the signal  (duration ETFs, excess over BIL cash)\n"+"="*102)
print(f"  slope proxy (IEF yield − BIL cash yield): inverted on {100*inv.mean():.0f}% of days; first inversion ~{first}\n")
gc=gate_carry()
for s,lbl in [("IEF","IEF 7-10y"),("TLT","TLT 20y+")]:
    gt=gate_trend(s); base=rtr[s]-cash
    rows=[("buy & hold", base), ("trend-gated (#1)", gt*base), ("CARRY-gated (slope>0)", gc*base),
          ("trend AND carry", gt*gc*base)]
    print(f"  --- {lbl} ---")
    print(f"    {'strategy':<24}{'ann xs':>8}{'Sharpe':>8}{'maxDD':>8}{'skew':>7}{'2020':>8}{'2022':>8}{'2023':>8}{'time on':>9}")
    for nm,e in rows:
        m=stats(e); on = (e!=0).mean()*100
        print(f"    {nm:<24}{m['ann']*100:>+7.1f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.0f}%{m['skew']:>+7.2f}{yr(e,2020)*100:>+7.1f}%{yr(e,2022)*100:>+7.1f}%{yr(e,2023)*100:>+7.1f}%{on:>8.0f}%")
    print()

# how correlated are the two signals?
gtI=gate_trend("IEF"); corr=np.corrcoef(gtI,gc)[0,1]
print(f"  signal overlap: trend vs carry gate correlation {corr:+.2f}  (agree {100*np.mean(gtI==gc):.0f}% of days)")
print("\n  READ (honest scorecard):")
print("  • CARRY IS A GENUINELY DISTINCT SIGNAL from trend — the two gates correlate just -0.09 and agree only 43%")
print("    of days. Trend reads price momentum (fast, catches the acute move); carry reads the curve STATE (own")
print("    duration only when the slope pays). They detect different things, so they compose rather than duplicate.")
print("  • COMBINING them is the best rates result yet. Trend-AND-carry on IEF: Sharpe -0.14 -> +0.30, maxDD -28%")
print("    -> -9%, skew +0.17 -> +0.64, 2022 -16% -> -4%, on just 30% of days. TLT the same shape (-0.13 -> +0.08,")
print("    maxDD -52% -> -23%). Trend dodged the 2022 price crash; carry avoided the 2023 negative-carry inversion")
print("    bleed — each covering the other's blind spot.")
print("  • HONEST CAVEAT — the carry proxy LAGS. Distribution yield is trailing-12m, so BIL's cash yield was slow")
print("    to reflect the 2022 hikes: carry-ALONE stayed long right through the 2022 crash (2022 -16.3%, = buy-hold)")
print("    and only registered the inversion in 2023 (where it then added +4%/+7%). A true real-time 2s10s would be")
print("    more responsive; this price-only proxy is a lagged approximation, and the early-2016 'inversion' is a")
print("    trailing-window artifact. Read carry as the SLOW state signal, trend as the FAST one.")
print("  • AND IT'S STILL THIN. Even combined, excess return is ~+1%/yr — the win is RISK (maxDD -9%, skew +0.64),")
print("    not carry harvested, and it leans on one big regime (2022). Not a validated keeper; a real, honest")
print("    improvement in how you HOLD a diversifier.")
print("  VERDICT: carry (curve slope) is a real, distinct signal, and trend+carry is the honest best way to hold")
print("  duration — bounded tail, positive skew, two uncorrelated signals covering each other. But it's a RISK")
print("  overlay on a crisis-mirror diversifier, not a harvested carry premium: the curve doesn't pay you to hold")
print("  duration this decade, it only tells you WHEN duration is least dangerous. Next: the CREDIT block (CDS/")
print("  index) — the default-risk premium, the first genuinely EARNED premium to test since the VRP.")
