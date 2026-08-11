#!/usr/bin/python3
# =============================================================================
# block_3_tradeable.py — BLAQUE BAUX BLOCK #3 (is the interlock a strategy?)
#
# If the blocks interlock, can a basket of derivative strategies harvest it?
# FINDING: not as lead-lag alpha. The linkages are priced INSTANTLY — yesterday's dollar
# or rate move has ~0 correlation to today's equity (UUP->EEM -0.05, TLT->SPY +0.06,
# UUP->SPY -0.07), so there is no next-day edge (the family's "correlation is priced
# instantly" law). What DOES survive the instability is (a) cross-asset TREND on the blocks
# (+0.43 Sharpe — trend is the robust way to trade unstable relationships) and, far more, (b)
# simply HOLDING the four blocks as a diversified book: +1.19 Sharpe at 4.1/5 effective bets.
# So Block earns its keep as a DIVERSIFIED cross-asset basket + risk framework, not as a
# stat-arb of the interlocks: the links are for hedging and sizing, the diversification is the edge.
#
# RESULTS AS TESTED (2016-2026):
#   lead-lag corr: UUP[t-1]->EEM[t] -0.05 | TLT[t-1]->SPY[t] +0.06 | UUP[t-1]->SPY[t] -0.07  (priced in)
#   cross-asset TREND (SPY/TLT/GLD/DBC/UUP): Sharpe +0.43
#   4-block EW buy-hold: Sharpe +1.19 | eff-bets 4.1/5
# Read-only.
# =============================================================================
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _block_common import load

B = load()
print("=" * 80, "\nBLOCK #3 — is the interlock tradeable?\n" + "=" * 80)

print("\n(i) LEAD-LAG — does yesterday's macro move predict today's equity?")
for pred, tgt in [("UUP", "EEM"), ("TLT", "SPY"), ("UUP", "SPY")]:
    print(f"    {pred}[t-1] -> {tgt}[t]: corr {B.leadlag(pred, tgt):+.2f}   (near 0 = priced instantly, no next-day edge)")

print("\n(ii) CROSS-ASSET TREND — the robust way to trade unstable relationships")
blocks4 = ["SPY", "TLT", "GLD", "DBC", "UUP"]
print(f"    trend on the blocks (SPY/TLT/GLD/DBC/UUP): Sharpe {B.sharpe(B.trend(blocks4)):+.2f}")

print("\n(iii) JUST HOLD THE BLOCKS — the diversification is the edge")
ew = B.R[:, [B.i[s] for s in blocks4]].mean(1)
print(f"    4-block EW buy-hold: Sharpe {B.sharpe(ew):+.2f}  |  eff-bets {B.eff_bets(blocks4):.1f}/5")

print("\nVERDICT: the interlock is NOT lead-lag alpha (priced instantly). The tradeable residue is")
print("cross-asset trend (+0.43, robust to the sign-flips) and, far more, simply owning the four")
print("blocks as a diversified book (+1.19 at 4.1/5 bets). Block earns its keep as a diversified")
print("cross-asset basket + risk framework — the linkages are for hedging and sizing, not stat-arb.")
