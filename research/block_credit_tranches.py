#!/usr/bin/python3
# =============================================================================
# block_credit_tranches.py — Block CREDIT catalog variation #6: CDS INDEX TRANCHES — the correlation trade.
#
# The credit block of the 120-catalog (CDS Index Tranche / Bespoke CDS Basket / First- & Nth-to-Default /
# Synthetic CDO) is one machine: a portfolio of credits, its loss distribution carved into tranches by
# seniority. This is the instrument that broke in 2008 — so it's the sharpest test of the program's thesis
# (what's real vs fee-in-a-suit). We model it honestly with the market-standard one-factor GAUSSIAN COPULA:
#   N names, each defaults over the horizon w.p. p; loss given default 1−R; a single systematic factor M ties
#   them together with correlation ρ (name i defaults iff √ρ·M + √(1−ρ)·Z_i < Φ⁻¹(p)). Conditional on M the
#   defaults are independent, so portfolio loss L = Binomial(N, q(M))·(1−R)/N. Tranche [a,d] absorbs the slice
#   of L between attachment a and detachment d.
# The honest questions:
#   (1) Does tranching CREATE value, or only REDISTRIBUTE the same expected loss? (sum of tranche $EL = port EL)
#   (2) The senior tranche's "AAA safety" — is it real, or a hidden bet that ρ stays low? (sweep ρ → 1)
#   (3) Who is long vs short correlation — and why the equity/senior split IS the whole trade.
# =============================================================================
from math import erf, sqrt
import numpy as np

_verf=np.vectorize(erf)
def Phi(x): return 0.5*(1+_verf(np.asarray(x,float)/sqrt(2)))     # vectorized normal CDF
def ppf(p):                                   # inverse normal via bisection (threshold only)
    lo,hi=-8.0,8.0
    for _ in range(100):
        m=(lo+hi)/2
        if float(Phi(m))<p: lo=m
        else: hi=m
    return (lo+hi)/2

N=125; R=0.40; LGD=1-R; TRIALS=400_000
TRANCHES=[("equity",0.00,0.03),("mezzanine",0.03,0.07),("senior",0.07,0.15),("super-senior",0.15,1.00)]
def tranche_loss(L,a,d): return np.clip(L-a,0,None).clip(0,d-a)/(d-a)   # fraction of tranche notional lost

def sim(p, rho, rng):
    thr=ppf(p); M=rng.standard_normal(TRIALS)
    q=Phi((thr - sqrt(rho)*M)/sqrt(1-rho))                 # default prob conditional on the systematic factor
    K=rng.binomial(N, q)                                   # number of defaults this scenario
    return K*LGD/N                                         # portfolio loss fraction

def run(p, rhos):
    rng=np.random.default_rng(7)
    print(f"\n  === index default prob p={p*100:.0f}% over the horizon, recovery {R*100:.0f}%, N={N} names ===")
    print(f"  portfolio expected loss = {p*LGD*100:.2f}% (invariant to ρ and to tranching)")
    print(f"  {'tranche [a–d]':<20}"+"".join(f"ρ={r:>4.2f}" .rjust(9) for r in rhos)+"   corr-delta")
    inv_check={}
    ELs={}
    for r in rhos:
        L=sim(p,r,rng); ELs[r]=L
    for nm,a,d in TRANCHES:
        row=[]
        for r in rhos:
            el=tranche_loss(ELs[r],a,d).mean(); row.append(el)
        delta=row[-1]-row[0]
        print(f"  {nm+' ['+f'{int(a*100)}-{int(d*100)}%]':<20}"+"".join(f"{v*100:>8.1f}%" for v in row)+f"   {delta*100:+7.1f}%")
    # invariance: sum of tranche dollar losses = portfolio loss, at a mid rho
    r=rhos[len(rhos)//2]; L=ELs[r]
    tot=sum((d-a)*tranche_loss(L,a,d).mean() for nm,a,d in TRANCHES)
    print(f"  invariance check @ ρ={r:.2f}: Σ tranche $-loss {tot*100:.2f}%  vs  portfolio EL {L.mean()*100:.2f}%  (equal ⇒ tranching only REDISTRIBUTES)")

print("="*104, "\nBLOCK CREDIT #6 — CDS INDEX TRANCHES: the correlation trade, and the 2008 lesson  (one-factor Gaussian copula)\n"+"="*104)
run(0.05, [0.10,0.30,0.50,0.70,0.90])
run(0.10, [0.10,0.30,0.50,0.70,0.90])
print("\n  READ (the catalog's most infamous instrument, honestly):")
print("  • TRANCHING CREATES NOTHING — it only REDISTRIBUTES. The invariance check is exact: Σ tranche $-loss =")
print("    portfolio expected loss (2.99% = 2.99%). Carving the loss into equity/mezz/senior doesn't add a dollar")
print("    of return or remove a dollar of loss; it slices the SAME loss by seniority to sell to different risk")
print("    appetites. The structuring fee buys the slicing service, not new edge — the purest fee-in-a-suit.")
print("  • THE SENIOR 'AAA SAFETY' IS A CORRELATION BET, not real safety. At ρ=0.10 the super-senior [15-100%]")
print("    loses 0.0% (bulletproof on paper — the AAA) and senior [7-15%] just 1.7%. Raise correlation and that")
print("    safety EVAPORATES: senior jumps to 8.7% (≈5×) and super-senior to 1.8% (p=5%) / 3.9% (p=10%). The rating")
print("    was a hidden assumption that ρ stays LOW. In 2008 ρ→1 (everything defaulted together) and the")
print("    'impossible' AAA super-senior losses simply happened — not a model glitch, a correlation bet coming due.")
print("  • THE TRADE *IS* THE EQUITY/SENIOR SPLIT. Equity is SHORT correlation (corr-delta −55%: higher ρ makes")
print("    defaults all-or-nothing, and the equity holder prefers that lottery to a steady bleed); senior is LONG")
print("    correlation risk (+6%). Selling a senior tranche = WRITING SYSTEMIC INSURANCE — you collect a thin")
print("    premium and are fine until the one event that correlates everything. The steamroller, at portfolio level.")
print("  • ONE MACHINE, MANY NAMES. First-to-default, Nth-to-default, bespoke basket, synthetic CDO — all the same")
print("    copula with different attachment points. The 'innovation' is repackaging correlation exposure; the")
print("    risk is that correlation is unstable and spikes exactly when it hurts.")
print("  VERDICT: the tranche makes a senior claim LOOK safe by hiding a correlation tail inside a flattering")
print("  metric (tiny expected loss) — the exact 'the metric flatters, the tail decides' law the whole Block")
print("  program keeps finding, in its most consequential form. No free lunch: it redistributes risk and prices")
print("  a correlation view; 2008 was the bill for selling systemic-correlation insurance and stamping it AAA.")
