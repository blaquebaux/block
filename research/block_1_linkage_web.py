#!/usr/bin/python3
# =============================================================================
# block_1_linkage_web.py — BLAQUE BAUX BLOCK #1 (how interlocked are the 4 blocks?)
#
# The premise: equity / FX / rates / commodities are more interlocked than credited.
# FINDING: partly. The links are real — the dollar is a hub (UUP correlates -0.13..-0.43
# to every other block) — but they are WEAK. Eight cross-block proxies still carry ~4.6
# independent factors (57% efficient), FAR more diversification than within a single block
# (40 equities collapse to 19%). So the four blocks are genuinely MORE diversified than
# interlocked: the interlock exists as a shared macro core (dollar / risk-on-off / regime),
# but it does not collapse the blocks into one. Cross-asset-class is still the real diversifier.
#
# RESULTS AS TESTED (2016-2026):
#   8 cross-block proxies -> eff-bets 4.6/8 (57% efficient)  [vs 40 equities 19%]
#   dollar hub (corr UUP to): GLD -0.43  EEM -0.28  EWZ -0.20  DBC -0.14  SPY -0.13
# Read-only.
# =============================================================================
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _block_common import load

B = load()
print("=" * 80, "\nBLOCK #1 — the linkage web: interlocked, or diversified?\n" + "=" * 80)

uni = ["SPY", "EEM", "UUP", "FXY", "TLT", "DBC", "GLD", "USO"]
print(f"\n  8 cross-block proxies -> eff-bets {B.eff_bets(uni):.1f}/8  ({100*B.eff_bets(uni)/8:.0f}% efficient)")
print(f"  (for contrast, 40 same-block equities collapse to ~19% efficient — cross-block IS the diversifier)")
print("\n  the DOLLAR as hub (corr of UUP to each block):")
for s in ["GLD", "EEM", "EWZ", "DBC", "SPY", "TLT"]:
    print(f"    UUP vs {s:4s}: {B.corr('UUP', s):+.2f}")

print("\nVERDICT: the interlock is real but weak — a shared macro core (the dollar, risk-on/off) links")
print("the blocks, yet they still carry ~4.6 of 8 independent factors, far more than within one block.")
print("The four derivative blocks are MORE diversified than interlocked; cross-asset-class remains the")
print("real diversifier (the spine's law). The linkage is a risk map, not a collapse into one factor.")
