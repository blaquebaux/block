#!/usr/bin/python3
# =============================================================================
# block_rates_cms.py — Block RATES catalog variation #7: CMS — the convexity fee, and where the margin hides.
#
# Continuing the "modify to death" program: the CMS family of the 120-catalog (Constant Maturity Swap, CMS
# Spread Option, Range Accrual). A CMS pays a LONG-tenor swap rate (e.g. 10y) on a SHORT schedule — and because
# the swap rate enters the payoff CONVEXLY (a bond's price is convex in yield), the fair CMS rate sits ABOVE the
# forward swap rate by a CONVEXITY ADJUSTMENT (Jensen). The catalog "what's real vs fee-in-a-suit" question:
#   (1) Is the convexity adjustment REAL value, or a desk fee? (its SIGN is model-independent — Jensen — but…)
#   (2) …where does the MARGIN hide? We show the adjustment's SIZE lives entirely in the VOL mark (σ) the desk
#       chooses — the CMS analog of the tranche's correlation assumption: the clean "fair CMS rate" flatters,
#       the σ assumption decides.
#   (3) CMS SPREAD OPTION (10y−2y): a curve-shape bet whose price hides in the rate-rate CORRELATION.
# Hull's replication convexity adjustment: CA ≈ −½·S₀²·σ²·T·(G''(S₀)/G'(S₀)), G = par-bond price vs yield.
# =============================================================================
from math import erf, sqrt, log, exp
import numpy as np

def Phi(x): return 0.5*(1+erf(x/sqrt(2)))
def G(y, n, S0):                              # price of an n-yr bond paying coupon S0, as a function of yield y
    return sum(S0/(1+y)**i for i in range(1,n+1)) + 1/(1+y)**n
def convexity_adj(S0, sig, T, n):             # Hull CMS convexity adjustment, in absolute rate terms
    h=1e-5
    Gp =(G(S0+h,n,S0)-G(S0-h,n,S0))/(2*h)
    Gpp=(G(S0+h,n,S0)-2*G(S0,n,S0)+G(S0-h,n,S0))/(h*h)
    return -0.5*S0*S0*sig*sig*T*(Gpp/Gp)      # >0 (Gpp/Gp<0): the CMS rate exceeds the forward

print("="*100, "\nBLOCK RATES #7 — CMS convexity: real value, or a fee hiding in the vol mark?  (Hull replication adjustment)\n"+"="*100)
S0=0.04; T=5.0                                # 4% forward swap rate, 5y to the CMS reset
print(f"  forward swap rate S0={S0*100:.1f}%, payment lag T={T:.0f}y — convexity adjustment (bps), by tenor × vol mark:")
print(f"  {'CMS tenor':<12}"+"".join(f"σ={s:>3.0f}%".rjust(10) for s in (15,25,35))+"     real?/fee?")
for n in (2,5,10,30):
    row=[convexity_adj(S0,s/100,T,n) for s in (15,25,35)]
    print(f"  {str(n)+'y swap':<12}"+"".join(f"{ca*1e4:>9.1f}" for ca in row)+f"     +{(row[2]-row[0])*1e4:.0f}bp swing on the σ mark alone")

# how much of the "fair CMS rate" is the vol assumption? at 10y, σ 25%->35%
ca25=convexity_adj(S0,0.25,T,10); ca35=convexity_adj(S0,0.35,T,10)
print(f"\n  THE FEE HIDES IN σ: a 10y CMS at σ=25% carries {ca25*1e4:.0f}bp of convexity; re-mark σ to 35% and it's")
print(f"  {ca35*1e4:.0f}bp — a {(ca35-ca25)*1e4:.0f}bp swing ({(ca35/ca25-1)*100:.0f}% bigger) from the vol assumption alone, on the SAME trade.")

