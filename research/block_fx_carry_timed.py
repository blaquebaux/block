#!/usr/bin/python3
# =============================================================================
# block_fx_carry_timed.py — Block FX block #2: REGIME-GATED carry — can timing dodge the steamroller?
#
# FX #1: G10 carry is a real but THIN premium with a negative-skew crash tail (crisis-corr +0.57 to equity),
# priced roughly fairly (Jensen alpha ~0). #2 asks whether TIMING rescues it — carry's crashes ARE volatility
# spikes / risk-off deleveragings, so gating exposure off in those regimes should (in theory) dodge the worst
# days. The real test is not just Sharpe: does gating FIX THE SKEW and CUT THE CRISIS-CORRELATION — i.e. remove
# the steamroller, not just trim the mean? Four lag-safe gates on the same dollar-neutral G10 carry basket:
#   vol(own)  — off when the basket's own 21d realized vol exceeds its 252d average (elevated vol)
#   vol(SPY)  — off when equity 21d vol exceeds its 252d average (risk-off proxy)
#   dollar    — off when the USD (UUP) is in a 100d uptrend (funding-ccy strength = carry unwind)
#   momentum  — off when the carry equity curve is below its own 100d average
#   combined  — vol(own) AND dollar
# =============================================================================
import os, json, urllib.request
from math import sqrt
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def load(sym, adj, start="2015-06-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment={adj}&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return {x["t"][:10]: x["c"] for x in b}

FX=["FXA","FXB","FXC","FXE","FXF","FXY"]; extra=["SPY","BIL","UUP"]
TR={s:load(s,"all")   for s in FX+extra}
PR={s:load(s,"split") for s in FX}
dates=sorted(set.intersection(*[set(TR[s]) for s in FX+extra], *[set(PR[s]) for s in FX]))
tr={s:np.array([TR[s][d] for d in dates],float) for s in FX+extra}
pr={s:np.array([PR[s][d] for d in dates],float) for s in FX}
DT=dates[1:]
rtr={s:tr[s][1:]/tr[s][:-1]-1 for s in FX+extra}
rpr={s:pr[s][1:]/pr[s][:-1]-1 for s in FX}
spx=rtr["SPY"]-rtr["BIL"]; uup=tr["UUP"][1:]
div={s:np.clip(rtr[s]-rpr[s],0,None) for s in FX}
Y={s:np.array([div[s][max(0,i-252):i].sum() for i in range(len(div[s]))]) for s in FX}

REB=21; carry=np.zeros(len(DT))
for t in range(252, len(DT)-REB, REB):
    rank=sorted(FX, key=lambda s: Y[s][t]); longs,shorts=rank[-2:],rank[:2]
    for d in range(t, min(t+REB,len(DT))):
        carry[d]=0.5*sum(rtr[s][d] for s in longs)-0.5*sum(rtr[s][d] for s in shorts)

def roll_std(x,w):
    return np.array([x[max(0,i-w):i].std()*sqrt(252) if i>1 else 0.0 for i in range(len(x))])
def roll_mean(x,w):
    return np.array([x[max(0,i-w):i].mean() if i>0 else 0.0 for i in range(len(x))])

ceq=np.cumprod(1+carry)                                    # carry equity curve (for momentum gate)
v21,v252=roll_std(carry,21),roll_std(carry,252)
s21,s252=roll_std(spx,21),roll_std(spx,252)
def lag(g): g=g.astype(float); out=np.zeros_like(g); out[1:]=g[:-1]; return out   # 1-day lag, no lookahead
gates={
 "vol(own)":  lag(v21<=v252),
 "vol(SPY)":  lag(s21<=s252),
 "dollar":    lag(np.array([uup[i]<roll_mean(uup,100)[i] if i>=100 else True for i in range(len(uup))])),
 "momentum":  lag(np.array([ceq[i]>roll_mean(ceq,100)[i] if i>=100 else True for i in range(len(ceq))])),
}
gates["combined"]=lag(((v21<=v252)&(np.array([uup[i]<roll_mean(uup,100)[i] if i>=100 else True for i in range(len(uup))]))))

def stats(e):
    m,s=e.mean()*252,e.std()*sqrt(252); sh=m/s if s>0 else float('nan')
    lv=np.cumprod(1+e); dd=(lv/np.maximum.accumulate(lv)-1).min()
    z=(e-e.mean())/e.std() if e.std()>0 else e*0
    return dict(ann=m,sh=sh,dd=dd,skew=float((z**3).mean()))
spxW=spx[252:]                                            # equity excess aligned to the post-warmup window
def crisis(e):
    k=int(len(spxW)*0.05); w=np.argsort(spxW)[:k]; return np.corrcoef(e[w],spxW[w])[0,1], e[w].mean()*100
def alpha(e):
    b=np.cov(e,spxW)[0,1]/np.var(spxW); return (e.mean()-b*spxW.mean())*252

W=slice(252,None)                                          # drop warmup
print("="*106, "\nBLOCK FX #2 — REGIME-GATED carry: can timing dodge the steamroller?  (dollar-neutral G10 carry, lag-safe gates)\n"+"="*106)
print("  the real test: does a gate FIX THE SKEW and CUT THE CRISIS-CORR, not just trim the mean?\n")
print(f"  {'strategy':<18}{'ann':>8}{'Sharpe':>8}{'maxDD':>8}{'skew':>7}{'α(Jensen)':>11}{'crisis-corr':>13}{'crisis-ret':>11}{'time on':>9}")
def row(nm,e):
    m=stats(e[W]); cc,cm=crisis(e[W]); a=alpha(e[W]); on=(e[W]!=0).mean()*100
    print(f"  {nm:<18}{m['ann']*100:>+7.1f}%{m['sh']:>+8.2f}{m['dd']*100:>+7.0f}%{m['skew']:>+7.2f}{a*100:>+10.1f}%{cc:>+13.2f}{cm:>+10.2f}%{on:>8.0f}%")
row("ungated (#1)",carry)
for nm,g in gates.items(): row(nm,carry*g)
print("\n  READ (honest scorecard):")
print("  • TIMING RESCUES CARRY — but only with the RIGHT signal. The equity-vol gate (vol(SPY)) does exactly what")
print("    timing should: crisis-corr +0.57 -> -0.01, maxDD -21% -> -12%, skew -0.54 -> -0.36 — the steamroller is")
print("    removed — while the Sharpe HOLDS (+0.32 -> +0.31, premium kept not trimmed) and Jensen alpha FLIPS")
print("    POSITIVE (-0.6% -> +0.6%). That is the first genuine positive independent alpha in the whole earned-")
print("    premium arc (VRP / credit / carry) — and it came from dodging the tail, not from the premium itself.")
print("  • THE WRONG GATES FAIL, honestly reported. vol(own) also kills the crisis-corr (-0.02) but OVER-TRIMS —")
print("    it cuts the return with the risk (Sharpe +0.32 -> +0.15). The DOLLAR gate cut drawdown but WORSENED skew")
print("    to -1.00 and kept crisis-corr +0.39 (it misses the acute unwind days). MOMENTUM whipsawed (Sharpe +0.09,")
print("    skew unchanged). Three gates that don't dodge the steamroller — only the equity-vol one does.")
print("  • THE LESSON — MATCH THE GATE TO THE FAILURE MODE. Carry's failure is equity-vol spikes, so an EQUITY-VOL")
print("    filter is the correct signal; price-momentum and dollar-trend are not. 'Match the signal to the sleeve,'")
print("    now proven at the gate level — the shape of the risk tells you which regime signal can neutralize it.")
print("  • CAVEAT: the winning alpha is SMALL (+0.6%) on one decade and a handful of crises, and gating adds")
print("    turnover this sim doesn't charge. A real, honest improvement — not a validated keeper.")
print("  VERDICT: yes, timing turns FX carry from a fairly-priced, crash-prone premium into a small POSITIVE-alpha,")
print("  tail-MANAGED one — the arc's first true (if thin) independent edge — and, exactly on the program's thesis,")
print("  the edge is RISK MANAGEMENT (removing the equity-correlated tail), not a fatter premium. Next and last")
print("  asset block: COMMODITIES carry (backwardation / roll-yield) — completing Block's four-block cross-asset map.")
