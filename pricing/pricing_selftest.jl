#!/usr/bin/env julia
# pricing_selftest.jl — proves each reference pricer satisfies the identity it MUST. Run: julia pricing_selftest.jl
include(joinpath(@__DIR__, "block_pricing.jl")); using .BlockPricing
using Printf

pass = Ref(true)
chk(name, ok, detail="") = (pass[] &= ok; @printf("  [%s] %-46s %s\n", ok ? "PASS" : "FAIL", name, detail))

println("="^72, "\nBLOCK PRICING — reference-pricer sanity identities\n", "="^72, "\n")

# 1) vanilla option — put-call parity: C − P == S·e^{−qT} − K·e^{−rT}
S,K,T,r,σ,q = 100.0, 105.0, 0.75, 0.045, 0.22, 0.015
c = bs_option(; S,K,T,r,σ,q, kind=:call).price; p = bs_option(; S,K,T,r,σ,q, kind=:put).price
parity = S*exp(-q*T) - K*exp(-r*T)
chk("BS put-call parity", abs((c-p) - parity) < 1e-8, @sprintf("C−P=%.4f vs %.4f", c-p, parity))
# greeks: gamma>0, vega>0, call delta in (0,1)
g = bs_option(; S,K,T,r,σ,q, kind=:call)
chk("BS greeks well-formed", g.gamma>0 && g.vega>0 && 0<g.delta<1, @sprintf("Δ=%.3f Γ=%.4f ν=%.2f", g.delta, g.gamma, g.vega))

# 2) IRS — par swap rate zeroes the swap value
times = collect(0.5:0.5:5.0)                      # semi-annual, 5y
dfs   = exp.(-0.04 .* times)                       # flat 4% continuous curve
K★    = par_swap_rate(; times, discount_factors=dfs)
v0    = irs_value(; notional=1e7, fixed_rate=K★, times, discount_factors=dfs)
chk("IRS par swap has zero value", abs(v0) < 1e-6, @sprintf("par rate=%.4f%%  value=%.2e", 100K★, v0))
# above par => payer loses, below par => payer gains
vhi = irs_value(; notional=1e7, fixed_rate=K★+0.01, times, discount_factors=dfs)
chk("IRS payer value monotonic in fixed rate", vhi < 0, @sprintf("value at +100bp fixed = %.0f", vhi))

# 3) FX forward — covered interest parity + zero value at the contracted forward
F = fx_forward_rate(; spot=1.10, r_dom=0.045, r_for=0.028, T=1.0)
chk("FX forward = CIP", abs(F - 1.10*exp((0.045-0.028)*1.0)) < 1e-10, @sprintf("F=%.5f", F))
vf = fx_forward_value(; spot=1.10, r_dom=0.045, r_for=0.028, T=1.0, contracted_fwd=F, notional=1e6, side=:long)
chk("FX forward zero value at F", abs(vf) < 1e-6, @sprintf("value=%.2e", vf))

# 4) CDS — par spread zeroes it, and matches the credit triangle h·(1−R)
ct = collect(0.25:0.25:5.0); cdf = exp.(-0.03 .* ct); h, R = 0.02, 0.4
s★ = par_cds_spread(; times=ct, discount_factors=cdf, hazard=h, recovery=R)
vc = cds_value(; notional=1e7, spread=s★, times=ct, discount_factors=cdf, hazard=h, recovery=R)
chk("CDS par spread has zero value", abs(vc) < 1e-6, @sprintf("par spread=%.0f bp  value=%.2e", 1e4*s★, vc))
chk("CDS credit triangle (par ≈ h·(1−R))", abs(s★ - h*(1-R)) < 5e-4, @sprintf("%.0fbp vs %.0fbp", 1e4*s★, 1e4*h*(1-R)))
# buying protection gains value if hazard rises after entry
vup = cds_value(; notional=1e7, spread=s★, times=ct, discount_factors=cdf, hazard=0.04, recovery=R, side=:buyer)
chk("CDS buyer gains as hazard rises", vup > 0, @sprintf("value at 2×hazard = %.0f", vup))

println("\n", pass[] ? "ALL IDENTITIES HOLD ✓" : "SOME CHECKS FAILED ✗")
exit(pass[] ? 0 : 1)