# --- CMS SPREAD OPTION: a curve bet whose price hides in the rate-rate correlation --------------------
print("\n"+"-"*100+"\n  CMS SPREAD OPTION (10y−2y steepener cap) — the price hides in the rate-rate CORRELATION:")
S10,S2=0.043,0.040; s10,s2=0.25,0.30; K=0.0; Topt=1.0    # 30bp curve, per-rate vols, ATM-ish strike on the spread
def spread_cap(rho):
    var=(s10*S10)**2+(s2*S2)**2-2*rho*(s10*S10)*(s2*S2)   # variance of the (10y-2y) spread (bp^2/yr, lognormal-ish)
    sd=sqrt(max(var,1e-12))*sqrt(Topt); fwd=S10-S2
    d=(fwd-K)/sd if sd>0 else 0.0
    return (fwd-K)*Phi(d)+sd*exp(-0.5*d*d)/sqrt(2*3.141592653589793)   # Bachelier call on the spread
print(f"  {'rate-rate corr ρ':<20}"+"".join(f"ρ={r:>4.1f}".rjust(9) for r in (0.0,0.3,0.6,0.9))+"   spread vol")
prices=[spread_cap(r) for r in (0.0,0.3,0.6,0.9)]
sds=[sqrt(max((s10*S10)**2+(s2*S2)**2-2*r*(s10*S10)*(s2*S2),0))*1e4 for r in (0.0,0.3,0.6,0.9)]
print(f"  {'spread-cap value (bp)':<20}"+"".join(f"{p*1e4:>8.1f}" for p in prices)+f"   {sds[0]:.0f}→{sds[-1]:.0f}bp")
print(f"  -> price falls {(1-prices[-1]/prices[0])*100:.0f}% from ρ=0.0 to ρ=0.9: the SAME curve option is worth wildly")
print(f"     different amounts depending on the correlation MARK — the buyer can't see it, so that's the desk margin.")
print("\n  READ (the convexity fee, honestly — and where the margin actually lives):")
print("  • THE CONVEXITY ADJUSTMENT IS REAL, not fee-in-a-suit in KIND. It is Jensen — the CMS payoff is convex in")
print("    rates — so its SIGN is model-independent: a 10y CMS genuinely carries ~25bp, a 30y ~60bp+ of convexity.")
print("    The buyer really does pay/receive it; it is not an invented line item.")
print("  • BUT THE MARGIN HIDES IN THE VOL MARK. The SAME 10y CMS is worth 9bp at σ=15% and 49bp at σ=35% — a 40bp")
print("    swing (the 30y swings ~97bp) purely from the vol ASSUMPTION, which the buyer cannot independently observe.")
print("    The desk quotes one clean number ('the fair CMS rate'); the σ inside it is invisible. The fee is not a")
print("    charge — it's a MARK.")
print("  • THE CMS SPREAD OPTION tells the same story on CORRELATION: the 10y−2y steepener cap falls 51% in value")
print("    (80→39bp) as the rate-rate ρ goes 0→0.9. The buyer pays for a correlation view they can't see.")
print("  • THE UNIFYING LAW (with tranches #6): exotic value lives in an UNOBSERVABLE parameter — σ for CMS, ρ for")
print("    the spread option and the tranche. So the 'fair price' flatters and the ASSUMPTION decides. It is the")
print("    metric-flatters/tail-decides law applied to PRICING: the margin is the gap between the quoted mark and the")
print("    true parameter, and the buyer has no independent meter. (Range accruals — the CMS family's third member —")
print("    are the same bet worn as yield: a strip of digitals that pays while rates stay calm, i.e. short vol.)")
print("  VERDICT: CMS convexity is real, honestly-earned value — and the catalog's clearest case of a fee that hides")
print("  in an ASSUMPTION rather than a line. The 'innovation' is the desk's information edge on an unobservable")
print("  (vol, correlation), not new economics. Modify-to-death rule: when value depends on σ or ρ, ask for the σ or")
print("  ρ, not just the price. Next catalog sections: commodity structures (crack/crush/Asian/swing) or FX exotics.")
