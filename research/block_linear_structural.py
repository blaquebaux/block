#!/usr/bin/python3
# =============================================================================
# block_linear_structural.py — Block catalog variation #10: LINEAR / STRUCTURAL — funding, basis, convention.
#
# The catalog's linear/structural entries (IRS, basis swap, zero-coupon & OIS swaps, cross-currency swap, NDF,
# asset swap, TOTAL RETURN SWAP, quanto, funding legs) carry NO option tail — so the program's "read the tail"
# lens shifts: their risk/fee lives in FUNDING, BASIS, and CONVENTION, not in a hidden payoff.
#   PART 1  TOTAL RETURN SWAP — synthetic leverage for a thin financing spread. The visible cost (the spread) is
#           trivial; the real cost is the FUNDING-PULL / MARGIN tail — a normal bear market wipes the equity
#           (Archegos, 2021). The linear analog of the option-tail traps: cheap-until-the-funding-is-pulled.
#   PART 2  CROSS-CURRENCY BASIS — the persistent CIP violation (the post-2008 USD funding premium). The signature
#           structural anomaly — and honestly NOT observable from an equity/ETF feed (it lives in the FX-forward /
#           xccy-swap market). We state the mechanism and known magnitudes; flagged, not faked (family data-honesty).
# =============================================================================
import os, json, urllib.request
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
def load(sym, start="2016-01-01", end="2026-08-01"):
    u=(f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day&start={start}&end={end}"
       f"&adjustment=all&feed=sip&limit=10000"); d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40))
    b=d.get("bars",{}).get(sym,[]); return [x["t"][:10] for x in b], np.array([x["c"] for x in b],float)

D,SPY=load("SPY"); r=SPY[1:]/SPY[:-1]-1; DT=D[1:]
def worst_dd(px):
    return (px/np.maximum.accumulate(px)-1).min()
def year_dd(y):
    idx=[i for i,d in enumerate(D) if d[:4]==str(y)]
    if not idx: return 0.0
    seg=SPY[idx[0]:idx[-1]+1]; return worst_dd(seg)

print("="*100, "\nBLOCK #10 — LINEAR / STRUCTURAL: funding, basis, convention  (no option tail — the risk is elsewhere)\n"+"="*100)

# --- PART 1: TRS synthetic leverage & the funding-pull tail (real SPY) -------------------------------
FEE=0.004   # ~40bp/yr financing spread over OIS — the VISIBLE cost of the TRS
full_dd=worst_dd(SPY)
print("  PART 1 — TOTAL RETURN SWAP: cheap synthetic leverage, and the margin tail it hides  (real SPY 2016-26)")
print(f"    the VISIBLE cost is a ~{FEE*100:.1f}%/yr financing spread. The HIDDEN cost is the margin wipeout:")
print(f"    {'leverage':<10}{'initial margin':>16}{'wipes if SPY falls':>20}{'wiped in-sample?':>20}")
worst_years={y:year_dd(y) for y in (2018,2020,2022)}
for L in (2,3,5,8):
    margin=1.0/L; wiped=[y for y,dd in worst_years.items() if dd<=-margin]
    tag=(f"YES — {', '.join(map(str,wiped))}" if wiped else "survived")
    print(f"    {str(L)+'x':<10}{margin*100:>14.0f}%{'−'+f'{margin*100:.0f}%':>20}{tag:>20}")
print(f"    full-sample SPY max drawdown {full_dd*100:.0f}% (COVID-2020) → any leverage above {1/abs(full_dd):.1f}x was wiped out entirely.")
print(f"    Archegos (2021) ran ~5–8× single-name exposure via TRS and vaporized ~\$10bn in days — the funding leg")
print(f"    got pulled. The financing spread said 'cheap'; the margin tail said otherwise. No option in sight.")

# --- PART 2: cross-currency basis — measurable? ------------------------------------------------------
print("\n  PART 2 — CROSS-CURRENCY BASIS (the CIP violation / post-2008 USD funding premium):")
print("    DATA-HONESTY FLAG: the xccy basis lives in the FX-forward & cross-currency-swap market; it is NOT")
print("    recoverable from an equity/ETF price feed. We state it, we do not fake it from proxies.")
print("    Mechanism: post-2008, covered interest parity fails — synthesizing USD via an FX swap costs MORE than")
print("    borrowing USD directly, by the 'basis' (negative for EUR/JPY vs USD). It persists because arbitraging")
print("    it consumes scarce dealer BALANCE SHEET (Basel leverage ratio), so it is a fee-for-scarcity, not a free")
print("    lunch — harvestable only by those with cheap balance sheet. Known magnitudes: EUR ≈ −20 to −50bp in")
print("    calm, JPY ≈ −30 to −80bp; both blow WIDER in stress (2008/2011, and ≈ −140bp for JPY in Mar-2020) —")
print("    a funding-stress gauge that widens exactly when USD is scarce. Same shape as every tail in this program,")
print("    on the funding axis: quiet, then a gap.")
print("\n  READ (linear/structural — the risk moved off the payoff and onto other axes):")
print("  • THE TRS IS THE TARF'S LINEAR TWIN. No option anywhere — just synthetic exposure for a ~0.4%/yr spread —")
print("    yet the tail is just as lethal: at 3× a normal bear (2020, −34%) wipes the equity; at 5× so do 2020 AND")
print("    2022; at 8×, add 2018. The visible 'fee' (the spread) is trivial; the real cost is the FUNDING-PULL /")
print("    margin tail — the leg can be re-margined or pulled precisely in the drawdown. Archegos is the proof.")
print("    Cheap-until-the-funding-is-pulled is the linear form of cheap-until-it-kills-you.")
print("  • THE CROSS-CURRENCY BASIS is a 'free arbitrage' that isn't free — it's a FEE FOR BALANCE-SHEET SCARCITY,")
print("    harvestable only by cheap-balance-sheet players, and it GAPS in stress (JPY ≈ −140bp, Mar-2020). Same")
print("    shape as every tail in this program, moved to the funding axis: quiet premium, then a gap. (And it's the")
print("    honest data-limit of the ETF feed — flagged, not faked.)")
print("  • QUANTO / CONVENTION: the quanto forward differs from the plain by ρ·σ_asset·σ_fx·T — its value hides in")
print("    the unobservable asset-FX CORRELATION, exactly like the CMS vol mark and the tranche's ρ. Day-count and")
print("    fixing conventions are the same in miniature: the desk's information edge on a detail the client discounts.")
print("  • THE GRAND UNIFYING LAW OF THE CATALOG (all 10 variations): a 'modification' never conjures return — it")
print("    RELOCATES risk onto an axis the buyer isn't watching. OPTION structures hide it in the TAIL (straddle,")
print("    tranche, TARF, barrier); EXOTIC pricing hides it in an UNOBSERVABLE MARK (CMS σ, tranche/quanto ρ);")
print("    LINEAR/STRUCTURAL hides it in the FUNDING leg or the BASIS (TRS, xccy). And the honest exceptions prove")
print("    the rule — the Asian, the average-rate forward, the crack spread, and the WEATHER derivative (a payoff")
print("    with ~zero market beta by construction) genuinely serve the user, priced fairly. VERDICT / the one rule")
print("    the whole program earns: read the payoff to the TAIL, the MARK, and the FUNDING — never the brochure.")
