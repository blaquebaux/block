#!/usr/bin/python3
# =============================================================================
# crossasset_allocator.py — emit today's governed CROSS-ASSET KEEPER-BOOK target (validated, live).
#
# The graduation of the seven-block study: assemble ONLY the validated keepers into today's target book and let
# the governed Julia driver route it through the Layer-3 safety gate. No LLM in the order path — reproducible
# code both sides. Equal-weight (1/3 each) the three keeper sleeves (validation: research/crossasset_keeper_book.py,
# book Sharpe +0.83, additive to equity):
#   GOLD            GLD +1/3                                   (the standout diversifier)
#   GATED DURATION  IEF +1/3  IFF 100d trend up AND curve slope>0   (crisis-mirror, tail-bounded; Rates #2)
#   GATED FX CARRY  +1/6 each top-2 yield / -1/6 each bottom-2  IFF equity is calm (SPY 21d vol <= 252d)  (FX #2)
# Emits {symbol: weight} (JSON + txt); crossasset_live.jl reads it. Signals use the last settled close (today-2),
# aligned with the driver's data asof.
#   python3 live/crossasset_allocator.py
# =============================================================================
import os, json, datetime, urllib.request
from math import sqrt
import numpy as np

H = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID",""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET_KEY","")}
END = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")   # settled close, aligned with the driver
def load(sym, adj="all", start="2015-06-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={END}"
       f"&adjustment={adj}&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return {x["t"][:10]: x["c"] for x in b}

FX=["FXA","FXB","FXC","FXE","FXF","FXY"]; core=["GLD","IEF","SPY","BIL"]
CFG=os.path.join(os.path.expanduser("~"), ".config", "blaquebaux")
OUT=os.environ.get("BB_ALLOC_TARGET", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "crossasset_target.txt"))

def main():
    if not H["APCA-API-KEY-ID"]: raise SystemExit("set ALPACA_KEY_ID / ALPACA_SECRET_KEY")
    TR={s:load(s) for s in FX+core}; PR={s:load(s,"split") for s in FX+["IEF","BIL"]}
    dates=sorted(set.intersection(*[set(TR[s]) for s in FX+core], *[set(PR[s]) for s in FX+["IEF","BIL"]]))
    P ={s:np.array([TR[s][d] for d in dates],float) for s in FX+core}
    pr={s:np.array([PR[s][d] for d in dates],float) for s in FX+["IEF","BIL"]}
    R ={s:P[s][1:]/P[s][:-1]-1 for s in FX+core}; rp={s:pr[s][1:]/pr[s][:-1]-1 for s in FX+["IEF","BIL"]}
    asof=dates[-1]
    def yld(s): d=np.clip(R[s]-rp[s],0,None); return d[-252:].sum()                     # current trailing 12m yield
    def rvol(x,w): return x[-w:].std()*sqrt(252)

    w={"GLD": 1/3.0}
    # gated duration
    trend = P["IEF"][-1] > P["IEF"][-100:].mean()
    carry = (yld("IEF") - yld("BIL")) > 0
    dur_on = bool(trend and carry); w["IEF"]= (1/3.0) if dur_on else 0.0
    # gated FX carry
    spx = R["SPY"]-R["BIL"]; vol_on = bool(rvol(spx,21) <= rvol(spx,252))
    ys={s:yld(s) for s in FX}; rank=sorted(FX,key=lambda s:ys[s]); longs,shorts=rank[-2:],rank[:2]
    if vol_on:
        for s in longs:  w[s]=w.get(s,0.0)+1/6.0
        for s in shorts: w[s]=w.get(s,0.0)-1/6.0
    w={s:round(v,6) for s,v in w.items() if abs(v)>1e-9}
    gross=sum(abs(v) for v in w.values())
    regime = f"dur:{'on' if dur_on else 'off'},fxcarry:{'on' if vol_on else 'off'}"
    out={"asof":asof,"mode":"keeperbook","regime":regime,"gross":round(gross,3),
         "duration_on":dur_on,"fxcarry_on":vol_on,"fx_longs":longs,"fx_shorts":shorts,"weights":w}
    print(f"CROSS-ASSET keeper-book  asof {asof}  {regime}  gross {gross:.2f}x  {len(w)} names")
    for s,v in sorted(w.items(), key=lambda x:-abs(x[1])): print(f"    {s:5} {v:+.3f}")
    json.dump(out, open(OUT.replace('.txt','.json'),"w"), indent=2)
    with open(OUT,"w") as f:
        f.write(f"# crossasset keeper-book  asof={asof} mode=keeperbook regime={regime} gross={gross:.3f}\n")
        for s,v in sorted(w.items()): f.write(f"{s} {v}\n")

if __name__=="__main__": main()
