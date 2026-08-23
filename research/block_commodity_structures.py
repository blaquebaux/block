#!/usr/bin/python3
# =============================================================================
# block_commodity_structures.py — Block COMMODITY catalog variation #8: crack spread, Asian option, three-way collar.
#
# The commodity block of the 120-catalog (crack/crush spreads, Asian averaging options, swing options, collars).
# Three structures chosen to span the HONEST range — the program isn't only about traps:
#   PART 1  CRACK SPREAD (UGA gasoline − USO crude) — the refiner's margin. Real hedge, or just commodity beta?
#   PART 2  ASIAN (average-rate) OPTION — the rare modification that pays the BUYER: averaging cuts the effective
#           vol, so the option is genuinely cheaper — a fair discount, not a desk fee. The honest counter-example.
#   PART 3  THREE-WAY COLLAR — the "zero-cost" hedge that widens the band by SELLING a deep put: below that strike
#           you are LONG THE CRASH again. The classic structure that re-sells the very tail it claims to hedge.
# Empirical on real ETF paths (USO has the 2020 crash — perfect for the three-way trap).
# =============================================================================
import os, json, urllib.request
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def load(sym, start="2016-01-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment=all&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return [x["t"][:10] for x in b], np.array([x["c"] for x in b],float)
def stats(p, per=252):
    m,s=p.mean()*per, p.std()*np.sqrt(per); sh=m/s if s>0 else float('nan')
    lv=np.cumprod(1+p); dd=(lv/np.maximum.accumulate(lv)-1).min()
    z=(p-p.mean())/p.std() if p.std()>0 else p*0
    return dict(ann=m, sh=sh, dd=dd, worst=p.min(), skew=float((z**3).mean()))

D,USO=load("USO"); _,UGA=load("UGA"); _,DBC=load("DBC"); _,SPY=load("SPY"); _,BIL=load("BIL")
n=min(len(USO),len(UGA),len(SPY),len(BIL)); USO,UGA,SPY,BIL,D=USO[-n:],UGA[-n:],SPY[-n:],BIL[-n:],D[-n:]
rU=USO[1:]/USO[:-1]-1; rG=UGA[1:]/UGA[:-1]-1; rSPY=SPY[1:]/SPY[:-1]-1; DT=D[1:]
def yr(p,y): return np.prod([1+p[i] for i,d in enumerate(DT) if d[:4]==str(y)])-1

print("="*100, "\nBLOCK COMMODITY #8 — crack spread · Asian option · three-way collar  (real ETF paths)\n"+"="*100)

# --- PART 1: crack spread (gasoline − crude) --------------------------------------------------------
crack=rG-rU; m=stats(crack); corr=np.corrcoef(crack,rSPY)[0,1]
print("  PART 1 — CRACK SPREAD (UGA gasoline − USO crude, the refiner margin):")
print(f"    ann {m['ann']*100:+.1f}%  Sharpe {m['sh']:+.2f}  vol {crack.std()*np.sqrt(252)*100:.0f}%  maxDD {m['dd']*100:+.0f}%  skew {m['skew']:+.2f}  corr-SPY {corr:+.2f}  2020 {yr(crack,2020)*100:+.0f}%  2022 {yr(crack,2022)*100:+.0f}%")

# --- PART 2: Asian (average-rate) vs vanilla, ATM, rolling 63d windows -------------------------------
W=63
van=[]; asi=[]
for t in range(0, len(USO)-W):
    S0=USO[t]; path=USO[t:t+W]; K=S0
    van.append(max(path[-1]-K,0)/K); asi.append(max(path.mean()-K,0)/K)
van=np.array(van); asi=np.array(asi)
term_vol=np.std([USO[t+W-1]/USO[t]-1 for t in range(len(USO)-W)])
avg_vol =np.std([USO[t:t+W].mean()/USO[t]-1 for t in range(len(USO)-W)])
print("\n  PART 2 — ASIAN (average-rate) vs VANILLA call, ATM, 3-mo (empirical expected payoff = fair value proxy):")
print(f"    vanilla E[payoff] {van.mean()*100:.2f}%   Asian E[payoff] {asi.mean()*100:.2f}%   Asian is {(1-asi.mean()/van.mean())*100:.0f}% CHEAPER")
print(f"    why: averaging cuts the effective vol — terminal σ {term_vol*100:.0f}% vs average σ {avg_vol*100:.0f}% (≈ /√3). The discount is REAL.")

# --- PART 3: plain collar vs three-way collar, rolling 63d, on USO ----------------------------------
Fp1,Fp2,Cc = -0.10, -0.30, +0.10        # floor -10%, re-sold put -30%, cap +10% (all "zero-cost" by assumption)
def collar(r):      return np.clip(r, Fp1, Cc)                                  # long put@Fp1, short call@Cc
def threeway(r):    return np.clip(r, Fp1, Cc) + np.minimum(r-Fp2,0.0)          # + short put@Fp2: re-eat losses below Fp2
rc=np.array([USO[t+W-1]/USO[t]-1 for t in range(len(USO)-W)])                   # 3-mo holding returns
pc=collar(rc); tw=threeway(rc)
print("\n  PART 3 — PLAIN COLLAR vs THREE-WAY COLLAR on USO (floor -10% / cap +10%; three-way re-sells a -30% put):")
print(f"    {'structure':<20}{'mean':>8}{'worst 3-mo':>12}{'skew':>8}")
for nm,x in [("unhedged USO",rc),("plain collar",pc),("three-way collar",tw)]:
    z=(x-x.mean())/x.std() if x.std()>0 else x*0
    print(f"    {nm:<20}{x.mean()*100:>+7.1f}%{x.min()*100:>+11.1f}%{float((z**3).mean()):>+8.2f}")
print(f"    -> the plain collar floors the loss at {Fp1*100:.0f}%; the three-way's worst 3-mo is {tw.min()*100:.0f}% — the")
print(f"       re-sold -30% put RE-OPENS the crash tail (2020 oil), exactly where you thought you were protected.")
print("\n  READ (the commodity block shows the full honest range — not everything is a trap):")
print("  • CRACK SPREAD is a REAL, diversifying exposure. Near-ZERO equity correlation (+0.05) and — rare —")
print("    POSITIVE skew (+1.25): the tail is on the UPSIDE (refining margins spike in supply shocks; long-crack")
print("    returned +95% in 2020 as crude collapsed but products held). Not standalone alpha (Sharpe +0.34, 25%")
print("    vol, −49% DD), but a genuinely uncorrelated, positive-skew sleeve — the mirror of the negative-skew")
print("    premia elsewhere in the book. A real refiner hedge, and a real diversifier for everyone else.")
print("  • ASIAN OPTION is the modification that pays the BUYER. Averaging cuts the effective vol (terminal 21% →")
print("    average 12%, ≈ /√3), so the Asian is 44% CHEAPER — and that discount is FAIR, not a trick. For a firm")
print("    with continuous/averaged exposure (an airline buying fuel all year, a treasurer hedging monthly) it's a")
print("    cheaper, better-matched hedge. The honest counter-example: not every catalog modification is desk margin.")
print("  • THREE-WAY COLLAR is the trap. 'Widen the zero-cost band' by re-selling a deep (−30%) put, and below that")
print("    strike you are LONG THE CRASH again: worst 3-mo −61% vs the plain collar's −10%, skew −2.16 vs −0.28. In")
print("    the 2020 oil crash the three-way blew through exactly where you thought you were protected. You sold back")
print("    the very tail you were buying — a slightly wider band in calm, paid for with the catastrophe.")
print("  VERDICT: the sharpened rule (with #6 tranches, #7 CMS) — a modification pays the BUYER when it genuinely")
print("  REDUCES risk (Asian averaging: real vol cut, fair price) and pays the DESK when it HIDES risk (three-way's")
print("  re-sold tail, the tranche's correlation, the CMS's vol mark). Read the payoff to the TAIL, not the brochure.")
print("  And some structures are neither trick nor trap but honest exposure (the crack spread). Next: FX exotics —")
print("  barrier / digital / target-forward, where the 'zero-cost' hedge hides a knockout tail.")
