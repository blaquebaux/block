#!/usr/bin/python3
# =============================================================================
# block_2_linkages_tested.py — BLAQUE BAUX BLOCK #2 (test the two proposed linkages)
#
# H1: a stronger currency makes the home country's equity fall (exporters lose competitiveness).
# H2: interest rates rise -> cost of doing business rises -> equity takes a hit.
#
# FINDINGS — both real, both with a crucial caveat:
#  H1 CONFIRMED, but only in LOCAL terms and for export/EM economies. Strong yen vs LOCAL Japan
#     (DXJ, hedged) = -0.47 (exporters hurt); but strong yen vs USD-Japan (EWJ) = +0.01 — the
#     currency TRANSLATION cancels the exporter hit inside the tradeable USD wrapper. Strong dollar
#     vs EM = -0.28/-0.20. Near-zero for the US (-0.13): the reserve issuer isn't the export story.
#  H2 CONFIRMED, but REGIME-DEPENDENT. Stock-bond correlation flips: -0.36 in 2016-2021 (bonds
#     HEDGE stocks) -> +0.11 in 2022-2026 (rates up, BOTH fall = H2 holds). The linkage is real in
#     an inflation regime and reversed in a growth-scare regime — unstable, exactly Bore's caution.
#
# RESULTS AS TESTED (2016-2026):
#   H1: FXY vs DXJ(local JP) -0.47 | FXY vs EWJ(USD JP) +0.01 | FXE vs HEDJ(local EU) +0.05
#       UUP vs EEM -0.28 | UUP vs EWZ -0.20 | UUP vs SPY -0.13
#   H2: SPY vs TLT: full -0.14 | 2016-2021 -0.36 | 2022-2026 +0.11  (sign flip)
# Read-only.
# =============================================================================
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _block_common import load

B = load()
print("=" * 80, "\nBLOCK #2 — do the proposed linkages hold?\n" + "=" * 80)

print("\nH1  CURRENCY -> EQUITY (a stronger currency hurts the home country's exporters)")
print(f"  JPY(FXY) vs LOCAL Japan  (DXJ, hedged):  {B.corr('FXY','DXJ'):+.2f}   <- strong yen hurts Nikkei exporters (H1 holds)")
print(f"  JPY(FXY) vs USD  Japan   (EWJ, unhedged):{B.corr('FXY','EWJ'):+.2f}   (translation cancels it: EWJ already contains the yen)")
print(f"  EUR(FXE) vs LOCAL Europe (HEDJ, hedged): {B.corr('FXE','HEDJ'):+.2f}   (Europe less export-concentrated -> weak)")
print(f"  USD(UUP) vs EM (EEM) {B.corr('UUP','EEM'):+.2f} | vs Brazil (EWZ) {B.corr('UUP','EWZ'):+.2f}   (strong $ hurts EM: H1 holds)")
print(f"  USD(UUP) vs US (SPY) {B.corr('UUP','SPY'):+.2f}   (reserve issuer -> near zero, NOT the exporter story)")

print("\nH2  RATES -> EQUITY (rates up -> cost up -> equity hit) — real, but stable?")
print(f"  stock-bond corr SPY vs TLT:   full {B.corr('SPY','TLT'):+.2f}")
print(f"    2016-2021 (low inflation):  {B.corr_window('SPY','TLT','2016-01-01','2021-12-31'):+.2f}   (bonds HEDGE stocks -> H2 reversed)")
print(f"    2022-2026 (inflation):      {B.corr_window('SPY','TLT','2022-01-01','2026-08-01'):+.2f}   (rates up, BOTH fall -> H2 holds)")

print("\nVERDICT: both linkages are REAL — the intuition is right. But H1 lives in LOCAL currency terms")
print("and is invisible in the USD wrappers you'd actually trade (translation cancels it), and it is")
print("asymmetric (export/EM yes, reserve-issuer no); and H2 is REGIME-DEPENDENT, flipping sign between")
print("growth-scare and inflation regimes. Real linkages, but conditional and unstable — a risk map.")
